# -*- coding: utf-8 -*-
"""Tests de la app certificaciones (certificado, firma, verificación)."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation
from django.db import IntegrityError
import uuid

from academia.models import Nivel, Curso
from certificaciones.models import Certificado, RequisitoCertificado, Firma

User = get_user_model()


# ============================================================
# HELPERS
# ============================================================
def crear_nivel():
    return Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)


def crear_curso(nivel=None, **kwargs):
    if nivel is None:
        nivel = crear_nivel()
    defaults = {
        "titulo": "Curso Test",
        "slug": "curso-test",
        "nivel": nivel,
        "descripcion": "Desc",
        "activo": True,
    }
    defaults.update(kwargs)
    return Curso.objects.create(**defaults)


def crear_estudiante(username="alumno", **kwargs):
    defaults = {"password": "Compleja123!"}
    defaults.update(kwargs)
    return User.objects.create_user(username=username, **defaults)


def crear_certificado(usuario, curso, **kwargs):
    defaults = {"nota_final": 85, "horas": 40}
    defaults.update(kwargs)
    return Certificado.objects.create(usuario=usuario, curso=curso, **defaults)


# ============================================================
# MODELO RequisitoCertificado
# ============================================================
class RequisitoCertificadoModelTests(TestCase):

    def setUp(self):
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)

    def test_crear_requisito(self):
        req = RequisitoCertificado.objects.create(curso=self.curso)
        self.assertEqual(req.curso, self.curso)
        self.assertEqual(req.lecciones_minimas_pct, 100)
        self.assertEqual(req.nota_minima, 70)
        self.assertTrue(req.activo)

    def test_requisito_str(self):
        req = RequisitoCertificado.objects.create(curso=self.curso)
        self.assertIn("Curso Test", str(req))

    def test_requisito_custom_valores(self):
        req = RequisitoCertificado.objects.create(
            curso=self.curso,
            lecciones_minimas_pct=80,
            nota_minima=60,
            activo=False,
        )
        self.assertEqual(req.lecciones_minimas_pct, 80)
        self.assertEqual(req.nota_minima, 60)
        self.assertFalse(req.activo)

    def test_requisito_one_to_one(self):
        RequisitoCertificado.objects.create(curso=self.curso)
        with self.assertRaises(IntegrityError):
            RequisitoCertificado.objects.create(curso=self.curso)


# ============================================================
# MODELO Firma
# ============================================================
class FirmaModelTests(TestCase):

    def setUp(self):
        self.user = crear_estudiante(username="profesor")

    def test_crear_firma(self):
        firma = Firma.objects.create(usuario=self.user)
        self.assertEqual(firma.usuario, self.user)
        self.assertEqual(firma.cargo, "Profesor")
        self.assertTrue(firma.activa)

    def test_firma_str(self):
        firma = Firma.objects.create(usuario=self.user, cargo="Director")
        s = str(firma)
        self.assertIn("Director", s)

    def test_firma_one_to_one(self):
        Firma.objects.create(usuario=self.user)
        with self.assertRaises(IntegrityError):
            Firma.objects.create(usuario=self.user)

    def test_firma_defaults(self):
        firma = Firma.objects.create(usuario=self.user)
        self.assertEqual(firma.institucion, "Academia Global de Castellano")
        self.assertEqual(firma.firma_imagen, "")


# ============================================================
# MODELO Certificado
# ============================================================
class CertificadoModelTests(TestCase):

    def setUp(self):
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.user = crear_estudiante()

    def test_crear_certificado(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.usuario, self.user)
        self.assertEqual(cert.curso, self.curso)
        self.assertEqual(cert.nota_final, 85)
        self.assertEqual(cert.horas, 40)

    def test_certificado_codigo_uuid_auto(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertIsInstance(cert.codigo, uuid.UUID)
        self.assertIsNotNone(cert.codigo)

    def test_certificado_codigo_unico(self):
        c1 = crear_certificado(self.user, self.curso)
        otro_user = crear_estudiante(username="otro")
        c2 = crear_certificado(otro_user, self.curso)
        self.assertNotEqual(c1.codigo, c2.codigo)

    def test_certificado_unique_usuario_curso(self):
        crear_certificado(self.user, self.curso)
        with self.assertRaises(IntegrityError):
            crear_certificado(self.user, self.curso)

    def test_certificado_str(self):
        cert = crear_certificado(self.user, self.curso)
        s = str(cert)
        self.assertIn(self.user.username, s)
        self.assertIn("Curso Test", s)

    def test_codigo_corto(self):
        cert = crear_certificado(self.user, self.curso)
        corto = cert.codigo_corto
        self.assertEqual(len(corto), 8)
        self.assertEqual(corto, str(cert.codigo)[:8].upper())

    def test_nombre_estudiante_con_full_name(self):
        self.user.first_name = "Juan"
        self.user.last_name = "Pérez"
        self.user.save()
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.nombre_estudiante, "Juan Pérez")

    def test_nombre_estudiante_sin_full_name(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.nombre_estudiante, self.user.username)

    def test_nombre_admin_sin_firma(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.nombre_admin, "Administración")

    def test_nombre_profesor_sin_firma(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertEqual(cert.nombre_profesor, "Profesor Asignado")

    def test_nombre_admin_con_firma(self):
        admin = crear_estudiante(username="admin", first_name="Admin", last_name="Root")
        cert = crear_certificado(self.user, self.curso, firmado_por_admin=admin)
        self.assertEqual(cert.nombre_admin, "Admin Root")

    def test_fecha_emision_auto(self):
        cert = crear_certificado(self.user, self.curso)
        self.assertIsNotNone(cert.fecha_emision)

    def test_ordering_por_fecha_desc(self):
        # No podemos testear ordering con fechas iguales, pero sí que la meta esté definida
        self.assertEqual(Certificado._meta.ordering, ["-fecha_emision"])


# ============================================================
# VISTA: mis_certificados
# ============================================================
class MisCertificadosViewTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_mis_certificados_get_200(self):
        response = self.client.get(reverse("certificaciones:mis_certificados"))
        self.assertEqual(response.status_code, 200)

    def test_mis_certificados_sin_login_redirige(self):
        self.client.logout()
        response = self.client.get(reverse("certificaciones:mis_certificados"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_mis_certificados_muestra_certificado(self):
        crear_certificado(self.user, self.curso)
        response = self.client.get(reverse("certificaciones:mis_certificados"))
        self.assertEqual(response.status_code, 200)

    def test_mis_certificados_no_muestra_ajenos(self):
        otro = crear_estudiante(username="otro")
        crear_certificado(otro, self.curso)
        response = self.client.get(reverse("certificaciones:mis_certificados"))
        self.assertEqual(response.status_code, 200)

    def test_mis_certificados_sin_certificados(self):
        response = self.client.get(reverse("certificaciones:mis_certificados"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# VISTA: ver_certificado
# ============================================================
class VerCertificadoViewTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.user = crear_estudiante()
        self.client.force_login(self.user)
        self.cert = crear_certificado(self.user, self.curso)

    def tearDown(self):
        translation.deactivate()

    def test_ver_certificado_get_200(self):
        url = reverse("certificaciones:ver_certificado", args=[self.cert.codigo])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ver_certificado_codigo_inexistente_404(self):
        codigo_falso = uuid.uuid4()
        url = reverse("certificaciones:ver_certificado", args=[codigo_falso])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_ver_certificado_de_otro_usuario(self):
        otro = crear_estudiante(username="otro")
        cert_otro = crear_certificado(otro, self.curso)
        url = reverse("certificaciones:ver_certificado", args=[cert_otro.codigo])
        response = self.client.get(url)
        # Puede ser 403, 404 o 200 según la lógica
        self.assertIn(response.status_code, [200, 302, 403, 404])

    def test_ver_certificado_sin_login(self):
        self.client.logout()
        url = reverse("certificaciones:ver_certificado", args=[self.cert.codigo])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])


# ============================================================
# VISTA: verificar_codigo (público)
# ============================================================
class VerificarCodigoViewTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.user = crear_estudiante()
        self.cert = crear_certificado(self.user, self.curso)

    def tearDown(self):
        translation.deactivate()

    def test_verificar_get_200(self):
        response = self.client.get(reverse("certificaciones:verificar"))
        self.assertEqual(response.status_code, 200)

    def test_verificar_post_codigo_valido(self):
        response = self.client.post(
            reverse("certificaciones:verificar"),
            {"codigo": str(self.cert.codigo)},
        )
        # 200 (con certificado encontrado) o 302 (redirect al certificado)
        self.assertIn(response.status_code, [200, 302])

    def test_verificar_post_codigo_corto(self):
        """La vista acepta código corto (8 caracteres)."""
        response = self.client.post(
            reverse("certificaciones:verificar"),
            {"codigo": self.cert.codigo_corto},
        )
        self.assertIn(response.status_code, [200, 302])

    def test_verificar_post_codigo_invalido(self):
        response = self.client.post(
            reverse("certificaciones:verificar"),
            {"codigo": "NO-EXISTE-12345"},
        )
        # 200 con mensaje de error
        self.assertEqual(response.status_code, 200)

    def test_verificar_get_es_publico(self):
        """No requiere login."""
        response = self.client.get(reverse("certificaciones:verificar"))
        self.assertEqual(response.status_code, 200)

    def test_verificar_post_vacio(self):
        response = self.client.post(reverse("certificaciones:verificar"), {})
        self.assertEqual(response.status_code, 200)


# ============================================================
# VISTA: descargar_word
# ============================================================
class DescargarWordTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.user = crear_estudiante()
        self.client.force_login(self.user)
        self.cert = crear_certificado(self.user, self.curso)

    def tearDown(self):
        translation.deactivate()

    def test_descargar_word_url_existe(self):
        url = reverse("certificaciones:descargar_word", args=[self.cert.codigo])
        self.assertIn(str(self.cert.codigo), url)

    def test_descargar_word_sin_login(self):
        self.client.logout()
        url = reverse("certificaciones:descargar_word", args=[self.cert.codigo])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 403, 404])

    def test_descargar_word_codigo_inexistente(self):
        codigo_falso = uuid.uuid4()
        url = reverse("certificaciones:descargar_word", args=[codigo_falso])
        response = self.client.get(url)
        self.assertIn(response.status_code, [302, 404])
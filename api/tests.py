# -*- coding: utf-8 -*-
"""Tests de la API REST."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

from academia.models import Nivel, Curso, Modulo, Leccion, Inscripcion
from certificaciones.models import Certificado
from gamificacion.models import PerfilGamificacion

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


def crear_modulo(curso, titulo="M1", orden=1):
    return Modulo.objects.create(curso=curso, titulo=titulo, orden=orden)


def crear_leccion(curso, titulo="L1", slug="l1", orden=1, **kwargs):
    defaults = {"contenido": "<p>Contenido</p>", "activa": True}
    defaults.update(kwargs)
    return Leccion.objects.create(
        curso=curso, titulo=titulo, slug=slug, orden=orden, **defaults
    )


def crear_certificado(usuario, curso):
    return Certificado.objects.create(usuario=usuario, curso=curso)


def crear_api_client(user=None):
    client = APIClient()
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


# ============================================================
# AUTENTICACIÓN
# ============================================================
class AuthTokenTests(TestCase):
    """Tests del endpoint /api/auth/."""

    def setUp(self):
        self.user = crear_estudiante(username="apiuser")

    def test_auth_con_credenciales_validas(self):
        response = self.client.post(
            "/api/auth/",
            {"username": "apiuser", "password": "Compleja123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_auth_con_credenciales_invalidas(self):
        response = self.client.post(
            "/api/auth/",
            {"username": "apiuser", "password": "mal"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_endpoint_requiere_token(self):
        """Sin token, endpoints protegidos devuelven 401."""
        response = self.client.get("/api/cursos/")
        self.assertEqual(response.status_code, 401)


# ============================================================
# CURSOS
# ============================================================
class CursosAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.curso_inactivo = crear_curso(
            nivel=self.nivel, titulo="Inactivo", slug="inactivo", activo=False
        )

    def test_listar_cursos_solo_activos(self):
        response = self.client.get("/api/cursos/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # El curso activo debe estar, el inactivo no
        resultados = data.get("results", data)
        slugs = [c["slug"] for c in resultados]
        self.assertIn("curso-test", slugs)
        self.assertNotIn("inactivo", slugs)

    def test_detalle_curso(self):
        response = self.client.get(f"/api/cursos/{self.curso.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["titulo"], "Curso Test")

    def test_modulos_de_curso(self):
        crear_modulo(self.curso, titulo="Módulo 1")
        crear_modulo(self.curso, titulo="Módulo 2", orden=2)
        response = self.client.get(f"/api/cursos/{self.curso.id}/modulos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_lecciones_de_curso(self):
        crear_leccion(self.curso, titulo="L1", slug="l1", orden=1)
        crear_leccion(self.curso, titulo="L2", slug="l2", orden=2)
        response = self.client.get(f"/api/cursos/{self.curso.id}/lecciones/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)


# ============================================================
# MODULOS
# ============================================================
class ModulosAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.modulo = crear_modulo(self.curso)

    def test_listar_modulos(self):
        response = self.client.get("/api/modulos/")
        self.assertEqual(response.status_code, 200)

    def test_detalle_modulo(self):
        response = self.client.get(f"/api/modulos/{self.modulo.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["titulo"], "M1")

    def test_lecciones_de_modulo(self):
        crear_leccion(self.curso, titulo="L1", slug="l1", orden=1, modulo=self.modulo)
        crear_leccion(self.curso, titulo="L2", slug="l2", orden=2, modulo=self.modulo)
        response = self.client.get(f"/api/modulos/{self.modulo.id}/lecciones/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)


# ============================================================
# LECCIONES
# ============================================================
class LeccionesAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.leccion = crear_leccion(
            self.curso, contenido="<h2>Título</h2><p>Párrafo</p>"
        )

    def test_listar_lecciones(self):
        response = self.client.get("/api/lecciones/")
        self.assertEqual(response.status_code, 200)

    def test_detalle_leccion_incluye_contenido_html(self):
        response = self.client.get(f"/api/lecciones/{self.leccion.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("contenido", data)
        self.assertIn("<h2>", data["contenido"])


# ============================================================
# INSCRIPCIONES
# ============================================================
class InscripcionesAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)

    def test_listar_mis_inscripciones_vacio(self):
        response = self.client.get("/api/inscripciones/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        resultados = data.get("results", data)
        self.assertEqual(len(resultados), 0)

    def test_crear_inscripcion(self):
        response = self.client.post(
            "/api/inscripciones/",
            {"curso": self.curso.id},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Inscripcion.objects.filter(usuario=self.user, curso=self.curso).exists()
        )

    def test_no_duplicar_inscripcion(self):
        Inscripcion.objects.create(usuario=self.user, curso=self.curso)
        response = self.client.post(
            "/api/inscripciones/",
            {"curso": self.curso.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_no_inscribirse_en_curso_inactivo(self):
        curso_inactivo = crear_curso(
            nivel=self.nivel, titulo="X", slug="x", activo=False
        )
        response = self.client.post(
            "/api/inscripciones/",
            {"curso": curso_inactivo.id},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_solo_veo_mis_inscripciones(self):
        otro = crear_estudiante(username="otro")
        Inscripcion.objects.create(usuario=otro, curso=self.curso)
        response = self.client.get("/api/inscripciones/")
        data = response.json()
        resultados = data.get("results", data)
        self.assertEqual(len(resultados), 0)


# ============================================================
# CERTIFICADOS
# ============================================================
class CertificadosAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)

    def test_listar_mis_certificados(self):
        crear_certificado(self.user, self.curso)
        response = self.client.get("/api/certificados/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        resultados = data.get("results", data)
        self.assertEqual(len(resultados), 1)

    def test_solo_veo_mis_certificados(self):
        otro = crear_estudiante(username="otro")
        crear_certificado(otro, self.curso)
        response = self.client.get("/api/certificados/")
        data = response.json()
        resultados = data.get("results", data)
        self.assertEqual(len(resultados), 0)

    def test_certificado_tiene_codigo_corto(self):
        crear_certificado(self.user, self.curso)
        response = self.client.get("/api/certificados/")
        data = response.json()
        resultados = data.get("results", data)
        cert = resultados[0]
        self.assertIn("codigo_corto", cert)
        self.assertEqual(len(cert["codigo_corto"]), 8)


# ============================================================
# PERFIL
# ============================================================
class PerfilAPITests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.client = crear_api_client(self.user)

    def test_perfil_get(self):
        response = self.client.get("/api/perfil/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("xp_total", data)
        self.assertIn("nivel_actual", data)

    def test_perfil_crea_si_no_existe(self):
        self.assertFalse(PerfilGamificacion.objects.filter(usuario=self.user).exists())
        self.client.get("/api/perfil/")
        self.assertTrue(PerfilGamificacion.objects.filter(usuario=self.user).exists())
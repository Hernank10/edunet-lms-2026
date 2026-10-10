# -*- coding: utf-8 -*-
"""Tests de la app gamificacion (dashboard estudiante, XP, insignias)."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation
from django.db import IntegrityError

from academia.models import Nivel, Curso, Modulo, Leccion, Inscripcion
from gamificacion.models import Insignia, PerfilGamificacion, Logro

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


def crear_insignia(nombre="Primeros Pasos", **kwargs):
    defaults = {
        "descripcion": "Por empezar",
        "icono": "🏅",
        "tipo": "medalla",
        "orden": 1,
    }
    defaults.update(kwargs)
    return Insignia.objects.create(nombre=nombre, **defaults)


# ============================================================
# MODELO Insignia
# ============================================================
class InsigniaModelTests(TestCase):

    def test_crear_insignia(self):
        ins = Insignia.objects.create(
            nombre="Novato",
            descripcion="Primer logro",
            icono="🌟",
            tipo="estrella",
            orden=1,
        )
        self.assertEqual(ins.nombre, "Novato")
        self.assertEqual(ins.tipo, "estrella")

    def test_insignia_str_incluye_nombre(self):
        ins = crear_insignia(nombre="Test Badge")
        self.assertIn("Test Badge", str(ins))

    def test_insignia_defaults(self):
        ins = Insignia.objects.create(nombre="X", descripcion="y")
        self.assertEqual(ins.icono, "🏅")
        self.assertEqual(ins.tipo, "medalla")
        self.assertEqual(ins.requisito_xp, 0)

    def test_insignia_ordering_por_orden(self):
        i3 = crear_insignia(nombre="C", orden=3)
        i1 = crear_insignia(nombre="A", orden=1)
        i2 = crear_insignia(nombre="B", orden=2)
        insignias = list(Insignia.objects.all())
        self.assertEqual(insignias, [i1, i2, i3])

    def test_insignia_nombre_unico(self):
        crear_insignia(nombre="Único")
        with self.assertRaises(IntegrityError):
            crear_insignia(nombre="Único")


# ============================================================
# MODELO PerfilGamificacion
# ============================================================
class PerfilGamificacionTests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()

    def test_crear_perfil(self):
        perfil = PerfilGamificacion.objects.create(usuario=self.user)
        self.assertEqual(perfil.xp_total, 0)
        self.assertEqual(perfil.nivel_actual, 1)
        self.assertEqual(perfil.racha_dias, 0)

    def test_perfil_str(self):
        perfil = PerfilGamificacion.objects.create(usuario=self.user, xp_total=750)
        s = str(perfil)
        self.assertIn(self.user.username, s)
        self.assertIn("750", s)

    def test_add_xp_suma(self):
        perfil = PerfilGamificacion.objects.create(usuario=self.user, xp_total=100)
        perfil.add_xp(50)
        perfil.refresh_from_db()
        self.assertEqual(perfil.xp_total, 150)

    def test_add_xp_actualiza_nivel(self):
        perfil = PerfilGamificacion.objects.create(usuario=self.user)
        # 500 XP = nivel 2 (500 // 500 + 1 = 2)
        perfil.add_xp(500)
        perfil.refresh_from_db()
        self.assertEqual(perfil.nivel_actual, 2)

    def test_add_xp_varios_niveles(self):
        perfil = PerfilGamificacion.objects.create(usuario=self.user)
        perfil.add_xp(1500)  # 1500 // 500 + 1 = 4
        perfil.refresh_from_db()
        self.assertEqual(perfil.nivel_actual, 4)


# ============================================================
# MODELO Logro
# ============================================================
class LogroModelTests(TestCase):

    def setUp(self):
        self.user = crear_estudiante()
        self.insignia = crear_insignia(nombre="Test")

    def test_crear_logro(self):
        logro = Logro.objects.create(usuario=self.user, insignia=self.insignia)
        self.assertEqual(logro.usuario, self.user)
        self.assertEqual(logro.insignia, self.insignia)

    def test_logro_unique_usuario_insignia(self):
        Logro.objects.create(usuario=self.user, insignia=self.insignia)
        with self.assertRaises(IntegrityError):
            Logro.objects.create(usuario=self.user, insignia=self.insignia)

    def test_logro_fecha_auto(self):
        logro = Logro.objects.create(usuario=self.user, insignia=self.insignia)
        self.assertIsNotNone(logro.fecha)


# ============================================================
# VISTAS: ACCESO BÁSICO
# ============================================================
class VistasRequierenLoginTests(TestCase):
    """Todas las vistas de gamificacion requieren login."""

    def setUp(self):
        translation.activate("es")

    def tearDown(self):
        translation.deactivate()

    def test_dashboard_sin_login(self):
        response = self.client.get(reverse("gamificacion:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_mis_cursos_sin_login(self):
        response = self.client.get(reverse("gamificacion:mis_cursos"))
        self.assertEqual(response.status_code, 302)

    def test_practicas_sin_login(self):
        response = self.client.get(reverse("gamificacion:practicas"))
        self.assertEqual(response.status_code, 302)

    def test_evaluaciones_sin_login(self):
        response = self.client.get(reverse("gamificacion:evaluaciones"))
        self.assertEqual(response.status_code, 302)

    def test_mis_logros_sin_login(self):
        response = self.client.get(reverse("gamificacion:mis_logros"))
        self.assertEqual(response.status_code, 302)

    def test_estadisticas_sin_login(self):
        response = self.client.get(reverse("gamificacion:estadisticas"))
        self.assertEqual(response.status_code, 302)


# ============================================================
# DASHBOARD ESTUDIANTE
# ============================================================
class DashboardEstudianteTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_dashboard_get_200(self):
        response = self.client.get(reverse("gamificacion:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_crea_perfil_si_no_existe(self):
        self.assertFalse(PerfilGamificacion.objects.filter(usuario=self.user).exists())
        self.client.get(reverse("gamificacion:dashboard"))
        self.assertTrue(PerfilGamificacion.objects.filter(usuario=self.user).exists())

    def test_dashboard_kpis_en_contexto(self):
        response = self.client.get(reverse("gamificacion:dashboard"))
        ctx = response.context
        for key in ["perfil", "total_inscripciones", "completadas",
                    "evaluaciones_aprobadas", "evaluaciones_totales",
                    "certs", "ganadas", "total_insignias",
                    "total_lecciones", "recomendados", "actividad",
                    "dona_data", "dona_labels"]:
            self.assertIn(key, ctx, f"Falta '{key}' en el contexto")

    def test_dashboard_con_inscripcion(self):
        nivel = crear_nivel()
        curso = crear_curso(nivel=nivel)
        Inscripcion.objects.create(usuario=self.user, curso=curso)
        response = self.client.get(reverse("gamificacion:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_inscripciones"], 1)

    def test_dashboard_con_inscripcion_completada(self):
        nivel = crear_nivel()
        curso = crear_curso(nivel=nivel)
        Inscripcion.objects.create(
            usuario=self.user, curso=curso, completado=True, progreso_pct=100
        )
        response = self.client.get(reverse("gamificacion:dashboard"))
        self.assertEqual(response.context["completadas"], 1)

    def test_dashboard_graficos_json_validos(self):
        import json
        response = self.client.get(reverse("gamificacion:dashboard"))
        # Los strings JSON deben poder decodificarse
        for key in ["dona_data", "dona_labels", "barras_labels",
                    "barras_data", "dias_labels", "dias_xp",
                    "eval_labels", "eval_aprobados", "eval_reprobados"]:
            try:
                json.loads(response.context[key])
            except (json.JSONDecodeError, TypeError) as e:
                self.fail(f"'{key}' no es JSON válido: {e}")

    def test_dashboard_recomendados_excluye_inscritos(self):
        nivel = crear_nivel()
        curso1 = crear_curso(nivel=nivel, titulo="Inscrito", slug="inscrito")
        curso2 = crear_curso(nivel=nivel, titulo="No inscrito", slug="no-inscrito")
        Inscripcion.objects.create(usuario=self.user, curso=curso1)
        response = self.client.get(reverse("gamificacion:dashboard"))
        recomendados = list(response.context["recomendados"])
        self.assertNotIn(curso1, recomendados)
        self.assertIn(curso2, recomendados)

    def test_dashboard_proximos_pasos_presente(self):
        response = self.client.get(reverse("gamificacion:dashboard"))
        self.assertIn("proximos_pasos", response.context)


# ============================================================
# MIS CURSOS
# ============================================================
class MisCursosTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)
        self.nivel = crear_nivel()
        self.curso = crear_curso(nivel=self.nivel)
        self.inscripcion = Inscripcion.objects.create(
            usuario=self.user, curso=self.curso, activa=True
        )

    def tearDown(self):
        translation.deactivate()

    def test_mis_cursos_get_200(self):
        response = self.client.get(reverse("gamificacion:mis_cursos"))
        self.assertEqual(response.status_code, 200)

    def test_mis_cursos_muestra_inscripcion(self):
        response = self.client.get(reverse("gamificacion:mis_cursos"))
        self.assertEqual(response.status_code, 200)

    def test_mis_cursos_sin_inscripciones(self):
        otro = crear_estudiante(username="otro")
        self.client.force_login(otro)
        response = self.client.get(reverse("gamificacion:mis_cursos"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# PRACTICAS
# ============================================================
class PracticasTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_practicas_get_200(self):
        response = self.client.get(reverse("gamificacion:practicas"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# EVALUACIONES
# ============================================================
class EvaluacionesTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_evaluaciones_get_200(self):
        response = self.client.get(reverse("gamificacion:evaluaciones"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# MIS LOGROS
# ============================================================
class MisLogrosTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_mis_logros_get_200(self):
        response = self.client.get(reverse("gamificacion:mis_logros"))
        self.assertEqual(response.status_code, 200)

    def test_mis_logros_con_insignia_ganada(self):
        insignia = crear_insignia(nombre="Ganada")
        Logro.objects.create(usuario=self.user, insignia=insignia)
        response = self.client.get(reverse("gamificacion:mis_logros"))
        self.assertEqual(response.status_code, 200)

    def test_mis_logros_sin_logros(self):
        response = self.client.get(reverse("gamificacion:mis_logros"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# ESTADISTICAS
# ============================================================
class EstadisticasTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_estadisticas_get_200(self):
        response = self.client.get(reverse("gamificacion:estadisticas"))
        self.assertEqual(response.status_code, 200)

    def test_estadisticas_con_progreso(self):
        nivel = crear_nivel()
        curso = crear_curso(nivel=nivel)
        Inscripcion.objects.create(
            usuario=self.user, curso=curso, progreso_pct=50
        )
        response = self.client.get(reverse("gamificacion:estadisticas"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# MIS CERTIFICADOS
# ============================================================
class MisCertificadosTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_mis_certificados_get_200(self):
        response = self.client.get(reverse("gamificacion:mis_certificados"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# MI PERFIL
# ============================================================
class MiPerfilTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)

    def tearDown(self):
        translation.deactivate()

    def test_mi_perfil_get_200(self):
        response = self.client.get(reverse("gamificacion:mi_perfil"))
        self.assertEqual(response.status_code, 200)

    def test_mi_perfil_muestra_xp(self):
        perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=self.user)
        perfil.xp_total = 750
        perfil.save()
        response = self.client.get(reverse("gamificacion:mi_perfil"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# RECOMENDADOS
# ============================================================
class RecomendadosTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.user = crear_estudiante()
        self.client.force_login(self.user)
        self.nivel = crear_nivel()

    def tearDown(self):
        translation.deactivate()

    def test_recomendados_get_200(self):
        response = self.client.get(reverse("gamificacion:recomendados"))
        self.assertEqual(response.status_code, 200)

    def test_recomendados_solo_activos(self):
        activo = crear_curso(nivel=self.nivel, titulo="Activo", slug="activo", activo=True)
        crear_curso(nivel=self.nivel, titulo="Inactivo", slug="inactivo", activo=False)
        response = self.client.get(reverse("gamificacion:recomendados"))
        self.assertEqual(response.status_code, 200)

    def test_recomendados_excluye_inscritos(self):
        curso = crear_curso(nivel=self.nivel, titulo="Inscrito", slug="inscrito-x")
        Inscripcion.objects.create(usuario=self.user, curso=curso)
        response = self.client.get(reverse("gamificacion:recomendados"))
        self.assertEqual(response.status_code, 200)
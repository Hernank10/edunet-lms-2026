# -*- coding: utf-8 -*-
"""Tests de los modelos de la app academia."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils.text import slugify

from academia.models import Nivel, Curso, Modulo, Leccion, Inscripcion

User = get_user_model()


# ============================================================
# NIVEL
# ============================================================
class NivelModelTests(TestCase):
    """Tests del modelo Nivel."""

    def test_crear_nivel(self):
        nivel = Nivel.objects.create(
            codigo="A1",
            descripcion="Básico",
            orden=1,
        )
        self.assertEqual(nivel.codigo, "A1")
        self.assertEqual(nivel.descripcion, "Básico")
        self.assertEqual(nivel.orden, 1)

    def test_nivel_str(self):
        nivel = Nivel.objects.create(codigo="B1", descripcion="Intermedio", orden=2)
        # Acepta cualquier representación que incluya el código
        self.assertIn("B1", str(nivel))

    def test_niveles_multiples(self):
        Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)
        Nivel.objects.create(codigo="A2", descripcion="Básico alto", orden=2)
        Nivel.objects.create(codigo="B1", descripcion="Intermedio", orden=3)
        self.assertEqual(Nivel.objects.count(), 3)


# ============================================================
# CURSO
# ============================================================
class CursoModelTests(TestCase):
    """Tests del modelo Curso."""

    def setUp(self):
        self.nivel = Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)

    def test_crear_curso(self):
        curso = Curso.objects.create(
            titulo="Lengua Castellana 1",
            slug="lengua-castellana-1",
            nivel=self.nivel,
            descripcion="Curso de prueba",
        )
        self.assertEqual(curso.titulo, "Lengua Castellana 1")
        self.assertEqual(curso.slug, "lengua-castellana-1")
        self.assertEqual(curso.nivel, self.nivel)
        self.assertTrue(curso.activo)  # activo=True por defecto

    def test_curso_str(self):
        curso = Curso.objects.create(
            titulo="Curso Test",
            slug="curso-test",
            nivel=self.nivel,
            descripcion="x",
        )
        self.assertIn("Curso Test", str(curso))

    def test_slug_unico(self):
        Curso.objects.create(
            titulo="A", slug="slug-a", nivel=self.nivel, descripcion="x"
        )
        with self.assertRaises(IntegrityError):
            Curso.objects.create(
                titulo="B", slug="slug-a", nivel=self.nivel, descripcion="x"
            )

    def test_activo_por_defecto_true(self):
        curso = Curso.objects.create(
            titulo="Test", slug="test-activo", nivel=self.nivel, descripcion="x"
        )
        self.assertTrue(curso.activo)

    def test_curso_inactivo(self):
        curso = Curso.objects.create(
            titulo="Test", slug="test-inactivo", nivel=self.nivel,
            descripcion="x", activo=False,
        )
        self.assertFalse(curso.activo)

    def test_curso_pertenece_a_nivel(self):
        curso = Curso.objects.create(
            titulo="Test", slug="test-nivel", nivel=self.nivel, descripcion="x"
        )
        self.assertEqual(curso.nivel.codigo, "A1")
        self.assertIn(curso, self.nivel.cursos.all())


# ============================================================
# MODULO
# ============================================================
class ModuloModelTests(TestCase):
    """Tests del modelo Modulo."""

    def setUp(self):
        self.nivel = Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)
        self.curso = Curso.objects.create(
            titulo="Curso Test", slug="curso-test",
            nivel=self.nivel, descripcion="x",
        )

    def test_crear_modulo(self):
        modulo = Modulo.objects.create(
            curso=self.curso,
            titulo="Módulo 1: Morfología",
            orden=1,
        )
        self.assertEqual(modulo.titulo, "Módulo 1: Morfología")
        self.assertEqual(modulo.curso, self.curso)
        self.assertTrue(modulo.activo)
        self.assertIsNotNone(modulo.fecha_creacion)

    def test_modulo_str(self):
        modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        self.assertIn("M1", str(modulo))

    def test_num_lecciones_vacio(self):
        modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        self.assertEqual(modulo.num_lecciones, 0)

    def test_num_lecciones_con_lecciones(self):
        modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        for i in range(3):
            Leccion.objects.create(
                curso=self.curso,
                modulo=modulo,
                titulo=f"Lección {i+1}",
                slug=f"leccion-{i+1}",
                orden=i + 1,
                contenido="x",
            )
        self.assertEqual(modulo.num_lecciones, 3)

    def test_ordering_por_orden(self):
        m3 = Modulo.objects.create(curso=self.curso, titulo="M3", orden=3)
        m1 = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        m2 = Modulo.objects.create(curso=self.curso, titulo="M2", orden=2)
        modulos = list(Modulo.objects.all())
        self.assertEqual(modulos, [m1, m2, m3])

    def test_cascade_delete_curso(self):
        """Al borrar el curso, se borran sus módulos."""
        Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        self.assertEqual(Modulo.objects.count(), 1)
        self.curso.delete()
        self.assertEqual(Modulo.objects.count(), 0)


# ============================================================
# LECCION
# ============================================================
class LeccionModelTests(TestCase):
    """Tests del modelo Leccion."""

    def setUp(self):
        self.nivel = Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)
        self.curso = Curso.objects.create(
            titulo="Curso Test", slug="curso-test",
            nivel=self.nivel, descripcion="x",
        )

    def test_crear_leccion(self):
        lec = Leccion.objects.create(
            curso=self.curso,
            titulo="Sustantivos",
            slug="sustantivos",
            orden=1,
            contenido="Contenido de prueba",
        )
        self.assertEqual(lec.titulo, "Sustantivos")
        self.assertEqual(lec.contenido, "Contenido de prueba")
        self.assertTrue(lec.activa)

    def test_slug_automatico(self):
        """Si no se pasa slug, save() lo genera desde el título."""
        lec = Leccion.objects.create(
            curso=self.curso,
            titulo="Los Adjetivos",
            orden=1,
            contenido="x",
        )
        self.assertEqual(lec.slug, slugify("Los Adjetivos"))

    def test_leccion_sin_modulo(self):
        """Leccion.modulo es opcional (null=True, blank=True)."""
        lec = Leccion.objects.create(
            curso=self.curso,
            titulo="Sin módulo",
            slug="sin-modulo",
            orden=1,
            contenido="x",
        )
        self.assertIsNone(lec.modulo)

    def test_leccion_con_modulo(self):
        modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        lec = Leccion.objects.create(
            curso=self.curso,
            modulo=modulo,
            titulo="Con módulo",
            slug="con-modulo",
            orden=1,
            contenido="x",
        )
        self.assertEqual(lec.modulo, modulo)
        self.assertIn(lec, modulo.lecciones.all())

    def test_ordering_por_orden(self):
        l3 = Leccion.objects.create(
            curso=self.curso, titulo="L3", slug="l3", orden=3, contenido="x"
        )
        l1 = Leccion.objects.create(
            curso=self.curso, titulo="L1", slug="l1", orden=1, contenido="x"
        )
        l2 = Leccion.objects.create(
            curso=self.curso, titulo="L2", slug="l2", orden=2, contenido="x"
        )
        lecciones = list(Leccion.objects.all())
        self.assertEqual(lecciones, [l1, l2, l3])

    def test_modulo_set_null_al_borrar(self):
        """Al borrar el módulo, Leccion.modulo queda en NULL (SET_NULL)."""
        modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)
        lec = Leccion.objects.create(
            curso=self.curso, modulo=modulo, titulo="Test",
            slug="test-null", orden=1, contenido="x",
        )
        modulo.delete()
        lec.refresh_from_db()
        self.assertIsNone(lec.modulo)


# ============================================================
# INSCRIPCION
# ============================================================
class InscripcionModelTests(TestCase):
    """Tests del modelo Inscripcion."""

    def setUp(self):
        self.nivel = Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)
        self.curso = Curso.objects.create(
            titulo="Curso Test", slug="curso-test",
            nivel=self.nivel, descripcion="x",
        )
        self.user = User.objects.create_user(
            username="alumno", password="Compleja123!"
        )

    def test_crear_inscripcion(self):
        ins = Inscripcion.objects.create(usuario=self.user, curso=self.curso)
        self.assertEqual(ins.usuario, self.user)
        self.assertEqual(ins.curso, self.curso)
        self.assertTrue(ins.activa)
        self.assertFalse(ins.completado)
        self.assertEqual(ins.progreso_pct, 0)

    def test_progreso_pct(self):
        ins = Inscripcion.objects.create(
            usuario=self.user, curso=self.curso, progreso_pct=50
        )
        self.assertEqual(ins.progreso_pct, 50)

    def test_inscripcion_completada(self):
        ins = Inscripcion.objects.create(
            usuario=self.user, curso=self.curso,
            completado=True, progreso_pct=100,
        )
        self.assertTrue(ins.completado)
        self.assertEqual(ins.progreso_pct, 100)

    def test_inscripcion_unique_usuario_curso(self):
        """No se puede inscribir dos veces al mismo usuario en el mismo curso."""
        Inscripcion.objects.create(usuario=self.user, curso=self.curso)
        with self.assertRaises(IntegrityError):
            Inscripcion.objects.create(usuario=self.user, curso=self.curso)

    def test_dos_usuarios_pueden_inscribirse(self):
        user2 = User.objects.create_user(username="alumno2", password="Compleja123!")
        Inscripcion.objects.create(usuario=self.user, curso=self.curso)
        Inscripcion.objects.create(usuario=user2, curso=self.curso)
        self.assertEqual(Inscripcion.objects.filter(curso=self.curso).count(), 2)


# ============================================================
# RELACIÓN Curso → Modulo → Leccion
# ============================================================
class CursoModuloLeccionRelationTests(TestCase):
    """Tests de integridad de la jerarquía Curso → Módulo → Lección."""

    def setUp(self):
        self.nivel = Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)
        self.curso = Curso.objects.create(
            titulo="Curso Test", slug="curso-test",
            nivel=self.nivel, descripcion="x",
        )
        self.modulo = Modulo.objects.create(curso=self.curso, titulo="M1", orden=1)

    def test_jerarquia_completa(self):
        lec1 = Leccion.objects.create(
            curso=self.curso, modulo=self.modulo, titulo="L1",
            slug="l1", orden=1, contenido="x",
        )
        lec2 = Leccion.objects.create(
            curso=self.curso, modulo=self.modulo, titulo="L2",
            slug="l2", orden=2, contenido="x",
        )
        self.assertEqual(self.modulo.lecciones.count(), 2)
        self.assertIn(lec1, self.curso.lecciones.all())
        self.assertIn(lec2, self.curso.lecciones.all())

    def test_curso_tiene_modulos(self):
        Modulo.objects.create(curso=self.curso, titulo="M2", orden=2)
        self.assertEqual(self.curso.modulos.count(), 2)

    def test_cascade_delete_curso_borra_todo(self):
        Leccion.objects.create(
            curso=self.curso, modulo=self.modulo, titulo="L1",
            slug="l1", orden=1, contenido="x",
        )
        self.curso.delete()
        self.assertEqual(Modulo.objects.count(), 0)
        self.assertEqual(Leccion.objects.count(), 0)
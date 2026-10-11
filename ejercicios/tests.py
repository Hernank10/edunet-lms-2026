# -*- coding: utf-8 -*-
"""Tests de la app ejercicios (Ejercicio, Evaluacion, Pregunta, Intento)."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from academia.models import Nivel, Curso, Leccion
from ejercicios.models import (
    Ejercicio, Evaluacion, PreguntaEvaluacion, IntentoEvaluacion
)

User = get_user_model()


# ============================================================
# HELPERS
# ============================================================
def crear_nivel():
    return Nivel.objects.create(codigo="A1", descripcion="Básico", orden=1)


def crear_curso():
    nivel = crear_nivel()
    return Curso.objects.create(
        titulo="Curso Test", slug="curso-test",
        nivel=nivel, descripcion="x",
    )


def crear_leccion(curso):
    return Leccion.objects.create(
        curso=curso, titulo="L1", slug="l1",
        orden=1, contenido="x",
    )


# ============================================================
# EJERCICIO
# ============================================================
class EjercicioModelTests(TestCase):

    def setUp(self):
        self.curso = crear_curso()
        self.leccion = crear_leccion(self.curso)

    def test_crear_ejercicio(self):
        e = Ejercicio.objects.create(
            leccion=self.leccion,
            tipo="opcion_multiple",
            enunciado="¿Cuál es el sustantivo?",
            datos={"opciones": ["casa", "correr", "rápido"]},
        )
        self.assertEqual(e.tipo, "opcion_multiple")
        self.assertTrue(e.activo)

    def test_ejercicio_str(self):
        e = Ejercicio.objects.create(
            leccion=self.leccion, tipo="vf",
            enunciado="X", datos={},
        )
        self.assertIn("vf", str(e))

    def test_ejercicio_datos_json(self):
        datos = {"opciones": ["A", "B"], "correcta": 0}
        e = Ejercicio.objects.create(
            leccion=self.leccion, tipo="opcion_multiple",
            enunciado="X", datos=datos,
        )
        e.refresh_from_db()
        self.assertEqual(e.datos, datos)

    def test_ejercicio_ordering_por_orden(self):
        e3 = Ejercicio.objects.create(leccion=self.leccion, tipo="vf", enunciado="3", datos={}, orden=3)
        e1 = Ejercicio.objects.create(leccion=self.leccion, tipo="vf", enunciado="1", datos={}, orden=1)
        e2 = Ejercicio.objects.create(leccion=self.leccion, tipo="vf", enunciado="2", datos={}, orden=2)
        ejercicios = list(Ejercicio.objects.order_by("orden"))
        self.assertEqual(ejercicios, [e1, e2, e3])


# ============================================================
# EVALUACION
# ============================================================
class EvaluacionModelTests(TestCase):

    def setUp(self):
        self.curso = crear_curso()

    def test_crear_evaluacion(self):
        ev = Evaluacion.objects.create(
            curso=self.curso,
            titulo="Examen final",
            num_preguntas=10,
            nota_minima=70,
        )
        self.assertEqual(ev.titulo, "Examen final")
        self.assertEqual(ev.nota_minima, 70)
        self.assertTrue(ev.activo)

    def test_evaluacion_str(self):
        ev = Evaluacion.objects.create(curso=self.curso, titulo="Test")
        self.assertEqual(str(ev), "Test")

    def test_defaults(self):
        ev = Evaluacion.objects.create(curso=self.curso, titulo="X")
        self.assertEqual(ev.num_preguntas, 10)
        self.assertEqual(ev.nota_minima, 70)
        self.assertEqual(ev.orden, 1)

    def test_evaluacion_cascade_curso(self):
        Evaluacion.objects.create(curso=self.curso, titulo="X")
        self.curso.delete()
        self.assertEqual(Evaluacion.objects.count(), 0)


# ============================================================
# PREGUNTA
# ============================================================
class PreguntaModelTests(TestCase):

    def setUp(self):
        self.curso = crear_curso()
        self.ev = Evaluacion.objects.create(curso=self.curso, titulo="X")

    def test_crear_pregunta(self):
        p = PreguntaEvaluacion.objects.create(
            evaluacion=self.ev,
            orden=1,
            enunciado="¿Cuál es un verbo?",
            opciones=["casa", "correr", "rápido", "azul"],
            respuesta_correcta="correr",
        )
        self.assertEqual(p.orden, 1)
        self.assertEqual(p.opciones[1], "correr")

    def test_pregunta_unique_orden(self):
        PreguntaEvaluacion.objects.create(
            evaluacion=self.ev, orden=1,
            enunciado="X", opciones=["A"], respuesta_correcta="A",
        )
        with self.assertRaises(IntegrityError):
            PreguntaEvaluacion.objects.create(
                evaluacion=self.ev, orden=1,
                enunciado="Y", opciones=["B"], respuesta_correcta="B",
            )

    def test_pregunta_str(self):
        p = PreguntaEvaluacion.objects.create(
            evaluacion=self.ev, orden=3,
            enunciado="¿X?", opciones=[], respuesta_correcta="A",
        )
        self.assertIn("P3:", str(p))

    def test_pregunta_opciones_json(self):
        opciones = ["a", "b", "c", "d"]
        p = PreguntaEvaluacion.objects.create(
            evaluacion=self.ev, orden=1,
            enunciado="X", opciones=opciones, respuesta_correcta="a",
        )
        p.refresh_from_db()
        self.assertEqual(p.opciones, opciones)


# ============================================================
# INTENTO
# ============================================================
class IntentoModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="u", password="Compleja123!")
        self.curso = crear_curso()
        self.ev = Evaluacion.objects.create(curso=self.curso, titulo="X")

    def test_crear_intento(self):
        i = IntentoEvaluacion.objects.create(
            usuario=self.user, evaluacion=self.ev,
            nota=85, aprobado=True,
        )
        self.assertEqual(i.nota, 85)
        self.assertTrue(i.aprobado)

    def test_intento_str(self):
        i = IntentoEvaluacion.objects.create(
            usuario=self.user, evaluacion=self.ev, nota=75,
        )
        self.assertIn("75%", str(i))

    def test_defaults(self):
        i = IntentoEvaluacion.objects.create(usuario=self.user, evaluacion=self.ev)
        self.assertEqual(i.nota, 0)
        self.assertFalse(i.aprobado)

    def test_intento_cascade_usuario(self):
        IntentoEvaluacion.objects.create(usuario=self.user, evaluacion=self.ev)
        self.user.delete()
        self.assertEqual(IntentoEvaluacion.objects.count(), 0)
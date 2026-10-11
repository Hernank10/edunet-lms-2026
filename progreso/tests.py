# -*- coding: utf-8 -*-
"""Tests de la app progreso (ProgresoLeccion)."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone

from academia.models import Nivel, Curso, Leccion
from progreso.models import ProgresoLeccion

User = get_user_model()


# ============================================================
# HELPERS
# ============================================================
def crear_leccion():
    nivel = Nivel.objects.create(codigo="A1", descripcion="B", orden=1)
    curso = Curso.objects.create(
        titulo="C", slug="c", nivel=nivel, descripcion="x"
    )
    return Leccion.objects.create(
        curso=curso, titulo="L1", slug="l1", orden=1, contenido="x"
    )


# ============================================================
# ProgresoLeccion
# ============================================================
class ProgresoLeccionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="u", password="Compleja123!")
        self.leccion = crear_leccion()

    def test_crear_progreso(self):
        p = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=self.leccion
        )
        self.assertFalse(p.completada)
        self.assertIsNone(p.fecha_completada)

    def test_progreso_str_no_completada(self):
        p = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=self.leccion
        )
        s = str(p)
        self.assertIn("u", s)

    def test_progreso_str_completada(self):
        p = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=self.leccion,
            completada=True, fecha_completada=timezone.now(),
        )
        self.assertTrue(p.completada)
        self.assertIsNotNone(p.fecha_completada)

    def test_progreso_unique_usuario_leccion(self):
        ProgresoLeccion.objects.create(usuario=self.user, leccion=self.leccion)
        with self.assertRaises(IntegrityError):
            ProgresoLeccion.objects.create(
                usuario=self.user, leccion=self.leccion
            )

    def test_progreso_cascade_usuario(self):
        ProgresoLeccion.objects.create(usuario=self.user, leccion=self.leccion)
        self.user.delete()
        self.assertEqual(ProgresoLeccion.objects.count(), 0)

    def test_progreso_cascade_leccion(self):
        ProgresoLeccion.objects.create(usuario=self.user, leccion=self.leccion)
        self.leccion.delete()
        self.assertEqual(ProgresoLeccion.objects.count(), 0)

    def test_marcar_completada(self):
        p = ProgresoLeccion.objects.create(
            usuario=self.user, leccion=self.leccion
        )
        p.completada = True
        p.fecha_completada = timezone.now()
        p.save()
        p.refresh_from_db()
        self.assertTrue(p.completada)
        self.assertIsNotNone(p.fecha_completada)
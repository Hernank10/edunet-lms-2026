# -*- coding: utf-8 -*-
"""Tests de la app contenido (Recurso, Tecnica, HtmlInteractivo)."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation

from contenido.models import Recurso, Tecnica, ProgresoTecnica, HtmlInteractivo

User = get_user_model()


# ============================================================
# MODELOS
# ============================================================
class RecursoModelTests(TestCase):

    def test_crear_recurso(self):
        r = Recurso.objects.create(
            titulo="100 técnicas de morfología",
            categoria="morfologia",
            tipo_estructura="dict_con_tecnicas",
            total_declarado=100,
            total_real=100,
        )
        self.assertEqual(r.titulo, "100 técnicas de morfología")
        self.assertEqual(r.categoria, "morfologia")
        self.assertTrue(r.id)
        self.assertEqual(r.nivel, "general")  # default

    def test_recurso_str(self):
        r = Recurso.objects.create(
            titulo="Recurso X", categoria="otros",
            tipo_estructura="dict_con_tecnicas",
        )
        self.assertIn("[otros]", str(r))
        self.assertIn("Recurso X", str(r))

    def test_recurso_bilingue(self):
        r = Recurso.objects.create(
            titulo="Bilingüe", categoria="idiomas",
            tipo_estructura="lista_bilingue", bilingue=True,
        )
        self.assertTrue(r.bilingue)

    def test_recurso_ordering(self):
        r1 = Recurso.objects.create(
            titulo="Z", categoria="morfologia",
            tipo_estructura="dict_con_tecnicas",
        )
        r2 = Recurso.objects.create(
            titulo="A", categoria="morfologia",
            tipo_estructura="dict_con_tecnicas",
        )
        recursos = list(Recurso.objects.all())
        self.assertEqual(recursos, [r2, r1])  # por título


class TecnicaModelTests(TestCase):

    def setUp(self):
        self.recurso = Recurso.objects.create(
            titulo="R", categoria="otros", tipo_estructura="dict_con_tecnicas"
        )

    def test_crear_tecnica(self):
        t = Tecnica.objects.create(
            recurso=self.recurso,
            numero=1,
            nombre="Técnica 1",
            teoria="Teoría",
            ejemplo="Ejemplo",
        )
        self.assertEqual(t.numero, 1)
        self.assertEqual(t.recurso, self.recurso)

    def test_tecnica_str(self):
        t = Tecnica.objects.create(recurso=self.recurso, numero=5, nombre="X")
        self.assertIn("5.", str(t))

    def test_tecnica_unique_recurso_numero(self):
        from django.db import IntegrityError
        Tecnica.objects.create(recurso=self.recurso, numero=1, nombre="A")
        with self.assertRaises(IntegrityError):
            Tecnica.objects.create(recurso=self.recurso, numero=1, nombre="B")

    def test_tecnica_cascade_delete_recurso(self):
        Tecnica.objects.create(recurso=self.recurso, numero=1, nombre="A")
        self.recurso.delete()
        self.assertEqual(Tecnica.objects.count(), 0)


class ProgresoTecnicaModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="u", password="Compleja123!")
        self.recurso = Recurso.objects.create(
            titulo="R", categoria="otros", tipo_estructura="dict_con_tecnicas"
        )
        self.tecnica = Tecnica.objects.create(
            recurso=self.recurso, numero=1, nombre="T1"
        )

    def test_crear_progreso(self):
        p = ProgresoTecnica.objects.create(usuario=self.user, tecnica=self.tecnica)
        self.assertFalse(p.completada)

    def test_progreso_unique(self):
        from django.db import IntegrityError
        ProgresoTecnica.objects.create(usuario=self.user, tecnica=self.tecnica)
        with self.assertRaises(IntegrityError):
            ProgresoTecnica.objects.create(usuario=self.user, tecnica=self.tecnica)

    def test_marcar_completada(self):
        p = ProgresoTecnica.objects.create(
            usuario=self.user, tecnica=self.tecnica, completada=True
        )
        self.assertTrue(p.completada)


class HtmlInteractivoModelTests(TestCase):

    def test_crear_html(self):
        h = HtmlInteractivo.objects.create(
            titulo="Cuaderno de morfología",
            slug="cuaderno-morfologia",
            categoria="morfologia",
            tipo="cuaderno",
            num_tecnicas=100,
        )
        self.assertEqual(h.titulo, "Cuaderno de morfología")
        self.assertEqual(h.slug, "cuaderno-morfologia")

    def test_html_str(self):
        h = HtmlInteractivo.objects.create(
            titulo="X", slug="x", categoria="otros", tipo="flota"
        )
        self.assertIn("[flota]", str(h))

    def test_slug_unico(self):
        from django.db import IntegrityError
        HtmlInteractivo.objects.create(
            titulo="A", slug="unico", categoria="otros", tipo="otro"
        )
        with self.assertRaises(IntegrityError):
            HtmlInteractivo.objects.create(
                titulo="B", slug="unico", categoria="otros", tipo="otro"
            )

    def test_url_static(self):
        h = HtmlInteractivo.objects.create(
            titulo="X", slug="x", categoria="otros", tipo="flota",
            archivo_static="html/test.html",
        )
        self.assertEqual(h.url_static, "/static/html/test.html")

    def test_url_visor(self):
        h = HtmlInteractivo.objects.create(
            titulo="X", slug="mi-slug", categoria="otros", tipo="flota"
        )
        self.assertEqual(h.url_visor, "/html/mi-slug/")


# ============================================================
# VISTAS
# ============================================================
class ContenidoViewsTests(TestCase):

    def setUp(self):
        translation.activate("es")
        self.recurso = Recurso.objects.create(
            titulo="R1", categoria="morfologia",
            tipo_estructura="dict_con_tecnicas",
        )
        self.tecnica = Tecnica.objects.create(
            recurso=self.recurso, numero=1, nombre="T1", teoria="Teoría"
        )
        self.html = HtmlInteractivo.objects.create(
            titulo="H1", slug="h1", categoria="morfologia",
            tipo="cuaderno", archivo_static="html/h1.html",
        )

    def tearDown(self):
        translation.deactivate()

    def test_hub_get_200(self):
        response = self.client.get(reverse("contenido:hub"))
        self.assertEqual(response.status_code, 200)

    def test_lista_recursos_get_200(self):
        response = self.client.get(reverse("contenido:lista_recursos"))
        self.assertEqual(response.status_code, 200)

    def test_detalle_recurso_get_200(self):
        response = self.client.get(
            reverse("contenido:detalle_recurso", args=[self.recurso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_tecnica_detalle_get_200(self):
        response = self.client.get(
            reverse("contenido:tecnica", args=[self.tecnica.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_lista_htmls_get_200(self):
        response = self.client.get(reverse("contenido:lista_htmls"))
        self.assertEqual(response.status_code, 200)

    def test_visor_html_get_200(self):
        response = self.client.get(
            reverse("contenido:visor_html", args=[self.html.slug])
        )
        self.assertEqual(response.status_code, 200)
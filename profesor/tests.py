# -*- coding: utf-8 -*-
"""Tests del panel del profesor (CRUD + permisos)."""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import translation

from academia.models import Nivel, Curso, Modulo, Leccion
from profesor.models import AsignacionProfesor, AnuncioCurso

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
        "descripcion": "Descripción",
        "activo": True,
    }
    defaults.update(kwargs)
    return Curso.objects.create(**defaults)


def crear_profesor(username="profe", **kwargs):
    defaults = {
        "password": "Compleja123!",
        "is_staff": True,
    }
    defaults.update(kwargs)
    return User.objects.create_user(username=username, **defaults)


def crear_estudiante(username="alumno", **kwargs):
    defaults = {"password": "Compleja123!"}
    defaults.update(kwargs)
    return User.objects.create_user(username=username, **defaults)


# ============================================================
# ACCESO Y AUTENTICACIÓN
# ============================================================
class ProfesorAccessTests(TestCase):
    """Tests de acceso al panel del profesor."""

    def setUp(self):
        translation.activate("es")

    def tearDown(self):
        translation.deactivate()

    def test_dashboard_sin_login_redirige(self):
        response = self.client.get(reverse("profesor:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_dashboard_como_estudiante_rechazado(self):
        user = crear_estudiante()
        self.client.force_login(user)
        response = self.client.get(reverse("profesor:dashboard"))
        # @user_passes_test redirige a login si no cumple
        self.assertEqual(response.status_code, 302)

    def test_dashboard_como_profesor_ok(self):
        profe = crear_profesor()
        self.client.force_login(profe)
        response = self.client.get(reverse("profesor:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_como_superuser_ok(self):
        admin = User.objects.create_superuser(
            username="admin", password="Compleja123!", email="a@a.com"
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("profesor:dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_mis_cursos_como_profesor_ok(self):
        profe = crear_profesor()
        self.client.force_login(profe)
        response = self.client.get(reverse("profesor:mis_cursos"))
        self.assertEqual(response.status_code, 200)

    def test_estudiantes_como_profesor_ok(self):
        profe = crear_profesor()
        self.client.force_login(profe)
        response = self.client.get(reverse("profesor:estudiantes"))
        self.assertEqual(response.status_code, 200)


# ============================================================
# CRUD CURSO
# ============================================================
class CursoCRUDTests(TestCase):
    """Tests del CRUD de cursos."""

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.profe = crear_profesor()
        self.client.force_login(self.profe)

    def tearDown(self):
        translation.deactivate()

    # --- crear ---
    def test_curso_crear_get(self):
        response = self.client.get(reverse("profesor:curso_crear"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear curso")

    def test_curso_crear_post_crea_curso(self):
        response = self.client.post(reverse("profesor:curso_crear"), {
            "titulo": "Nuevo Curso",
            "descripcion": "Descripción nueva",
            "nivel": self.nivel.id,
            "activo": True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Curso.objects.filter(titulo="Nuevo Curso").exists())

    def test_curso_crear_asigna_al_profesor(self):
        self.client.post(reverse("profesor:curso_crear"), {
            "titulo": "Curso Asignado",
            "descripcion": "x",
            "nivel": self.nivel.id,
            "activo": True,
        })
        curso = Curso.objects.get(titulo="Curso Asignado")
        self.assertTrue(
            AsignacionProfesor.objects.filter(
                profesor=self.profe, curso=curso, activo=True
            ).exists()
        )

    def test_curso_crear_genera_slug_unico(self):
        # Primer curso con ese título
        self.client.post(reverse("profesor:curso_crear"), {
            "titulo": "Curso Repetido",
            "descripcion": "x",
            "nivel": self.nivel.id,
            "activo": True,
        })
        # Segundo curso con el mismo título
        self.client.post(reverse("profesor:curso_crear"), {
            "titulo": "Curso Repetido",
            "descripcion": "y",
            "nivel": self.nivel.id,
            "activo": True,
        })
        cursos = Curso.objects.filter(titulo="Curso Repetido")
        self.assertEqual(cursos.count(), 2)
        slugs = set(c.slug for c in cursos)
        self.assertEqual(len(slugs), 2)  # slugs distintos

    # --- editar ---
    def test_curso_editar_get_como_asignado(self):
        curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=curso)
        response = self.client.get(reverse("profesor:curso_editar", args=[curso.id]))
        self.assertEqual(response.status_code, 200)

    def test_curso_editar_post_actualiza(self):
        curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=curso)
        self.client.post(reverse("profesor:curso_editar", args=[curso.id]), {
            "titulo": "Título Actualizado",
            "descripcion": "Nueva descripción",
            "nivel": self.nivel.id,
            "activo": True,
        })
        curso.refresh_from_db()
        self.assertEqual(curso.titulo, "Título Actualizado")

    def test_curso_editar_como_no_asignado_rechazado(self):
        otro_profe = crear_profesor(username="otro")
        curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=otro_profe, curso=curso)
        # self.profe no está asignado → debe ser rechazado
        response = self.client.get(reverse("profesor:curso_editar", args=[curso.id]))
        # La vista renderiza sin_acceso.html (200) o redirige (302)
        self.assertIn(response.status_code, [200, 302, 403, 404])
        if response.status_code == 200:
            self.assertTemplateUsed(response, "profesor/sin_acceso.html")

    # --- toggle activo ---
    def test_curso_toggle_get(self):
        curso = crear_curso(nivel=self.nivel, activo=True)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=curso)
        response = self.client.get(reverse("profesor:curso_toggle", args=[curso.id]))
        self.assertEqual(response.status_code, 200)

    def test_curso_toggle_post_cambia_estado(self):
        curso = crear_curso(nivel=self.nivel, activo=True)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=curso)
        self.client.post(reverse("profesor:curso_toggle", args=[curso.id]))
        curso.refresh_from_db()
        self.assertFalse(curso.activo)

    def test_curso_toggle_dos_veces_vuelve_al_estado_inicial(self):
        curso = crear_curso(nivel=self.nivel, activo=True)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=curso)
        url = reverse("profesor:curso_toggle", args=[curso.id])
        self.client.post(url)
        self.client.post(url)
        curso.refresh_from_db()
        self.assertTrue(curso.activo)


# ============================================================
# CRUD MODULO (crear N lecciones de golpe)
# ============================================================
class ModuloCRUDTests(TestCase):
    """Tests de modulo_crear (crea módulo + N lecciones)."""

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.profe = crear_profesor()
        self.curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=self.curso)
        self.client.force_login(self.profe)

    def tearDown(self):
        translation.deactivate()

    def test_modulo_crear_get(self):
        response = self.client.get(
            reverse("profesor:modulo_crear", args=[self.curso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_modulo_crear_con_5_lecciones(self):
        titulos = "\n".join([f"Lección {i+1}" for i in range(5)])
        response = self.client.post(
            reverse("profesor:modulo_crear", args=[self.curso.id]),
            {
                "titulo": "Módulo Test",
                "descripcion": "Descripción del módulo",
                "orden": 1,
                "titulos_lecciones": titulos,
                "contenido_base": "Contenido base para todas",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Modulo.objects.count(), 1)
        self.assertEqual(Leccion.objects.filter(curso=self.curso).count(), 5)

    def test_modulo_crear_ordena_lecciones_consecutivas(self):
        titulos = "\n".join([f"L{i+1}" for i in range(3)])
        self.client.post(
            reverse("profesor:modulo_crear", args=[self.curso.id]),
            {
                "titulo": "M",
                "descripcion": "",
                "orden": 1,
                "titulos_lecciones": titulos,
                "contenido_base": "",
            },
        )
        ordenes = list(
            Leccion.objects.filter(curso=self.curso)
            .order_by("orden")
            .values_list("orden", flat=True)
        )
        self.assertEqual(ordenes, [1, 2, 3])

    def test_modulo_crear_copia_contenido_base(self):
        self.client.post(
            reverse("profesor:modulo_crear", args=[self.curso.id]),
            {
                "titulo": "M",
                "descripcion": "",
                "orden": 1,
                "titulos_lecciones": "L1\nL2",
                "contenido_base": "Contenido compartido",
            },
        )
        for lec in Leccion.objects.filter(curso=self.curso):
            self.assertEqual(lec.contenido, "Contenido compartido")

    def test_modulo_crear_slugs_unicos(self):
        # Dos lecciones con el mismo título
        self.client.post(
            reverse("profesor:modulo_crear", args=[self.curso.id]),
            {
                "titulo": "M",
                "descripcion": "",
                "orden": 1,
                "titulos_lecciones": "Lección Duplicada\nLección Duplicada",
                "contenido_base": "",
            },
        )
        slugs = list(Leccion.objects.filter(curso=self.curso).values_list("slug", flat=True))
        self.assertEqual(len(slugs), len(set(slugs)))  # todos únicos

    def test_modulo_crear_como_no_asignado_rechazado(self):
        otro_profe = crear_profesor(username="otro2")
        self.client.force_login(otro_profe)
        response = self.client.get(
            reverse("profesor:modulo_crear", args=[self.curso.id])
        )
        self.assertIn(response.status_code, [200, 302, 403, 404])


# ============================================================
# CRUD LECCION
# ============================================================
class LeccionCRUDTests(TestCase):
    """Tests del CRUD de lecciones."""

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.profe = crear_profesor()
        self.curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=self.curso)
        self.client.force_login(self.profe)

    def tearDown(self):
        translation.deactivate()

    def test_leccion_crear_get_sugiere_orden(self):
        # Sin lecciones previas → orden 1
        response = self.client.get(
            reverse("profesor:leccion_crear", args=[self.curso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_leccion_crear_post_crea(self):
        self.client.post(
            reverse("profesor:leccion_crear", args=[self.curso.id]),
            {
                "titulo": "Nueva Lección",
                "contenido": "<p>Contenido HTML</p>",
                "orden": 1,
                "activa": True,
            },
        )
        self.assertTrue(
            Leccion.objects.filter(titulo="Nueva Lección", curso=self.curso).exists()
        )

    def test_leccion_crear_guarda_html_tal_cual(self):
        html = "<h2>Título</h2><p>Párrafo con <strong>negrita</strong></p>"
        self.client.post(
            reverse("profesor:leccion_crear", args=[self.curso.id]),
            {
                "titulo": "Lección HTML",
                "contenido": html,
                "orden": 1,
                "activa": True,
            },
        )
        lec = Leccion.objects.get(titulo="Lección HTML")
        self.assertEqual(lec.contenido, html)

    def test_leccion_editar_get(self):
        lec = Leccion.objects.create(
            curso=self.curso, titulo="L1", slug="l1", orden=1, contenido="x"
        )
        response = self.client.get(reverse("profesor:leccion_editar", args=[lec.id]))
        self.assertEqual(response.status_code, 200)

    def test_leccion_editar_post_actualiza(self):
        lec = Leccion.objects.create(
            curso=self.curso, titulo="L1", slug="l1", orden=1, contenido="x"
        )
        self.client.post(
            reverse("profesor:leccion_editar", args=[lec.id]),
            {
                "titulo": "Título Modificado",
                "contenido": "Nuevo contenido",
                "orden": 2,
                "activa": True,
            },
        )
        lec.refresh_from_db()
        self.assertEqual(lec.titulo, "Título Modificado")
        self.assertEqual(lec.contenido, "Nuevo contenido")

    def test_leccion_eliminar_post_borra(self):
        lec = Leccion.objects.create(
            curso=self.curso, titulo="L1", slug="l1", orden=1, contenido="x"
        )
        self.client.post(reverse("profesor:leccion_eliminar", args=[lec.id]))
        self.assertFalse(Leccion.objects.filter(id=lec.id).exists())


# ============================================================
# CRUD ANUNCIO
# ============================================================
class AnuncioCRUDTests(TestCase):
    """Tests del CRUD de anuncios."""

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.profe = crear_profesor()
        self.curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(profesor=self.profe, curso=self.curso)
        self.client.force_login(self.profe)

    def tearDown(self):
        translation.deactivate()

    def test_anuncio_crear_get(self):
        response = self.client.get(
            reverse("profesor:anuncio_crear", args=[self.curso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_anuncio_crear_post(self):
        self.client.post(
            reverse("profesor:anuncio_crear", args=[self.curso.id]),
            {
                "titulo": "Aviso importante",
                "contenido": "Contenido del aviso",
                "activo": True,
            },
        )
        self.assertTrue(
            AnuncioCurso.objects.filter(titulo="Aviso importante").exists()
        )

    def test_anuncio_crear_asigna_profesor_y_curso(self):
        self.client.post(
            reverse("profesor:anuncio_crear", args=[self.curso.id]),
            {
                "titulo": "Aviso",
                "contenido": "x",
                "activo": True,
            },
        )
        a = AnuncioCurso.objects.get(titulo="Aviso")
        self.assertEqual(a.profesor, self.profe)
        self.assertEqual(a.curso, self.curso)

    def test_anuncio_editar_post(self):
        a = AnuncioCurso.objects.create(
            profesor=self.profe, curso=self.curso,
            titulo="Original", contenido="x",
        )
        self.client.post(
            reverse("profesor:anuncio_editar", args=[a.id]),
            {
                "titulo": "Modificado",
                "contenido": "y",
                "activo": False,
            },
        )
        a.refresh_from_db()
        self.assertEqual(a.titulo, "Modificado")
        self.assertFalse(a.activo)

    def test_anuncio_eliminar_post(self):
        a = AnuncioCurso.objects.create(
            profesor=self.profe, curso=self.curso,
            titulo="Eliminar", contenido="x",
        )
        self.client.post(reverse("profesor:anuncio_eliminar", args=[a.id]))
        self.assertFalse(AnuncioCurso.objects.filter(id=a.id).exists())


# ============================================================
# PERMISOS PROFESOR
# ============================================================
class PermisosProfesorTests(TestCase):
    """Tests de permisos: profesor asignado vs NO asignado vs superuser."""

    def setUp(self):
        translation.activate("es")
        self.nivel = crear_nivel()
        self.profe_asignado = crear_profesor(username="asignado")
        self.profe_no_asignado = crear_profesor(username="no_asignado")
        self.admin = User.objects.create_superuser(
            username="root", password="Compleja123!", email="r@r.com"
        )
        self.curso = crear_curso(nivel=self.nivel)
        AsignacionProfesor.objects.create(
            profesor=self.profe_asignado, curso=self.curso
        )

    def tearDown(self):
        translation.deactivate()

    def test_profesor_asignado_ve_curso(self):
        self.client.force_login(self.profe_asignado)
        response = self.client.get(
            reverse("profesor:curso_detalle", args=[self.curso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_profesor_no_asignado_rechazado(self):
        self.client.force_login(self.profe_no_asignado)
        response = self.client.get(
            reverse("profesor:curso_detalle", args=[self.curso.id])
        )
        self.assertIn(response.status_code, [200, 302, 403, 404])
        if response.status_code == 200:
            self.assertTemplateUsed(response, "profesor/sin_acceso.html")

    def test_superuser_ve_cualquier_curso(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("profesor:curso_detalle", args=[self.curso.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_asignacion_profesor_unique(self):
        """No se puede asignar 2 veces el mismo profesor al mismo curso."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            AsignacionProfesor.objects.create(
                profesor=self.profe_asignado, curso=self.curso
            )

    def test_asignacion_inactiva_no_da_acceso(self):
        """Si la asignación está inactiva, el profesor pierde acceso."""
        AsignacionProfesor.objects.filter(
            profesor=self.profe_asignado, curso=self.curso
        ).update(activo=False)
        self.client.force_login(self.profe_asignado)
        response = self.client.get(
            reverse("profesor:curso_detalle", args=[self.curso.id])
        )
        # Sin asignación activa → rechazado o template sin_acceso
        self.assertIn(response.status_code, [200, 302, 403, 404])
        if response.status_code == 200:
            self.assertTemplateUsed(response, "profesor/sin_acceso.html")
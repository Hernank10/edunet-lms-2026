from django.urls import path
from . import views

app_name = "profesor"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Mis cursos
    path("cursos/", views.mis_cursos, name="mis_cursos"),

    path("curso/nuevo/", views.curso_crear, name="curso_crear"),

    # Curso detalle
    path("curso/<int:curso_id>/", views.curso_detalle, name="curso_detalle"),

    # CRUD Curso
    path("curso/<int:curso_id>/editar/", views.curso_editar, name="curso_editar"),
    path("curso/<int:curso_id>/toggle/", views.curso_toggle_activo, name="curso_toggle"),

    # CRUD Leccion
    path("curso/<int:curso_id>/leccion/nueva/", views.leccion_crear, name="leccion_crear"),

    path("curso/<int:curso_id>/modulo/nuevo/", views.modulo_crear, name="modulo_crear"),
    path("leccion/<int:leccion_id>/editar/", views.leccion_editar, name="leccion_editar"),
    path("leccion/<int:leccion_id>/eliminar/", views.leccion_eliminar, name="leccion_eliminar"),

    # CRUD Evaluacion
    path("curso/<int:curso_id>/evaluacion/nueva/", views.evaluacion_crear, name="evaluacion_crear"),
    path("evaluacion/<int:evaluacion_id>/", views.evaluacion_detalle, name="evaluacion_detalle"),
    path("evaluacion/<int:evaluacion_id>/editar/", views.evaluacion_editar, name="evaluacion_editar"),
    path("evaluacion/<int:evaluacion_id>/eliminar/", views.evaluacion_eliminar, name="evaluacion_eliminar"),

    # CRUD Pregunta
    path("evaluacion/<int:evaluacion_id>/pregunta/nueva/", views.pregunta_crear, name="pregunta_crear"),
    path("pregunta/<int:pregunta_id>/editar/", views.pregunta_editar, name="pregunta_editar"),
    path("pregunta/<int:pregunta_id>/eliminar/", views.pregunta_eliminar, name="pregunta_eliminar"),

    # CRUD Anuncio
    path("curso/<int:curso_id>/anuncio/nuevo/", views.anuncio_crear, name="anuncio_crear"),
    path("anuncio/<int:anuncio_id>/editar/", views.anuncio_editar, name="anuncio_editar"),
    path("anuncio/<int:anuncio_id>/eliminar/", views.anuncio_eliminar, name="anuncio_eliminar"),

    # Subir imagen (TinyMCE)
    path("subir-imagen/", views.subir_imagen, name="subir_imagen"),

    # Otros
    path("estudiantes/", views.estudiantes, name="estudiantes"),
    path("analiticas/", views.analiticas, name="analiticas"),
    path("certificados/", views.certificados, name="certificados"),
    path("curso/<int:curso_id>/anuncio/", views.crear_anuncio, name="crear_anuncio"),
]
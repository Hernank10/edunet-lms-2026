from django.urls import path
from . import views

app_name = "profesor"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cursos/", views.mis_cursos, name="mis_cursos"),
    path("curso/<int:curso_id>/", views.curso_detalle, name="curso_detalle"),
    path("curso/<int:curso_id>/anuncio/", views.crear_anuncio, name="crear_anuncio"),
    path("estudiantes/", views.estudiantes, name="estudiantes"),
    path("analiticas/", views.analiticas, name="analiticas"),
    path("certificados/", views.certificados, name="certificados"),
]

# -*- coding: utf-8 -*-
"""URLs de la API REST."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register(r"cursos", views.CursoViewSet, basename="curso")
router.register(r"modulos", views.ModuloViewSet, basename="modulo")
router.register(r"lecciones", views.LeccionViewSet, basename="leccion")
router.register(r"inscripciones", views.InscripcionViewSet, basename="inscripcion")
router.register(r"certificados", views.CertificadoViewSet, basename="certificado")
router.register(r"perfil", views.PerfilViewSet, basename="perfil")

urlpatterns = [
    path("", include(router.urls)),
]
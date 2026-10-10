# -*- coding: utf-8 -*-
"""ViewSets de la API REST."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from academia.models import Curso, Modulo, Leccion, Inscripcion
from certificaciones.models import Certificado
from gamificacion.models import PerfilGamificacion
from gamificacion.views import _get_perfil

from .serializers import (
    CursoListSerializer,
    CursoDetailSerializer,
    ModuloSerializer,
    LeccionListSerializer,
    LeccionDetailSerializer,
    InscripcionSerializer,
    InscripcionCreateSerializer,
    CertificadoSerializer,
    PerfilGamificacionSerializer,
)


# ============================================================
# CURSO
# ============================================================
class CursoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para cursos activos."""
    queryset = Curso.objects.filter(activo=True).select_related("nivel").order_by("-id")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CursoDetailSerializer
        return CursoListSerializer

    @action(detail=True, methods=["get"])
    def modulos(self, request, pk=None):
        """GET /api/cursos/{id}/modulos/"""
        curso = self.get_object()
        modulos = curso.modulos.filter(activo=True).order_by("orden")
        serializer = ModuloSerializer(modulos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def lecciones(self, request, pk=None):
        """GET /api/cursos/{id}/lecciones/"""
        curso = self.get_object()
        lecciones = curso.lecciones.filter(activa=True).order_by("orden")
        serializer = LeccionListSerializer(lecciones, many=True)
        return Response(serializer.data)


# ============================================================
# MODULO
# ============================================================
class ModuloViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para módulos."""
    queryset = Modulo.objects.filter(activo=True).select_related("curso").order_by("orden")
    serializer_class = ModuloSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def lecciones(self, request, pk=None):
        """GET /api/modulos/{id}/lecciones/"""
        modulo = self.get_object()
        lecciones = modulo.lecciones.filter(activa=True).order_by("orden")
        serializer = LeccionListSerializer(lecciones, many=True)
        return Response(serializer.data)


# ============================================================
# LECCION
# ============================================================
class LeccionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para lecciones."""
    queryset = Leccion.objects.filter(activa=True).select_related("curso", "modulo").order_by("curso_id", "orden")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return LeccionDetailSerializer
        return LeccionListSerializer


# ============================================================
# INSCRIPCION
# ============================================================
class InscripcionViewSet(viewsets.ModelViewSet):
    """ViewSet para las inscripciones del usuario autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Inscripcion.objects.filter(
            usuario=self.request.user
        ).select_related("curso").order_by("-fecha")

    def get_serializer_class(self):
        if self.action == "create":
            return InscripcionCreateSerializer
        return InscripcionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inscripcion = serializer.save()
        # Devolver la representación con el serializer completo
        response_serializer = InscripcionSerializer(inscripcion)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ============================================================
# CERTIFICADO
# ============================================================
class CertificadoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet de solo lectura para los certificados del usuario."""
    serializer_class = CertificadoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Certificado.objects.filter(
            usuario=self.request.user
        ).select_related("curso").order_by("-fecha_emision")


# ============================================================
# PERFIL DE GAMIFICACIÓN
# ============================================================
class PerfilViewSet(viewsets.ViewSet):
    """Endpoint /api/perfil/ para el perfil del usuario autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        perfil = _get_perfil(request.user)
        serializer = PerfilGamificacionSerializer(perfil)
        return Response(serializer.data)
# -*- coding: utf-8 -*-
"""Serializers de la API REST."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from academia.models import Nivel, Curso, Modulo, Leccion, Inscripcion
from certificaciones.models import Certificado
from gamificacion.models import PerfilGamificacion

User = get_user_model()


# ============================================================
# SERIALIZERS BÁSICOS
# ============================================================
class NivelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nivel
        fields = ["id", "codigo", "descripcion", "orden"]


class LeccionListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados (sin contenido HTML)."""
    class Meta:
        model = Leccion
        fields = ["id", "titulo", "slug", "orden", "activa", "modulo"]


class LeccionDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con el contenido HTML."""
    curso_titulo = serializers.CharField(source="curso.titulo", read_only=True)

    class Meta:
        model = Leccion
        fields = [
            "id", "titulo", "slug", "orden", "contenido",
            "activa", "modulo", "curso", "curso_titulo",
        ]


class ModuloSerializer(serializers.ModelSerializer):
    num_lecciones = serializers.IntegerField(read_only=True)

    class Meta:
        model = Modulo
        fields = [
            "id", "titulo", "descripcion", "orden",
            "activo", "curso", "num_lecciones", "fecha_creacion",
        ]


# ============================================================
# CURSO
# ============================================================
class CursoListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listado."""
    nivel_codigo = serializers.CharField(source="nivel.codigo", read_only=True)
    num_lecciones = serializers.SerializerMethodField()
    num_modulos = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = [
            "id", "titulo", "slug", "nivel", "nivel_codigo",
            "descripcion", "activo", "num_lecciones", "num_modulos",
        ]

    def get_num_lecciones(self, obj):
        return obj.lecciones.count()

    def get_num_modulos(self, obj):
        return obj.modulos.count()


class CursoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo con nivel anidado."""
    nivel = NivelSerializer(read_only=True)
    modulos = ModuloSerializer(many=True, read_only=True)

    class Meta:
        model = Curso
        fields = [
            "id", "titulo", "slug", "nivel", "descripcion",
            "activo", "modulos",
        ]


# ============================================================
# INSCRIPCION
# ============================================================
class InscripcionSerializer(serializers.ModelSerializer):
    curso_titulo = serializers.CharField(source="curso.titulo", read_only=True)
    curso_slug = serializers.CharField(source="curso.slug", read_only=True)

    class Meta:
        model = Inscripcion
        fields = [
            "id", "usuario", "curso", "curso_titulo", "curso_slug",
            "fecha", "activa", "completado", "progreso_pct",
        ]
        read_only_fields = ["usuario", "fecha"]


class InscripcionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear inscripciones (usuario se asigna automáticamente)."""
    class Meta:
        model = Inscripcion
        fields = ["curso"]

    def validate_curso(self, curso):
        if not curso.activo:
            raise serializers.ValidationError("El curso no está activo.")
        return curso

    def create(self, validated_data):
        usuario = self.context["request"].user
        curso = validated_data["curso"]
        inscripcion, created = Inscripcion.objects.get_or_create(
            usuario=usuario,
            curso=curso,
            defaults={"activa": True},
        )
        if not created:
            raise serializers.ValidationError("Ya estás inscrito en este curso.")
        return inscripcion


# ============================================================
# CERTIFICADO
# ============================================================
class CertificadoSerializer(serializers.ModelSerializer):
    curso_titulo = serializers.CharField(source="curso.titulo", read_only=True)
    codigo_corto = serializers.CharField(read_only=True)
    nombre_estudiante = serializers.CharField(read_only=True)
    nombre_admin = serializers.CharField(read_only=True)
    nombre_profesor = serializers.CharField(read_only=True)

    class Meta:
        model = Certificado
        fields = [
            "id", "codigo", "codigo_corto",
            "curso", "curso_titulo",
            "fecha_emision", "nota_final", "horas",
            "nombre_estudiante", "nombre_admin", "nombre_profesor",
        ]


# ============================================================
# PERFIL DE GAMIFICACIÓN
# ============================================================
class PerfilGamificacionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="usuario.username", read_only=True)

    class Meta:
        model = PerfilGamificacion
        fields = [
            "id", "username", "xp_total", "nivel_actual",
            "racha_dias", "cursos_completados", "lecciones_completadas",
        ]
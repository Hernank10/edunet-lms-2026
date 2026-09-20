from django.contrib import admin
from .models import Idioma, Nivel, Curso, Leccion, Inscripcion


@admin.register(Idioma)
class IdiomaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Nivel)
class NivelAdmin(admin.ModelAdmin):
    list_display = ("codigo", "descripcion", "orden")
    ordering = ("orden",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "nivel", "activo")
    list_filter = ("nivel", "activo")
    search_fields = ("titulo",)
    prepopulated_fields = {"slug": ("titulo",)}


@admin.register(Leccion)
class LeccionAdmin(admin.ModelAdmin):
    list_display = ("curso", "orden", "titulo", "activa")
    list_filter = ("activa", "curso")
    search_fields = ("titulo",)


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "curso", "progreso_pct", "completado", "fecha")
    list_filter = ("completado", "activa")
    search_fields = ("usuario__username", "curso__titulo")
    raw_id_fields = ("usuario", "curso")
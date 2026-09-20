from django.contrib import admin
from .models import AsignacionProfesor, AnuncioCurso, NotaProfesor


@admin.register(AsignacionProfesor)
class AsignacionProfesorAdmin(admin.ModelAdmin):
    list_display = ("profesor", "curso", "activo", "fecha_asignacion")
    list_filter = ("activo", "curso")
    search_fields = ("profesor__username", "curso__titulo")
    raw_id_fields = ("profesor", "curso")


@admin.register(AnuncioCurso)
class AnuncioCursoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "profesor", "curso", "fecha", "activo")
    list_filter = ("activo", "curso")
    search_fields = ("titulo", "contenido")


@admin.register(NotaProfesor)
class NotaProfesorAdmin(admin.ModelAdmin):
    list_display = ("profesor", "estudiante", "curso", "fecha")
    list_filter = ("curso",)
    search_fields = ("profesor__username", "estudiante__username", "texto")

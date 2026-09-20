from django.contrib import admin
from .models import ProgresoLeccion


@admin.register(ProgresoLeccion)
class ProgresoLeccionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "leccion", "completada", "fecha_completada")
    list_filter = ("completada", "leccion__curso")
    search_fields = ("usuario__username",)


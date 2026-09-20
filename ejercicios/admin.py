from django.contrib import admin
from .models import Ejercicio, Evaluacion, PreguntaEvaluacion, IntentoEvaluacion


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ("leccion", "tipo", "activo", "orden")
    list_filter = ("tipo", "activo")


class PreguntaInline(admin.TabularInline):
    model = PreguntaEvaluacion
    extra = 0
    fields = ("orden", "enunciado", "respuesta_correcta")


@admin.register(Evaluacion)
class EvaluacionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "curso", "num_preguntas", "nota_minima", "activo")
    list_filter = ("curso", "activo")
    search_fields = ("titulo",)
    inlines = [PreguntaInline]


@admin.register(PreguntaEvaluacion)
class PreguntaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ("evaluacion", "orden", "enunciado")
    list_filter = ("evaluacion",)


@admin.register(IntentoEvaluacion)
class IntentoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "evaluacion", "nota", "aprobado", "fecha")
    list_filter = ("aprobado", "evaluacion")

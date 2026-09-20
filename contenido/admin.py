from django.contrib import admin
from .models import Recurso, Tecnica, ProgresoTecnica, HtmlInteractivo


class TecnicaInline(admin.TabularInline):
    model = Tecnica
    extra = 0
    fields = ("numero", "nombre", "categoria_interna")


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "nivel", "total_real", "bilingue", "fecha_importacion")
    list_filter = ("categoria", "nivel", "bilingue", "tipo_estructura")
    search_fields = ("titulo", "subtitulo")
    inlines = [TecnicaInline]


@admin.register(Tecnica)
class TecnicaAdmin(admin.ModelAdmin):
    list_display = ("recurso", "numero", "nombre", "categoria_interna")
    list_filter = ("recurso__categoria",)
    search_fields = ("nombre", "teoria")


@admin.register(ProgresoTecnica)
class ProgresoTecnicaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "tecnica", "completada", "fecha")
    list_filter = ("completada",)



@admin.register(HtmlInteractivo)
class HtmlInteractivoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "tipo", "nivel", "num_tecnicas", "fecha_importacion")
    list_filter = ("categoria", "tipo", "nivel")
    search_fields = ("titulo", "descripcion")
    readonly_fields = ("fecha_importacion",)
    prepopulated_fields = {"slug": ("titulo",)}

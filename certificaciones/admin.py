from django.contrib import admin
from .models import Certificado, RequisitoCertificado


@admin.register(RequisitoCertificado)
class RequisitoCertificadoAdmin(admin.ModelAdmin):
    list_display = ("curso", "lecciones_minimas_pct", "nota_minima", "activo")


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "curso", "codigo_corto", "nota_final", "fecha_emision")
    list_filter = ("curso",)
    search_fields = ("usuario__username", "curso__titulo", "codigo")
    readonly_fields = ("codigo", "fecha_emision")

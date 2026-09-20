from django.contrib import admin
from .models import Certificado, RequisitoCertificado, Firma


@admin.register(RequisitoCertificado)
class RequisitoCertificadoAdmin(admin.ModelAdmin):
    list_display = ("curso", "lecciones_minimas_pct", "nota_minima", "activo")


@admin.register(Firma)
class FirmaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cargo", "institucion", "activa")
    list_filter = ("activa", "cargo")


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_corto", "usuario", "curso", "nota_final",
        "firmado_por_admin", "firmado_por_profesor", "fecha_emision"
    )
    list_filter = ("curso",)
    search_fields = ("usuario__username", "curso__titulo", "codigo")
    readonly_fields = ("codigo", "fecha_emision")
    raw_id_fields = ("usuario", "curso", "firmado_por_admin", "firmado_por_profesor")

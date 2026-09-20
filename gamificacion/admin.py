from django.contrib import admin
from .models import Insignia, Logro, PerfilGamificacion


@admin.register(Insignia)
class InsigniaAdmin(admin.ModelAdmin):
    list_display = ("icono", "nombre", "tipo", "requisito_xp")


@admin.register(PerfilGamificacion)
class PerfilGamificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nivel_actual", "xp_total", "racha_dias")


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ("usuario", "insignia", "fecha")

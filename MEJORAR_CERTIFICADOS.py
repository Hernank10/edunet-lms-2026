# -*- coding: utf-8 -*-
"""
MEJORAR_CERTIFICADOS.py
Añade campos de firma al certificado + mejoras al dashboard.
"""
import os
import sys
import django

BASE = r"E:\02_proyectos\edunet_academia"


def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {path}")


sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


# ============================================================
# 1. MEJORAR MODELO CERTIFICADO (añadir firmas)
# ============================================================
write("certificaciones/models.py", '''import uuid
from django.conf import settings
from django.db import models
from academia.models import Curso

User = settings.AUTH_USER_MODEL


class RequisitoCertificado(models.Model):
    """Requisitos para obtener el certificado de un curso."""
    curso = models.OneToOneField(
        Curso, on_delete=models.CASCADE, related_name="requisito_certificado"
    )
    lecciones_minimas_pct = models.PositiveIntegerField(default=100)
    nota_minima = models.PositiveIntegerField(default=70)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Requisitos: {self.curso.titulo}"

    class Meta:
        verbose_name = "Requisito de certificado"
        verbose_name_plural = "Requisitos de certificados"


class Firma(models.Model):
    """Firma de un administrador o profesor para certificados."""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="firma_certificado"
    )
    cargo = models.CharField(
        max_length=100,
        default="Profesor",
        help_text="Cargo que aparece bajo la firma (ej. Director, Profesor Titular)"
    )
    institucion = models.CharField(
        max_length=200,
        default="Academia Global de Castellano"
    )
    firma_imagen = models.CharField(
        max_length=500,
        blank=True,
        help_text="Ruta al archivo de imagen de la firma (opcional)"
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmas"

    def __str__(self):
        return f"{self.usuario.get_full_name|default:self.usuario.username} ({self.cargo})"


class Certificado(models.Model):
    """Certificado emitido a un estudiante al completar un curso."""
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="certificados"
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="certificados"
    )
    codigo = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    nota_final = models.PositiveIntegerField(default=100)
    horas = models.PositiveIntegerField(default=40)

    # Firmas
    firmado_por_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificados_firmados_admin",
        help_text="Administrador que firma el certificado"
    )
    firmado_por_profesor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificados_firmados_profesor",
        help_text="Profesor que firma el certificado"
    )

    # Cargo e institución congelados al momento de emisión
    cargo_admin = models.CharField(max_length=100, blank=True, default="Director General")
    cargo_profesor = models.CharField(max_length=100, blank=True, default="Profesor Titular")
    institucion = models.CharField(max_length=200, default="Academia Global de Castellano")

    pdf = models.FileField(upload_to="certificados/", blank=True, null=True)

    class Meta:
        unique_together = ("usuario", "curso")
        ordering = ["-fecha_emision"]
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def __str__(self):
        return f"{self.usuario.username} — {self.curso.titulo}"

    @property
    def codigo_corto(self):
        return str(self.codigo)[:8].upper()

    @property
    def nombre_estudiante(self):
        return self.usuario.get_full_name or self.usuario.username

    @property
    def nombre_admin(self):
        if self.firmado_por_admin:
            return self.firmado_por_admin.get_full_name or self.firmado_por_admin.username
        return "Administración"

    @property
    def nombre_profesor(self):
        if self.firmado_por_profesor:
            return self.firmado_por_profesor.get_full_name or self.firmado_por_profesor.username
        return "Profesor Asignado"
''')


# ============================================================
# 2. ACTUALIZAR ADMIN
# ============================================================
write("certificaciones/admin.py", '''from django.contrib import admin
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
''')


# ============================================================
# 3. VISTA DEL CERTIFICADO ESTILO DIPLOMA
# ============================================================
write("certificaciones/templates/certificaciones/ver_certificado.html", '''{% extends "base.html" %}

{% block content %}
<div class="container my-5">
  <div class="text-center mb-3">
    <a href="{% url 'certificaciones:mis_certificados' %}" class="btn btn-outline-secondary">
      ← Volver
    </a>
    <button onclick="window.print()" class="btn btn-primary">
      🖨️ Imprimir / Guardar como PDF
    </button>
  </div>

  <!-- DIPLOMA -->
  <div id="diploma" class="mx-auto p-5" style="max-width: 900px; background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); border: 15px double #b8860b; position: relative;">

    <!-- Esquinas decorativas -->
    <div style="position:absolute; top:10px; left:10px; font-size:2rem; color:#b8860b;">❦</div>
    <div style="position:absolute; top:10px; right:10px; font-size:2rem; color:#b8860b;">❦</div>
    <div style="position:absolute; bottom:10px; left:10px; font-size:2rem; color:#b8860b;">❦</div>
    <div style="position:absolute; bottom:10px; right:10px; font-size:2rem; color:#b8860b;">❦</div>

    <!-- Header -->
    <div class="text-center">
      <div style="font-size:4rem;">🎓</div>
      <h1 style="font-family:'Georgia',serif; color:#8b4513; font-size:2.5rem; margin-top:10px;">
        CERTIFICADO DE FINALIZACIÓN
      </h1>
      <p style="font-family:'Georgia',serif; font-style:italic; color:#666;">
        {{ cert.institucion }}
      </p>
      <hr style="border:2px solid #b8860b; width:60%; margin:20px auto;">
    </div>

    <!-- Cuerpo -->
    <div class="text-center" style="font-family:'Georgia',serif; padding:30px 0;">
      <p style="font-size:1.2rem; color:#444;">Se otorga el presente certificado a</p>

      <h2 style="font-size:2.5rem; color:#1a5490; font-family:'Georgia',serif; margin:20px 0; border-bottom:1px solid #ccc; display:inline-block; padding:0 40px 10px;">
        {{ cert.nombre_estudiante }}
      </h2>

      <p style="font-size:1.1rem; margin-top:20px; color:#444;">
        por haber completado satisfactoriamente el curso
      </p>

      <h3 style="font-size:1.8rem; color:#8b4513; margin:15px 0; font-family:'Georgia',serif;">
        "{{ cert.curso.titulo }}"
      </h3>

      <p style="font-size:1rem; color:#666; margin-top:15px;">
        Nivel <strong>{{ cert.curso.nivel.codigo }}</strong> ·
        Nota final <strong>{{ cert.nota_final }}/100</strong> ·
        Duración <strong>{{ cert.horas }} horas</strong>
      </p>
    </div>

    <!-- Firmas -->
    <div class="row mt-5 text-center" style="font-family:'Georgia',serif;">
      <div class="col-6">
        <div style="border-top:2px solid #333; padding-top:10px; margin:0 20px;">
          <strong>{{ cert.nombre_admin }}</strong>
          <br><small>{{ cert.cargo_admin }}</small>
          <br><small style="color:#888;">Firma del Administrador</small>
        </div>
      </div>
      <div class="col-6">
        <div style="border-top:2px solid #333; padding-top:10px; margin:0 20px;">
          <strong>{{ cert.nombre_profesor }}</strong>
          <br><small>{{ cert.cargo_profesor }}</small>
          <br><small style="color:#888;">Firma del Profesor</small>
        </div>
      </div>
    </div>

    <!-- Sello y fecha -->
    <div class="row mt-5 align-items-center">
      <div class="col-md-3 text-center">
        <div style="border:3px solid #b8860b; border-radius:50%; width:100px; height:100px; line-height:94px; margin:0 auto; color:#b8860b; font-family:'Georgia',serif; font-weight:bold;">
          SELLO<br>OFICIAL
        </div>
      </div>
      <div class="col-md-6 text-center" style="font-family:'Georgia',serif;">
        <p style="font-size:0.9rem; color:#666;">Emitido el</p>
        <p style="font-size:1.1rem;"><strong>{{ cert.fecha_emision|date:"d \\d\\e F \\d\\e Y" }}</strong></p>
      </div>
      <div class="col-md-3 text-center">
        <div style="border:2px dashed #666; padding:10px; font-family:monospace; font-size:0.8rem;">
          Código<br><strong>{{ cert.codigo_corto }}</strong>
        </div>
      </div>
    </div>

    <!-- Verificación -->
    <div class="text-center mt-4">
      <small style="color:#888; font-family:'Georgia',serif;">
        Este certificado puede verificarse en
        <a href="{% url 'certificaciones:verificar' %}">la página de verificación</a>
        con el código completo
      </small>
    </div>

    <!-- Marca de agua -->
    <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-30deg); font-size:8rem; color:rgba(184,134,11,0.05); font-family:'Georgia',serif; font-weight:bold; pointer-events:none; z-index:0;">
      OFICIAL
    </div>
  </div>
</div>

<style>
  @media print {
    nav, footer, .btn { display: none !important; }
    #diploma { border-width: 10px; box-shadow: none; }
  }
</style>
{% endblock %}
''')


print()
print("=" * 60)
print("  CERTIFICADOS MEJORADOS")
print("=" * 60)
print()
print("⚠️  Ahora ejecuta en OTRO CMD:")
print("  E:\\pydj5.bat manage.py makemigrations certificaciones")
print("  E:\\pydj5.bat manage.py migrate certificaciones")
print()
print("Luego ejecuta EMITIR_CERTIFICADOS.py")
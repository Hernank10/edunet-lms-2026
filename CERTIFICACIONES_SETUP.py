# -*- coding: utf-8 -*-
"""
CERTIFICACIONES_SETUP.py
Añade sistema de certificaciones a EduNet Academia.
Ejecutar: E:\pydj5.bat E:\02_proyectos\edunet_academia\CERTIFICACIONES_SETUP.py
"""
import os
import sys
import uuid
import django

BASE = r"E:\02_proyectos\edunet_academia"


def write(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {path}")


# ==================================================
# 1. Django setup
# ==================================================
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


# ==================================================
# 2. Modelos de certificaciones
# ==================================================
write("certificaciones/models.py", '''import uuid
from django.conf import settings
from django.db import models
from academia.models import Curso

User = settings.AUTH_USER_MODEL


class RequisitoCertificado(models.Model):
    """Requisitos para obtener el certificado de un curso."""

    curso = models.OneToOneField(
        Curso,
        on_delete=models.CASCADE,
        related_name="requisito_certificado"
    )
    lecciones_minimas_pct = models.PositiveIntegerField(
        default=100,
        help_text="% mínimo de lecciones completadas (0-100)"
    )
    nota_minima = models.PositiveIntegerField(
        default=70,
        help_text="Nota mínima (0-100)"
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Requisitos: {self.curso.titulo}"

    class Meta:
        verbose_name = "Requisito de certificado"
        verbose_name_plural = "Requisitos de certificados"


class Certificado(models.Model):
    """Certificado emitido a un estudiante al completar un curso."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Código único de verificación"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    nota_final = models.PositiveIntegerField(
        default=100,
        help_text="Nota final del curso (0-100)"
    )
    horas = models.PositiveIntegerField(
        default=40,
        help_text="Horas lectivas del curso"
    )
    pdf = models.FileField(
        upload_to="certificados/",
        blank=True,
        null=True,
        help_text="PDF del certificado (opcional)"
    )

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
''')


# ==================================================
# 3. Admin
# ==================================================
write("certificaciones/admin.py", '''from django.contrib import admin
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
''')


# ==================================================
# 4. Vistas
# ==================================================
write("certificaciones/views.py", '''from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from academia.models import Curso
from progreso.models import ProgresoLeccion
from .models import Certificado, RequisitoCertificado


@login_required
def mis_certificados(request):
    """Lista de certificados del usuario + cursos en progreso."""
    usuario = request.user

    # Certificados obtenidos
    obtenidos = Certificado.objects.filter(usuario=usuario).select_related("curso")

    # Cursos en progreso hacia certificado
    en_progreso = []
    for curso in Curso.objects.filter(activo=True):
        # ¿Ya tiene certificado?
        if Certificado.objects.filter(usuario=usuario, curso=curso).exists():
            continue

        lecciones = curso.lecciones.all()
        total = lecciones.count()
        completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__curso=curso,
            completada=True
        ).count()

        pct = int((completadas / total) * 100) if total > 0 else 0

        requisito = getattr(curso, "requisito_certificado", None)
        pct_min = requisito.lecciones_minimas_pct if requisito else 100

        en_progreso.append({
            "curso": curso,
            "completadas": completadas,
            "total": total,
            "pct": pct,
            "pct_min": pct_min,
            "listo": pct >= pct_min,
        })

    return render(request, "certificaciones/mis_certificados.html", {
        "obtenidos": obtenidos,
        "en_progreso": en_progreso,
    })


@login_required
def ver_certificado(request, codigo):
    """Ver un certificado propio por código."""
    certificado = get_object_or_404(Certificado, codigo=codigo)

    # Solo el dueño o staff puede verlo desde aquí
    if certificado.usuario != request.user and not request.user.is_staff:
        raise Http404("Certificado no encontrado")

    return render(request, "certificaciones/ver_certificado.html", {
        "cert": certificado,
    })


def verificar_codigo(request):
    """Vista pública para verificar un certificado por código."""
    cert = None
    error = None

    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip()
        try:
            cert = Certificado.objects.select_related("usuario", "curso").get(codigo=codigo)
        except (Certificado.DoesNotExist, ValueError):
            error = "❌ Código no válido. Verifica el código e inténtalo de nuevo."

    return render(request, "certificaciones/verificar_codigo.html", {
        "cert": cert,
        "error": error,
    })
''')


# ==================================================
# 5. URLs
# ==================================================
write("certificaciones/urls.py", '''from django.urls import path
from . import views

app_name = "certificaciones"

urlpatterns = [
    path("", views.mis_certificados, name="mis_certificados"),
    path("verificar/", views.verificar_codigo, name="verificar"),
    path("<uuid:codigo>/", views.ver_certificado, name="ver_certificado"),
]
''')


# ==================================================
# 6. Templates
# ==================================================
write("certificaciones/templates/certificaciones/mis_certificados.html", '''{% extends "gamificacion/_base_estudiante.html" %}

{% block contenido %}
<h2 class="mb-4">🎓 Mis Certificados</h2>

<!-- Obtenidos -->
<h4>✅ Obtenidos ({{ obtenidos|length }})</h4>
<div class="row mb-4">
  {% for cert in obtenidos %}
    <div class="col-md-6 mb-3">
      <div class="card border-success h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between">
            <h5>{{ cert.curso.titulo }}</h5>
            <span class="badge bg-success">✅ Emitido</span>
          </div>
          <p class="text-muted small mb-1">
            📅 {{ cert.fecha_emision|date:"d M Y" }} · 📝 Nota: {{ cert.nota_final }}/100
          </p>
          <p class="text-muted small">
            🔑 Código: <code>{{ cert.codigo_corto }}</code>
          </p>
          <a href="{% url 'certificaciones:ver_certificado' cert.codigo %}" class="btn btn-outline-success btn-sm">
            Ver certificado
          </a>
        </div>
      </div>
    </div>
  {% empty %}
    <div class="col-12">
      <div class="alert alert-info">
        Aún no has obtenido certificados. ¡Completa un curso para conseguir el tuyo!
      </div>
    </div>
  {% endfor %}
</div>

<!-- En progreso -->
<h4>⏳ En progreso ({{ en_progreso|length }})</h4>
<div class="row">
  {% for item in en_progreso %}
    <div class="col-md-6 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <h5>{{ item.curso.titulo }}</h5>
          <div class="progress mb-2" style="height: 15px;">
            <div class="progress-bar {% if item.listo %}bg-success{% endif %}" style="width: {{ item.pct }}%;">
              {{ item.pct }}%
            </div>
          </div>
          <p class="small mb-2">
            {{ item.completadas }} / {{ item.total }} lecciones
            (necesitas {{ item.pct_min }}%)
          </p>
          {% if item.listo %}
            <span class="badge bg-success">🎉 ¡Listo para certificado!</span>
          {% else %}
            <span class="badge bg-secondary">Faltan {{ item.pct_min|add:"-100"|add:item.pct|default:item.pct }}%</span>
          {% endif %}
        </div>
      </div>
    </div>
  {% empty %}
    <p class="text-muted">No hay cursos en progreso.</p>
  {% endfor %}
</div>

<!-- Verificar código -->
<div class="card mt-4">
  <div class="card-body">
    <h5>🔍 Verificar un certificado</h5>
    <p class="text-muted small">Introduce el código único para verificar la autenticidad.</p>
    <a href="{% url 'certificaciones:verificar' %}" class="btn btn-outline-primary btn-sm">
      Ir al verificador
    </a>
  </div>
</div>
{% endblock %}
''')


write("certificaciones/templates/certificaciones/ver_certificado.html", '''{% extends "base.html" %}

{% block content %}
<div class="container mt-5" style="max-width: 800px;">
  <div class="card border-success shadow">
    <div class="card-body text-center p-5">
      <div style="font-size: 4rem;">🏆</div>
      <h1 class="mt-3">Certificado de Finalización</h1>
      <hr>
      <p class="lead">Se certifica que</p>
      <h2 class="text-primary">{{ cert.usuario.get_full_name|default:cert.usuario.username }}</h2>
      <p class="lead">ha completado satisfactoriamente el curso</p>
      <h3 class="text-success">{{ cert.curso.titulo }}</h3>
      <p class="mt-3">
        Nivel <strong>{{ cert.curso.nivel.codigo }}</strong> ·
        Nota final: <strong>{{ cert.nota_final }}/100</strong> ·
        Duración: <strong>{{ cert.horas }} horas</strong>
      </p>
      <hr>
      <div class="row mt-4">
        <div class="col-md-6">
          <small class="text-muted">Fecha de emisión</small>
          <p>{{ cert.fecha_emision|date:"d \d\e F \d\e Y" }}</p>
        </div>
        <div class="col-md-6">
          <small class="text-muted">Código único</small>
          <p><code>{{ cert.codigo }}</code></p>
        </div>
      </div>
      <div class="mt-4">
        <span class="badge bg-success">✅ Certificado verificado</span>
      </div>
      <p class="text-muted small mt-4">
        Este certificado puede verificarse en cualquier momento en
        <a href="{% url 'certificaciones:verificar' %}">la página de verificación</a>.
      </p>
    </div>
  </div>

  <div class="text-center mt-3">
    <a href="{% url 'certificaciones:mis_certificados' %}" class="btn btn-outline-secondary">
      ← Volver a mis certificados
    </a>
  </div>
</div>
{% endblock %}
''')


write("certificaciones/templates/certificaciones/verificar_codigo.html", '''{% extends "base.html" %}

{% block content %}
<div class="container mt-5" style="max-width: 700px;">
  <h2 class="mb-4">🔍 Verificar certificado</h2>

  <p class="text-muted">
    Introduce el código único que aparece en el certificado para verificar su autenticidad.
  </p>

  <form method="post" class="mb-4">
    {% csrf_token %}
    <div class="input-group">
      <input type="text" name="codigo" class="form-control" placeholder="Código único" required>
      <button type="submit" class="btn btn-primary">Verificar</button>
    </div>
  </form>

  {% if error %}
    <div class="alert alert-danger">{{ error }}</div>
  {% endif %}

  {% if cert %}
    <div class="card border-success">
      <div class="card-body">
        <h4>✅ Certificado válido</h4>
        <ul class="list-group list-group-flush">
          <li class="list-group-item"><strong>Estudiante:</strong> {{ cert.usuario.get_full_name|default:cert.usuario.username }}</li>
          <li class="list-group-item"><strong>Curso:</strong> {{ cert.curso.titulo }}</li>
          <li class="list-group-item"><strong>Nivel:</strong> {{ cert.curso.nivel.codigo }}</li>
          <li class="list-group-item"><strong>Nota:</strong> {{ cert.nota_final }}/100</li>
          <li class="list-group-item"><strong>Fecha:</strong> {{ cert.fecha_emision|date:"d M Y" }}</li>
        </ul>
        <a href="{% url 'certificaciones:ver_certificado' cert.codigo %}" class="btn btn-success mt-3">
          Ver certificado completo
        </a>
      </div>
    </div>
  {% endif %}
</div>
{% endblock %}
''')


# ==================================================
# 7. Añadir certificaciones a config/urls.py
# ==================================================
urls_path = os.path.join(BASE, "config", "urls.py")
with open(urls_path, encoding="utf-8") as f:
    urls = f.read()

if 'include("certificaciones.urls")' not in urls:
    urls = urls.replace(
        'path("", include("gamificacion.urls")),',
        'path("", include("gamificacion.urls")),\n    path("certificados/", include("certificaciones.urls")),'
    )
    with open(urls_path, "w", encoding="utf-8") as f:
        f.write(urls)
    print("[OK] config/urls.py — añadido '/certificados/'")
else:
    print("[SKIP] config/urls.py — certificaciones ya estaba")


# ==================================================
# 8. Añadir "Certificados" al sidebar
# ==================================================
sidebar_path = os.path.join(BASE, "gamificacion", "templates", "gamificacion", "_sidebar.html")
if os.path.exists(sidebar_path):
    with open(sidebar_path, encoding="utf-8") as f:
        sidebar = f.read()

    if "certificaciones:mis_certificados" not in sidebar:
        sidebar = sidebar.replace(
            '<li class="nav-item mb-1">\n      <a class="nav-link text-white" href="{% url \'gamificacion:estadisticas\' %}">📈 Estadísticas</a>\n    </li>',
            '''<li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:estadisticas' %}">📈 Estadísticas</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'certificaciones:mis_certificados' %}">🎓 Certificados</a>
    </li>'''
        )
        with open(sidebar_path, "w", encoding="utf-8") as f:
            f.write(sidebar)
        print("[OK] _sidebar.html — añadido 'Certificados'")
    else:
        print("[SKIP] _sidebar.html — ya tenía certificaciones")


# ==================================================
# 9. Añadir tarjeta al dashboard
# ==================================================
dash_path = os.path.join(BASE, "gamificacion", "templates", "gamificacion", "dashboard.html")
if os.path.exists(dash_path):
    with open(dash_path, encoding="utf-8") as f:
        dash = f.read()

    if "certificaciones:mis_certificados" not in dash:
        # Añadir tarjeta de certificados después de "Próximos objetivos"
        marker = '<!-- INSIGNIAS -->'
        tarjeta = '''<!-- CERTIFICADOS -->
<div class="card mb-4 border-success">
  <div class="card-body d-flex justify-content-between align-items-center">
    <div>
      <h5 class="mb-1">🎓 Certificaciones</h5>
      <p class="text-muted mb-0 small">Consulta tus certificados obtenidos y en progreso.</p>
    </div>
    <a href="{% url 'certificaciones:mis_certificados' %}" class="btn btn-success">
      Ver certificados →
    </a>
  </div>
</div>

<!-- INSIGNIAS -->'''
        dash = dash.replace(marker, tarjeta, 1)
        with open(dash_path, "w", encoding="utf-8") as f:
            f.write(dash)
        print("[OK] dashboard.html — añadida tarjeta de certificaciones")
    else:
        print("[SKIP] dashboard.html — ya tenía certificaciones")


# ==================================================
# 10. Migrar
# ==================================================
print("\n=== Migrando BD ===")
from django.core.management import call_command

call_command("makemigrations", "certificaciones", verbosity=0)
call_command("migrate", verbosity=0)
print("[OK] Migraciones aplicadas")


# ==================================================
# 11. Datos de prueba
# ==================================================
print("\n=== Creando datos de prueba ===")
from certificaciones.models import Certificado, RequisitoCertificado
from academia.models import Curso
from django.contrib.auth import get_user_model

User = get_user_model()

# Requisitos por defecto para cada curso
for curso in Curso.objects.all():
    req, created = RequisitoCertificado.objects.get_or_create(
        curso=curso,
        defaults={"lecciones_minimas_pct": 100, "nota_minima": 70}
    )
    if created:
        print(f"  + Requisito: {curso.titulo}")

# Usuario demo (si existe)
if User.objects.filter(username="estudiante").exists():
    u = User.objects.get(username="estudiante")
    # Intentar crear un certificado demo si hay cursos
    cursos = Curso.objects.all()[:1]
    for curso in cursos:
        cert, created = Certificado.objects.get_or_create(
            usuario=u,
            curso=curso,
            defaults={"nota_final": 95, "horas": 40}
        )
        if created:
            print(f"[OK] Certificado demo: {u.username} → {curso.titulo}")


# ==================================================
# 12. Resumen final
# ==================================================
print("\n" + "=" * 50)
print("  CERTIFICACIONES INSTALADAS")
print("=" * 50)
print()
print("URLs nuevas:")
print("  /estudiante/certificados/          → Mis certificados")
print("  /certificados/verificar/           → Verificar código")
print("  /certificados/<uuid>/              → Ver certificado")
print()
print("Rearranca con:")
print("  cd /d E:\\02_proyectos\\edunet_academia")
print("  E:\\pydj5.bat manage.py runserver 8011 --noreload")
print()
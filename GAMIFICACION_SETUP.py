# -*- coding: utf-8 -*-
"""
GAMIFICACION_SETUP.py
Crea el dashboard del estudiante con gamificación para EduNet Academia.
Ejecutar: E:\pydj5.bat E:\02_proyectos\edunet_academia\GAMIFICACION_SETUP.py
"""
import os
import sys
import django

BASE = r"E:\02_proyectos\edunet_academia"


def write(path, content):
    """Escribe un archivo (crea carpetas si hace falta)."""
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] {path}")


def append_once(path, marker, content):
    """Añade contenido a un archivo solo si no contiene el marker."""
    full = os.path.join(BASE, path)
    if not os.path.exists(full):
        print(f"[SKIP] {path} no existe")
        return
    with open(full, encoding="utf-8") as f:
        txt = f.read()
    if marker in txt:
        print(f"[SKIP] {path} ya tiene '{marker}'")
        return
    with open(full, "a", encoding="utf-8") as f:
        f.write("\n\n" + content + "\n")
    print(f"[OK] {path} — añadido")


# ==================================================
# 1. Configurar Django
# ==================================================
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


# ==================================================
# 2. Crear app gamificacion
# ==================================================
app_dir = os.path.join(BASE, "gamificacion")
os.makedirs(app_dir, exist_ok=True)
os.makedirs(os.path.join(app_dir, "migrations"), exist_ok=True)

write("gamificacion/__init__.py", "")
write("gamificacion/migrations/__init__.py", "")
write("gamificacion/apps.py", '''from django.apps import AppConfig


class GamificacionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gamificacion"
    verbose_name = "Gamificación"
''')


# ==================================================
# 3. Modelos de gamificación
# ==================================================
write("gamificacion/models.py", '''from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Insignia(models.Model):
    """Insignia / medalla / logro desbloqueable."""

    TIPOS = (
        ("estrella", "⭐ Estrella"),
        ("medalla", "🏅 Medalla"),
        ("libro", "📚 Libro"),
        ("trofeo", "🏆 Trofeo"),
        ("corona", "👑 Corona"),
    )

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    icono = models.CharField(
        max_length=10,
        default="🏅",
        help_text="Emoji o símbolo de la insignia"
    )
    tipo = models.CharField(max_length=20, choices=TIPOS, default="medalla")
    requisito_xp = models.PositiveIntegerField(
        default=0,
        help_text="XP mínima para desbloquear"
    )
    requisito_cursos = models.PositiveIntegerField(
        default=0,
        help_text="Cursos completados para desbloquear"
    )
    requisito_lecciones = models.PositiveIntegerField(
        default=0,
        help_text="Lecciones completadas para desbloquear"
    )
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["orden"]
        verbose_name = "Insignia"
        verbose_name_plural = "Insignias"

    def __str__(self):
        return f"{self.icono} {self.nombre}"


class Logro(models.Model):
    """Registro de insignia obtenida por un usuario."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logros")
    insignia = models.ForeignKey(Insignia, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "insignia")
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario} → {self.insignia}"


class PerfilGamificacion(models.Model):
    """Perfil de gamificación del usuario (XP, nivel, racha)."""

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil_gam")
    xp_total = models.PositiveIntegerField(default=0)
    nivel_actual = models.PositiveIntegerField(default=1)
    racha_dias = models.PositiveIntegerField(default=0)
    ultima_actividad = models.DateField(null=True, blank=True)
    cursos_completados = models.PositiveIntegerField(default=0)
    lecciones_completadas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Perfil de gamificación"
        verbose_name_plural = "Perfiles de gamificación"

    def __str__(self):
        return f"{self.usuario} — Nivel {self.nivel_actual} — {self.xp_total} XP"

    @property
    def xp_siguiente_nivel(self):
        """XP necesaria para el siguiente nivel (500 por nivel)."""
        return self.nivel_actual * 500

    @property
    def progreso_nivel(self):
        """Porcentaje de progreso al siguiente nivel."""
        if self.xp_siguiente_nivel == 0:
            return 0
        return min(100, int((self.xp_total % 500) / 500 * 100))

    @property
    def titulo_nivel(self):
        """Título según nivel."""
        titulos = {
            1: "🌱 Aprendiz",
            2: "📖 Estudiante",
            3: "✏️ Practicante",
            4: "🎯 Avanzado",
            5: "🏅 Experto",
            6: "🏆 Maestro",
            7: "👑 Gran Maestro",
        }
        return titulos.get(self.nivel_actual, "🌟 Leyenda")

    def add_xp(self, cantidad):
        """Suma XP y recalcula nivel."""
        self.xp_total += cantidad
        self.nivel_actual = max(1, self.xp_total // 500 + 1)
        self.save()


class PuntosXP(models.Model):
    """Registro de puntos XP ganados."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="puntos_xp")
    accion = models.CharField(max_length=100)
    puntos = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Puntos XP"
        verbose_name_plural = "Puntos XP"

    def __str__(self):
        return f"{self.usuario} — {self.accion} (+{self.puntos})"
''')


# ==================================================
# 4. Admin
# ==================================================
write("gamificacion/admin.py", '''from django.contrib import admin
from .models import Insignia, Logro, PerfilGamificacion, PuntosXP


@admin.register(Insignia)
class InsigniaAdmin(admin.ModelAdmin):
    list_display = ("icono", "nombre", "tipo", "requisito_xp", "requisito_cursos", "orden")
    list_filter = ("tipo",)
    search_fields = ("nombre",)


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = ("usuario", "insignia", "fecha")
    list_filter = ("insignia",)


@admin.register(PerfilGamificacion)
class PerfilGamificacionAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nivel_actual", "xp_total", "racha_dias", "cursos_completados")


@admin.register(PuntosXP)
class PuntosXPAdmin(admin.ModelAdmin):
    list_display = ("usuario", "accion", "puntos", "fecha")
''')


# ==================================================
# 5. Vistas del dashboard del estudiante
# ==================================================
write("gamificacion/views.py", '''from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from academia.models import Curso, Leccion
from progreso.models import ProgresoLeccion
from .models import Insignia, Logro, PerfilGamificacion


def _get_perfil(user):
    """Devuelve (o crea) el perfil de gamificación del usuario."""
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=user)
    return perfil


@login_required
def dashboard_estudiante(request):
    """Dashboard principal del estudiante."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    # Cursos activos con progreso
    cursos = Curso.objects.filter(activo=True).select_related("nivel")
    cursos_data = []

    for curso in cursos:
        lecciones = curso.lecciones.all()
        total = lecciones.count()
        completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__curso=curso,
            completada=True
        ).count()

        progreso = int((completadas / total) * 100) if total > 0 else 0

        # Próxima lección no completada
        proxima = None
        for lec in lecciones:
            if not ProgresoLeccion.objects.filter(
                usuario=usuario, leccion=lec, completada=True
            ).exists():
                proxima = lec
                break

        cursos_data.append({
            "curso": curso,
            "total": total,
            "completadas": completadas,
            "progreso": progreso,
            "proxima": proxima,
        })

    # Lecciones en curso (no completadas)
    lecciones_en_curso = []
    for curso in cursos:
        for lec in curso.lecciones.all():
            completada = ProgresoLeccion.objects.filter(
                usuario=usuario, leccion=lec, completada=True
            ).exists()
            if not completada:
                lecciones_en_curso.append({
                    "leccion": lec,
                    "curso": curso,
                })
                break  # solo la siguiente de cada curso

    # Insignias ganadas y bloqueadas
    todas = Insignia.objects.all()
    ganadas_ids = set(Logro.objects.filter(usuario=usuario).values_list("insignia_id", flat=True))

    insignias_ganadas = [i for i in todas if i.id in ganadas_ids]
    insignias_bloqueadas = [i for i in todas if i.id not in ganadas_ids]

    # Próximos objetivos (insignias bloqueadas más cercanas)
    objetivos = sorted(
        insignias_bloqueadas,
        key=lambda i: abs(i.requisito_xp - perfil.xp_total)
    )[:3]

    context = {
        "perfil": perfil,
        "cursos": cursos_data,
        "lecciones_en_curso": lecciones_en_curso,
        "insignias_ganadas": insignias_ganadas,
        "insignias_bloqueadas": insignias_bloqueadas,
        "objetivos": objetivos,
    }

    return render(request, "gamificacion/dashboard.html", context)


@login_required
def mis_cursos(request):
    """Lista de cursos con progreso."""
    usuario = request.user
    cursos = Curso.objects.filter(activo=True).select_related("nivel")

    cursos_data = []
    for curso in cursos:
        lecciones = curso.lecciones.all()
        total = lecciones.count()
        completadas = ProgresoLeccion.objects.filter(
            usuario=usuario,
            leccion__curso=curso,
            completada=True
        ).count()
        progreso = int((completadas / total) * 100) if total > 0 else 0

        cursos_data.append({
            "curso": curso,
            "total": total,
            "completadas": completadas,
            "progreso": progreso,
        })

    return render(request, "gamificacion/mis_cursos.html", {"cursos": cursos_data})


@login_required
def practicas(request):
    """Prácticas pendientes (lecciones sin completar)."""
    usuario = request.user
    pendientes = []

    for curso in Curso.objects.filter(activo=True):
        for lec in curso.lecciones.all():
            completada = ProgresoLeccion.objects.filter(
                usuario=usuario, leccion=lec, completada=True
            ).exists()
            if not completada:
                pendientes.append({"leccion": lec, "curso": curso})

    return render(request, "gamificacion/practicas.html", {"pendientes": pendientes})


@login_required
def evaluaciones(request):
    """Evaluaciones (por ahora, lista de cursos con ejercicios)."""
    usuario = request.user
    cursos = Curso.objects.filter(activo=True)
    return render(request, "gamificacion/evaluaciones.html", {"cursos": cursos})


@login_required
def mis_logros(request):
    """Insignias ganadas y bloqueadas."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    todas = Insignia.objects.all()
    ganadas_ids = set(Logro.objects.filter(usuario=usuario).values_list("insignia_id", flat=True))

    insignias_ganadas = [i for i in todas if i.id in ganadas_ids]
    insignias_bloqueadas = [i for i in todas if i.id not in ganadas_ids]

    return render(request, "gamificacion/mis_logros.html", {
        "perfil": perfil,
        "ganadas": insignias_ganadas,
        "bloqueadas": insignias_bloqueadas,
    })


@login_required
def estadisticas(request):
    """Estadísticas detalladas."""
    usuario = request.user
    perfil = _get_perfil(usuario)
    return render(request, "gamificacion/estadisticas.html", {"perfil": perfil})
''')


# ==================================================
# 6. URLs de gamificacion
# ==================================================
write("gamificacion/urls.py", '''from django.urls import path
from . import views

app_name = "gamificacion"

urlpatterns = [
    path("", views.dashboard_estudiante, name="dashboard"),
    path("cursos/", views.mis_cursos, name="mis_cursos"),
    path("practicas/", views.practicas, name="practicas"),
    path("evaluaciones/", views.evaluaciones, name="evaluaciones"),
    path("logros/", views.mis_logros, name="mis_logros"),
    path("estadisticas/", views.estadisticas, name="estadisticas"),
]
''')


# ==================================================
# 7. Templates con gamificación visual
# ==================================================
write("gamificacion/templates/gamificacion/_sidebar.html", '''<nav class="sidebar bg-dark text-white p-3" style="min-height: 100vh; width: 240px; position: fixed; top: 0; left: 0; overflow-y: auto;">
  <h5 class="mb-4">🎓 EduNet</h5>

  <ul class="nav flex-column">
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:dashboard' %}">📊 Dashboard</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:mis_cursos' %}">🎓 Mis Cursos</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:practicas' %}">✏️ Prácticas</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:evaluaciones' %}">🏆 Evaluaciones</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:mis_logros' %}">🏅 Logros</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'gamificacion:estadisticas' %}">📈 Estadísticas</a>
    </li>
    <li class="nav-item mb-1">
      <a class="nav-link text-white" href="{% url 'accounts:perfil' %}">👤 Mi Perfil</a>
    </li>
    <li class="nav-item mt-3">
      <form method="post" action="{% url 'logout' %}">
        {% csrf_token %}
        <button type="submit" class="btn btn-outline-light btn-sm w-100">🚪 Salir</button>
      </form>
    </li>
  </ul>
</nav>
''')


write("gamificacion/templates/gamificacion/_base_estudiante.html", '''{% extends "base.html" %}

{% block content %}
<div class="d-flex">
  {% include "gamificacion/_sidebar.html" %}

  <main class="flex-grow-1 p-4" style="margin-left: 240px;">
    {% if messages %}
      {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">{{ message }}</div>
      {% endfor %}
    {% endif %}

    {% block contenido %}{% endblock %}
  </main>
</div>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/dashboard.html", '''{% extends "gamificacion/_base_estudiante.html" %}

{% block contenido %}
<h2 class="mb-4">📊 Mi Dashboard</h2>

<!-- ESTADÍSTICAS -->
<div class="row mb-4">
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-primary h-100">
      <div class="card-body text-center">
        <h3>💎 {{ perfil.xp_total }}</h3>
        <p class="mb-0">XP Total</p>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-success h-100">
      <div class="card-body text-center">
        <h3>🏅 Nivel {{ perfil.nivel_actual }}</h3>
        <p class="mb-0">{{ perfil.titulo_nivel }}</p>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-warning h-100">
      <div class="card-body text-center">
        <h3>🔥 {{ perfil.racha_dias }}</h3>
        <p class="mb-0">Días de racha</p>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-info h-100">
      <div class="card-body text-center">
        <h3>🎓 {{ cursos|length }}</h3>
        <p class="mb-0">Cursos activos</p>
      </div>
    </div>
  </div>
</div>

<!-- BARRA DE NIVEL -->
<div class="card mb-4">
  <div class="card-body">
    <div class="d-flex justify-content-between">
      <strong>Nivel {{ perfil.nivel_actual }} → {{ perfil.nivel_actual|add:1 }}</strong>
      <span>{{ perfil.xp_total }} / {{ perfil.xp_siguiente_nivel }} XP</span>
    </div>
    <div class="progress mt-2" style="height: 20px;">
      <div class="progress-bar bg-success" style="width: {{ perfil.progreso_nivel }}%;">
        {{ perfil.progreso_nivel }}%
      </div>
    </div>
  </div>
</div>

<!-- CURSOS -->
<h4 class="mt-4">🎓 Mis Cursos</h4>
<div class="row mb-4">
  {% for item in cursos %}
    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <h5>{{ item.curso.titulo }}</h5>
          <p class="text-muted small">{{ item.curso.nivel.codigo }} · {{ item.curso.nivel.descripcion }}</p>
          <div class="progress mb-2" style="height: 12px;">
            <div class="progress-bar" style="width: {{ item.progreso }}%;">{{ item.progreso }}%</div>
          </div>
          <p class="small mb-2">{{ item.completadas }} / {{ item.total }} lecciones</p>
          {% if item.proxima %}
            <a href="{% url 'academia:lesson_detail' item.proxima.pk %}" class="btn btn-primary btn-sm w-100">
              ▶ Continuar
            </a>
          {% else %}
            <span class="badge bg-success w-100">✅ Curso completado</span>
          {% endif %}
        </div>
      </div>
    </div>
  {% empty %}
    <p>No hay cursos aún.</p>
  {% endfor %}
</div>

<!-- LECCIONES EN CURSO -->
<h4 class="mt-4">📚 Lecciones en curso</h4>
<ul class="list-group mb-4">
  {% for item in lecciones_en_curso %}
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ item.leccion.titulo }}</strong>
        <br><small class="text-muted">{{ item.curso.titulo }}</small>
      </div>
      <a href="{% url 'academia:lesson_detail' item.leccion.pk %}" class="btn btn-primary btn-sm">Continuar</a>
    </li>
  {% empty %}
    <li class="list-group-item text-muted">No hay lecciones pendientes.</li>
  {% endfor %}
</ul>

<!-- INSIGNIAS -->
<div class="row">
  <div class="col-md-6 mb-4">
    <h4>🏅 Insignias ganadas ({{ insignias_ganadas|length }})</h4>
    <div class="d-flex flex-wrap gap-2">
      {% for ins in insignias_ganadas %}
        <div class="card text-center p-2" style="width: 100px;" title="{{ ins.descripcion }}">
          <div style="font-size: 2rem;">{{ ins.icono }}</div>
          <small>{{ ins.nombre }}</small>
        </div>
      {% empty %}
        <p class="text-muted">Aún no has ganado insignias. ¡Sigue aprendiendo!</p>
      {% endfor %}
    </div>
  </div>

  <div class="col-md-6 mb-4">
    <h4>🎯 Próximos objetivos</h4>
    <ul class="list-group">
      {% for obj in objetivos %}
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <span>{{ obj.icono }} {{ obj.nombre }}</span>
          <small class="text-muted">{{ obj.requisito_xp }} XP</small>
        </li>
      {% empty %}
        <li class="list-group-item text-muted">¡Todos los objetivos completados!</li>
      {% endfor %}
    </ul>
  </div>
</div>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/mis_cursos.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🎓 Mis Cursos</h2>

<div class="row">
  {% for item in cursos %}
    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <h5>{{ item.curso.titulo }}</h5>
          <p class="text-muted small">{{ item.curso.nivel.codigo }}</p>
          <div class="progress mb-2">
            <div class="progress-bar" style="width: {{ item.progreso }}%;">{{ item.progreso }}%</div>
          </div>
          <p class="small">{{ item.completadas }} / {{ item.total }} lecciones</p>
          <a href="{% url 'academia:course_lessons' item.curso.id %}" class="btn btn-primary btn-sm w-100">
            Ver lecciones
          </a>
        </div>
      </div>
    </div>
  {% empty %}
    <p>No hay cursos aún.</p>
  {% endfor %}
</div>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/practicas.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">✏️ Prácticas pendientes</h2>

<ul class="list-group">
  {% for item in pendientes %}
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ item.leccion.titulo }}</strong>
        <br><small class="text-muted">{{ item.curso.titulo }}</small>
      </div>
      <a href="{% url 'academia:lesson_detail' item.leccion.pk %}" class="btn btn-primary btn-sm">Practicar</a>
    </li>
  {% empty %}
    <li class="list-group-item text-muted">¡No hay prácticas pendientes!</li>
  {% endfor %}
</ul>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/evaluaciones.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🏆 Evaluaciones</h2>

<div class="alert alert-info">
  ℹ️ Las evaluaciones se añadirán próximamente. Por ahora puedes practicar con las lecciones.
</div>

<ul class="list-group">
  {% for curso in cursos %}
    <li class="list-group-item d-flex justify-content-between align-items-center">
      <span>{{ curso.titulo }}</span>
      <span class="badge bg-secondary">Próximamente</span>
    </li>
  {% endfor %}
</ul>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/mis_logros.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🏅 Mis Logros</h2>

<h4>Ganadas ({{ ganadas|length }})</h4>
<div class="d-flex flex-wrap gap-3 mb-4">
  {% for ins in ganadas %}
    <div class="card text-center p-3" style="width: 140px;">
      <div style="font-size: 2.5rem;">{{ ins.icono }}</div>
      <strong>{{ ins.nombre }}</strong>
      <small class="text-muted">{{ ins.descripcion|truncatechars:40 }}</small>
    </div>
  {% empty %}
    <p class="text-muted">Aún no has ganado insignias.</p>
  {% endfor %}
</div>

<h4>Bloqueadas ({{ bloqueadas|length }})</h4>
<div class="d-flex flex-wrap gap-3">
  {% for ins in bloqueadas %}
    <div class="card text-center p-3 bg-light" style="width: 140px; opacity: 0.6;">
      <div style="font-size: 2.5rem;">🔒</div>
      <strong>{{ ins.nombre }}</strong>
      <small class="text-muted">{{ ins.requisito_xp }} XP</small>
    </div>
  {% empty %}
    <p class="text-muted">¡Todas las insignias desbloqueadas!</p>
  {% endfor %}
</div>
{% endblock %}
''')


write("gamificacion/templates/gamificacion/estadisticas.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">📈 Mis Estadísticas</h2>

<div class="row">
  <div class="col-md-6">
    <ul class="list-group">
      <li class="list-group-item d-flex justify-content-between">
        <span>💎 XP Total</span><strong>{{ perfil.xp_total }}</strong>
      </li>
      <li class="list-group-item d-flex justify-content-between">
        <span>🏅 Nivel</span><strong>{{ perfil.nivel_actual }} ({{ perfil.titulo_nivel }})</strong>
      </li>
      <li class="list-group-item d-flex justify-content-between">
        <span>🔥 Racha</span><strong>{{ perfil.racha_dias }} días</strong>
      </li>
      <li class="list-group-item d-flex justify-content-between">
        <span>🎓 Cursos completados</span><strong>{{ perfil.cursos_completados }}</strong>
      </li>
      <li class="list-group-item d-flex justify-content-between">
        <span>📚 Lecciones completadas</span><strong>{{ perfil.lecciones_completadas }}</strong>
      </li>
    </ul>
  </div>
</div>
{% endblock %}
''')


# ==================================================
# 8. settings.py — añadir app
# ==================================================
settings_path = os.path.join(BASE, "config", "settings.py")
with open(settings_path, encoding="utf-8") as f:
    settings = f.read()

if "gamificacion" not in settings:
    settings = settings.replace(
        '"certificaciones",',
        '"certificaciones",\n    "gamificacion",'
    )
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings)
    print("[OK] settings.py — añadido 'gamificacion' a INSTALLED_APPS")
else:
    print("[SKIP] settings.py — 'gamificacion' ya estaba")


# ==================================================
# 9. config/urls.py — añadir ruta
# ==================================================
urls_path = os.path.join(BASE, "config", "urls.py")
with open(urls_path, encoding="utf-8") as f:
    urls = f.read()

if 'include("gamificacion.urls")' not in urls:
    urls = urls.replace(
        'path("", include("academia.urls")),',
        'path("", include("academia.urls")),\n    path("estudiante/", include("gamificacion.urls")),'
    )
    with open(urls_path, "w", encoding="utf-8") as f:
        f.write(urls)
    print("[OK] config/urls.py — añadido '/estudiante/'")
else:
    print("[SKIP] config/urls.py — ya tenía gamificacion")


# ==================================================
# 10. Migrar
# ==================================================
print("\n=== Migrando BD ===")
from django.core.management import call_command

call_command("makemigrations", "gamificacion", verbosity=0)
call_command("migrate", verbosity=0)
print("[OK] Migraciones aplicadas")


# ==================================================
# 11. Datos de prueba: insignias + usuario demo
# ==================================================
print("\n=== Creando datos de prueba ===")
from gamificacion.models import Insignia, PerfilGamificacion
from django.contrib.auth import get_user_model

User = get_user_model()

INSIGNIAS = [
    ("Primeros Pasos", "Completa tu primera lección", "🌱", "estrella", 10, 0, 1, 1),
    ("Aprendiz Aplicado", "Completa 5 lecciones", "⭐", "estrella", 50, 0, 5, 2),
    ("Estudiante Constante", "Completa 10 lecciones", "⭐", "estrella", 100, 0, 10, 3),
    ("Lector Voraz", "Completa 25 lecciones", "📚", "libro", 250, 0, 25, 4),
    ("Racha de Fuego", "Mantén 7 días de racha", "🔥", "medalla", 0, 0, 0, 5),
    ("Coleccionista", "Completa 1 curso entero", "🏅", "medalla", 0, 1, 0, 6),
    ("Maestro de Cursos", "Completa 5 cursos", "🏆", "trofeo", 0, 5, 0, 7),
    ("Sabio", "Alcanza 500 XP", "🧠", "medalla", 500, 0, 0, 8),
    ("Erudito", "Alcanza 1000 XP", "📖", "libro", 1000, 0, 0, 9),
    ("Leyenda", "Alcanza 5000 XP", "👑", "corona", 5000, 0, 0, 10),
]

for nombre, desc, icono, tipo, xp, cursos, lecciones, orden in INSIGNIAS:
    obj, created = Insignia.objects.get_or_create(
        nombre=nombre,
        defaults={
            "descripcion": desc,
            "icono": icono,
            "tipo": tipo,
            "requisito_xp": xp,
            "requisito_cursos": cursos,
            "requisito_lecciones": lecciones,
            "orden": orden,
        }
    )
    if created:
        print(f"  + Insignia: {icono} {nombre}")

# Usuario demo
if not User.objects.filter(username="estudiante").exists():
    u = User.objects.create_user("estudiante", "est@example.com", "estudiante123")
    PerfilGamificacion.objects.get_or_create(usuario=u, defaults={"xp_total": 150, "nivel_actual": 1})
    print("[OK] Usuario demo: estudiante / estudiante123")
else:
    print("[SKIP] Usuario 'estudiante' ya existe")


# ==================================================
# 12. Resumen final
# ==================================================
print("\n" + "=" * 50)
print("  GAMIFICACIÓN INSTALADA")
print("=" * 50)
print()
print("URLs nuevas:")
print("  http://127.0.0.1:8011/estudiante/          → Dashboard")
print("  http://127.0.0.
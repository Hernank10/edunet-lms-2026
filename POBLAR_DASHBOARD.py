# -*- coding: utf-8 -*-
"""
POBLAR_DASHBOARD.py
Enriquece el dashboard público con stats, recursos, HTMLs y categorías.
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
# 1. VIEWS de academia — dashboard enriquecido
# ============================================================
write("academia/views.py", '''from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from .models import Curso, Leccion, Inscripcion
from progreso.models import ProgresoLeccion
from contenido.models import Recurso, Tecnica, HtmlInteractivo
from ejercicios.models import Evaluacion


# ============================================================
# DASHBOARD PÚBLICO
# ============================================================
def dashboard(request):
    """Dashboard público con todo el contenido."""
    # Cursos
    cursos = Curso.objects.filter(activo=True).select_related("nivel").order_by("titulo")
    total_cursos = cursos.count()

    # Recursos JSON
    total_recursos = Recurso.objects.count()
    total_tecnicas = Tecnica.objects.count()

    # HTMLs
    total_htmls = HtmlInteractivo.objects.count()

    # Usuarios y certificados
    from django.contrib.auth import get_user_model
    from certificaciones.models import Certificado
    User = get_user_model()
    total_usuarios = User.objects.count()
    total_certificados = Certificado.objects.count()

    # Categorías con contadores
    categorias = []
    for codigo, nombre in Recurso.CATEGORIAS:
        n_rec = Recurso.objects.filter(categoria=codigo).count()
        n_html = HtmlInteractivo.objects.filter(categoria=codigo).count()
        if n_rec + n_html > 0:
            categorias.append({
                "codigo": codigo,
                "nombre": nombre,
                "recursos": n_rec,
                "htmls": n_html,
                "total": n_rec + n_html,
            })
    categorias.sort(key=lambda x: -x["total"])

    # Últimos recursos (6)
    ultimos_recursos = Recurso.objects.all().order_by("-fecha_importacion")[:6]

    # Últimos HTMLs (6)
    ultimos_htmls = HtmlInteractivo.objects.all().order_by("-fecha_importacion")[:6]

    # Cursos por nivel
    niveles = {}
    for curso in cursos:
        codigo = curso.nivel.codigo
        niveles[codigo] = niveles.get(codigo, 0) + 1

    return render(request, "academia/dashboard.html", {
        "cursos": cursos[:12],  # primeros 12
        "total_cursos": total_cursos,
        "total_recursos": total_recursos,
        "total_tecnicas": total_tecnicas,
        "total_htmls": total_htmls,
        "total_usuarios": total_usuarios,
        "total_certificados": total_certificados,
        "categorias": categorias,
        "ultimos_recursos": ultimos_recursos,
        "ultimos_htmls": ultimos_htmls,
        "niveles": niveles,
    })


# ============================================================
# CURSO DETALLE
# ============================================================
def curso_detail(request, slug):
    """Detalle de un curso con lecciones."""
    curso = get_object_or_404(Curso, slug=slug)
    lecciones = curso.lecciones.all()
    return render(request, "academia/curso_detail.html", {
        "curso": curso,
        "lecciones": lecciones,
    })


# ============================================================
# CURSO → LECCIONES
# ============================================================
def course_lessons(request, curso_id):
    """Lecciones de un curso."""
    curso = get_object_or_404(Curso, id=curso_id)
    lecciones = Leccion.objects.filter(curso=curso).order_by("orden")

    if request.user.is_authenticated:
        progreso_usuario = {
            p.leccion_id: p.completada
            for p in ProgresoLeccion.objects.filter(
                usuario=request.user,
                leccion__curso=curso
            )
        }
    else:
        progreso_usuario = {}

    lecciones_con_estado = []
    desbloqueada = True

    for leccion in lecciones:
        completada = progreso_usuario.get(leccion.id, False)
        lecciones_con_estado.append({
            "leccion": leccion,
            "completada": completada,
            "desbloqueada": desbloqueada,
        })
        if not completada:
            desbloqueada = False

    return render(request, "academia/course_lessons.html", {
        "curso": curso,
        "lecciones": lecciones_con_estado,
    })


# ============================================================
# LECCIÓN DETALLE
# ============================================================
def lesson_detail(request, pk):
    """Detalle de una lección."""
    leccion = get_object_or_404(Leccion, pk=pk)
    return render(request, "academia/lesson_detail.html", {
        "leccion": leccion,
    })


# ============================================================
# LECCIÓN DETALLE por slug (compatibilidad)
# ============================================================
def leccion_detail(request, slug):
    """Alias de lesson_detail por slug."""
    leccion = get_object_or_404(Leccion, slug=slug)
    return render(request, "academia/lesson_detail.html", {
        "leccion": leccion,
    })
''')


# ============================================================
# 2. URLS de academia
# ============================================================
write("academia/urls.py", '''from django.urls import path
from . import views

app_name = "academia"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("curso/<slug:slug>/", views.curso_detail, name="curso_detail"),
    path("curso/<int:curso_id>/lecciones/", views.course_lessons, name="course_lessons"),
    path("leccion/<int:pk>/", views.lesson_detail, name="lesson_detail"),
    path("leccion/slug/<slug:slug>/", views.leccion_detail, name="leccion_detail"),
]
''')


# ============================================================
# 3. Template dashboard.html enriquecido
# ============================================================
write("academia/templates/academia/dashboard.html", '''{% extends "base.html" %}

{% block content %}
<div class="container mt-4">

  <!-- HERO -->
  <div class="p-5 mb-4 bg-primary text-white rounded">
    <h1 class="display-4">🎓 Academia Global de Castellano</h1>
    <p class="lead">Aprende, practica y certifícate con 42 cursos, 2.000+ técnicas y 428 apps interactivas.</p>
    <a href="{% url 'contenido:hub' %}" class="btn btn-light btn-lg">Explorar contenido →</a>
    <a href="{% url 'gamificacion:dashboard' %}" class="btn btn-outline-light btn-lg">Mi dashboard</a>
  </div>

  <!-- STATS -->
  <div class="row mb-4">
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-primary h-100">
        <div class="card-body text-center">
          <h3>{{ total_cursos }}</h3>
          <small>🎓 Cursos</small>
        </div>
      </div>
    </div>
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-success h-100">
        <div class="card-body text-center">
          <h3>{{ total_recursos }}</h3>
          <small>📄 Recursos</small>
        </div>
      </div>
    </div>
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-info h-100">
        <div class="card-body text-center">
          <h3>{{ total_tecnicas }}</h3>
          <small>🎯 Técnicas</small>
        </div>
      </div>
    </div>
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-warning h-100">
        <div class="card-body text-center">
          <h3>{{ total_htmls }}</h3>
          <small>🌐 HTMLs</small>
        </div>
      </div>
    </div>
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-secondary h-100">
        <div class="card-body text-center">
          <h3>{{ total_usuarios }}</h3>
          <small>👥 Usuarios</small>
        </div>
      </div>
    </div>
    <div class="col-md-3 col-lg-2 mb-3">
      <div class="card text-white bg-dark h-100">
        <div class="card-body text-center">
          <h3>{{ total_certificados }}</h3>
          <small>🏆 Certificados</small>
        </div>
      </div>
    </div>
  </div>

  <!-- ACCESOS RÁPIDOS -->
  <div class="row mb-4">
    <div class="col-md-4 mb-3">
      <a href="{% url 'contenido:lista_recursos' %}" class="card h-100 text-decoration-none">
        <div class="card-body text-center">
          <div style="font-size:3rem;">📄</div>
          <h5>Recursos JSON</h5>
          <p class="text-muted">{{ total_recursos }} recursos con {{ total_tecnicas }} técnicas</p>
        </div>
      </a>
    </div>
    <div class="col-md-4 mb-3">
      <a href="{% url 'contenido:lista_htmls' %}" class="card h-100 text-decoration-none">
        <div class="card-body text-center">
          <div style="font-size:3rem;">🌐</div>
          <h5>HTMLs interactivos</h5>
          <p class="text-muted">{{ total_htmls }} apps: flotas, cuadernos, juegos</p>
        </div>
      </a>
    </div>
    <div class="col-md-4 mb-3">
      <a href="{% url 'contenido:hub' %}" class="card h-100 text-decoration-none">
        <div class="card-body text-center">
          <div style="font-size:3rem;">📚</div>
          <h5>Hub de contenido</h5>
          <p class="text-muted">{{ categorias|length }} categorías temáticas</p>
        </div>
      </a>
    </div>
  </div>

  <!-- CATEGORÍAS -->
  <h3 class="mb-3">📂 Explorar por categoría</h3>
  <div class="row mb-5">
    {% for cat in categorias %}
      <div class="col-md-4 col-lg-3 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <h6>{{ cat.nombre }}</h6>
            <p class="text-muted small mb-2">
              {{ cat.recursos }} recursos · {{ cat.htmls }} HTMLs
            </p>
            <div class="d-grid gap-1">
              <a href="{% url 'contenido:lista_recursos' %}?categoria={{ cat.codigo }}"
                 class="btn btn-sm btn-outline-primary">
                📄 {{ cat.recursos }} recursos
              </a>
              <a href="{% url 'contenido:lista_htmls' %}?categoria={{ cat.codigo }}"
                 class="btn btn-sm btn-outline-success">
                🌐 {{ cat.htmls }} HTMLs
              </a>
            </div>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>

  <!-- ÚLTIMOS RECURSOS -->
  <h3 class="mb-3">📄 Últimos recursos añadidos</h3>
  <div class="row mb-5">
    {% for rec in ultimos_recursos %}
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <span class="badge bg-secondary">{{ rec.get_categoria_display }}</span>
            <h6 class="mt-2">{{ rec.titulo|truncatechars:55 }}</h6>
            <p class="small text-muted">🎯 {{ rec.total_real }} técnicas</p>
            <a href="{% url 'contenido:detalle_recurso' rec.pk %}" class="btn btn-primary btn-sm w-100">
              Ver técnicas
            </a>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>

  <!-- ÚLTIMOS HTMLs -->
  <h3 class="mb-3">🌐 Últimas apps interactivas</h3>
  <div class="row mb-5">
    {% for html in ultimos_htmls %}
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <span class="badge bg-warning text-dark">{{ html.get_tipo_display }}</span>
            <h6 class="mt-2">{{ html.titulo|truncatechars:55 }}</h6>
            <p class="small text-muted">{{ html.get_categoria_display }}</p>
            <a href="{% url 'contenido:visor_html' html.slug %}" class="btn btn-success btn-sm w-100">
              ▶ Abrir
            </a>
          </div>
        </div>
      </div>
    {% endfor %}
  </div>

  <!-- CURSOS -->
  <h3 class="mb-3">🎓 Cursos ({{ total_cursos }})</h3>
  <div class="row">
    {% for curso in cursos %}
      <div class="col-md-4 mb-3">
        <div class="card h-100">
          <div class="card-body">
            <span class="badge bg-secondary">{{ curso.nivel.codigo }}</span>
            <h6 class="mt-2">{{ curso.titulo|truncatechars:60 }}</h6>
            <p class="small text-muted">{{ curso.descripcion|truncatechars:80 }}</p>
            <a href="{% url 'academia:curso_detail' curso.slug %}"
               class="btn btn-primary btn-sm w-100">
              Ver curso
            </a>
          </div>
        </div>
      </div>
    {% empty %}
      <p class="text-muted">No hay cursos aún.</p>
    {% endfor %}
  </div>

  <div class="text-center mt-4 mb-5">
    <a href="{% url 'gamificacion:dashboard' %}" class="btn btn-lg btn-success">
      🎮 Ir a mi panel de estudiante
    </a>
  </div>

</div>
{% endblock %}
''')


# ============================================================
# 4. Actualizar base.html — navbar con enlaces clave
# ============================================================
write("templates/base.html", '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Academia Global de Castellano</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>

  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <a class="navbar-brand" href="/">🌍 Castellano Global</a>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto">
          <li class="nav-item"><a class="nav-link" href="{% url 'contenido:hub' %}">📚 Contenido</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'contenido:lista_recursos' %}">📄 Recursos</a></li>
          <li class="nav-item"><a class="nav-link" href="{% url 'contenido:lista_htmls' %}">🌐 HTMLs</a></li>
        </ul>
        <ul class="navbar-nav">
          {% if user.is_authenticated %}
            {% if user.is_superuser %}
              <li class="nav-item"><a class="nav-link" href="/admin/">⚙️ Admin</a></li>
            {% elif user.is_staff %}
              <li class="nav-item"><a class="nav-link" href="{% url 'profesor:dashboard' %}">👨‍🏫 Profesor</a></li>
            {% else %}
              <li class="nav-item"><a class="nav-link" href="{% url 'gamificacion:dashboard' %}">🎮 Estudiante</a></li>
            {% endif %}
            <li class="nav-item"><a class="nav-link" href="{% url 'accounts:perfil' %}">👤 {{ user.username }}</a></li>
            <li class="nav-item">
              <form method="post" action="{% url 'logout' %}" class="d-inline">
                {% csrf_token %}
                <button type="submit" class="btn btn-link nav-link">Salir</button>
              </form>
            </li>
          {% else %}
            <li class="nav-item"><a class="nav-link" href="{% url 'login' %}">🔐 Entrar</a></li>
            <li class="nav-item"><a class="nav-link" href="{% url 'accounts:registro' %}">📝 Registro</a></li>
          {% endif %}
        </ul>
      </div>
    </div>
  </nav>

  <main class="container-fluid">
    {% if messages %}
      {% for message in messages %}
        <div class="alert alert-{{ message.tags }} mt-3">{{ message }}</div>
      {% endfor %}
    {% endif %}

    {% block content %}{% endblock %}
  </main>

  <footer class="bg-dark text-white text-center py-3 mt-5">
    <small>🎓 EduNet Academia 2026 · LMS de Lengua Castellana</small>
  </footer>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''')


print()
print("=" * 60)
print("  DASHBOARD POBLADO")
print("=" * 60)
print()
print("Rearrancar:")
print("  E:\\pydj5.bat manage.py runserver 8011 --noreload")
print()
print("Abrir:")
print("  http://127.0.0.1:8011/")
# -*- coding: utf-8 -*-
"""
MEJORAR_ESTUDIANTE.py
Mejora el dashboard del estudiante con más secciones y vistas.
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
# 1. AMPLIAR VIEWS.PY DE GAMIFICACION
# ============================================================
write("gamificacion/views.py", '''from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from academia.models import Curso, Leccion, Inscripcion
from progreso.models import ProgresoLeccion
from ejercicios.models import Evaluacion, IntentoEvaluacion
from certificaciones.models import Certificado
from contenido.models import Recurso, Tecnica, HtmlInteractivo
from .models import Insignia, Logro, PerfilGamificacion


def _get_perfil(user):
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=user)
    return perfil


# ============================================================
# DASHBOARD PRINCIPAL DEL ESTUDIANTE
# ============================================================
@login_required
def dashboard_estudiante(request):
    """Dashboard principal del estudiante."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    # Inscripciones activas (últimas 6)
    inscripciones_activas = Inscripcion.objects.filter(
        usuario=usuario, activa=True
    ).select_related("curso", "curso__nivel").order_by("-fecha")[:6]

    # Estadísticas
    total_inscripciones = Inscripcion.objects.filter(usuario=usuario).count()
    completadas = Inscripcion.objects.filter(usuario=usuario, completado=True).count()
    en_progreso = Inscripcion.objects.filter(usuario=usuario, activa=True, completado=False).count()

    # Evaluaciones
    intentos = IntentoEvaluacion.objects.filter(usuario=usuario)
    evaluaciones_aprobadas = intentos.filter(aprobado=True).count()
    evaluaciones_totales = intentos.count()

    # Certificados
    certs = Certificado.objects.filter(usuario=usuario).count()

    # Logros
    logros = Logro.objects.filter(usuario=usuario).select_related("insignia")
    total_insignias = Insignia.objects.count()
    ganadas = logros.count()

    # Insignias recientes (últimas 5)
    ultimas_insignias = logros.order_by("-fecha")[:5]

    # Progreso global
    total_lecciones = ProgresoLeccion.objects.filter(usuario=usuario, completada=True).count()

    # Cursos recomendados (los que no está inscrito)
    cursos_inscritos_ids = Inscripcion.objects.filter(usuario=usuario).values_list("curso_id", flat=True)
    recomendados = Curso.objects.filter(activo=True).exclude(id__in=cursos_inscritos_ids)[:3]

    # Actividad reciente (últimos intentos)
    actividad = intentos.select_related("evaluacion", "evaluacion__curso").order_by("-fecha")[:5]

    return render(request, "gamificacion/dashboard.html", {
        "perfil": perfil,
        "inscripciones": inscripciones_activas,
        "total_inscripciones": total_inscripciones,
        "completadas": completadas,
        "en_progreso": en_progreso,
        "evaluaciones_aprobadas": evaluaciones_aprobadas,
        "evaluaciones_totales": evaluaciones_totales,
        "certs": certs,
        "ganadas": ganadas,
        "total_insignias": total_insignias,
        "ultimas_insignias": ultimas_insignias,
        "total_lecciones": total_lecciones,
        "recomendados": recomendados,
        "actividad": actividad,
    })


# ============================================================
# MIS CURSOS
# ============================================================
@login_required
def mis_cursos(request):
    """Lista completa de cursos del estudiante."""
    usuario = request.user

    filtro = request.GET.get("filtro", "todos")
    qs = Inscripcion.objects.filter(usuario=usuario).select_related("curso", "curso__nivel")

    if filtro == "activos":
        qs = qs.filter(activa=True, completado=False)
    elif filtro == "completados":
        qs = qs.filter(completado=True)

    qs = qs.order_by("-fecha")

    return render(request, "gamificacion/mis_cursos.html", {
        "inscripciones": qs,
        "filtro": filtro,
    })


# ============================================================
# PRÁCTICAS
# ============================================================
@login_required
def practicas(request):
    """Prácticas pendientes."""
    usuario = request.user
    pendientes = []

    for insc in Inscripcion.objects.filter(usuario=usuario, activa=True, completado=False).select_related("curso"):
        for lec in insc.curso.lecciones.all()[:3]:
            completada = ProgresoLeccion.objects.filter(
                usuario=usuario, leccion=lec, completada=True
            ).exists()
            if not completada:
                pendientes.append({
                    "leccion": lec,
                    "curso": insc.curso,
                    "orden": lec.orden,
                })
                break

    return render(request, "gamificacion/practicas.html", {"pendientes": pendientes[:20]})


# ============================================================
# EVALUACIONES
# ============================================================
@login_required
def evaluaciones(request):
    """Evaluaciones disponibles."""
    usuario = request.user

    # Solo evaluaciones de cursos en los que está inscrito
    cursos_ids = Inscripcion.objects.filter(usuario=usuario).values_list("curso_id", flat=True)
    evaluaciones_qs = Evaluacion.objects.filter(curso_id__in=cursos_ids).select_related("curso")

    data = []
    for ev in evaluaciones_qs:
        intentos = IntentoEvaluacion.objects.filter(usuario=usuario, evaluacion=ev)
        mejor = intentos.order_by("-nota").first()
        data.append({
            "evaluacion": ev,
            "intentos": intentos.count(),
            "mejor_nota": mejor.nota if mejor else None,
            "aprobado": intentos.filter(aprobado=True).exists(),
            "num_preguntas": ev.preguntas.count(),
        })

    return render(request, "gamificacion/evaluaciones.html", {"evaluaciones": data})


# ============================================================
# MIS LOGROS
# ============================================================
@login_required
def mis_logros(request):
    """Insignias ganadas y bloqueadas."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    todas = Insignia.objects.all()
    ganadas_ids = set(Logro.objects.filter(usuario=usuario).values_list("insignia_id", flat=True))
    ganadas = [i for i in todas if i.id in ganadas_ids]
    bloqueadas = [i for i in todas if i.id not in ganadas_ids]

    return render(request, "gamificacion/mis_logros.html", {
        "perfil": perfil,
        "ganadas": ganadas,
        "bloqueadas": bloqueadas,
    })


# ============================================================
# ESTADÍSTICAS
# ============================================================
@login_required
def estadisticas(request):
    """Estadísticas detalladas."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    # Progreso por curso
    cursos_data = []
    for insc in Inscripcion.objects.filter(usuario=usuario).select_related("curso"):
        intentos = IntentoEvaluacion.objects.filter(usuario=usuario, evaluacion__curso=insc.curso)
        promedio = intentos.aggregate(avg=__import__("django.db.models", fromlist=["Avg"]).Avg("nota"))["avg"]

        cursos_data.append({
            "curso": insc.curso,
            "progreso": insc.progreso_pct,
            "intentos": intentos.count(),
            "promedio": round(promedio, 1) if promedio else 0,
        })

    return render(request, "gamificacion/estadisticas.html", {
        "perfil": perfil,
        "cursos_data": cursos_data,
    })


# ============================================================
# MIS CERTIFICADOS
# ============================================================
@login_required
def mis_certificados(request):
    """Certificados obtenidos + cursos en progreso."""
    usuario = request.user

    obtenidos = Certificado.objects.filter(usuario=usuario).select_related("curso")

    # Cursos que pueden generar certificado
    en_progreso = []
    for insc in Inscripcion.objects.filter(usuario=usuario, completado=True):
        if not Certificado.objects.filter(usuario=usuario, curso=insc.curso).exists():
            en_progreso.append(insc.curso)

    return render(request, "gamificacion/mis_certificados.html", {
        "obtenidos": obtenidos,
        "en_progreso": en_progreso,
    })


# ============================================================
# MI PERFIL
# ============================================================
@login_required
def mi_perfil(request):
    """Perfil del estudiante."""
    usuario = request.user
    perfil = _get_perfil(usuario)

    return render(request, "gamificacion/mi_perfil.html", {
        "perfil": perfil,
        "usuario": usuario,
    })


# ============================================================
# RECOMENDADOS
# ============================================================
@login_required
def recomendados(request):
    """Cursos recomendados (no inscritos)."""
    usuario = request.user
    cursos_inscritos = Inscripcion.objects.filter(usuario=usuario).values_list("curso_id", flat=True)

    cursos = Curso.objects.filter(activo=True).exclude(id__in=cursos_inscritos).select_related("nivel")[:12]

    # Enriquecer con número de lecciones
    cursos_data = []
    for c in cursos:
        cursos_data.append({
            "curso": c,
            "lecciones": c.lecciones.count(),
        })

    return render(request, "gamificacion/recomendados.html", {"cursos": cursos_data})
''')


# ============================================================
# 2. ACTUALIZAR URLS DE GAMIFICACION
# ============================================================
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
    path("certificados/", views.mis_certificados, name="mis_certificados"),
    path("perfil/", views.mi_perfil, name="mi_perfil"),
    path("recomendados/", views.recomendados, name="recomendados"),
]
''')


# ============================================================
# 3. TEMPLATES NUEVOS
# ============================================================

# Dashboard mejorado
write("gamificacion/templates/gamificacion/dashboard.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">👋 ¡Hola, {{ user.get_full_name|default:user.username }}!</h2>

<!-- Stats -->
<div class="row mb-4">
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-primary h-100">
      <div class="card-body text-center">
        <h3>{{ perfil.xp_total }}</h3>
        <small>💎 XP Total</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-success h-100">
      <div class="card-body text-center">
        <h3>Nivel {{ perfil.nivel_actual }}</h3>
        <small>🏅 {{ perfil.titulo_nivel|default:"Aprendiz" }}</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-warning h-100">
      <div class="card-body text-center">
        <h3>{{ perfil.racha_dias }}</h3>
        <small>🔥 Racha de días</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-white bg-info h-100">
      <div class="card-body text-center">
        <h3>{{ total_lecciones }}</h3>
        <small>📚 Lecciones completadas</small>
      </div>
    </div>
  </div>
</div>

<!-- Barra de nivel -->
<div class="card mb-4">
  <div class="card-body">
    <div class="d-flex justify-content-between mb-2">
      <strong>Nivel {{ perfil.nivel_actual }} → {{ perfil.nivel_actual|add:1 }}</strong>
      <span>{{ perfil.xp_total }} / {{ perfil.xp_siguiente_nivel|default:"500" }} XP</span>
    </div>
    <div class="progress" style="height: 25px;">
      <div class="progress-bar bg-success progress-bar-striped progress-bar-animated"
           style="width: {{ perfil.progreso_nivel|default:0 }}%;">
        {{ perfil.progreso_nivel|default:0 }}%
      </div>
    </div>
  </div>
</div>

<!-- Resumen en 4 columnas -->
<div class="row mb-4">
  <div class="col-md-3 mb-3">
    <div class="card text-center border-primary">
      <div class="card-body">
        <h4 class="text-primary">{{ total_inscripciones }}</h4>
        <small>🎓 Mis cursos</small>
        <br><small class="text-muted">{{ completadas }} completados</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-center border-success">
      <div class="card-body">
        <h4 class="text-success">{{ evaluaciones_aprobadas }}/{{ evaluaciones_totales }}</h4>
        <small>📝 Evaluaciones</small>
        <br><small class="text-muted">Aprobadas</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-center border-warning">
      <div class="card-body">
        <h4 class="text-warning">{{ certs }}</h4>
        <small>🏆 Certificados</small>
        <br><small class="text-muted">Obtenidos</small>
      </div>
    </div>
  </div>
  <div class="col-md-3 mb-3">
    <div class="card text-center border-info">
      <div class="card-body">
        <h4 class="text-info">{{ ganadas }}/{{ total_insignias }}</h4>
        <small>🏅 Insignias</small>
        <br><small class="text-muted">Ganadas</small>
      </div>
    </div>
  </div>
</div>

<!-- Cursos en progreso -->
<div class="row mb-4">
  <div class="col-md-8">
    <h4>🎓 Continúa donde lo dejaste</h4>
    <div class="row">
      {% for ins in inscripciones %}
        <div class="col-md-6 mb-3">
          <div class="card h-100">
            <div class="card-body">
              <h6>{{ ins.curso.titulo|truncatechars:55 }}</h6>
              <small class="text-muted">{{ ins.curso.nivel.codigo }}</small>
              <div class="progress my-2" style="height:12px;">
                <div class="progress-bar" style="width: {{ ins.progreso_pct }}%;">
                  {{ ins.progreso_pct }}%
                </div>
              </div>
              {% if ins.completado %}
                <span class="badge bg-success">✅ Completado</span>
              {% else %}
                <a href="{% url 'academia:course_lessons' ins.curso.id %}" class="btn btn-primary btn-sm w-100">
                  Continuar →
                </a>
              {% endif %}
            </div>
          </div>
        </div>
      {% empty %}
        <p class="text-muted">No tienes cursos activos.
          <a href="{% url 'gamificacion:recomendados' %}">Ver recomendados</a>
        </p>
      {% endfor %}
    </div>
  </div>

  <div class="col-md-4">
    <h4>🏅 Últimas insignias</h4>
    <div class="card">
      <div class="card-body">
        {% for logro in ultimas_insignias %}
          <div class="d-flex align-items-center mb-2">
            <div style="font-size:2rem; width:50px;">{{ logro.insignia.icono }}</div>
            <div>
              <strong>{{ logro.insignia.nombre }}</strong>
              <br><small class="text-muted">{{ logro.fecha|date:"d M Y" }}</small>
            </div>
          </div>
        {% empty %}
          <p class="text-muted">Aún no has ganado insignias.</p>
        {% endfor %}
        <a href="{% url 'gamificacion:mis_logros' %}" class="btn btn-sm btn-outline-primary w-100 mt-2">
          Ver todas →
        </a>
      </div>
    </div>
  </div>
</div>

<!-- Actividad reciente -->
<div class="row">
  <div class="col-md-6">
    <h4>📅 Actividad reciente</h4>
    <ul class="list-group">
      {% for a in actividad %}
        <li class="list-group-item d-flex justify-content-between">
          <div>
            <small>{{ a.evaluacion.titulo|truncatechars:50 }}</small>
          </div>
          <div>
            {% if a.aprobado %}
              <span class="badge bg-success">{{ a.nota }}%</span>
            {% else %}
              <span class="badge bg-danger">{{ a.nota }}%</span>
            {% endif %}
          </div>
        </li>
      {% empty %}
        <li class="list-group-item text-muted">Sin actividad reciente.</li>
      {% endfor %}
    </ul>
  </div>

  <div class="col-md-6">
    <h4>🎯 Cursos recomendados</h4>
    <div class="list-group">
      {% for c in recomendados %}
        <a href="{% url 'academia:course_lessons' c.id %}" class="list-group-item list-group-item-action">
          <div class="d-flex justify-content-between">
            <div>
              <strong>{{ c.titulo|truncatechars:50 }}</strong>
              <br><small>{{ c.nivel.codigo }}</small>
            </div>
            <span class="badge bg-primary align-self-center">Ver</span>
          </div>
        </a>
      {% empty %}
        <p class="text-muted">Sin recomendaciones.</p>
      {% endfor %}
    </div>
  </div>
</div>
{% endblock %}
''')


# Mis certificados
write("gamificacion/templates/gamificacion/mis_certificados.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🏆 Mis Certificados</h2>

<h4>Obtenidos ({{ obtenidos|length }})</h4>
<div class="row mb-4">
  {% for cert in obtenidos %}
    <div class="col-md-6 mb-3">
      <div class="card border-success h-100">
        <div class="card-body">
          <div class="d-flex justify-content-between mb-2">
            <h5>{{ cert.curso.titulo|truncatechars:50 }}</h5>
            <span class="badge bg-success">✅</span>
          </div>
          <p class="small mb-1">📅 {{ cert.fecha_emision|date:"d M Y" }}</p>
          <p class="small mb-2">📝 Nota: {{ cert.nota_final }}%</p>
          <p class="small">🔑 Código: <code>{{ cert.codigo_corto }}</code></p>
          <a href="{% url 'certificaciones:ver_certificado' cert.codigo %}" class="btn btn-success btn-sm">
            Ver certificado
          </a>
        </div>
      </div>
    </div>
  {% empty %}
    <p class="text-muted">Aún no has obtenido certificados.</p>
  {% endfor %}
</div>

<h4>Cursos completados sin certificado ({{ en_progreso|length }})</h4>
<div class="row">
  {% for curso in en_progreso %}
    <div class="col-md-4 mb-3">
      <div class="card">
        <div class="card-body">
          <h6>{{ curso.titulo|truncatechars:50 }}</h6>
          <span class="badge bg-warning">Pendiente emitir</span>
        </div>
      </div>
    </div>
  {% empty %}
    <p class="text-muted">Todos los cursos completados tienen certificado.</p>
  {% endfor %}
</div>
{% endblock %}
''')


# Mi perfil
write("gamificacion/templates/gamificacion/mi_perfil.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">👤 Mi Perfil</h2>

<div class="row">
  <div class="col-md-4 mb-3">
    <div class="card text-center">
      <div class="card-body">
        <div style="font-size:5rem;">👤</div>
        <h4>{{ usuario.get_full_name|default:usuario.username }}</h4>
        <p class="text-muted">@{{ usuario.username }}</p>
        <p class="badge bg-primary">{{ perfil.titulo_nivel|default:"Aprendiz" }}</p>
      </div>
    </div>
  </div>

  <div class="col-md-8">
    <div class="card">
      <div class="card-body">
        <h5>Información</h5>
        <ul class="list-group list-group-flush">
          <li class="list-group-item d-flex justify-content-between">
            <span>📧 Email</span><strong>{{ usuario.email|default:"—" }}</strong>
          </li>
          <li class="list-group-item d-flex justify-content-between">
            <span>🌍 Idioma nativo</span><strong>{{ usuario.idioma_nativo|default:"Castellano" }}</strong>
          </li>
          <li class="list-group-item d-flex justify-content-between">
            <span>🕐 Zona horaria</span><strong>{{ usuario.zona_horaria|default:"UTC" }}</strong>
          </li>
          <li class="list-group-item d-flex justify-content-between">
            <span>📅 Miembro desde</span><strong>{{ usuario.date_joined|date:"M Y" }}</strong>
          </li>
        </ul>
      </div>
    </div>

    <div class="card mt-3">
      <div class="card-body">
        <h5>Progreso de gamificación</h5>
        <ul class="list-group list-group-flush">
          <li class="list-group-item d-flex justify-content-between">
            <span>💎 XP Total</span><strong>{{ perfil.xp_total }}</strong>
          </li>
          <li class="list-group-item d-flex justify-content-between">
            <span>🏅 Nivel</span><strong>{{ perfil.nivel_actual }}</strong>
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
  </div>
</div>
{% endblock %}
''')


# Recomendados
write("gamificacion/templates/gamificacion/recomendados.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🎯 Cursos recomendados para ti</h2>
<div class="row">
  {% for item in cursos %}
    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <span class="badge bg-secondary">{{ item.curso.nivel.codigo }}</span>
          <h6 class="mt-2">{{ item.curso.titulo|truncatechars:60 }}</h6>
          <p class="small text-muted">{{ item.curso.descripcion|truncatechars:80 }}</p>
          <p class="small">📚 {{ item.lecciones }} lecciones</p>
          <a href="{% url 'academia:course_lessons' item.curso.id %}" class="btn btn-primary btn-sm w-100">
            Ver curso
          </a>
        </div>
      </div>
    </div>
  {% empty %}
    <p class="text-muted">No hay cursos recomendados.</p>
  {% endfor %}
</div>
{% endblock %}
''')


# Mis cursos (mejorado con filtros)
write("gamificacion/templates/gamificacion/mis_cursos.html", '''{% extends "gamificacion/_base_estudiante.html" %}
{% block contenido %}
<h2 class="mb-4">🎓 Mis Cursos</h2>

<ul class="nav nav-pills mb-3">
  <li class="nav-item">
    <a class="nav-link {% if filtro == 'todos' %}active{% endif %}" href="?filtro=todos">Todos</a>
  </li>
  <li class="nav-item">
    <a class="nav-link {% if filtro == 'activos' %}active{% endif %}" href="?filtro=activos">En progreso</a>
  </li>
  <li class="nav-item">
    <a class="nav-link {% if filtro == 'completados' %}active{% endif %}" href="?filtro=completados">Completados</a>
  </li>
</ul>

<div class="row">
  {% for ins in inscripciones %}
    <div class="col-md-4 mb-3">
      <div class="card h-100">
        <div class="card-body">
          <span class="badge bg-secondary">{{ ins.curso.nivel.codigo }}</span>
          <h6 class="mt-2">{{ ins.curso.titulo|truncatechars:60 }}</h6>
          <div class="progress my-2" style="height:12px;">
            <div class="progress-bar" style="width: {{ ins.progreso_pct }}%;">
              {{ ins.progreso_pct }}%
            </div>
          </div>
          {% if ins.completado %}
            <span class="badge bg-success w-100">✅ Completado</span>
          {% else %}
            <a href="{% url 'academia:course_lessons' ins.curso.id %}" class="btn btn-primary btn-sm w-100">
              Continuar
            </a>
          {% endif %}
        </div>
      </div>
    </div>
  {% empty %}
    <p class="text-muted">No tienes cursos en esta categoría.</p>
  {% endfor %}
</div>
{% endblock %}
''')


# ============================================================
# 4. REDIRECCIÓN POR ROL
# ============================================================
redir_path = os.path.join(BASE, "accounts", "views.py")
with open(redir_path, encoding="utf-8") as f:
    views_content = f.read()

# Añadir vista de redirección por rol
if "def panel(request):" not in views_content:
    views_content += '''


from django.shortcuts import redirect


def panel(request):
    """Redirige al usuario según su rol."""
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_superuser:
        return redirect("/admin/")
    elif request.user.is_staff:
        return redirect("profesor:dashboard")
    else:
        return redirect("gamificacion:dashboard")
'''
    with open(redir_path, "w", encoding="utf-8") as f:
        f.write(views_content)
    print("[OK] accounts/views.py — vista 'panel' añadida")


# Añadir URL para /panel/
accounts_urls = os.path.join(BASE, "accounts", "urls.py")
with open(accounts_urls, encoding="utf-8") as f:
    accounts_urls_content = f.read()

if '"panel/"' not in accounts_urls_content:
    accounts_urls_content = accounts_urls_content.replace(
        "urlpatterns = [",
        'urlpatterns = [\n    path("panel/", views.panel, name="panel"),'
    )
    with open(accounts_urls, "w", encoding="utf-8") as f:
        f.write(accounts_urls_content)
    print("[OK] accounts/urls.py — URL /panel/ añadida")


print()
print("=" * 60)
print("  DASHBOARD DEL ESTUDIANTE MEJORADO")
print("=" * 60)
print()
print("URLs nuevas:")
print("  /estudiante/                → Dashboard")
print("  /estudiante/cursos/          → Mis cursos")
print("  /estudiante/practicas/       → Prácticas pendientes")
print("  /estudiante/evaluaciones/    → Evaluaciones")
print("  /estudiante/logros/          → Insignias")
print("  /estudiante/certificados/    → Mis certificados")
print("  /estudiante/perfil/          → Mi perfil")
print("  /estudiante/recomendados/    → Cursos recomendados")
print("  /estudiante/estadisticas/    → Estadísticas")
print("  /panel/                      → Redirige por rol")
print()
print("Rearrancar:")
print("  E:\\pydj5.bat manage.py runserver 8011 --noreload")
print()
print("Probar con: prof_garcia / profesor1234")
print("             est001_lucía / estudiante1234")
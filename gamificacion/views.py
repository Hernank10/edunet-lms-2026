from django.shortcuts import render, get_object_or_404, redirect
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
    """Dashboard principal del estudiante con graficos y estadisticas."""
    import json
    from datetime import timedelta
    from django.utils import timezone

    usuario = request.user
    perfil = _get_perfil(usuario)

    # ============ INSCRIPCIONES ============
    inscripciones_activas = Inscripcion.objects.filter(
        usuario=usuario, activa=True
    ).select_related("curso", "curso__nivel").order_by("-fecha")[:6]

    total_inscripciones = Inscripcion.objects.filter(usuario=usuario).count()
    completadas = Inscripcion.objects.filter(usuario=usuario, completado=True).count()
    en_progreso = Inscripcion.objects.filter(usuario=usuario, activa=True, completado=False).count()
    sin_empezar = max(0, total_inscripciones - completadas - en_progreso)

    # ============ EVALUACIONES ============
    intentos = IntentoEvaluacion.objects.filter(usuario=usuario)
    evaluaciones_aprobadas = intentos.filter(aprobado=True).count()
    evaluaciones_totales = intentos.count()
    evaluaciones_reprobadas = evaluaciones_totales - evaluaciones_aprobadas

    # ============ CERTIFICADOS ============
    certs = Certificado.objects.filter(usuario=usuario).count()

    # ============ LOGROS ============
    logros = Logro.objects.filter(usuario=usuario).select_related("insignia")
    total_insignias = Insignia.objects.count()
    ganadas = logros.count()
    ultimas_insignias = logros.order_by("-fecha")[:5]

    # ============ PROGRESO ============
    total_lecciones = ProgresoLeccion.objects.filter(usuario=usuario, completada=True).count()

    # ============ CURSOS RECOMENDADOS ============
    cursos_inscritos_ids = Inscripcion.objects.filter(usuario=usuario).values_list("curso_id", flat=True)
    recomendados = Curso.objects.filter(activo=True).exclude(id__in=cursos_inscritos_ids)[:3]

    # ============ ACTIVIDAD RECIENTE ============
    actividad = intentos.select_related("evaluacion", "evaluacion__curso").order_by("-fecha")[:5]

    # ============ DATOS PARA GRAFICOS ============

    # --- Grafico A: Dona de cursos ---
    dona_labels = ["Completados", "En progreso", "Sin empezar"]
    dona_data = [completadas, en_progreso, sin_empezar]

    # --- Grafico B: Barras de progreso por curso ---
    inscripciones_con_progreso = Inscripcion.objects.filter(
        usuario=usuario
    ).select_related("curso").order_by("-progreso_pct")[:5]
    barras_labels = [i.curso.titulo[:35] + ("..." if len(i.curso.titulo) > 35 else "") for i in inscripciones_con_progreso]
    barras_data = [i.progreso_pct for i in inscripciones_con_progreso]

    # --- Grafico C: Linea de XP ultimos 30 dias ---
    hoy = timezone.now().date()
    hace_30 = hoy - timedelta(days=29)
    dias_labels = []
    dias_xp = []
    for i in range(30):
        dia = hace_30 + timedelta(days=i)
        dias_labels.append(dia.strftime("%d/%m"))
        # XP ganado ese dia (simulado: contar lecciones completadas x 10 XP)
        progreso_dia = ProgresoLeccion.objects.filter(
            usuario=usuario, completada=True, fecha_completada__date=dia
        ).count()
        dias_xp.append(progreso_dia * 10)

    # --- Grafico E: Barras apiladas evaluaciones por curso ---
    cursos_con_eval = []
    for curso in Curso.objects.filter(inscripciones__usuario=usuario).distinct()[:5]:
        intentos_curso = intentos.filter(evaluacion__curso=curso)
        cursos_con_eval.append({
            "titulo": curso.titulo[:30] + ("..." if len(curso.titulo) > 30 else ""),
            "aprobados": intentos_curso.filter(aprobado=True).count(),
            "reprobados": intentos_curso.filter(aprobado=False).count(),
        })

    eval_labels = [c["titulo"] for c in cursos_con_eval]
    eval_aprobados = [c["aprobados"] for c in cursos_con_eval]
    eval_reprobados = [c["reprobados"] for c in cursos_con_eval]

    # --- Proximos pasos ---
    proximos_pasos = []
    # 1. Curso mas cercano a completar
    casi_completos = Inscripcion.objects.filter(
        usuario=usuario, completado=False, progreso_pct__gte=70
    ).select_related("curso").order_by("-progreso_pct")[:1]
    for ins in casi_completos:
        proximos_pasos.append({
            "icono": "🎯",
            "texto": "Casi terminas: " + ins.curso.titulo[:50] + " (" + str(ins.progreso_pct) + "%)",
            "url": "/es/curso/" + str(ins.curso.id) + "/lecciones/",
        })
    # 2. Siguiente insignia
    insignias_pendientes = Insignia.objects.exclude(
        id__in=logros.values_list("insignia_id", flat=True)
    )[:1]
    for ins in insignias_pendientes:
        proximos_pasos.append({
            "icono": "🏅",
            "texto": "Siguiente insignia: " + ins.nombre,
            "url": "/es/estudiante/logros/",
        })
    # 3. Evaluaciones pendientes
    if evaluaciones_totales == 0:
        proximos_pasos.append({
            "icono": "🏆",
            "texto": "Aun no has hecho ninguna evaluacion. Empieza una!",
            "url": "/es/estudiante/evaluaciones/",
        })

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
        # Datos para graficos (JSON)
        "dona_data": json.dumps(dona_data),
        "dona_labels": json.dumps(dona_labels),
        "barras_labels": json.dumps(barras_labels),
        "barras_data": json.dumps(barras_data),
        "dias_labels": json.dumps(dias_labels),
        "dias_xp": json.dumps(dias_xp),
        "eval_labels": json.dumps(eval_labels),
        "eval_aprobados": json.dumps(eval_aprobados),
        "eval_reprobados": json.dumps(eval_reprobados),
        "proximos_pasos": proximos_pasos,
    })
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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from academia.models import Curso, Leccion, Inscripcion
from progreso.models import ProgresoLeccion
from ejercicios.models import Evaluacion, IntentoEvaluacion
from certificaciones.models import Certificado
from .models import AsignacionProfesor, AnuncioCurso, NotaProfesor


def es_profesor(user):
    """Verifica que el usuario es staff (profesor/admin)."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================
@login_required
@user_passes_test(es_profesor)
def dashboard(request):
    """Panel principal del profesor."""
    profesor = request.user

    # Cursos asignados
    asignaciones = AsignacionProfesor.objects.filter(
        profesor=profesor, activo=True
    ).select_related("curso")

    # Si es superuser, mostrar todos los cursos
    if profesor.is_superuser:
        cursos = Curso.objects.filter(activo=True)
    else:
        cursos = [a.curso for a in asignaciones]

    cursos_ids = [c.id for c in cursos]

    # Estadísticas globales
    total_cursos = len(cursos)
    total_estudiantes = Inscripcion.objects.filter(
        curso_id__in=cursos_ids
    ).values("usuario").distinct().count()
    total_inscripciones = Inscripcion.objects.filter(curso_id__in=cursos_ids).count()
    total_evaluaciones = Evaluacion.objects.filter(curso_id__in=cursos_ids).count()
    total_intentos = IntentoEvaluacion.objects.filter(
        evaluacion__curso_id__in=cursos_ids
    ).count()
    total_certificados = Certificado.objects.filter(curso_id__in=cursos_ids).count()

    # Actividad reciente
    actividad = IntentoEvaluacion.objects.filter(
        evaluacion__curso_id__in=cursos_ids
    ).select_related("usuario", "evaluacion").order_by("-fecha")[:10]

    # Top cursos por inscripciones
    cursos_top = []
    for curso in cursos:
        insc = Inscripcion.objects.filter(curso=curso).count()
        comp = Inscripcion.objects.filter(curso=curso, completado=True).count()
        cursos_top.append({
            "curso": curso,
            "inscripciones": insc,
            "completados": comp,
            "pct": int((comp / insc * 100)) if insc > 0 else 0,
        })
    cursos_top.sort(key=lambda x: -x["inscripciones"])
    cursos_top = cursos_top[:5]

    return render(request, "profesor/dashboard.html", {
        "total_cursos": total_cursos,
        "total_estudiantes": total_estudiantes,
        "total_inscripciones": total_inscripciones,
        "total_evaluaciones": total_evaluaciones,
        "total_intentos": total_intentos,
        "total_certificados": total_certificados,
        "actividad": actividad,
        "cursos_top": cursos_top,
    })


# ============================================================
# MIS CURSOS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def mis_cursos(request):
    """Lista de cursos que imparte el profesor."""
    profesor = request.user

    if profesor.is_superuser:
        cursos = Curso.objects.filter(activo=True).select_related("nivel")
    else:
        asignaciones = AsignacionProfesor.objects.filter(
            profesor=profesor, activo=True
        ).select_related("curso", "curso__nivel")
        cursos = [a.curso for a in asignaciones]

    cursos_data = []
    for curso in cursos:
        insc = Inscripcion.objects.filter(curso=curso).count()
        comp = Inscripcion.objects.filter(curso=curso, completado=True).count()
        lecciones = curso.lecciones.count()
        evs = Evaluacion.objects.filter(curso=curso).count()

        cursos_data.append({
            "curso": curso,
            "inscripciones": insc,
            "completados": comp,
            "pct_completado": int((comp / insc * 100)) if insc > 0 else 0,
            "lecciones": lecciones,
            "evaluaciones": evs,
        })

    return render(request, "profesor/mis_cursos.html", {"cursos": cursos_data})


# ============================================================
# DETALLE DE CURSO
# ============================================================
@login_required
@user_passes_test(es_profesor)
def curso_detalle(request, curso_id):
    """Detalle de un curso con estudiantes."""
    curso = get_object_or_404(Curso, id=curso_id)
    profesor = request.user

    # Verificar acceso
    if not profesor.is_superuser:
        if not AsignacionProfesor.objects.filter(profesor=profesor, curso=curso, activo=True).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    # Inscripciones
    inscripciones = Inscripcion.objects.filter(curso=curso).select_related("usuario")

    # Estudiantes con su progreso
    estudiantes = []
    for insc in inscripciones:
        intentos = IntentoEvaluacion.objects.filter(
            usuario=insc.usuario,
            evaluacion__curso=curso
        )
        mejor_nota = intentos.order_by("-nota").first()

        estudiantes.append({
            "usuario": insc.usuario,
            "progreso_pct": insc.progreso_pct,
            "completado": insc.completado,
            "intentos": intentos.count(),
            "mejor_nota": mejor_nota.nota if mejor_nota else None,
            "aprobado": intentos.filter(aprobado=True).exists(),
        })

    # Ordenar por progreso
    estudiantes.sort(key=lambda x: -x["progreso_pct"])

    # Evaluaciones del curso
    evaluaciones = Evaluacion.objects.filter(curso=curso)

    # Anuncios
    anuncios = AnuncioCurso.objects.filter(curso=curso, activo=True)

    return render(request, "profesor/curso_detalle.html", {
        "curso": curso,
        "estudiantes": estudiantes,
        "evaluaciones": evaluaciones,
        "anuncios": anuncios,
    })


# ============================================================
# ESTUDIANTES
# ============================================================
@login_required
@user_passes_test(es_profesor)
def estudiantes(request):
    """Lista de todos los estudiantes."""
    profesor = request.user

    if profesor.is_superuser:
        cursos_ids = list(Curso.objects.values_list("id", flat=True))
    else:
        cursos_ids = list(
            AsignacionProfesor.objects.filter(profesor=profesor, activo=True)
            .values_list("curso_id", flat=True)
        )

    # Estudiantes que han interactuado con cursos
    estudiantes_ids = Inscripcion.objects.filter(
        curso_id__in=cursos_ids
    ).values_list("usuario_id", flat=True).distinct()

    from django.contrib.auth import get_user_model
    User = get_user_model()
    estudiantes = User.objects.filter(id__in=estudiantes_ids).order_by("username")

    # Para cada estudiante, contar cursos
    data = []
    for est in estudiantes[:200]:  # limitar a 200
        insc = Inscripcion.objects.filter(usuario=est, curso_id__in=cursos_ids).count()
        comp = Inscripcion.objects.filter(usuario=est, curso_id__in=cursos_ids, completado=True).count()
        data.append({
            "usuario": est,
            "inscripciones": insc,
            "completados": comp,
        })

    return render(request, "profesor/estudiantes.html", {"estudiantes": data})


# ============================================================
# ESTADÍSTICAS / ANALÍTICAS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def analiticas(request):
    """Analíticas avanzadas."""
    profesor = request.user

    if profesor.is_superuser:
        cursos_ids = list(Curso.objects.values_list("id", flat=True))
    else:
        cursos_ids = list(
            AsignacionProfesor.objects.filter(profesor=profesor, activo=True)
            .values_list("curso_id", flat=True)
        )

    # Evaluaciones: promedio por curso
    cursos_stats = []
    for curso in Curso.objects.filter(id__in=cursos_ids):
        intentos = IntentoEvaluacion.objects.filter(evaluacion__curso=curso)
        avg = intentos.aggregate(promedio=Avg("nota"))["promedio"] or 0
        aprobados = intentos.filter(aprobado=True).count()
        total = intentos.count()

        cursos_stats.append({
            "curso": curso,
            "intentos": total,
            "promedio": round(avg, 1),
            "aprobados": aprobados,
            "pct_aprobados": int((aprobados / total * 100)) if total > 0 else 0,
        })

    cursos_stats.sort(key=lambda x: -x["intentos"])

    return render(request, "profesor/analiticas.html", {
        "cursos_stats": cursos_stats,
    })


# ============================================================
# ANUNCIOS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def crear_anuncio(request, curso_id):
    """Crear un anuncio en un curso."""
    curso = get_object_or_404(Curso, id=curso_id)
    profesor = request.user

    if request.method == "POST":
        titulo = request.POST.get("titulo", "").strip()
        contenido = request.POST.get("contenido", "").strip()

        if titulo and contenido:
            AnuncioCurso.objects.create(
                profesor=profesor,
                curso=curso,
                titulo=titulo,
                contenido=contenido,
            )
            return redirect("profesor:curso_detalle", curso_id=curso.id)

    return render(request, "profesor/crear_anuncio.html", {"curso": curso})


# ============================================================
# CERTIFICADOS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def certificados(request):
    """Certificados emitidos en los cursos del profesor."""
    profesor = request.user

    if profesor.is_superuser:
        cursos_ids = list(Curso.objects.values_list("id", flat=True))
    else:
        cursos_ids = list(
            AsignacionProfesor.objects.filter(profesor=profesor, activo=True)
            .values_list("curso_id", flat=True)
        )

    certs = Certificado.objects.filter(
        curso_id__in=cursos_ids
    ).select_related("usuario", "curso").order_by("-fecha_emision")

    return render(request, "profesor/certificados.html", {"certificados": certs})

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
from .forms import CursoForm, LeccionForm, EvaluacionForm, PreguntaEvaluacionForm, AnuncioForm


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


# ============================================================
# CRUD DE CURSOS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def curso_editar(request, curso_id):
    """Editar un curso existente."""
    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar permiso
    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        form = CursoForm(instance=curso)

    return render(request, "profesor/curso_form.html", {
        "form": form,
        "curso": curso,
        "titulo_pagina": "Editar curso",
        "accion": "Guardar cambios",
    })


@login_required
@user_passes_test(es_profesor)
def curso_toggle_activo(request, curso_id):
    """Activa o desactiva un curso."""
    curso = get_object_or_404(Curso, id=curso_id)

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return redirect("profesor:dashboard")

    if request.method == "POST":
        curso.activo = not curso.activo
        curso.save()
        return redirect("profesor:curso_detalle", curso_id=curso.id)

    return render(request, "profesor/curso_toggle_confirm.html", {"curso": curso})


# ============================================================
# CRUD DE LECCIONES
# ============================================================
@login_required
@user_passes_test(es_profesor)
def leccion_crear(request, curso_id):
    """Crear una nueva leccion."""
    curso = get_object_or_404(Curso, id=curso_id)

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = LeccionForm(request.POST)
        if form.is_valid():
            leccion = form.save(commit=False)
            leccion.curso = curso
            # Generar slug
            from django.utils.text import slugify
            base_slug = slugify(leccion.titulo)[:50]
            slug = base_slug
            n = 1
            while Leccion.objects.filter(curso=curso, slug=slug).exists():
                slug = (base_slug[:46] + "-" + str(n))[:50]
                n += 1
            leccion.slug = slug
            leccion.save()
            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        # Sugerir siguiente orden
        ultimo = Leccion.objects.filter(curso=curso).order_by("-orden").first()
        siguiente = (ultimo.orden + 1) if ultimo else 1
        form = LeccionForm(initial={"orden": siguiente})

    return render(request, "profesor/leccion_form.html", {
        "form": form,
        "curso": curso,
        "titulo_pagina": "Crear leccion",
        "accion": "Crear leccion",
    })


@login_required
@user_passes_test(es_profesor)
def leccion_editar(request, leccion_id):
    """Editar una leccion existente."""
    leccion = get_object_or_404(Leccion, id=leccion_id)
    curso = leccion.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = LeccionForm(request.POST, instance=leccion)
        if form.is_valid():
            form.save()
            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        form = LeccionForm(instance=leccion)

    return render(request, "profesor/leccion_form.html", {
        "form": form,
        "curso": curso,
        "leccion": leccion,
        "titulo_pagina": "Editar leccion",
        "accion": "Guardar cambios",
    })


@login_required
@user_passes_test(es_profesor)
def leccion_eliminar(request, leccion_id):
    """Eliminar una leccion."""
    leccion = get_object_or_404(Leccion, id=leccion_id)
    curso = leccion.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        leccion.delete()
        return redirect("profesor:curso_detalle", curso_id=curso.id)

    return render(request, "profesor/leccion_confirm_delete.html", {
        "leccion": leccion,
        "curso": curso,
    })


# ============================================================
# CRUD DE EVALUACIONES
# ============================================================
@login_required
@user_passes_test(es_profesor)
def evaluacion_crear(request, curso_id):
    """Crear una nueva evaluacion."""
    curso = get_object_or_404(Curso, id=curso_id)

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = EvaluacionForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.curso = curso
            ev.save()
            return redirect("profesor:evaluacion_detalle", evaluacion_id=ev.id)
    else:
        form = EvaluacionForm(initial={"num_preguntas": 10, "nota_minima": 60, "activo": True})

    return render(request, "profesor/evaluacion_form.html", {
        "form": form,
        "curso": curso,
        "titulo_pagina": "Crear evaluacion",
        "accion": "Crear evaluacion",
    })


@login_required
@user_passes_test(es_profesor)
def evaluacion_editar(request, evaluacion_id):
    """Editar una evaluacion."""
    ev = get_object_or_404(Evaluacion, id=evaluacion_id)
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = EvaluacionForm(request.POST, instance=ev)
        if form.is_valid():
            form.save()
            return redirect("profesor:evaluacion_detalle", evaluacion_id=ev.id)
    else:
        form = EvaluacionForm(instance=ev)

    return render(request, "profesor/evaluacion_form.html", {
        "form": form,
        "curso": curso,
        "evaluacion": ev,
        "titulo_pagina": "Editar evaluacion",
        "accion": "Guardar cambios",
    })


@login_required
@user_passes_test(es_profesor)
def evaluacion_eliminar(request, evaluacion_id):
    """Eliminar una evaluacion."""
    ev = get_object_or_404(Evaluacion, id=evaluacion_id)
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        ev.delete()
        return redirect("profesor:curso_detalle", curso_id=curso.id)

    return render(request, "profesor/evaluacion_confirm_delete.html", {
        "evaluacion": ev,
        "curso": curso,
    })


@login_required
@user_passes_test(es_profesor)
def evaluacion_detalle(request, evaluacion_id):
    """Ver detalle de una evaluacion y sus preguntas."""
    ev = get_object_or_404(Evaluacion, id=evaluacion_id)
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    preguntas = ev.preguntas.order_by("orden")
    intentos = ev.intentos.select_related("usuario").order_by("-fecha")[:50]

    return render(request, "profesor/evaluacion_detalle.html", {
        "evaluacion": ev,
        "curso": curso,
        "preguntas": preguntas,
        "intentos": intentos,
    })


# ============================================================
# CRUD DE PREGUNTAS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def pregunta_crear(request, evaluacion_id):
    """Crear una pregunta en una evaluacion."""
    ev = get_object_or_404(Evaluacion, id=evaluacion_id)
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = PreguntaEvaluacionForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.evaluacion = ev
            pregunta.opciones = form.cleaned_data["opciones_texto"]
            pregunta.save()
            return redirect("profesor:evaluacion_detalle", evaluacion_id=ev.id)
    else:
        ultimo = ev.preguntas.order_by("-orden").first()
        siguiente = (ultimo.orden + 1) if ultimo else 1
        form = PreguntaEvaluacionForm(initial={"orden": siguiente})

    return render(request, "profesor/pregunta_form.html", {
        "form": form,
        "evaluacion": ev,
        "curso": curso,
        "titulo_pagina": "Crear pregunta",
        "accion": "Crear pregunta",
    })


@login_required
@user_passes_test(es_profesor)
def pregunta_editar(request, pregunta_id):
    """Editar una pregunta."""
    pregunta = get_object_or_404(PreguntaEvaluacion, id=pregunta_id)
    ev = pregunta.evaluacion
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = PreguntaEvaluacionForm(request.POST, instance=pregunta)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.opciones = form.cleaned_data["opciones_texto"]
            pregunta.save()
            return redirect("profesor:evaluacion_detalle", evaluacion_id=ev.id)
    else:
        form = PreguntaEvaluacionForm(instance=pregunta)

    return render(request, "profesor/pregunta_form.html", {
        "form": form,
        "evaluacion": ev,
        "curso": curso,
        "pregunta": pregunta,
        "titulo_pagina": "Editar pregunta",
        "accion": "Guardar cambios",
    })


@login_required
@user_passes_test(es_profesor)
def pregunta_eliminar(request, pregunta_id):
    """Eliminar una pregunta."""
    pregunta = get_object_or_404(PreguntaEvaluacion, id=pregunta_id)
    ev = pregunta.evaluacion
    curso = ev.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        pregunta.delete()
        return redirect("profesor:evaluacion_detalle", evaluacion_id=ev.id)

    return render(request, "profesor/pregunta_confirm_delete.html", {
        "pregunta": pregunta,
        "evaluacion": ev,
        "curso": curso,
    })


# ============================================================
# CRUD DE ANUNCIOS
# ============================================================
@login_required
@user_passes_test(es_profesor)
def anuncio_crear(request, curso_id):
    """Crear un anuncio."""
    curso = get_object_or_404(Curso, id=curso_id)

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = AnuncioForm(request.POST)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.profesor = request.user
            anuncio.curso = curso
            anuncio.save()
            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        form = AnuncioForm(initial={"activo": True})

    return render(request, "profesor/anuncio_form.html", {
        "form": form,
        "curso": curso,
        "titulo_pagina": "Crear anuncio",
        "accion": "Publicar anuncio",
    })


@login_required
@user_passes_test(es_profesor)
def anuncio_editar(request, anuncio_id):
    """Editar un anuncio."""
    anuncio = get_object_or_404(AnuncioCurso, id=anuncio_id)
    curso = anuncio.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = AnuncioForm(request.POST, instance=anuncio)
        if form.is_valid():
            form.save()
            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        form = AnuncioForm(instance=anuncio)

    return render(request, "profesor/anuncio_form.html", {
        "form": form,
        "curso": curso,
        "anuncio": anuncio,
        "titulo_pagina": "Editar anuncio",
        "accion": "Guardar cambios",
    })


@login_required
@user_passes_test(es_profesor)
def anuncio_eliminar(request, anuncio_id):
    """Eliminar un anuncio."""
    anuncio = get_object_or_404(AnuncioCurso, id=anuncio_id)
    curso = anuncio.curso

    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        anuncio.delete()
        return redirect("profesor:curso_detalle", curso_id=curso.id)

    return render(request, "profesor/anuncio_confirm_delete.html", {
        "anuncio": anuncio,
        "curso": curso,
    })

@login_required
@user_passes_test(es_profesor)
def curso_crear(request):
    """Crear un nuevo curso."""
    if request.method == "POST":
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save(commit=False)
            # Generar slug unico
            from django.utils.text import slugify
            base_slug = slugify(curso.titulo)[:50] or "curso"
            slug = base_slug
            n = 1
            while Curso.objects.filter(slug=slug).exists():
                slug = (base_slug[:46] + "-" + str(n))[:50]
                n += 1
            curso.slug = slug
            curso.save()

            # Asignar el curso al profesor actual
            AsignacionProfesor.objects.get_or_create(
                profesor=request.user,
                curso=curso,
                defaults={"activo": True},
            )

            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        form = CursoForm(initial={"activo": True})

    return render(request, "profesor/curso_form.html", {
        "form": form,
        "titulo_pagina": "Crear curso",
        "accion": "Crear curso",
        "es_nuevo": True,
    })

# ============================================================
# ANALITICAS (version mejorada con datos para graficas)
# ============================================================
@login_required
@user_passes_test(es_profesor)
def analiticas(request):
    """Analiticas avanzadas con datos para graficas."""
    profesor = request.user

    # Cursos del profesor
    if profesor.is_superuser:
        cursos_ids = list(Curso.objects.values_list("id", flat=True))
    else:
        cursos_ids = list(
            AsignacionProfesor.objects.filter(profesor=profesor, activo=True)
            .values_list("curso_id", flat=True)
        )

    # ============ KPIs GLOBALES ============
    todos_intentos = IntentoEvaluacion.objects.filter(evaluacion__curso_id__in=cursos_ids)
    total_intentos = todos_intentos.count()
    total_aprobados = todos_intentos.filter(aprobado=True).count()
    promedio_global = todos_intentos.aggregate(p=Avg("nota"))["p"] or 0
    pct_aprobados_global = int((total_aprobados / total_intentos * 100)) if total_intentos > 0 else 0

    # ============ STATS POR CURSO ============
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
            "reprobados": total - aprobados,
            "pct_aprobados": int((aprobados / total * 100)) if total > 0 else 0,
        })

    cursos_stats.sort(key=lambda x: -x["intentos"])

    # ============ DATOS PARA GRAFICAS ============
    # 1. Top 10 cursos con mas intentos
    top_cursos = cursos_stats[:10]
    chart_labels = [c["curso"].titulo[:30] + ("..." if len(c["curso"].titulo) > 30 else "") for c in top_cursos]
    chart_promedios = [c["promedio"] for c in top_cursos]
    chart_aprobados = [c["aprobados"] for c in top_cursos]
    chart_reprobados = [c["reprobados"] for c in top_cursos]
    chart_intentos = [c["intentos"] for c in top_cursos]

    # 2. Datos para dona global
    chart_global = {
        "aprobados": total_aprobados,
        "reprobados": total_intentos - total_aprobados,
    }

    # 3. Evolucion temporal (ultimos 30 dias)
    from datetime import timedelta
    from django.utils import timezone
    hoy = timezone.now().date()
    hace_30 = hoy - timedelta(days=29)
    dias_labels = []
    dias_intentos = []
    dias_aprobados = []
    for i in range(30):
        dia = hace_30 + timedelta(days=i)
        dias_labels.append(dia.strftime("%d/%m"))
        intentos_dia = todos_intentos.filter(fecha__date=dia)
        dias_intentos.append(intentos_dia.count())
        dias_aprobados.append(intentos_dia.filter(aprobado=True).count())

    # ============ CONTEXTO ============
    return render(request, "profesor/analiticas.html", {
        "cursos_stats": cursos_stats,
        # KPIs
        "total_intentos": total_intentos,
        "total_aprobados": total_aprobados,
        "promedio_global": round(promedio_global, 1),
        "pct_aprobados_global": pct_aprobados_global,
        # Datos para graficas (serializados a JSON en el template)
        "chart_labels": chart_labels,
        "chart_promedios": chart_promedios,
        "chart_aprobados": chart_aprobados,
        "chart_reprobados": chart_reprobados,
        "chart_intentos": chart_intentos,
        "chart_global_aprobados": chart_global["aprobados"],
        "chart_global_reprobados": chart_global["reprobados"],
        "dias_labels": dias_labels,
        "dias_intentos": dias_intentos,
        "dias_aprobados": dias_aprobados,
    })

# ============================================================
# CRUD DE MODULOS (crea N lecciones de golpe)
# ============================================================
@login_required
@user_passes_test(es_profesor)
def modulo_crear(request, curso_id):
    """Crear un modulo con N lecciones de golpe."""
    from academia.models import Modulo
    from .forms import ModuloForm

    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar permiso
    if not request.user.is_superuser:
        if not AsignacionProfesor.objects.filter(
            profesor=request.user, curso=curso, activo=True
        ).exists():
            return render(request, "profesor/sin_acceso.html", {"curso": curso})

    if request.method == "POST":
        form = ModuloForm(request.POST)
        if form.is_valid():
            titulo = form.cleaned_data["titulo"]
            descripcion = form.cleaned_data["descripcion"]
            orden = form.cleaned_data["orden"] or 1
            titulos = form.cleaned_data["titulos_lecciones"]
            contenido_base = form.cleaned_data["contenido_base"]

            # Crear el modulo
            modulo = Modulo.objects.create(
                curso=curso,
                titulo=titulo,
                descripcion=descripcion,
                orden=orden,
                activo=True,
            )

            # Determinar el siguiente orden de leccion
            ultimo = Leccion.objects.filter(curso=curso).order_by("-orden").first()
            orden_leccion = (ultimo.orden + 1) if ultimo else 1

            # Crear las lecciones
            from django.utils.text import slugify
            creadas = 0
            for titulo_lec in titulos:
                # Generar slug unico
                base_slug = slugify(titulo_lec)[:50] or "leccion"
                slug = base_slug
                n = 1
                while Leccion.objects.filter(curso=curso, slug=slug).exists():
                    slug = (base_slug[:46] + "-" + str(n))[:50]
                    n += 1

                Leccion.objects.create(
                    curso=curso,
                    modulo=modulo,
                    titulo=titulo_lec,
                    slug=slug,
                    orden=orden_leccion,
                    contenido=contenido_base,
                    activa=True,
                )
                orden_leccion += 1
                creadas += 1

            return redirect("profesor:curso_detalle", curso_id=curso.id)
    else:
        # Sugerir siguiente orden
        from academia.models import Modulo
        ultimo = Modulo.objects.filter(curso=curso).order_by("-orden").first()
        siguiente = (ultimo.orden + 1) if ultimo else 1
        form = ModuloForm(initial={"orden": siguiente})

    return render(request, "profesor/modulo_form.html", {
        "form": form,
        "curso": curso,
        "titulo_pagina": "Crear modulo",
        "accion": "Crear modulo y lecciones",
    })

# ============================================================
# SUBIR IMAGEN (para TinyMCE)
# ============================================================
import uuid
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
@user_passes_test(es_profesor)
@require_POST
def subir_imagen(request):
    """Endpoint para subir imágenes desde TinyMCE."""
    archivo = request.FILES.get("file")
    if not archivo:
        return JsonResponse({"error": "No se recibió archivo"}, status=400)

    # Validar tipo
    tipos_ok = ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"]
    if archivo.content_type not in tipos_ok:
        return JsonResponse(
            {"error": "Tipo de archivo no permitido. Solo JPG, PNG, GIF, WEBP, SVG."},
            status=400,
        )

    # Validar tamaño (5 MB)
    if archivo.size > 5 * 1024 * 1024:
        return JsonResponse({"error": "El archivo excede 5 MB."}, status=400)

    # Generar nombre único
    ext = os.path.splitext(archivo.name)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        ext = ".jpg"
    nombre = f"{uuid.uuid4().hex}{ext}"
    ruta = f"lecciones/{nombre}"

    # Guardar
    ruta_guardada = default_storage.save(ruta, ContentFile(archivo.read()))
    url = default_storage.url(ruta_guardada)

    # TinyMCE espera {"location": "URL"}
    return JsonResponse({"location": url})

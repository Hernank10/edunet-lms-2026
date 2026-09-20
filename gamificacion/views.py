from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from academia.models import Curso, Leccion, Inscripcion
from progreso.models import ProgresoLeccion
from certificaciones.models import Certificado
from .models import Insignia, Logro, PerfilGamificacion


def _get_perfil(user):
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=user)
    return perfil


@login_required
def dashboard_estudiante(request):
    usuario = request.user
    perfil = _get_perfil(usuario)
    inscripciones = Inscripcion.objects.filter(usuario=usuario, activa=True).select_related("curso")[:6]
    total_inscripciones = Inscripcion.objects.filter(usuario=usuario).count()
    completadas = Inscripcion.objects.filter(usuario=usuario, completado=True).count()
    certs = Certificado.objects.filter(usuario=usuario).count()
    logros = Logro.objects.filter(usuario=usuario).select_related("insignia")
    todas = Insignia.objects.all()
    ganadas_ids = set(logros.values_list("insignia_id", flat=True))
    ganadas = [i for i in todas if i.id in ganadas_ids]
    bloqueadas = [i for i in todas if i.id not in ganadas_ids]
    return render(request, "gamificacion/dashboard.html", {
        "perfil": perfil, "inscripciones": inscripciones,
        "total_inscripciones": total_inscripciones,
        "completadas": completadas, "certs": certs,
        "insignias_ganadas": ganadas,
        "insignias_bloqueadas": bloqueadas[:6],
        "objetivos": bloqueadas[:3],
    })


@login_required
def mis_cursos(request):
    inscripciones = Inscripcion.objects.filter(usuario=request.user).select_related("curso", "curso__nivel").order_by("-fecha")
    return render(request, "gamificacion/mis_cursos.html", {"inscripciones": inscripciones})


@login_required
def practicas(request):
    pendientes = []
    for insc in Inscripcion.objects.filter(usuario=request.user, activa=True, completado=False):
        for lec in insc.curso.lecciones.all()[:5]:
            if not ProgresoLeccion.objects.filter(usuario=request.user, leccion=lec, completada=True).exists():
                pendientes.append({"leccion": lec, "curso": insc.curso})
                break
    return render(request, "gamificacion/practicas.html", {"pendientes": pendientes[:20]})


@login_required
def evaluaciones(request):
    from ejercicios.models import Evaluacion, IntentoEvaluacion
    evaluaciones = Evaluacion.objects.filter(curso__inscripciones__usuario=request.user).distinct()
    data = []
    for ev in evaluaciones:
        intentos = IntentoEvaluacion.objects.filter(usuario=request.user, evaluacion=ev)
        mejor = intentos.order_by("-nota").first()
        data.append({"evaluacion": ev, "intentos": intentos.count(), "mejor_nota": mejor.nota if mejor else None, "aprobado": intentos.filter(aprobado=True).exists()})
    return render(request, "gamificacion/evaluaciones.html", {"evaluaciones": data})


@login_required
def mis_logros(request):
    perfil = _get_perfil(request.user)
    todas = Insignia.objects.all()
    ganadas_ids = set(Logro.objects.filter(usuario=request.user).values_list("insignia_id", flat=True))
    ganadas = [i for i in todas if i.id in ganadas_ids]
    bloqueadas = [i for i in todas if i.id not in ganadas_ids]
    return render(request, "gamificacion/mis_logros.html", {"perfil": perfil, "ganadas": ganadas, "bloqueadas": bloqueadas})


@login_required
def estadisticas(request):
    perfil = _get_perfil(request.user)
    return render(request, "gamificacion/estadisticas.html", {"perfil": perfil})

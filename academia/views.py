from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Curso, Leccion
from progreso.models import ProgresoLeccion
from progreso.utils import leccion_disponible


def dashboard(request):
    """Lista de cursos disponibles."""
    cursos = Curso.objects.select_related("nivel").filter(activo=True)
    return render(request, "academia/dashboard.html", {
        "cursos": cursos
    })


@login_required
def course_lessons(request, curso_id):
    """Muestra las lecciones de un curso con su estado."""
    curso = get_object_or_404(Curso, id=curso_id)
    lecciones = Leccion.objects.filter(curso=curso).order_by("orden")

    progreso_usuario = {
        p.leccion_id: p.completada
        for p in ProgresoLeccion.objects.filter(
            usuario=request.user,
            leccion__curso=curso
        )
    }

    lecciones_con_estado = []
    desbloqueada = True

    for leccion in lecciones:
        completada = progreso_usuario.get(leccion.id, False)
        lecciones_con_estado.append({
            "leccion": leccion,
            "completada": completada,
            "desbloqueada": desbloqueada
        })
        if not completada:
            desbloqueada = False

    return render(
        request,
        "academia/course_lessons.html",
        {
            "curso": curso,
            "lecciones": lecciones_con_estado
        }
    )


@login_required
def lesson_detail(request, pk):
    """Detalle de una lección concreta."""
    leccion = get_object_or_404(Leccion, pk=pk)

    if not leccion_disponible(request.user, leccion):
        return HttpResponseForbidden(
            "Esta lección está bloqueada. Completa la anterior."
        )

    if request.method == "POST":
        progreso, _ = ProgresoLeccion.objects.get_or_create(
            usuario=request.user,
            leccion=leccion
        )
        progreso.completada = True
        progreso.save()
        return redirect("academia:course_lessons", curso_id=leccion.curso.id)

    return render(request, "academia/lesson_detail.html", {
        "leccion": leccion
    })
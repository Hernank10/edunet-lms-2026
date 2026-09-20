from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
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
    """Detalle de una lección + marcar como completada."""
    leccion = get_object_or_404(Leccion, pk=pk)

    if request.method == "POST" and request.user.is_authenticated:
        progreso, _ = ProgresoLeccion.objects.get_or_create(
            usuario=request.user,
            leccion=leccion
        )
        progreso.completada = True
        progreso.save()

        # Dar XP si es la primera vez
        from gamificacion.models import PerfilGamificacion
        perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=request.user)
        perfil.add_xp(10)

        return redirect("academia:course_lessons", curso_id=leccion.curso.id)

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

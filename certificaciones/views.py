from django.shortcuts import render, get_object_or_404
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

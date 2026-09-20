from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Recurso, Tecnica, HtmlInteractivo


# ==================================================
# HUB PRINCIPAL
# ==================================================
def hub(request):
    """Página principal de contenido: recursos + HTMLs."""
    total_recursos = Recurso.objects.count()
    total_tecnicas = Tecnica.objects.count()
    total_htmls = HtmlInteractivo.objects.count()

    # Categorías con contadores
    categorias = []
    for codigo, nombre in Recurso.CATEGORIAS:
        n_rec = Recurso.objects.filter(categoria=codigo).count()
        n_htm = HtmlInteractivo.objects.filter(categoria=codigo).count()
        if n_rec + n_htm > 0:
            categorias.append({
                "codigo": codigo,
                "nombre": nombre,
                "recursos": n_rec,
                "htmls": n_htm,
                "total": n_rec + n_htm,
            })
    categorias.sort(key=lambda x: -x["total"])

    return render(request, "contenido/hub.html", {
        "total_recursos": total_recursos,
        "total_tecnicas": total_tecnicas,
        "total_htmls": total_htmls,
        "categorias": categorias,
    })


# ==================================================
# RECURSOS (JSON)
# ==================================================
def lista_recursos(request):
    """Lista de recursos filtrable."""
    qs = Recurso.objects.all()

    cat = request.GET.get("categoria")
    nivel = request.GET.get("nivel")
    busqueda = request.GET.get("q")

    if cat:
        qs = qs.filter(categoria=cat)
    if nivel:
        qs = qs.filter(nivel=nivel)
    if busqueda:
        qs = qs.filter(Q(titulo__icontains=busqueda) | Q(subtitulo__icontains=busqueda))

    paginator = Paginator(qs, 24)
    page = paginator.get_page(request.GET.get("page"))

    # Categorías con contadores
    categorias = []
    for codigo, nombre in Recurso.CATEGORIAS:
        n = Recurso.objects.filter(categoria=codigo).count()
        if n > 0:
            categorias.append({"codigo": codigo, "nombre": nombre, "n": n})

    return render(request, "contenido/lista_recursos.html", {
        "page": page,
        "categorias": categorias,
        "categoria_actual": cat,
        "nivel_actual": nivel,
        "busqueda": busqueda or "",
    })


def detalle_recurso(request, pk):
    """Detalle de un recurso con sus técnicas."""
    recurso = get_object_or_404(Recurso, pk=pk)
    tecnicas = recurso.tecnicas.all()
    return render(request, "contenido/detalle_recurso.html", {
        "recurso": recurso,
        "tecnicas": tecnicas,
    })


def tecnica_detalle(request, pk):
    """Vista individual de una técnica (flashcard)."""
    tecnica = get_object_or_404(Tecnica, pk=pk)
    # Siguiente y anterior
    siguiente = Tecnica.objects.filter(
        recurso=tecnica.recurso, numero__gt=tecnica.numero
    ).order_by("numero").first()
    anterior = Tecnica.objects.filter(
        recurso=tecnica.recurso, numero__lt=tecnica.numero
    ).order_by("-numero").first()

    return render(request, "contenido/tecnica.html", {
        "tecnica": tecnica,
        "siguiente": siguiente,
        "anterior": anterior,
    })


# ==================================================
# HTMLs INTERACTIVOS
# ==================================================
def lista_htmls(request):
    """Lista de HTMLs filtrable."""
    qs = HtmlInteractivo.objects.all()

    cat = request.GET.get("categoria")
    tipo = request.GET.get("tipo")
    busqueda = request.GET.get("q")

    if cat:
        qs = qs.filter(categoria=cat)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if busqueda:
        qs = qs.filter(titulo__icontains=busqueda)

    paginator = Paginator(qs, 24)
    page = paginator.get_page(request.GET.get("page"))

    # Categorías con contadores
    categorias = []
    for codigo, nombre in HtmlInteractivo.CATEGORIAS:
        n = HtmlInteractivo.objects.filter(categoria=codigo).count()
        if n > 0:
            categorias.append({"codigo": codigo, "nombre": nombre, "n": n})

    # Tipos con contadores
    tipos = []
    for codigo, nombre in HtmlInteractivo.TIPOS:
        n = HtmlInteractivo.objects.filter(tipo=codigo).count()
        if n > 0:
            tipos.append({"codigo": codigo, "nombre": nombre, "n": n})

    return render(request, "contenido/lista_htmls.html", {
        "page": page,
        "categorias": categorias,
        "tipos": tipos,
        "categoria_actual": cat,
        "tipo_actual": tipo,
        "busqueda": busqueda or "",
    })


def visor_html(request, slug):
    """Visor de un HTML con iframe."""
    obj = get_object_or_404(HtmlInteractivo, slug=slug)
    return render(request, "contenido/visor_html.html", {
        "obj": obj,
    })

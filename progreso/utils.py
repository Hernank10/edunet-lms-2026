from .models import ProgresoLeccion
from academia.models import Leccion


def leccion_disponible(usuario, leccion):
    """
    Devuelve True si el usuario puede acceder a la lección
    """

    # Primera lección del curso
    if leccion.orden == 1:
        return True

    leccion_anterior = Leccion.objects.filter(
        curso=leccion.curso,
        orden=leccion.orden - 1
    ).first()

    if not leccion_anterior:
        return True

    return ProgresoLeccion.objects.filter(
        usuario=usuario,
        leccion=leccion_anterior,
        completada=True
    ).exists()


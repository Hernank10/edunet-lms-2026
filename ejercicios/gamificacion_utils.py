"""
gamificacion_utils.py
Funciones para integrar evaluaciones con gamificación.
"""
from django.db.models import Sum
from .models import Evaluacion, IntentoEvaluacion
from gamificacion.models import Insignia, Logro, PerfilGamificacion


XP_POR_APROBAR = 50
XP_POR_PREGUNTA_CORRECTA = 5


def procesar_intento(usuario, evaluacion, respuestas):
    """
    Procesa un intento de evaluación.

    - respuestas: dict {orden: opcion_elegida}
    - Devuelve: dict con nota, aprobado, xp_ganado, insignias_nuevas
    """
    preguntas = evaluacion.preguntas.all()
    total = preguntas.count()
    correctas = 0

    for p in preguntas:
        if respuestas.get(str(p.orden)) == p.respuesta_correcta:
            correctas += 1

    nota = int((correctas / total) * 100) if total > 0 else 0
    aprobado = nota >= evaluacion.nota_minima

    # XP
    xp_ganado = 0
    if aprobado:
        xp_ganado = XP_POR_APROBAR + correctas * XP_POR_PREGUNTA_CORRECTA

    # Guardar intento
    intento = IntentoEvaluacion.objects.create(
        usuario=usuario,
        evaluacion=evaluacion,
        nota=nota,
        aprobado=aprobado,
    )

    # Actualizar perfil de gamificación
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=usuario)
    if xp_ganado > 0:
        perfil.add_xp(xp_ganado)

    # Verificar insignias
    insignias_nuevas = verificar_insignias(usuario)

    return {
        "intento": intento,
        "nota": nota,
        "aprobado": aprobado,
        "correctas": correctas,
        "total": total,
        "xp_ganado": xp_ganado,
        "insignias_nuevas": insignias_nuevas,
    }


def verificar_insignias(usuario):
    """
    Revisa si el usuario merece nuevas insignias y las otorga.
    Devuelve la lista de insignias nuevas.
    """
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=usuario)
    aprobadas = IntentoEvaluacion.objects.filter(usuario=usuario, aprobado=True).count()
    cursos_comp = perfil.cursos_completados

    insignias_nuevas = []

    for ins in Insignia.objects.all():
        # ¿Ya la tiene?
        if Logro.objects.filter(usuario=usuario, insignia=ins).exists():
            continue

        cumple = False

        # Por XP
        if ins.requisito_xp > 0 and perfil.xp_total >= ins.requisito_xp:
            cumple = True

        # Por evaluaciones aprobadas (usamos requisito_lecciones como proxy)
        if "Evaluación" in ins.nombre or "Quiz" in ins.nombre:
            if "Primera" in ins.nombre and aprobadas >= 1:
                cumple = True
            elif "Constante" in ins.nombre and aprobadas >= 5:
                cumple = True
            elif "Rey" in ins.nombre and aprobadas >= 20:
                cumple = True

        # Por cursos
        if ins.requisito_cursos > 0 and cursos_comp >= ins.requisito_cursos:
            cumple = True

        if cumple:
            Logro.objects.create(usuario=usuario, insignia=ins)
            insignias_nuevas.append(ins)

    return insignias_nuevas

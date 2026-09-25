# -*- coding: utf-8 -*-
"""
POBLAR_EVALUACIONES.py
Añade 10 preguntas a cada evaluación que no las tenga.
"""
import os
import sys
import random
import django

BASE = r"E:\02_proyectos\edunet_academia"
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academia.models import Curso
from ejercicios.models import Evaluacion, PreguntaEvaluacion


def generar_preguntas(titulo_curso, titulo_ev):
    """Genera 10 preguntas para una evaluación."""
    preguntas = [
        {
            "enunciado": f"¿Cuál es el objetivo principal del curso '{titulo_curso}'?",
            "opciones": [
                "Comprender y aplicar los conceptos fundamentales",
                "Memorizar datos sin contexto",
                "Aprender solo teoría",
                "Ninguna de las anteriores",
            ],
            "correcta": "Comprender y aplicar los conceptos fundamentales",
            "explicacion": "El curso busca comprensión y aplicación práctica.",
        },
        {
            "enunciado": f"¿Cuál de estas NO es una característica del curso?",
            "opciones": [
                "Contenido práctico",
                "Ejemplos reales",
                "Solo teoría sin práctica",
                "Ejercicios interactivos",
            ],
            "correcta": "Solo teoría sin práctica",
            "explicacion": "El curso incluye práctica y ejercicios.",
        },
        {
            "enunciado": "¿Qué tipo de evaluación es esta?",
            "opciones": [
                "Evaluación final del curso",
                "Evaluación diagnóstica",
                "Evaluación formativa",
                "Evaluación informal",
            ],
            "correcta": "Evaluación final del curso",
            "explicacion": "Es la evaluación final que certifica el curso.",
        },
        {
            "enunciado": "¿Cuál es la nota mínima para aprobar?",
            "opciones": ["70%", "50%", "60%", "80%"],
            "correcta": "70%",
            "explicacion": "La nota mínima es 70%.",
        },
        {
            "enunciado": "¿Qué obtienes al aprobar la evaluación?",
            "opciones": [
                "Un certificado de finalización",
                "Solo un comentario",
                "Nada",
                "Puntos de experiencia",
            ],
            "correcta": "Un certificado de finalización",
            "explicacion": "Al aprobar se emite un certificado.",
        },
        {
            "enunciado": "¿Cuál es el mejor enfoque para estudiar este curso?",
            "opciones": [
                "Estudiar regularmente y practicar",
                "Solo leer una vez",
                "Estudiar la noche anterior",
                "No estudiar",
            ],
            "correcta": "Estudiar regularmente y practicar",
            "explicacion": "La constancia es clave para aprender.",
        },
        {
            "enunciado": "¿Qué son las 'lecciones' en este curso?",
            "opciones": [
                "Unidades didácticas del curso",
                "Errores comunes",
                "Ejemplos avanzados",
                "Ninguna de las anteriores",
            ],
            "correcta": "Unidades didácticas del curso",
            "explicacion": "Las lecciones son unidades del curso.",
        },
        {
            "enunciado": "¿Cuántos intentos tienes para aprobar?",
            "opciones": [
                "Múltiples intentos",
                "Solo uno",
                "Dos intentos",
                "Ninguno",
            ],
            "correcta": "Múltiples intentos",
            "explicacion": "Puedes intentar la evaluación varias veces.",
        },
        {
            "enunciado": "¿Qué es el XP en el sistema?",
            "opciones": [
                "Puntos de experiencia",
                "Nota de evaluación",
                "Tiempo de estudio",
                "Certificado",
            ],
            "correcta": "Puntos de experiencia",
            "explicacion": "XP = Experience Points.",
        },
        {
            "enunciado": "¿Cuál es el beneficio principal de completar el curso?",
            "opciones": [
                "Dominar los conceptos y obtener certificado",
                "Solo obtener puntos",
                "Ninguno",
                "Solo por diversión",
            ],
            "correcta": "Dominar los conceptos y obtener certificado",
            "explicacion": "El objetivo es aprender y certificarse.",
        },
    ]
    return preguntas


# ============================================================
# POBLAR EVALUACIONES
# ============================================================
print("=" * 60)
print("  POBLANDO EVALUACIONES")
print("=" * 60)
print()

evaluaciones_procesadas = 0
preguntas_creadas = 0

for ev in Evaluacion.objects.all():
    if ev.preguntas.count() >= 5:
        continue

    curso_titulo = ev.curso.titulo

    # Eliminar preguntas viejas (basura)
    ev.preguntas.all().delete()

    # Crear 10 preguntas
    preguntas = generar_preguntas(curso_titulo, ev.titulo)
    random.shuffle(preguntas)

    for i, p in enumerate(preguntas, 1):
        PreguntaEvaluacion.objects.create(
            evaluacion=ev,
            orden=i,
            enunciado=p["enunciado"],
            opciones=p["opciones"],
            respuesta_correcta=p["correcta"],
            explicacion=p["explicacion"],
        )
        preguntas_creadas += 1

    ev.num_preguntas = 10
    ev.save()
    evaluaciones_procesadas += 1

print(f"[OK] Evaluaciones procesadas: {evaluaciones_procesadas}")
print(f"[OK] Preguntas creadas:       {preguntas_creadas}")
print(f"[OK] Total en BD:             {PreguntaEvaluacion.objects.count()}")
print()
print("=== LISTO ===")
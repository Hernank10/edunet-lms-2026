# -*- coding: utf-8 -*-
"""
POBLAR_EJERCICIOS.py
Añade 3-5 ejercicios por lección.
"""
import os
import sys
import random
import django

BASE = r"E:\02_proyectos\edunet_academia"
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from academia.models import Curso, Leccion
from ejercicios.models import Ejercicio


# Plantillas de ejercicios
def generar_ejercicios(titulo, tema):
    """Genera 4 ejercicios variados para una lección."""
    return [
        {
            "tipo": "opcion_multiple",
            "enunciado": f"¿Cuál de las siguientes opciones describe mejor '{tema}'?",
            "datos": {
                "opciones": [
                    f"Es un concepto fundamental de {tema}",
                    f"Es una técnica avanzada de {tema}",
                    f"Es un error común en {tema}",
                    f"Ninguna de las anteriores",
                ],
                "correcta": 0,
                "explicacion": f"'{tema}' es un concepto fundamental que veremos en esta lección.",
            },
        },
        {
            "tipo": "vf",
            "enunciado": f"Verdadero o Falso: '{tema}' se aplica solo en contextos académicos.",
            "datos": {
                "respuesta": False,
                "explicacion": f"'{tema}' se aplica en contextos académicos, profesionales y personales.",
            },
        },
        {
            "tipo": "completar",
            "enunciado": f"Completa: '{tema}' es esencial para dominar el castellano en el nivel _______.",
            "datos": {
                "respuesta": "correspondiente",
                "explicacion": f"El dominio de '{tema}' depende del nivel educativo.",
            },
        },
        {
            "tipo": "ordenar",
            "enunciado": f"Ordena los pasos para aplicar '{tema}':",
            "datos": {
                "pasos": [
                    "Identificar el contexto",
                    "Seleccionar la técnica adecuada",
                    "Aplicar el concepto",
                    "Revisar el resultado",
                ],
                "explicacion": f"Aplicar '{tema}' requiere estos 4 pasos.",
            },
        },
    ]


# ============================================================
# POBLAR EJERCICIOS
# ============================================================
print("=" * 60)
print("  POBLANDO EJERCICIOS")
print("=" * 60)
print()

creados = 0
lecciones_procesadas = 0

for curso in Curso.objects.filter(activo=True):
    for leccion in curso.lecciones.all():
        # Saltar si ya tiene ejercicios
        if leccion.ejercicios.exists():
            continue

        # Extraer tema
        tema = leccion.titulo.split(":")[-1].strip()
        if " - Parte" in tema:
            tema = tema.split(" - Parte")[0].strip()

        # Crear 4 ejercicios
        for i, ej_data in enumerate(generar_ejercicios(leccion.titulo, tema), 1):
            Ejercicio.objects.create(
                leccion=leccion,
                tipo=ej_data["tipo"],
                enunciado=ej_data["enunciado"],
                datos=ej_data["datos"],
                activo=True,
                orden=i,
            )
            creados += 1

        lecciones_procesadas += 1

print(f"[OK] Lecciones procesadas: {lecciones_procesadas}")
print(f"[OK] Ejercicios creados:   {creados}")
print(f"[OK] Total en BD:          {Ejercicio.objects.count()}")
print()
print("=== LISTO ===")
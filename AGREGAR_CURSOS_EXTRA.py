# -*- coding: utf-8 -*-
"""
AGREGAR_CURSOS_EXTRA.py
Añade 20 cursos temáticos con lecciones y evaluaciones.
"""
import os
import sys
import random
import django

BASE = r"E:\02_proyectos\edunet_academia"
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from academia.models import Idioma, Nivel, Curso, Leccion, Inscripcion
from ejercicios.models import Evaluacion, PreguntaEvaluacion
from profesor.models import AsignacionProfesor
from progreso.models import ProgresoLeccion

User = get_user_model()


# ============================================================
# CURSOS TEMÁTICOS
# ============================================================
CURSOS_NUEVOS = [
    ("Taller de Escritura Creativa", "A2", "Desarrolla tu voz narrativa y crea historias memorables", 15),
    ("Gramática Avanzada del Castellano", "B2", "Domina las estructuras sintácticas complejas", 20),
    ("Literatura Hispanoamericana", "B1", "Recorre los grandes autores del siglo XX", 18),
    ("Redacción Periodística", "B2", "Técnicas profesionales para escribir noticias", 12),
    ("Ortografía para Profesionales", "A2", "Reglas esenciales para una escritura impecable", 15),
    ("Retórica y Persuasión", "B1", "El arte de convencer con palabras", 15),
    ("Fonética y Pronunciación", "A1", "Mejora tu acento y pronunciación", 12),
    ("Etimologías Grecolatinas", "B1", "Descubre el origen de las palabras", 10),
    ("Análisis Sintáctico", "B2", "Estructura de las oraciones en profundidad", 20),
    ("Escritura Académica", "C1", "Tesis, ensayos y artículos científicos", 25),
    ("Castellano para Extranjeros", "A1", "Curso intensivo para hispanohablantes no nativos", 30),
    ("Literatura Española Clásica", "B2", "Del Cantar del Mío Cid al Siglo de Oro", 22),
    ("Taller de Poesía", "B1", "Métrica, rima y verso libre", 12),
    ("Comunicación Empresarial", "B1", "Correos, informes y presentaciones efectivas", 15),
    ("Corrección de Estilo", "B2", "Edita y mejora textos profesionales", 15),
    ("Guion Cinematográfico", "B2", "Estructura narrativa para cine y TV", 18),
    ("Periodismo Digital", "B2", "Redacción para medios digitales", 12),
    ("Redes Sociales y Contenido", "A2", "Escribe para el mundo digital", 10),
    ("Locución y Oratoria", "B1", "Habla en público con confianza", 12),
    ("Preparación Saber Pro", "C1", "Entrenamiento intensivo para el examen", 25),
]


# ============================================================
# CREAR CURSOS
# ============================================================
print("=" * 60)
print("  CREANDO CURSOS EXTRA")
print("=" * 60)
print()

# Niveles
niveles = {n.codigo: n for n in Nivel.objects.all()}

cursos_creados = 0
lecciones_creadas = 0
evaluaciones_creadas = 0

for titulo, nivel_codigo, descripcion, num_lecciones in CURSOS_NUEVOS:
    nivel = niveles.get(nivel_codigo)
    if not nivel:
        continue

    curso, created = Curso.objects.get_or_create(
        titulo=titulo,
        defaults={
            "nivel": nivel,
            "descripcion": descripcion,
            "activo": True,
        }
    )

    if not created:
        print(f"  [=] {titulo}")
        continue

    cursos_creados += 1

    # Crear lecciones
    for i in range(1, num_lecciones + 1):
        lec, _ = Leccion.objects.get_or_create(
            curso=curso,
            orden=i,
            defaults={
                "titulo": f"Lección {i}: {titulo} - Parte {i}",
                "contenido": f"Contenido de la lección {i} del curso {titulo}.",
                "activa": True,
            }
        )
        lecciones_creadas += 1

    # Crear evaluación
    ev, _ = Evaluacion.objects.get_or_create(
        curso=curso,
        titulo=f"Evaluación final: {titulo}",
        defaults={
            "descripcion": f"Evaluación final del curso {titulo}",
            "nota_minima": 70,
            "activo": True,
        }
    )
    evaluaciones_creadas += 1

    # Crear 10 preguntas
    for i in range(1, 11):
        PreguntaEvaluacion.objects.get_or_create(
            evaluacion=ev,
            orden=i,
            defaults={
                "enunciado": f"Pregunta {i} sobre {titulo}",
                "opciones": ["Opción A", "Opción B", "Opción C", "Opción D"],
                "respuesta_correcta": "Opción A",
                "explicacion": f"Respuesta correcta según el curso {titulo}",
            }
        )

    print(f"  [+] {titulo} ({num_lecciones} lecciones)")

print()
print(f"[OK] Cursos creados:      {cursos_creados}")
print(f"[OK] Lecciones creadas:   {lecciones_creadas}")
print(f"[OK] Evaluaciones:        {evaluaciones_creadas}")


# ============================================================
# ASIGNAR PROFESORES A LOS NUEVOS CURSOS
# ============================================================
print()
print("=== Asignando profesores ===")

profesores = list(User.objects.filter(is_staff=True, is_superuser=False))
asignaciones = 0

cursos_sin_prof = Curso.objects.filter(activo=True).exclude(
    id__in=AsignacionProfesor.objects.values_list("curso_id", flat=True)
)

for curso in cursos_sin_prof:
    prof = random.choice(profesores)
    AsignacionProfesor.objects.get_or_create(
        profesor=prof,
        curso=curso,
        defaults={"activo": True}
    )
    asignaciones += 1

print(f"[OK] Asignaciones creadas: {asignaciones}")


# ============================================================
# INSCRIBIR ESTUDIANTES EN LOS NUEVOS CURSOS
# ============================================================
print()
print("=== Inscribiendo estudiantes ===")

estudiantes = list(User.objects.filter(is_staff=False, is_superuser=False))
inscripciones_nuevas = 0

for curso in Curso.objects.filter(activo=True):
    # Inscribir 20-40 estudiantes aleatorios
    num = random.randint(20, min(40, len(estudiantes)))
    seleccionados = random.sample(estudiantes, num)

    for est in seleccionados:
        insc, created = Inscripcion.objects.get_or_create(
            usuario=est,
            curso=curso,
            defaults={"activa": True}
        )
        if created:
            inscripciones_nuevas += 1

print(f"[OK] Inscripciones nuevas: {inscripciones_nuevas}")


# ============================================================
# RESUMEN FINAL
# ============================================================
print()
print("=" * 60)
print("  RESUMEN FINAL")
print("=" * 60)
print(f"Cursos:       {Curso.objects.count()}")
print(f"Lecciones:    {Leccion.objects.count()}")
print(f"Evaluaciones: {Evaluacion.objects.count()}")
print(f"Preguntas:    {PreguntaEvaluacion.objects.count()}")
print(f"Inscripciones: {Inscripcion.objects.count()}")
print()
print("=== LISTO ===")
print("Rearrancar:")
print("  E:\\pydj5.bat manage.py runserver 8011 --noreload")
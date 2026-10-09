# -*- coding: utf-8 -*-
"""
Seed de relaciones:
- Asigna 3-5 cursos a cada profesor (AsignacionProfesor)
- Matricula a cada estudiante en 3-5 cursos (Inscripcion)
- Crea perfil de gamificacion para cada estudiante

Uso:
    python seed_relations.py            # dry-run
    python seed_relations.py --apply    # aplica
"""
import os, sys, random
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.utils import timezone
from django.db import transaction

from accounts.models import User
from academia.models import Curso, Inscripcion
from profesor.models import AsignacionProfesor
from gamificacion.models import PerfilGamificacion


def log(msg):
    print(msg)


def asignar_cursos_a_profesores(cursos, apply_changes):
    """Asigna 3-5 cursos a cada profesor."""
    profesores = User.objects.filter(is_staff=True, is_superuser=False).order_by("username")
    log("Profesores: " + str(profesores.count()))

    total_asignaciones = 0
    for prof in profesores:
        n = random.randint(3, 5)
        seleccion = random.sample(cursos, min(n, len(cursos)))

        for curso in seleccion:
            if apply_changes:
                obj, created = AsignacionProfesor.objects.get_or_create(
                    profesor=prof,
                    curso=curso,
                )
                if created:
                    total_asignaciones += 1
            else:
                if not AsignacionProfesor.objects.filter(profesor=prof, curso=curso).exists():
                    total_asignaciones += 1

        log("  " + prof.username + "  -> " + str(len(seleccion)) + " cursos")

    return total_asignaciones


def matricular_estudiantes(cursos, apply_changes):
    """Matricula a cada estudiante en 3-5 cursos."""
    estudiantes = User.objects.filter(is_staff=False, is_superuser=False).order_by("username")
    print()
    log("Estudiantes: " + str(estudiantes.count()))

    total_matriculas = 0
    total_perfiles = 0

    for i, est in enumerate(estudiantes, 1):
        n = random.randint(3, 5)
        seleccion = random.sample(cursos, min(n, len(cursos)))

        for curso in seleccion:
            if apply_changes:
                obj, created = Inscripcion.objects.get_or_create(
                    usuario=est,
                    curso=curso,
                    defaults={"activa": True, "completado": False},
                )
                if created:
                    total_matriculas += 1
            else:
                if not Inscripcion.objects.filter(usuario=est, curso=curso).exists():
                    total_matriculas += 1

        # Perfil de gamificacion
        if apply_changes:
            perfil, created = PerfilGamificacion.objects.get_or_create(
                usuario=est,
                defaults={"xp_total": 0, "nivel_actual": 1, "racha_dias": 0},
            )
            if created:
                total_perfiles += 1
        else:
            if not PerfilGamificacion.objects.filter(usuario=est).exists():
                total_perfiles += 1

        if i % 20 == 0:
            log("  ... procesados " + str(i) + " estudiantes")

    return total_matriculas, total_perfiles


def main():
    apply_changes = "--apply" in sys.argv

    print("=" * 60)
    print(" SEED RELATIONS - EduNet Academia")
    print("=" * 60)
    print("Modo: " + ("APLICAR" if apply_changes else "DRY-RUN"))
    print()

    cursos = list(Curso.objects.all())
    log("Cursos en BD: " + str(len(cursos)))

    if not cursos:
        log("[!] No hay cursos. Crea cursos antes.")
        return

    random.seed(42)

    # Asignaciones
    print()
    print("--- Asignaciones profesor-curso ---")
    total_asig = asignar_cursos_a_profesores(cursos, apply_changes)
    log("  Nuevas asignaciones: " + str(total_asig))

    # Matriculas
    print()
    print("--- Matriculas estudiante-curso ---")
    total_mat, total_perf = matricular_estudiantes(cursos, apply_changes)

    # Resumen
    print()
    print("=" * 60)
    print(" RESUMEN")
    print("=" * 60)
    print("Asignaciones nuevas: " + str(total_asig))
    print("Matriculas nuevas:   " + str(total_mat))
    print("Perfiles nuevos:     " + str(total_perf))
    print()

    if apply_changes:
        print("[OK] Datos creados.")
    else:
        print("DRY-RUN. Para aplicar: --apply")
    print("=" * 60)


if __name__ == "__main__":
    main()
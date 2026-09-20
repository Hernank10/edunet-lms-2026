# -*- coding: utf-8 -*-
"""ASIGNAR_PROFESORES.py - Asigna cursos a los 9 profesores."""
import os
import sys
import random
import django

BASE = r"E:\02_proyectos\edunet_academia"
sys.path.insert(0, BASE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from academia.models import Curso
from profesor.models import AsignacionProfesor

User = get_user_model()

# Obtener profesores
profesores = User.objects.filter(is_staff=True, is_superuser=False)
print(f"Profesores: {profesores.count()}")

cursos = list(Curso.objects.filter(activo=True))
print(f"Cursos: {len(cursos)}")

# Asignar cada curso a 1-2 profesores aleatorios
asignaciones_creadas = 0

for curso in cursos:
    num_profs = random.randint(1, 2)
    profes_elegidos = random.sample(list(profesores), min(num_profs, len(profesores)))

    for prof in profes_elegidos:
        asign, created = AsignacionProfesor.objects.get_or_create(
            profesor=prof,
            curso=curso,
            defaults={"activo": True}
        )
        if created:
            asignaciones_creadas += 1

print(f"\n[OK] Asignaciones creadas: {asignaciones_creadas}")
print(f"     Total en BD: {AsignacionProfesor.objects.count()}")

# Resumen
print("\n=== Cursos por profesor ===")
for prof in profesores:
    n = AsignacionProfesor.objects.filter(profesor=prof, activo=True).count()
    print(f"  {prof.username:25} → {n} cursos")

print()
print("=== LISTO ===")
print("Rearrancar: E:\\pydj5.bat manage.py runserver 8011 --noreload")
print()
print("URLs:")
print("  http://127.0.0.1:8011/profesor/")
print()
print("Login: prof_garcia / profesor1234")
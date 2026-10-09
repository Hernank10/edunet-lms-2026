# -*- coding: utf-8 -*-
"""
Seed de datos de prueba para EduNet Academia.

Crea:
- 3 superusuarios (admin01, admin02, admin03)
- 9 profesores (prof01..prof09, is_staff=True)
- 96 estudiantes (est01..est96)

Uso:
    python seed_test_data.py            # dry-run (no guarda)
    python seed_test_data.py --apply    # aplica los cambios
"""
import os
import sys
from pathlib import Path

# IMPORTANTE: Añadir el directorio del proyecto al sys.path
# para que Python encuentre el paquete `config`.
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import random
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User


# ============ DATOS ============
NOMBRES_ADMIN = [
    ("admin01", "Hernan",   "Garcia",   "admin01@edunet.com"),
    ("admin02", "Laura",    "Martinez", "admin02@edunet.com"),
    ("admin03", "Diego",    "Rodriguez","admin03@edunet.com"),
]

NOMBRES_PROFESORES = [
    ("prof01", "Carlos",   "Ramirez",   "prof01@edunet.com"),
    ("prof02", "Maria",    "Lopez",     "prof02@edunet.com"),
    ("prof03", "Andres",   "Gomez",     "prof03@edunet.com"),
    ("prof04", "Sofia",    "Fernandez", "prof04@edunet.com"),
    ("prof05", "Javier",   "Torres",    "prof05@edunet.com"),
    ("prof06", "Lucia",    "Sanchez",   "prof06@edunet.com"),
    ("prof07", "Fernando", "Diaz",      "prof07@edunet.com"),
    ("prof08", "Camila",   "Moreno",    "prof08@edunet.com"),
    ("prof09", "Ricardo",  "Jimenez",   "prof09@edunet.com"),
]

NOMBRES_ESTUDIANTES = [
    "Ana", "Luis", "Maria", "Carlos", "Sofia", "Diego", "Valentina", "Andres",
    "Camila", "Javier", "Isabella", "Fernando", "Lucia", "Ricardo", "Daniela",
    "Alejandro", "Paula", "Santiago", "Gabriela", "Mateo", "Mariana", "Sebastian",
    "Valeria", "Nicolas", "Daniela2", "Juan", "Juliana", "Felipe", "Natalia",
    "Emilio", "Carolina", "Tomas", "Adriana", "Martin", "Elena", "Pablo",
    "Sara", "Joaquin", "Antonella", "Guillermo", "Renata", "Bruno", "Alejandra",
    "Ivan", "Florencia", "Simon", "Veronica", "Oscar", "Ximena", "Rafael",
]

APELLIDOS = [
    "Garcia", "Rodriguez", "Martinez", "Lopez", "Gonzalez", "Perez", "Sanchez",
    "Ramirez", "Torres", "Flores", "Rivera", "Gomez", "Diaz", "Cruz", "Morales",
    "Ortiz", "Gutierrez", "Chavez", "Ramos", "Ruiz", "Hernandez", "Jimenez",
    "Mendoza", "Vargas", "Castillo", "Romero", "Suarez", "Rojas", "Silva",
    "Pena", "Vega", "Cabrera", "Rios", "Munoz", "Aguilar", "Nunez",
]

PASSWORDS = {
    "admin":      "admin1234",
    "profesor":   "profesor1234",
    "estudiante": "estudiante1234",
}


def log(msg):
    print(msg)


def crear_admin(username, first, last, email):
    if User.objects.filter(username=username).exists():
        return None, False
    u = User.objects.create_superuser(
        username=username, email=email, password=PASSWORDS["admin"],
        first_name=first, last_name=last,
    )
    return u, True


def crear_profesor(username, first, last, email):
    if User.objects.filter(username=username).exists():
        return None, False
    u = User.objects.create_user(
        username=username, email=email, password=PASSWORDS["profesor"],
        first_name=first, last_name=last,
        is_staff=True, is_superuser=False,
    )
    return u, True


def crear_estudiante(username, first, last, email, idioma, zona):
    if User.objects.filter(username=username).exists():
        return None, False
    u = User.objects.create_user(
        username=username, email=email, password=PASSWORDS["estudiante"],
        first_name=first, last_name=last,
        idioma_nativo=idioma, zona_horaria=zona,
    )
    return u, True


def main():
    apply_changes = "--apply" in sys.argv

    print("=" * 70)
    print(" SEED TEST DATA - EduNet Academia")
    print("=" * 70)
    print("Modo: " + ("APLICAR CAMBIOS" if apply_changes else "DRY-RUN (no guarda)"))
    print()

    log("Usuarios existentes en BD: " + str(User.objects.count()))

    # ============ ADMINS ============
    print()
    print("--- Superusuarios ---")
    admins_creados = 0
    for username, first, last, email in NOMBRES_ADMIN:
        if apply_changes:
            u, created = crear_admin(username, first, last, email)
        else:
            created = not User.objects.filter(username=username).exists()
        if created:
            log("  [+] " + username + "  (" + first + " " + last + ")  pass=" + PASSWORDS["admin"])
            admins_creados += 1
        else:
            log("  [=] " + username + " ya existe")

    # ============ PROFESORES ============
    print()
    print("--- Profesores ---")
    profesores_creados = 0
    for username, first, last, email in NOMBRES_PROFESORES:
        if apply_changes:
            u, created = crear_profesor(username, first, last, email)
        else:
            created = not User.objects.filter(username=username).exists()
        if created:
            log("  [+] " + username + "  (" + first + " " + last + ")  pass=" + PASSWORDS["profesor"])
            profesores_creados += 1
        else:
            log("  [=] " + username + " ya existe")

    # ============ ESTUDIANTES ============
    print()
    print("--- Estudiantes (96) ---")
    estudiantes_creados = 0
    idiomas = ["Espanol", "Ingles", "Portugues", "Frances", "Aleman", "Italiano"]
    zonas = ["UTC-5", "UTC-6", "UTC-3", "UTC+0", "UTC+1", "UTC+2"]

    for i in range(1, 97):
        username = "est" + str(i).zfill(3)
        first = NOMBRES_ESTUDIANTES[(i - 1) % len(NOMBRES_ESTUDIANTES)]
        last = APELLIDOS[(i - 1) % len(APELLIDOS)]
        email = username + "@estudiante.edunet.com"
        idioma = random.choice(idiomas)
        zona = random.choice(zonas)

        if apply_changes:
            u, created = crear_estudiante(username, first, last, email, idioma, zona)
        else:
            created = not User.objects.filter(username=username).exists()
        if created:
            estudiantes_creados += 1

    log("  Estudiantes a crear: " + str(estudiantes_creados))
    log("  Password: " + PASSWORDS["estudiante"])

    # ============ RESUMEN ============
    print()
    print("=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    print("Superusuarios: " + str(admins_creados))
    print("Profesores:    " + str(profesores_creados))
    print("Estudiantes:   " + str(estudiantes_creados))
    print()
    print("Passwords:")
    print("  Admins:      " + PASSWORDS["admin"])
    print("  Profesores:  " + PASSWORDS["profesor"])
    print("  Estudiantes: " + PASSWORDS["estudiante"])
    print()

    if not apply_changes:
        print("DRY-RUN. NO se ha guardado nada.")
        print("Para aplicar: E:\\pydj5.bat seed_test_data.py --apply")
    else:
        print("[OK] Datos de prueba creados.")
        print("Total usuarios ahora en BD: " + str(User.objects.count()))

    print("=" * 70)


if __name__ == "__main__":
    main()
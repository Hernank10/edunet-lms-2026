# -*- coding: utf-8 -*-
"""Verifica que los usuarios de prueba existen en la BD."""
import os, sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from accounts.models import User

total = User.objects.count()
admins = User.objects.filter(is_superuser=True).count()
profesores = User.objects.filter(is_staff=True, is_superuser=False).count()
estudiantes = User.objects.filter(is_staff=False, is_superuser=False).count()

print("=" * 60)
print(" VERIFICACION DE USUARIOS EN BD")
print("=" * 60)
print("Total usuarios:  " + str(total))
print("  Superusuarios: " + str(admins))
print("  Profesores:    " + str(profesores))
print("  Estudiantes:   " + str(estudiantes))
print()

# Verificar los usuarios especificos del seed
print("--- Usuarios del seed ---")
for username in ["admin01", "admin02", "admin03",
                 "prof01", "prof02", "prof03",
                 "est001", "est002", "est096"]:
    exists = User.objects.filter(username=username).exists()
    mark = "[+]" if exists else "[!]"
    print("  " + mark + " " + username)

print()
print("--- Primeros 5 estudiantes ---")
for u in User.objects.filter(username__startswith="est").order_by("username")[:5]:
    print("  " + u.username + "  |  " + u.first_name + " " + u.last_name + "  |  " + u.email)

print()
print("=" * 60)
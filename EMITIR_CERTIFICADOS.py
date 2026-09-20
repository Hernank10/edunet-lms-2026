# -*- coding: utf-8 -*-
"""
EMITIR_CERTIFICADOS.py
Emite certificados con firmas de admin + profesor.
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
from django.utils import timezone
from academia.models import Curso, Inscripcion
from certificaciones.models import Certificado, Firma
from profesor.models import AsignacionProfesor

User = get_user_model()


# ============================================================
# 1. CREAR FIRMAS PARA ADMINS Y PROFESORES
# ============================================================
print("=" * 60)
print("  CREANDO FIRMAS")
print("=" * 60)
print()

# Firmas para superusers (cargo: Director)
admins = User.objects.filter(is_superuser=True)
for admin in admins:
    firma, created = Firma.objects.get_or_create(
        usuario=admin,
        defaults={
            "cargo": "Director General",
            "institucion": "Academia Global de Castellano",
            "activa": True,
        }
    )
    print(f"  {'+' if created else '='} {admin.username} → {firma.cargo}")

# Firmas para profesores
profesores = User.objects.filter(is_staff=True, is_superuser=False)
for prof in profesores:
    firma, created = Firma.objects.get_or_create(
        usuario=prof,
        defaults={
            "cargo": "Profesor Titular",
            "institucion": "Academia Global de Castellano",
            "activa": True,
        }
    )
    print(f"  {'+' if created else '='} {prof.username} → {firma.cargo}")

print(f"\n  Total firmas: {Firma.objects.count()}")


# ============================================================
# 2. EMITIR CERTIFICADOS CON FIRMAS
# ============================================================
print()
print("=" * 60)
print("  EMITIENDO CERTIFICADOS CON FIRMAS")
print("=" * 60)
print()

# Admin principal para firmar
admin_firmante = User.objects.filter(is_superuser=True).first()
if not admin_firmante:
    print("[ERROR] No hay superusuarios")
    sys.exit(1)

# Emitir certificados a inscripciones completadas
certs_creados = 0
certs_actualizados = 0

inscripciones_completas = Inscripcion.objects.filter(
    completado=True,
    usuario__is_staff=False,
    usuario__is_superuser=False
).select_related("usuario", "curso")

for insc in inscripciones_completas[:50]:  # máximo 50 por vez
    # Si ya existe, actualizar firmas
    cert, created = Certificado.objects.get_or_create(
        usuario=insc.usuario,
        curso=insc.curso,
        defaults={
            "nota_final": random.randint(80, 100),
            "horas": random.choice([20, 30, 40, 50, 60]),
            "firmado_por_admin": admin_firmante,
            "cargo_admin": "Director General",
            "cargo_profesor": "Profesor Titular",
            "institucion": "Academia Global de Castellano",
        }
    )

    # Buscar profesor asignado al curso
    asignacion = AsignacionProfesor.objects.filter(
        curso=insc.curso, activo=True
    ).select_related("profesor").first()

    if asignacion:
        cert.firmado_por_profesor = asignacion.profesor

    if not cert.firmado_por_admin:
        cert.firmado_por_admin = admin_firmante

    cert.save()

    if created:
        certs_creados += 1
        print(f"  [+] {cert.codigo_corto} | {insc.usuario.username:20} | {insc.curso.titulo[:40]}")
    else:
        certs_actualizados += 1

print()
print(f"[OK] Nuevos: {certs_creados}")
print(f"[OK] Actualizados: {certs_actualizados}")
print(f"[OK] Total en BD: {Certificado.objects.count()}")


# ============================================================
# 3. RESUMEN
# ============================================================
print()
print("=" * 60)
print("  RESUMEN FINAL")
print("=" * 60)
print(f"Firmas:       {Firma.objects.count()}")
print(f"Certificados: {Certificado.objects.count()}")
print(f"  Con admin:    {Certificado.objects.exclude(firmado_por_admin=None).count()}")
print(f"  Con profesor: {Certificado.objects.exclude(firmado_por_profesor=None).count()}")
print()
print("Ver un certificado:")
primer = Certificado.objects.first()
if primer:
    print(f"  http://127.0.0.1:8011/certificados/{primer.codigo}/")
print()
print("=== LISTO ===")
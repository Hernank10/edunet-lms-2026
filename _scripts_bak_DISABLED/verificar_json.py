# -*- coding: utf-8 -*-
"""verificar_json.py - Cuenta cuántos JSON son válidos."""
import json
import glob
import os

BASE = r"E:\02_proyectos\edunet_academia\contenido\json"

total = 0
ok = 0
errores = []

for path in glob.glob(os.path.join(BASE, "**", "*.json"), recursive=True):
    total += 1
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Contar items según formato
        if isinstance(data, list):
            n = len(data)
        elif isinstance(data, dict):
            if "tecnicas" in data:
                n = len(data["tecnicas"])
            else:
                n = 1
        else:
            n = 0

        ok += 1
        print(f"[OK]  {n:4} items | {os.path.basename(path)[:60]}")
    except Exception as ex:
        errores.append((path, str(ex)))
        print(f"[ERR] {os.path.basename(path)[:60]}")
        print(f"      → {ex}")

print()
print("=" * 60)
print(f"  TOTAL: {total} | OK: {ok} | ERRORES: {len(errores)}")
print("=" * 60)

if errores:
    print("\nErrores pendientes:")
    for p, e in errores:
        print(f"  - {os.path.basename(p)}")
        print(f"    {e[:100]}")
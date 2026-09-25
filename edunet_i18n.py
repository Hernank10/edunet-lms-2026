# -*- coding: utf-8 -*-
"""
edunet_i18n.py - Pipeline completo de i18n para edunet_academia.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(r"E:\02_proyectos\edunet_academia")
TEMPLATES_DIR = BASE_DIR / "templates"
LOCALE_DIR = BASE_DIR / "locale"
JSON_FILE = BASE_DIR / "i18n_traducciones.json"
PYDJ5 = r"E:\pydj5.bat"

IDIOMAS = ["es", "en", "zh-hans", "hi", "ar", "pt", "bn",
           "ru", "ja", "de", "fr", "ko", "it", "tr", "vi"]

CADENAS = [
    "Castellano Global", "Contenido", "Recursos", "HTMLs",
    "Entrar", "Registro", "Academia Global de Castellano",
    "Aprende, practica y certifícate con 42 cursos, 2.000+ técnicas y 428 apps interactivas.",
    "Cursos", "Técnicas", "Usuarios", "Certificados",
    "Recursos JSON", "30 recursos con 2097 técnicas",
    "HTMLs interactivos", "428 apps: flotas, cuadernos, juegos",
    "Hub de contenido", "12 categorías temáticas",
    "Explorar por categoría", "Salir", "Admin", "Profesor",
    "Estudiante", "Perfil",
]

def ejecutar(cmd, desc):
    print(f"\n>>> {desc}")
    print(f"    {cmd}")
    r = subprocess.run(cmd, shell=True, cwd=str(BASE_DIR),
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.stdout: print(r.stdout[-3000:])
    if r.stderr: print("STDERR:", r.stderr[-2000:])
    return r.returncode

def backup(ruta):
    bak = ruta.with_suffix(ruta.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(ruta, bak)

def asegurar_load_i18n(contenido):
    if "{% load i18n %}" in contenido:
        return contenido
    return "{% load i18n %}\n" + contenido

def marcar_cadena(contenido, cadena):
    cadena_esc = re.escape(cadena)
    patron = re.compile(
        r'(>\s*(?:[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+\s*)*)'
        r'(' + cadena_esc + r')(\s*<)', re.UNICODE)
    if '{% trans "' + cadena + '" %}' in contenido:
        return contenido, 0
    nuevo, n = patron.subn(r'\1{% trans "' + cadena + r'" %}\3', contenido)
    return nuevo, n

def marcar_plantilla(ruta):
    contenido = ruta.read_text(encoding="utf-8")
    total = 0
    detalle = {}
    for cadena in CADENAS:
        contenido, n = marcar_cadena(contenido, cadena)
        if n > 0:
            detalle[cadena] = n
            total += n
    if total > 0:
        contenido = asegurar_load_i18n(contenido)
        backup(ruta)
        ruta.write_text(contenido, encoding="utf-8")
    return total, detalle

def fase1_marcar():
    print("\n" + "=" * 60)
    print("FASE 1 - Marcar cadenas")
    print("=" * 60)
    plantillas = sorted(TEMPLATES_DIR.rglob("*.html"))
    for d in BASE_DIR.iterdir():
        if d.is_dir() and (d / "templates").exists():
            plantillas.extend(sorted((d / "templates").rglob("*.html")))
    print(f"Plantillas: {len(plantillas)}")
    total_global = 0
    for p in plantillas:
        total, detalle = marcar_plantilla(p)
        if total > 0:
            try: rel = p.relative_to(BASE_DIR)
            except: rel = p
            print(f"  OK {rel} -> {total}")
            total_global += total
    print(f"\nTOTAL: {total_global} cadenas marcadas")

def fase2_makemessages():
    print("\n" + "=" * 60)
    print("FASE 2 - makemessages")
    print("=" * 60)
    langs = " ".join([f"-l {l}" for l in IDIOMAS])
    cmd = (f'{PYDJ5} manage.py makemessages -a {langs} '
           f'--ignore=.venv --ignore=env --ignore=_scripts_bak_DISABLED '
           f'--ignore=static --ignore=contenido --ignore=ejercicios')
    ejecutar(cmd, "makemessages")

def fase3_traducir():
    print("\n" + "=" * 60)
    print("FASE 3 - Traducir .po desde JSON")
    print("=" * 60)
    if not JSON_FILE.exists():
        print(f"  ERROR: no existe {JSON_FILE}")
        return
    with JSON_FILE.open(encoding="utf-8-sig") as f:
        traducciones = json.load(f)
    print(f"  Cadenas: {len(traducciones)}")
    total = 0
    for idioma in IDIOMAS:
        carpeta = "zh_Hans" if idioma == "zh-hans" else idioma
        po = LOCALE_DIR / carpeta / "LC_MESSAGES" / "django.po"
        if not po.exists():
            print(f"  SKIP {idioma}")
            continue
        contenido = po.read_text(encoding="utf-8")
        lineas = contenido.split("\n")
        salida = []
        i = 0
        cambios = 0
        while i < len(lineas):
            linea = lineas[i]
            salida.append(linea)
            if linea.startswith('msgid "'):
                msgid = linea[len('msgid "'):].rstrip('"')
                if (i + 1 < len(lineas)
                        and lineas[i + 1].strip() == 'msgstr ""'
                        and msgid):
                    t = traducciones.get(msgid, {}).get(carpeta) \
                        or traducciones.get(msgid, {}).get(idioma)
                    if t:
                        indent = " " * (len(lineas[i + 1]) - len(lineas[i + 1].lstrip()))
                        salida.append(f'{indent}msgstr "{t}"')
                        cambios += 1
                        i += 2
                        continue
            i += 1
        if cambios > 0:
            po.write_text("\n".join(salida), encoding="utf-8")
        print(f"  {idioma:<10} {cambios} traducciones")
        total += cambios
    print(f"\nTOTAL: {total} msgstr")

def fase4_compilar():
    print("\n" + "=" * 60)
    print("FASE 4 - compilemessages")
    print("=" * 60)
    ejecutar(f"{PYDJ5} manage.py compilemessages", "compilemessages")

def main():
    print("=" * 60)
    print("EDUNET i18n")
    print("=" * 60)
    if not BASE_DIR.exists():
        print(f"ERROR: no existe {BASE_DIR}")
        return
    fases = sys.argv[1:] if len(sys.argv) > 1 else ["1", "2", "3", "4"]
    if "1" in fases: fase1_marcar()
    if "2" in fases: fase2_makemessages()
    if "3" in fases: fase3_traducir()
    if "4" in fases: fase4_compilar()
    print("\nLISTO")

if __name__ == "__main__":
    main()

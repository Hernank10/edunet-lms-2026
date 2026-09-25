# -*- coding: utf-8 -*-
"""
edunet_i18n_setup.py
FASE 1-3: Configura i18n en edunet_academia (15 idiomas, solo interfaz).
- LocaleMiddleware en settings.py
- LANGUAGES (15 idiomas)
- LOCALE_PATHS
- i18n_patterns en urls.py
- Selector dinamico en base.html
- pydj5.bat sin BOM
"""

import re
import shutil
from pathlib import Path

# ============================================================
# CONFIGURACION
# ============================================================
BASE_DIR = Path(r"E:\02_proyectos\edunet_academia")
SETTINGS = BASE_DIR / "config" / "settings.py"
URLS = BASE_DIR / "config" / "urls.py"
BASE_HTML = BASE_DIR / "templates" / "base.html"
PYDJ5 = Path(r"E:\pydj5.bat")

LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
    ("zh-hans", "简体中文"),
    ("hi", "हिन्दी"),
    ("ar", "العربية"),
    ("pt", "Português"),
    ("bn", "বাংলা"),
    ("ru", "Русский"),
    ("ja", "日本語"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("ko", "한국어"),
    ("it", "Italiano"),
    ("tr", "Türkçe"),
    ("vi", "Tiếng Việt"),
]

LOCALE_MIDDLEWARE_LINE = '    "django.middleware.locale.LocaleMiddleware",\n'
SESSION_MIDDLEWARE = 'django.contrib.sessions.middleware.SessionMiddleware'


def backup(ruta):
    """Crea backup .bak si no existe."""
    bak = ruta.with_suffix(ruta.suffix + ".bak")
    if not bak.exists():
        shutil.copy2(ruta, bak)
        print(f"  Backup: {bak.name}")


def leer(ruta):
    return ruta.read_text(encoding="utf-8")


def escribir(ruta, contenido):
    ruta.write_text(contenido, encoding="utf-8")


# ============================================================
# SETTINGS.PY
# ============================================================
def configurar_settings():
    print("\n=== 1. configurando settings.py ===")
    if not SETTINGS.exists():
        print(f"  ERROR: no existe {SETTINGS}")
        return
    backup(SETTINGS)
    contenido = leer(SETTINGS)

    # 1. LocaleMiddleware
    if "LocaleMiddleware" not in contenido:
        if SESSION_MIDDLEWARE in contenido:
            contenido = contenido.replace(
                SESSION_MIDDLEWARE + ",",
                SESSION_MIDDLEWARE + ",\n" + LOCALE_MIDDLEWARE_LINE.rstrip(),
                1
            )
            print("  + LocaleMiddleware anadido")
        else:
            print("  WARN: no se encontro SessionMiddleware")
    else:
        print("  LocaleMiddleware ya existe")

    # 2. LANGUAGES
    if "LANGUAGES = [" not in contenido:
        bloque = "\nLANGUAGES = [\n"
        for code, name in LANGUAGES:
            bloque += f'    ("{code}", "{name}"),\n'
        bloque += "]\n"
        contenido += "\n# i18n\n" + bloque
        print("  + LANGUAGES (15 idiomas) anadido")
    else:
        print("  LANGUAGES ya existe")

    # 3. LOCALE_PATHS
    if "LOCALE_PATHS" not in contenido:
        contenido += '\nLOCALE_PATHS = [\n    BASE_DIR / "locale",\n]\n'
        print("  + LOCALE_PATHS anadido")
    else:
        print("  LOCALE_PATHS ya existe")

    escribir(SETTINGS, contenido)


# ============================================================
# URLS.PY
# ============================================================
def configurar_urls():
    print("\n=== 2. configurando urls.py ===")
    if not URLS.exists():
        print(f"  ERROR: no existe {URLS}")
        return
    backup(URLS)
    contenido = leer(URLS)

    # 1. Import i18n_patterns
    if "from django.conf.urls.i18n import i18n_patterns" not in contenido:
        contenido = "from django.conf.urls.i18n import i18n_patterns\n" + contenido
        print("  + import i18n_patterns")

    # 2. path i18n/
    if 'path("i18n/"' not in contenido and "path('i18n/'" not in contenido:
        # insertar dentro de urlpatterns = [ ... ] al inicio
        match = re.search(r'urlpatterns\s*=\s*\[', contenido)
        if match:
            pos = match.end()
            contenido = (contenido[:pos]
                         + '\n    path("i18n/", include("django.conf.urls.i18n")),'
                         + contenido[pos:])
            print("  + path i18n/")
        else:
            print("  WARN: no se encontro urlpatterns = [")

    escribir(URLS, contenido)


# ============================================================
# BASE.HTML - Selector dinamico
# ============================================================
SELECTOR_HTML = '''{% load i18n %}
<li class="nav-item dropdown">
  <a class="nav-link dropdown-toggle" href="#" id="langDropdown" role="button" data-bs-toggle="dropdown">
    🌍 {{ LANGUAGE_CODE|upper }}
  </a>
  <ul class="dropdown-menu dropdown-menu-end">
    <li>
      <form method="post" action="{% url 'set_language' %}">
        {% csrf_token %}
        <input type="hidden" name="next" value="{{ request.path }}">
        {% get_current_language as CURRENT_LANG %}
        {% get_available_languages as AVAILABLE_LANGUAGES %}
        {% for code, name in AVAILABLE_LANGUAGES %}
          <button type="submit" name="language" value="{{ code }}"
                  class="dropdown-item {% if code == CURRENT_LANG %}active{% endif %}">
            {{ name }}
          </button>
        {% endfor %}
      </form>
    </li>
  </ul>
</li>
'''


def configurar_base_html():
    print("\n=== 3. configurando base.html ===")
    if not BASE_HTML.exists():
        print(f"  ERROR: no existe {BASE_HTML}")
        return
    backup(BASE_HTML)
    contenido = leer(BASE_HTML)

    # 1. load i18n
    if "{% load i18n %}" not in contenido:
        if contenido.lstrip().startswith("{% extends"):
            lineas = contenido.split("\n", 1)
            contenido = lineas[0] + "\n{% load i18n %}\n" + (lineas[1] if len(lineas) > 1 else "")
        else:
            contenido = "{% load i18n %}\n" + contenido
        print("  + {% load i18n %}")

    # 2. Selector (solo si no existe)
    if 'id="langDropdown"' in contenido or "set_language" in contenido:
        print("  Selector ya existe, no se toca")
    else:
        # insertar antes de </ul> del navbar
        if "</ul>" in contenido:
            idx = contenido.find("</ul>")
            contenido = contenido[:idx] + SELECTOR_HTML + contenido[idx:]
            print("  + selector dinamico insertado")
        else:
            print("  WARN: no se encontro </ul> para insertar")

    escribir(BASE_HTML, contenido)


# ============================================================
# PYDJ5.BAT sin BOM
# ============================================================
def arreglar_pydj5():
    print("\n=== 4. arreglando pydj5.bat ===")
    if not PYDJ5.exists():
        print(f"  WARN: no existe {PYDJ5}")
        return
    contenido = (
        "@echo off\r\n"
        "set PYTHONUTF8=1\r\n"
        "set PYTHONIOENCODING=utf-8\r\n"
        "E:\\PythonPortable_Django5\\python.exe %*\r\n"
    )
    PYDJ5.write_bytes(contenido.encode("ascii"))
    print("  pydj5.bat re-creado sin BOM")


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("EDUNET i18n SETUP - 15 idiomas, solo interfaz")
    print("=" * 60)
    print(f"BASE_DIR: {BASE_DIR}")

    if not BASE_DIR.exists():
        print(f"ERROR: no existe {BASE_DIR}")
        return

    configurar_settings()
    configurar_urls()
    configurar_base_html()
    arreglar_pydj5()

    print("\n" + "=" * 60)
    print("SETUP COMPLETADO")
    print("=" * 60)
    print("\nSiguiente paso:")
    print("  1. Revisar config/settings.py, config/urls.py, templates/base.html")
    print("  2. Ejecutar: E:\\pydj5.bat manage.py check")
    print("  3. Ejecutar: E:\\pydj5.bat manage.py makemessages -a")
    print("  4. Ejecutar: edunet_i18n_run.py")


if __name__ == "__main__":
    main()
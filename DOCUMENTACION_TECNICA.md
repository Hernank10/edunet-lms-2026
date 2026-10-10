# EduNet Academia - Documentacion Tecnica

**LMS de Lengua Castellana** - Django 5.2.11 + Python 3.12.4 (portable)

**Repositorio:** https://github.com/Hernank10/edunet-lms-2026

---

## Estado del Proyecto

### Tests implementados

| App | Tests | Estado |
|-----|-------|--------|
| accounts | 10 | Pusheado |
| academia | 29 | Pusheado |
| profesor | 38 | Pusheado |
| gamificacion | 43 | Pusheado |
| certificaciones | 39 | Pusheado |
| **Total** | **159** | **OK ~20s** |

---

## Comandos Esenciales

```cmd
cd /d "E:\02_proyectos\edunet_academia"
E:\PythonPortable_Django5\python.exe manage.py runserver 8011 --noreload
E:\PythonPortable_Django5\python.exe manage.py check
E:\PythonPortable_Django5\python.exe manage.py migrate
E:\PythonPortable_Django5\python.exe -m pytest -q
E:\PythonPortable_Django5\python.exe -m pytest accounts/ -v
```

---

## Errores Encontrados y Fixes

### Error 1: Found 0 test(s) en manage.py test accounts
- Causa: tests.py vacio
- Fix: Escribir tests con TestCase

### Error 2: TemplateSyntaxError: Unclosed tag on line 4 block
- Causa: {% block extra_js %} anidado en {% block contenido %}
- Fix: Poner script dentro de contenido, sin bloque adicional

### Error 3: Archivos HTML rotos con menor-que faltantes
- Causa: -replace con regex de PowerShell en HTML
- Fix: Restaurar desde Git y NUNCA usar -replace para HTML

### Error 4: 404 != 200 en test_get_registro_devuelve_200
- Causa: LANGUAGE_CODE=es-co no esta en LANGUAGES
- Fix: translation.activate(es) en setUp

### Error 5: pytest tarda 3+ min en collecting
- Causa: Sin norecursedirs, recorre static/, media/, contenido/
- Fix: Anadir norecursedirs en pytest.ini

### Error 6: --reuse-db no mejora (sigue 40s)
- Causa: Django 5.x usa SQLite en memoria por defecto
- Fix: Quitar --reuse-db y --no-migrations. Anadir MD5PasswordHasher

### Error 7: NameError: name default is not defined en Firma.__str__
- Causa: Sintaxis de template Django (|default:) en Python
- Fix: self.usuario.get_full_name() or self.usuario.username

### Error 8: bound method != Juan Perez
- Causa: Olvidar parentesis en metodos
- Fix: get_full_name() con parentesis

### Error 9: ValidationError no es un UUID valido en verificar_codigo
- Causa: No capturar ValidationError
- Fix: except (Certificado.DoesNotExist, ValidationError, ValueError)

### Error 10: El nombre de archivo no son correctos
- Causa: CMD no maneja comillas dobles anidadas
- Fix: Usar PowerShell con here-strings

### Error 11: ModuleNotFoundError: No module named certificaciones
- Causa: python.exe -c sin DJANGO_SETTINGS_MODULE
- Fix: Usar manage.py shell -c

---

## Testing - Guia Completa

### pytest.ini

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*

norecursedirs =
    .git
    .tox
    .venv
    venv
    env
    __pycache__
    static
    media
    node_modules
    *.egg
    migrations
    contenido
    docs
    .pytest_cache

addopts = -v --tb=short
```

### conftest.py

```python
import pytest

@pytest.fixture(autouse=True)
def use_fast_password_hasher(settings):
    settings.PASSWORD_HASHERS = [django.contrib.auth.hashers.MD5PasswordHasher]

@pytest.fixture(autouse=True)
def disable_password_validation(settings):
    settings.AUTH_PASSWORD_VALIDATORS = []
```

---

## Optimizacion (24x mas rapido)

| Config | 120 tests |
|--------|-----------|
| PBKDF2 + archivo + reuse-db | 353s |
| MD5 + memoria | 14.52s |

**3 cambios:**
1. BD memoria (quitar TEST.NAME en settings.py)
2. MD5PasswordHasher en conftest.py
3. norecursedirs en pytest.ini

---

## Reglas del Proyecto

- NUNCA -replace con regex en HTML/templates
- Usar [System.IO.File]::WriteAllText con here-strings
- NUNCA |default: en Python (solo templates)
- SIEMPRE () en metodos: get_full_name()
- Al filtrar por UUIDField, capturar ValidationError
- Un solo {% block %} por template hijo

---

## Editor WYSIWYG TinyMCE

- Ubicacion: profesor/templates/profesor/leccion_form.html y modulo_form.html
- Regla: script dentro de {% block contenido %}, antes del {% endblock %}
- Vista estudiante: usar {{ leccion.contenido|safe }}

---

## Git

### Commits importantes

| Hash | Descripcion |
|------|-------------|
| ecd211b | feat: CRUD profesor + dashboard |
| 6dd1ba8 | test: 10 accounts + pytest.ini |
| 7cc798d | test(academia): 29 tests |
| f344364 | test(profesor): 38 tests |
| 3932c00 | perf(test): 24x mas rapido |
| efa888a | test(certificaciones): 39 tests |

---

**Ultima actualizacion:** Octubre 2026

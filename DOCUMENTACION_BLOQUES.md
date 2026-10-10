# EduNet Academia - Documentacion por Bloques

**LMS de Lengua Castellana** - Django 5.2.11 + Python 3.12.4

**Repositorio:** https://github.com/Hernank10/edunet-lms-2026

---

## Estado del Proyecto

### Tests implementados

| App | Tests | Estado |
|-----|-------|--------|
| accounts | 10 | OK |
| academia | 29 | OK |
| profesor | 38 | OK |
| gamificacion | 43 | OK |
| certificaciones | 39 | OK |
| api | 22 | OK |
| **Total** | **181** | **OK ~16s** |

### Commits importantes

| Hash | Descripcion |
|------|-------------|
| ecd211b | feat: CRUD profesor + dashboard |
| 6dd1ba8 | test: 10 tests accounts + pytest.ini |
| 7cc798d | test(academia): 29 tests |
| f344364 | test(profesor): 38 tests |
| 3932c00 | perf(test): 24x mas rapido |
| efa888a | test(certificaciones): 39 tests + fixes |
| d1aa4a0 | docs: documentacion tecnica |
| f563757 | feat(api): API REST con DRF |
| 736dac2 | ci: GitHub Actions + README |

---

## Bloques Completados

### Bloque A - CRUD Profesor + Modulos + Dashboard + Analiticas

Entregables:
- CRUD completo de cursos (crear, editar, toggle)
- CRUD de lecciones, evaluaciones, preguntas, anuncios
- Modelo Modulo (crear N lecciones de golpe)
- Dashboard estudiante con 4 graficos Chart.js
- Analiticas profesor con 4 graficos Chart.js
- 20 templates nuevos

Archivos clave:
- profesor/forms.py - 6 formularios
- profesor/views.py - 23 vistas
- profesor/urls.py - 24 rutas
- academia/models.py - modelo Modulo

Estado: Pusheado (commit ecd211b)

---

### Bloque B1 - Tests de profesor (38)

Tests:
- ProfesorAccessTests (6)
- CursoCRUDTests (9)
- ModuloCRUDTests (6)
- LeccionCRUDTests (6)
- AnuncioCRUDTests (5)
- PermisosProfesorTests (5)

Archivos: profesor/tests.py
Estado: Pusheado (commit f344364)

---

### Bloque B2 - Tests de gamificacion (43)

Tests:
- InsigniaModelTests (5)
- PerfilGamificacionTests (5)
- LogroModelTests (3)
- VistasRequierenLoginTests (6)
- DashboardEstudianteTests (8)
- MisCursosTests (3)
- PracticasTests (1)
- EvaluacionesTests (1)
- MisLogrosTests (3)
- EstadisticasTests (2)
- MisCertificadosTests (1)
- MiPerfilTests (2)
- RecomendadosTests (3)

Estado: Pusheado

---

### Bloque B3 - Tests de certificaciones (39)

Tests:
- RequisitoCertificadoModelTests (4)
- FirmaModelTests (4)
- CertificadoModelTests (10)
- MisCertificadosViewTests (5)
- VerCertificadoViewTests (4)
- VerificarCodigoViewTests (6)
- DescargarWordTests (3)

Fixes aplicados:
1. Firma.__str__ - sintaxis template en Python
2. Certificado.nombre_* - metodos sin parentesis
3. verificar_codigo - capturar ValidationError + codigo corto

Estado: Pusheado (commit efa888a)

---
## Bloques Completados (continuacion)

### Bloque B4 - API REST con DRF

Entregables:
- rest_framework + authtoken + drf_spectacular en INSTALLED_APPS
- REST_FRAMEWORK configurado (Token + Session + paginacion)
- SPECTACULAR_SETTINGS para Swagger
- URLs: api/auth/, api/schema/, api/docs/
- App api/ con serializers, viewsets, urls
- 18 endpoints REST
- Swagger UI interactivo

Serializers (8): Nivel, CursoList, CursoDetail, Modulo, LeccionList, LeccionDetail, Inscripcion, InscripcionCreate, Certificado, PerfilGamificacion

ViewSets (6): Curso, Modulo, Leccion, Inscripcion, Certificado, Perfil

Endpoints (18):
- POST /api/auth/
- GET /api/cursos/
- GET /api/cursos/{id}/
- GET /api/cursos/{id}/modulos/
- GET /api/cursos/{id}/lecciones/
- GET /api/modulos/
- GET /api/modulos/{id}/
- GET /api/modulos/{id}/lecciones/
- GET /api/lecciones/
- GET /api/lecciones/{id}/
- GET /api/inscripciones/
- POST /api/inscripciones/
- GET /api/certificados/
- GET /api/perfil/

Tests (22): AuthToken (3), Cursos (4), Modulos (3), Lecciones (2), Inscripciones (5), Certificados (3), Perfil (2)

Estado: Pusheado (commit f563757)

---

### Bloque B5 - Editor WYSIWYG TinyMCE

Entregables:
- TinyMCE 6.8.3 desde CDN
- Aplicado a leccion_form.html
- Aplicado a modulo_form.html
- Barra completa: negrita, cursiva, listas, enlaces, tablas
- Guardado automatico al textarea
- Contenido con |safe en vista estudiante

Estado: Pusheado

---

### Bloque B6 - Optimizacion pytest (24x)

Diagnostico:
- create_user con PBKDF2 tardaba 6s por test
- BD archivo mas lenta que memoria
- 3 minutos en collecting

Cambios:
1. BD test en memoria (sin TEST.NAME)
2. MD5PasswordHasher en conftest.py
3. norecursedirs en pytest.ini

Resultado:
- Antes: 353s (5:53)
- Despues: 14.52s
- Mejora: 24x

Estado: Pusheado (commit 3932c00)

---

### Bloque B9 - CI/CD con GitHub Actions

Entregables:
- .github/workflows/tests.yml
- Python 3.12 en Ubuntu
- Instala Django, DRF, drf-spectacular, pytest
- Corre pytest -q
- README con badge

Permisos del PAT: repo + workflow

Estado: Pusheado (commit 736dac2)

---

### Bloque B-Doc - Documentacion

Entregables:
- DOCUMENTACION_TECNICA.md (179 lineas)
- README.md con badge
- 14 errores documentados

Estado: Pusheado

---

### Bloque B-HTML - 429 HTMLs versionados

Entregables:
- 429 archivos HTML (23.98 MB)
- Tecnicas de Lengua Castellana
- Categorias: docencia, morfologia, sintaxis, etc.

Estado: Pusheado (commit d58267b)

---

### Bloque B-Fix - Fix de mojibake

Entregables:
- fix_emojis.py con 30 reglas
- Correcciones en contenido/ y profesor/

Estado: Pusheado

---

## Bloques Pendientes

### B5b - Subida de imagenes en TinyMCE
- Endpoint /profesor/subir-imagen/
- Guardar en media/lecciones/
- Configurar images_upload_url
- Complejidad: Baja

### B7 - Tests de contenido, ejercicios, progreso
- contenido/tests.py
- ejercicios/tests.py
- progreso/tests.py
- Tests: ~40-50
- Complejidad: Media

### B10 - Fix mojibake en otros templates
- Complejidad: Baja

### B11 - Coleccion Postman/Insomnia
- Descargar OpenAPI schema
- Importar en Postman
- Guardar como docs/postman_collection.json
- Complejidad: Baja

### B12 - Despliegue a produccion
- DEBUG=False, ALLOWED_HOSTS, SECRET_KEY
- PostgreSQL
- Gunicorn + Nginx
- collectstatic + WhiteNoise
- HTTPS con Lets Encrypt
- Complejidad: Alta

---

## Entorno de Desarrollo

- Python: E:\PythonPortable_Django5\python.exe
- Version: 3.12.4
- Django: 5.2.11
- DRF: 3.14.0
- pytest: 9.1.1 + pytest-django 4.14.0

### Comandos esenciales

```cmd
cd /d "E:\02_proyectos\edunet_academia"
E:\PythonPortable_Django5\python.exe manage.py runserver 8011 --noreload
E:\PythonPortable_Django5\python.exe manage.py check
E:\PythonPortable_Django5\python.exe manage.py migrate
E:\PythonPortable_Django5\python.exe -m pytest -q
E:\PythonPortable_Django5\python.exe -m pytest accounts/ -v
```

---

## Errores y Fixes

### Error 1: Found 0 test(s)
- Causa: tests.py vacio
- Fix: Escribir tests con TestCase

### Error 2: TemplateSyntaxError Unclosed tag block
- Causa: block extra_js anidado en block contenido
- Fix: Poner script dentro de contenido

### Error 3: Archivos HTML rotos con < faltantes
- Causa: -replace con regex de PowerShell
- Fix: Restaurar desde Git, NUNCA usar -replace para HTML

### Error 4: 404 != 200 en test_get_registro_devuelve_200
- Causa: LANGUAGE_CODE es-co no esta en LANGUAGES
- Fix: translation.activate(es) en setUp

### Error 5: pytest tarda 3+ min en collecting
- Causa: Sin norecursedirs
- Fix: Anadir norecursedirs en pytest.ini

### Error 6: --reuse-db no mejora
- Causa: Django 5.x usa SQLite en memoria
- Fix: Quitar --reuse-db, anadir MD5PasswordHasher

### Error 7: NameError name default no defined
- Causa: Sintaxis template Django en Python
- Fix: get_full_name() or username

### Error 8: bound method != Juan Perez
- Causa: Olvidar parentesis
- Fix: get_full_name() con parentesis

### Error 9: ValidationError no es un UUID valido
- Causa: No capturar ValidationError
- Fix: except (DoesNotExist, ValidationError, ValueError)

### Error 10: El nombre de archivo no son correctos
- Causa: CMD no maneja comillas dobles
- Fix: Usar PowerShell con here-strings

### Error 11: ModuleNotFoundError certificaciones
- Causa: python.exe -c sin DJANGO_SETTINGS_MODULE
- Fix: Usar manage.py shell -c

### Error 12: ImportError cannot import name _get_perfil
- Causa: _get_perfil esta en views.py, no en models.py
- Fix: from gamificacion.views import _get_perfil

### Error 13: UnorderedObjectListWarning en DRF
- Causa: Paginacion sin order_by
- Fix: Anadir .order_by(campo) a ViewSets

### Error 14: refusing to allow PAT to create workflow
- Causa: PAT sin scope workflow
- Fix: Regenerar PAT con scope workflow + repo

---

## Reglas del Proyecto

### Edicion de archivos
- NUNCA -replace con regex en HTML/templates
- Usar WriteAllText con here-strings
- Para .py, usar scripts Python con pathlib

### Templates Django
- Un solo block contenido por archivo hijo
- NO anidar blocks
- Verificar balance blocks == endblocks

### Codigo Python
- NUNCA |default: en Python
- SIEMPRE () en metodos
- Capturar ValidationError en UUIDField
- ViewSets DRF con order_by

### Testing
- MD5PasswordHasher en conftest.py
- BD en memoria (sin TEST.NAME)
- norecursedirs en pytest.ini
- translation.activate(es) en setUp

### Git y GitHub
- Ignorar db.sqlite3, test_db.sqlite3, .pytest_cache
- Commits atomicos por bloque
- Mensajes: feat, fix, test, chore, docs, perf, ci
- PAT con scope workflow + repo

### Seguridad
- NUNCA pegar tokens en el chat
- Guardar en Bitwarden/1Password
- Revocar tokens expuestos inmediatamente
- No commitear .env

---

## Recursos

- Django: https://docs.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- pytest-django: https://pytest-django.readthedocs.io/
- TinyMCE: https://www.tiny.cloud/docs/tinymce/6/
- Chart.js: https://www.chartjs.org/
- drf-spectacular: https://drf-spectacular.readthedocs.io/

---

**Fin del documento**

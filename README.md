# EduNet Academia

LMS de Lengua Castellana - Django 5.2.11 + Python 3.12.4

[![Tests](https://github.com/Hernank10/edunet-lms-2026/actions/workflows/tests.yml/badge.svg)](https://github.com/Hernank10/edunet-lms-2026/actions/workflows/tests.yml)

## Descripcion

Plataforma de aprendizaje (LMS) orientada a la preparacion para el concurso docente en Lengua Castellana en Colombia y la prueba Saber Pro.

## Caracteristicas

- **Profesores:** CRUD completo de cursos, modulos, lecciones, evaluaciones, preguntas y anuncios
- **Estudiantes:** Dashboard con graficos, gamificacion (XP, insignias, logros), certificados
- **Editor WYSIWYG** (TinyMCE) para contenido de lecciones
- **API REST** con token auth para app movil (Swagger en /api/docs/)
- **Certificados** con exportacion a Word (.docx) y verificacion publica por codigo
- **429 HTMLs interactivos** con tecnicas de Lengua Castellana

## Stack

- Django 5.2.11
- Django REST Framework 3.14
- drf-spectacular (Swagger/OpenAPI 3)
- SQLite (desarrollo) / PostgreSQL (produccion)
- TinyMCE 6 (editor WYSIWYG)
- Chart.js (graficos)
- Bootstrap 5

## Desarrollo

```bash
# Instalar dependencias
pip install django==5.2.11 djangorestframework==3.14.0 drf-spectacular
pip install pytest pytest-django pytest-cov pytest-xdist

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr servidor
python manage.py runserver 8011

# Correr tests
pytest -q
```

## Tests

- **181 tests** cubriendo 6 apps (accounts, academia, profesor, gamificacion, certificaciones, api)
- Corren en ~16 segundos
- CI/CD con GitHub Actions (cada push)

## API REST

Documentacion interactiva en /api/docs/ (Swagger UI).

Endpoints principales:

- POST /api/auth/ - Login (obtener token)
- GET /api/cursos/ - Listar cursos
- GET /api/cursos/{id}/modulos/ - Modulos del curso
- GET /api/lecciones/{id}/ - Detalle de leccion (con HTML)
- GET /api/inscripciones/ - Mis inscripciones
- POST /api/inscripciones/ - Inscribirse en un curso
- GET /api/certificados/ - Mis certificados
- GET /api/perfil/ - Mi perfil de gamificacion

## Licencia

Privado - Todos los derechos reservados.

🎓 Edunet Academia

Plataforma educativa para la enseñanza de lenguas con progreso pedagógico automático

🌍 Descripción general

Edunet Academia es una plataforma educativa desarrollada en Django cuyo objetivo es facilitar el aprendizaje estructurado de la lengua castellana y la escritura académica, con especial atención a hablantes de las lenguas más habladas del mundo.

El proyecto combina:

Pedagogía progresiva

Tecnología web moderna

Evaluación formativa

Seguimiento automático del progreso del estudiante

Está diseñada para contextos educativos reales, investigación pedagógica y expansión internacional.

🧠 Enfoque pedagógico

La plataforma se basa en un modelo de aprendizaje guiado:

El estudiante se inscribe en un curso

Accede a lecciones secuenciales

Responde ejercicios integrados

El sistema valida respuestas

Se registra el progreso

Se desbloquean nuevas lecciones automáticamente

Este enfoque fomenta:

Autonomía

Aprendizaje significativo

Evaluación continua

Motivación intrínseca

🏗️ Arquitectura del proyecto

El proyecto sigue una arquitectura modular por apps:

edunet_project/
├── academia/          # Cursos, niveles, lecciones
├── ejercicios/        # Ejercicios y evaluaciones
├── progreso/          # Seguimiento pedagógico
├── accounts/          # Usuarios y roles
├── analytics/         # Métricas educativas
├── certificaciones/   # Certificados académicos
├── practice/          # Práctica guiada
├── templates/         # Plantillas base
├── config/            # Configuración del proyecto
└── manage.py

⚙️ Tecnologías utilizadas

Python 3.11+

Django 5/6

SQLite (desarrollo)

Bootstrap 5

HTML5 / CSS3

Git + GitHub

Preparado para:

PostgreSQL

Docker

Despliegue en la nube

👥 Roles del sistema

👨‍🎓 Estudiante: consume contenido y progresa

👩‍�� Docente: crea cursos, lecciones y ejercicios

🛠 Administrador: gestiona la plataforma

🚀 Instalación local
git clone https://github.com/USUARIO/edunet-academia.git
cd edunet-academia
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


Accede en:
👉 http://127.0.0.1:8000/

🧪 Estado del proyecto

🟡 En desarrollo activo
✔ Dashboard funcional
✔ Administración completa
🚧 Progreso automático en implementación

📚 Uso educativo y académico

Este proyecto puede utilizarse para:

Instituciones educativas

Investigación en didáctica de lenguas

Plataformas de e-learning

Formación docente

Educación intercultural

📜 Licencia

Este proyecto está licenciado bajo la MIT License.
El contenido educativo puede adaptarse a Creative Commons según el uso.

🤝 Contribuciones

Las contribuciones son bienvenidas:

Fork del proyecto

Crear rama (feature/nueva-funcionalidad)

Commit claro

Pull Request documentado

✨ Visión futura

Soporte multilingüe (i18n)

Inteligencia pedagógica adaptativa

Evaluación automática avanzada

Certificación verificable

Integración con IA educativa

👤 Autor

Hernán Acevedo Mar
Proyecto educativo y tecnológico para la democratización del aprendizaje lingüístico.

❤️ Filosofía

Aprender una lengua no es memorizar reglas,
es construir pensamiento, identidad y diálogo.

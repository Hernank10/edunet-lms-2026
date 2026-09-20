from django.db import models
from django.utils.text import slugify


class Idioma(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text="Lengua materna del estudiante (ej. Árabe, Coreano, Inglés)"
    )

    def __str__(self):
        return self.nombre


class Nivel(models.Model):
    codigo = models.CharField(
        max_length=2,
        unique=True,
        help_text="Nivel MCER: A1, A2, B1, B2, C1, C2"
    )
    descripcion = models.TextField()

    orden = models.PositiveSmallIntegerField(
        help_text="Orden pedagógico del nivel"
    )

    def __str__(self):
        return self.codigo

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    nivel = models.ForeignKey(
        Nivel,
        on_delete=models.CASCADE,
        related_name="cursos"
    )

    descripcion = models.TextField(blank=True)

    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo

class Leccion(models.Model):
    curso  = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="lecciones"
    )

    titulo = models.CharField(max_length=200)

    slug = models.SlugField(blank=True)

    orden = models.PositiveSmallIntegerField(
        help_text="Orden pedagógico dentro del curso"
    )

    contenido = models.TextField(
        help_text="Contenido principal de la lección"
    )

    activa = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["orden"]
        unique_together = ("curso", "orden")

    def __str__(self):
        return f"{self.curso} · {self.titulo}"


from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Lesson(models.Model):
    curso  = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Exercise(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="exercises"
    )
    question = models.TextField()
    options = models.JSONField()  # PostgreSQL JSONB
    correct_answer = models.CharField(max_length=200)

    def __str__(self):
        return self.question[:50]


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "lesson")



class Inscripcion(models.Model):
    """Inscripción de un usuario a un curso."""
    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="inscripciones"
    )
    fecha = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    completado = models.BooleanField(default=False)
    progreso_pct = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("usuario", "curso")
        ordering = ["-fecha"]
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"

    def __str__(self):
        return f"{self.usuario.username} → {self.curso.titulo[:50]}"

    def actualizar_progreso(self):
        """Recalcula el progreso del estudiante en este curso."""
        from progreso.models import ProgresoLeccion

        total = self.curso.lecciones.count()
        if total == 0:
            self.progreso_pct = 0
            self.save()
            return

        completadas = ProgresoLeccion.objects.filter(
            usuario=self.usuario,
            leccion__curso=self.curso,
            completada=True
        ).count()

        self.progreso_pct = int((completadas / total) * 100)
        self.completado = self.progreso_pct >= 100
        self.save()
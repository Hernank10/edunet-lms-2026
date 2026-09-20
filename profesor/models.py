from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class AsignacionProfesor(models.Model):
    """Asigna un profesor a un curso."""
    profesor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cursos_asignados",
        limit_choices_to={"is_staff": True}
    )
    curso = models.ForeignKey(
        "academia.Curso",
        on_delete=models.CASCADE,
        related_name="profesores"
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profesor", "curso")
        verbose_name = "Asignación de profesor"
        verbose_name_plural = "Asignaciones de profesores"
        ordering = ["-fecha_asignacion"]

    def __str__(self):
        return f"{self.profesor.username} → {self.curso.titulo[:50]}"


class AnuncioCurso(models.Model):
    """Anuncio que un profesor publica en su curso."""
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)
    curso = models.ForeignKey("academia.Curso", on_delete=models.CASCADE, related_name="anuncios")
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.titulo} ({self.curso.titulo[:30]})"


class NotaProfesor(models.Model):
    """Nota privada del profesor sobre un estudiante."""
    profesor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notas_creadas")
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notas_recibidas")
    curso = models.ForeignKey("academia.Curso", on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.profesor.username} → {self.estudiante.username}"

from django.db import models
from academia.models import Leccion


class Ejercicio(models.Model):
    TIPOS = (
        ("opcion_multiple", "Opción múltiple"),
        ("completar", "Completar"),
        ("vf", "Verdadero / Falso"),
        ("ordenar", "Ordenar"),
        ("relacionar", "Relacionar"),
    )

    leccion = models.ForeignKey(
        Leccion,
        related_name="ejercicios",
        on_delete=models.CASCADE
    )

    tipo = models.CharField(max_length=30, choices=TIPOS)
    enunciado = models.TextField()

    datos = models.JSONField(
        help_text="Configuración dinámica del ejercicio"
    )

    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.leccion} — {self.tipo}"




class Evaluacion(models.Model):
    """Evaluación final de un curso (quiz con puntuación)."""
    curso = models.ForeignKey(
        "academia.Curso",
        on_delete=models.CASCADE,
        related_name="evaluaciones"
    )
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField(blank=True)
    num_preguntas = models.PositiveIntegerField(default=10)
    nota_minima = models.PositiveIntegerField(default=70)
    orden = models.PositiveIntegerField(default=1)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["curso", "orden"]
        verbose_name = "Evaluación"
        verbose_name_plural = "Evaluaciones"

    def __str__(self):
        return f"{self.titulo}"


class PreguntaEvaluacion(models.Model):
    """Una pregunta de una evaluación."""
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="preguntas"
    )
    orden = models.PositiveIntegerField(default=1)
    enunciado = models.TextField()
    opciones = models.JSONField(
        default=list,
        help_text="Lista de opciones: ['A', 'B', 'C', 'D']"
    )
    respuesta_correcta = models.CharField(max_length=500)
    explicacion = models.TextField(blank=True)

    class Meta:
        ordering = ["evaluacion", "orden"]
        unique_together = ("evaluacion", "orden")

    def __str__(self):
        return f"P{self.orden}: {self.enunciado[:60]}"


class IntentoEvaluacion(models.Model):
    """Un intento de evaluación por parte de un usuario."""
    usuario = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="intentos_evaluacion"
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        related_name="intentos"
    )
    nota = models.PositiveIntegerField(default=0)
    aprobado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Intento de evaluación"
        verbose_name_plural = "Intentos de evaluación"

    def __str__(self):
        return f"{self.usuario} — {self.evaluacion} — {self.nota}%"

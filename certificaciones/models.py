import uuid
from django.conf import settings
from django.db import models
from academia.models import Curso

User = settings.AUTH_USER_MODEL


class RequisitoCertificado(models.Model):
    """Requisitos para obtener el certificado de un curso."""

    curso = models.OneToOneField(
        Curso,
        on_delete=models.CASCADE,
        related_name="requisito_certificado"
    )
    lecciones_minimas_pct = models.PositiveIntegerField(
        default=100,
        help_text="% mínimo de lecciones completadas (0-100)"
    )
    nota_minima = models.PositiveIntegerField(
        default=70,
        help_text="Nota mínima (0-100)"
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Requisitos: {self.curso.titulo}"

    class Meta:
        verbose_name = "Requisito de certificado"
        verbose_name_plural = "Requisitos de certificados"


class Certificado(models.Model):
    """Certificado emitido a un estudiante al completar un curso."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name="certificados"
    )
    codigo = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text="Código único de verificación"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    nota_final = models.PositiveIntegerField(
        default=100,
        help_text="Nota final del curso (0-100)"
    )
    horas = models.PositiveIntegerField(
        default=40,
        help_text="Horas lectivas del curso"
    )
    pdf = models.FileField(
        upload_to="certificados/",
        blank=True,
        null=True,
        help_text="PDF del certificado (opcional)"
    )

    class Meta:
        unique_together = ("usuario", "curso")
        ordering = ["-fecha_emision"]
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def __str__(self):
        return f"{self.usuario.username} — {self.curso.titulo}"

    @property
    def codigo_corto(self):
        return str(self.codigo)[:8].upper()

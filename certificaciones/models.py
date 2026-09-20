import uuid
from django.conf import settings
from django.db import models
from academia.models import Curso

User = settings.AUTH_USER_MODEL


class RequisitoCertificado(models.Model):
    """Requisitos para obtener el certificado de un curso."""
    curso = models.OneToOneField(
        Curso, on_delete=models.CASCADE, related_name="requisito_certificado"
    )
    lecciones_minimas_pct = models.PositiveIntegerField(default=100)
    nota_minima = models.PositiveIntegerField(default=70)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Requisitos: {self.curso.titulo}"

    class Meta:
        verbose_name = "Requisito de certificado"
        verbose_name_plural = "Requisitos de certificados"


class Firma(models.Model):
    """Firma de un administrador o profesor para certificados."""
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="firma_certificado"
    )
    cargo = models.CharField(
        max_length=100,
        default="Profesor",
        help_text="Cargo que aparece bajo la firma (ej. Director, Profesor Titular)"
    )
    institucion = models.CharField(
        max_length=200,
        default="Academia Global de Castellano"
    )
    firma_imagen = models.CharField(
        max_length=500,
        blank=True,
        help_text="Ruta al archivo de imagen de la firma (opcional)"
    )
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmas"

    def __str__(self):
        return f"{self.usuario.get_full_name|default:self.usuario.username} ({self.cargo})"


class Certificado(models.Model):
    """Certificado emitido a un estudiante al completar un curso."""
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="certificados"
    )
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, related_name="certificados"
    )
    codigo = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    nota_final = models.PositiveIntegerField(default=100)
    horas = models.PositiveIntegerField(default=40)

    # Firmas
    firmado_por_admin = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificados_firmados_admin",
        help_text="Administrador que firma el certificado"
    )
    firmado_por_profesor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificados_firmados_profesor",
        help_text="Profesor que firma el certificado"
    )

    # Cargo e institución congelados al momento de emisión
    cargo_admin = models.CharField(max_length=100, blank=True, default="Director General")
    cargo_profesor = models.CharField(max_length=100, blank=True, default="Profesor Titular")
    institucion = models.CharField(max_length=200, default="Academia Global de Castellano")

    pdf = models.FileField(upload_to="certificados/", blank=True, null=True)

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

    @property
    def nombre_estudiante(self):
        return self.usuario.get_full_name or self.usuario.username

    @property
    def nombre_admin(self):
        if self.firmado_por_admin:
            return self.firmado_por_admin.get_full_name or self.firmado_por_admin.username
        return "Administración"

    @property
    def nombre_profesor(self):
        if self.firmado_por_profesor:
            return self.firmado_por_profesor.get_full_name or self.firmado_por_profesor.username
        return "Profesor Asignado"

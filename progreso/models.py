from django.conf import settings
from django.db import models
from academia.models import Leccion

User = settings.AUTH_USER_MODEL


class ProgresoLeccion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    leccion = models.ForeignKey(Leccion, on_delete=models.CASCADE)

    completada = models.BooleanField(default=False)
    fecha_completada = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("usuario", "leccion")

    def __str__(self):
        estado = "✔" if self.completada else "⏳"
        return f"{self.usuario} · {self.leccion} {estado}"


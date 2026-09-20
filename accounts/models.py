from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Usuario personalizado para la Academia Global de Castellano
    """
    idioma_nativo = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lengua materna del estudiante"
    )

    zona_horaria = models.CharField(
        max_length=50,
        default="UTC",
        help_text="Zona horaria del usuario"
    )

    def __str__(self):
        return self.username


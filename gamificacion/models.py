from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Insignia(models.Model):
    TIPOS = (
        ("estrella", "⭐ Estrella"),
        ("medalla", "🏅 Medalla"),
        ("libro", "📚 Libro"),
        ("trofeo", "🏆 Trofeo"),
        ("corona", "👑 Corona"),
    )
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField()
    icono = models.CharField(max_length=10, default="🏅")
    tipo = models.CharField(max_length=20, choices=TIPOS, default="medalla")
    requisito_xp = models.PositiveIntegerField(default=0)
    requisito_cursos = models.PositiveIntegerField(default=0)
    requisito_lecciones = models.PositiveIntegerField(default=0)
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.icono} {self.nombre}"


class PerfilGamificacion(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil_gam")
    xp_total = models.PositiveIntegerField(default=0)
    nivel_actual = models.PositiveIntegerField(default=1)
    racha_dias = models.PositiveIntegerField(default=0)
    cursos_completados = models.PositiveIntegerField(default=0)
    lecciones_completadas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.usuario} — Nivel {self.nivel_actual} — {self.xp_total} XP"

    def add_xp(self, cantidad):
        self.xp_total += cantidad
        self.nivel_actual = max(1, self.xp_total // 500 + 1)
        self.save()


class Logro(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logros")
    insignia = models.ForeignKey(Insignia, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("usuario", "insignia")

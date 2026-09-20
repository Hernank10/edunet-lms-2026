from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Recurso(models.Model):
    """Un JSON de técnicas importado."""

    CATEGORIAS = (
        ("retorica", "Retórica"),
        ("fonetica_fonologia", "Fonética y Fonología"),
        ("morfologia", "Morfología"),
        ("sintaxis", "Sintaxis"),
        ("semantica", "Semántica"),
        ("linguistica", "Lingüística"),
        ("ortografia", "Ortografía"),
        ("redaccion", "Redacción"),
        ("literatura", "Literatura"),
        ("idiomas", "Idiomas"),
        ("docencia", "Docencia"),
        ("historia_lengua", "Historia de la lengua"),
        ("otros", "Otros"),
    )

    NIVELES = (
        ("primaria", "Primaria"),
        ("bachillerato", "Bachillerato"),
        ("universitario", "Universitario"),
        ("concurso", "Concurso docente"),
        ("general", "General"),
    )

    titulo = models.CharField(max_length=300)
    subtitulo = models.CharField(max_length=300, blank=True)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS, default="otros")
    nivel = models.CharField(max_length=20, choices=NIVELES, default="general")
    tipo_estructura = models.CharField(
        max_length=30,
        help_text="dict_con_tecnicas, lista_plana, lista_bilingue"
    )
    total_declarado = models.PositiveIntegerField(default=0)
    total_real = models.PositiveIntegerField(default=0)
    bilingue = models.BooleanField(default=False)
    archivo_origen = models.CharField(max_length=500, blank=True)
    fecha_importacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["categoria", "titulo"]
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"

    def __str__(self):
        return f"[{self.categoria}] {self.titulo[:60]}"


class Tecnica(models.Model):
    """Una técnica individual dentro de un recurso."""
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name="tecnicas")
    numero = models.PositiveIntegerField()
    nombre = models.CharField(max_length=300)
    categoria_interna = models.CharField(max_length=200, blank=True)

    teoria = models.TextField(blank=True)
    ejemplo = models.TextField(blank=True)
    ejercicio = models.TextField(blank=True)
    respuesta = models.TextField(blank=True)

    # Para formato bilingüe
    titulo_en = models.CharField(max_length=300, blank=True)
    teoria_en = models.TextField(blank=True)
    ejemplo_en = models.TextField(blank=True)

    class Meta:
        ordering = ["recurso", "numero"]
        unique_together = ("recurso", "numero")
        verbose_name = "Técnica"
        verbose_name_plural = "Técnicas"

    def __str__(self):
        return f"{self.numero}. {self.nombre[:60]}"


class ProgresoTecnica(models.Model):
    """Progreso de un usuario en una técnica."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progreso_tecnicas")
    tecnica = models.ForeignKey(Tecnica, on_delete=models.CASCADE)
    completada = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("usuario", "tecnica")

    def __str__(self):
        return f"{self.usuario} — {self.tecnica.numero}"



class HtmlInteractivo(models.Model):
    """Un HTML interactivo (flota, cuaderno, juego, app)."""

    TIPOS = (
        ("flota", "Flota"),
        ("cuaderno", "Cuaderno"),
        ("juego", "Juego"),
        ("archivo_vector", "Archivo de Vector"),
        ("app", "App interactiva"),
        ("cuaderno_ejercicios", "Cuaderno de ejercicios"),
        ("otro", "Otro"),
    )

    CATEGORIAS = Recurso.CATEGORIAS  # reutilizar
    NIVELES = Recurso.NIVELES

    titulo = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    categoria = models.CharField(max_length=30, choices=CATEGORIAS, default="otros")
    tipo = models.CharField(max_length=30, choices=TIPOS, default="otro")
    nivel = models.CharField(max_length=20, choices=NIVELES, default="general")
    num_tecnicas = models.PositiveIntegerField(default=0)
    archivo_original = models.CharField(max_length=500, blank=True)
    archivo_static = models.CharField(max_length=500, blank=True)
    descripcion = models.TextField(blank=True)
    fecha_importacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["categoria", "tipo", "titulo"]
        verbose_name = "HTML interactivo"
        verbose_name_plural = "HTMLs interactivos"

    def __str__(self):
        return f"[{self.tipo}] {self.titulo[:60]}"

    @property
    def url_static(self):
        """URL para servir el HTML."""
        return f"/static/{self.archivo_static}"

    @property
    def url_visor(self):
        """URL del visor interno."""
        return f"/html/{self.slug}/"

# -*- coding: utf-8 -*-
"""
Formularios CRUD para el panel del profesor.
"""
from django import forms
from academia.models import Curso, Leccion, Inscripcion
from ejercicios.models import Evaluacion, PreguntaEvaluacion
from .models import AnuncioCurso


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["titulo", "descripcion", "nivel", "activo"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titulo del curso"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Descripcion del curso"
            }),
            "nivel": forms.Select(attrs={"class": "form-select"}),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "titulo": "Titulo",
            "descripcion": "Descripcion",
            "nivel": "Nivel",
            "activo": "Curso activo",
        }


class LeccionForm(forms.ModelForm):
    class Meta:
        model = Leccion
        fields = ["titulo", "contenido", "orden", "activa"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titulo de la leccion"
            }),
            "contenido": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 8,
                "placeholder": "Contenido de la leccion (Markdown o HTML)"
            }),
            "orden": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ["titulo", "descripcion", "num_preguntas", "nota_minima", "orden", "activo"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titulo de la evaluacion"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripcion breve"
            }),
            "num_preguntas": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 100
            }),
            "nota_minima": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 100
            }),
            "orden": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PreguntaEvaluacionForm(forms.ModelForm):
    """
    Formulario para crear/editar preguntas.
    Las opciones se ingresan como texto (una por linea).
    """
    opciones_texto = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Una opcion por linea, ej:\nOpcion A\nOpcion B\nOpcion C\nOpcion D"
        }),
        required=True,
        label="Opciones (una por linea)",
        help_text="Ingresa cada opcion en una linea separada. Debe haber al menos 2 opciones."
    )

    class Meta:
        model = PreguntaEvaluacion
        fields = ["orden", "enunciado", "respuesta_correcta", "explicacion"]
        widgets = {
            "orden": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1
            }),
            "enunciado": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Escribe la pregunta aqui..."
            }),
            "respuesta_correcta": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Respuesta correcta (debe coincidir con una opcion)"
            }),
            "explicacion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Explicacion de por que es correcta (opcional)"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si es una edicion, precargar opciones_texto
        if self.instance and self.instance.pk and self.instance.opciones:
            opciones = self.instance.opciones
            if isinstance(opciones, list):
                self.fields["opciones_texto"].initial = "\n".join(str(o) for o in opciones)
            elif isinstance(opciones, dict):
                # Si es un dict {a: "texto", b: "texto2"}
                self.fields["opciones_texto"].initial = "\n".join(str(v) for v in opciones.values())

    def clean_opciones_texto(self):
        texto = self.cleaned_data["opciones_texto"]
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        if len(lineas) < 2:
            raise forms.ValidationError("Debe haber al menos 2 opciones.")
        return lineas

    def clean(self):
        cleaned = super().clean()
        opciones = cleaned.get("opciones_texto")
        respuesta = cleaned.get("respuesta_correcta")
        if opciones and respuesta:
            # La respuesta correcta debe ser una de las opciones (comparacion flexible)
            resp_norm = respuesta.strip().lower()
            opciones_norm = [str(o).strip().lower() for o in opciones]
            if resp_norm not in opciones_norm:
                # Si no coincide, asumimos que es la letra (a, b, c, d)
                letras = ["a", "b", "c", "d", "e", "f", "g", "h"]
                if resp_norm in letras[:len(opciones)]:
                    # Guardar como texto de la opcion
                    idx = letras.index(resp_norm)
                    cleaned["respuesta_correcta"] = str(opciones[idx])
                else:
                    raise forms.ValidationError(
                        "La respuesta correcta debe coincidir con una de las opciones (o ser una letra a-h)."
                    )
        return cleaned


class AnuncioForm(forms.ModelForm):
    class Meta:
        model = AnuncioCurso
        fields = ["titulo", "contenido", "activo"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Titulo del anuncio"
            }),
            "contenido": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Contenido del anuncio"
            }),
            "activo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

# ============================================================
# FORMULARIO DE MODULO (crea N lecciones de golpe)
# ============================================================
class ModuloForm(forms.Form):
    """
    Formulario para crear un modulo con N lecciones de golpe.
    El profesor escribe los titulos de las lecciones (uno por linea).
    """
    titulo = forms.CharField(
        max_length=200,
        label="Titulo del modulo",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Ej: Modulo 1: Morfologia"
        })
    )
    descripcion = forms.CharField(
        required=False,
        label="Descripcion del modulo",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
            "placeholder": "Descripcion breve (opcional)"
        })
    )
    orden = forms.IntegerField(
        required=False,
        min_value=1,
        initial=1,
        label="Orden del modulo",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": 1
        })
    )
    titulos_lecciones = forms.CharField(
        label="Titulos de las lecciones (una por linea)",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 12,
            "placeholder": "Escribe un titulo por linea, ej:\n" +
                           "Leccion 1: Sustantivos\n" +
                           "Leccion 2: Adjetivos\n" +
                           "Leccion 3: Verbos\n" +
                           "Leccion 4: Adverbios\n" +
                           "Leccion 5: Preposiciones\n" +
                           "Leccion 6: Conjunciones\n" +
                           "Leccion 7: Pronombres\n" +
                           "Leccion 8: Articulos\n" +
                           "Leccion 9: Interjecciones\n" +
                           "Leccion 10: Repaso"
        }),
        help_text="Cada linea sera una leccion. Puedes crear tantas como quieras (recomendado: 10)."
    )
    contenido_base = forms.CharField(
        required=False,
        label="Contenido base (opcional)",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Si lo rellenas, se copiara a TODAS las lecciones como contenido inicial. Luego puedes editarlas una por una."
        }),
        help_text="Se copiara a todas las lecciones. Dejalo vacio si quieres lecciones sin contenido."
    )

    def clean_titulos_lecciones(self):
        texto = self.cleaned_data["titulos_lecciones"]
        lineas = [l.strip() for l in texto.splitlines() if l.strip()]
        if len(lineas) < 1:
            raise forms.ValidationError("Debes ingresar al menos 1 titulo de leccion.")
        if len(lineas) > 50:
            raise forms.ValidationError("Maximo 50 lecciones por modulo.")
        return lineas
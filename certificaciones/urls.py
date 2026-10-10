from django.urls import path
from . import views, word_export

app_name = "certificaciones"

urlpatterns = [
    path("", views.mis_certificados, name="mis_certificados"),
    path("verificar/", views.verificar_codigo, name="verificar"),
    path("<uuid:codigo>/word/", word_export.descargar_word, name="descargar_word"),
    path("<uuid:codigo>/", views.ver_certificado, name="ver_certificado"),
]

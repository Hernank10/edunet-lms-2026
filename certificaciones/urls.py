from django.urls import path
from . import views

app_name = "certificaciones"

urlpatterns = [
    path("", views.mis_certificados, name="mis_certificados"),
    path("verificar/", views.verificar_codigo, name="verificar"),
    path("<uuid:codigo>/", views.ver_certificado, name="ver_certificado"),
]

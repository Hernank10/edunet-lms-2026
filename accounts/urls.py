from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("panel/", views.panel, name="panel"),
    path("registro/", views.registro, name="registro"),
    path("perfil/", views.perfil, name="perfil"),
]

from django.urls import path
from . import views

app_name = "contenido"

urlpatterns = [
    path("", views.hub, name="hub"),
    path("recursos/", views.lista_recursos, name="lista_recursos"),
    path("recursos/<int:pk>/", views.detalle_recurso, name="detalle_recurso"),
    path("tecnica/<int:pk>/", views.tecnica_detalle, name="tecnica"),
    path("html/", views.lista_htmls, name="lista_htmls"),
    path("html/<slug:slug>/", views.visor_html, name="visor_html"),
]
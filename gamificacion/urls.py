from django.urls import path
from . import views

app_name = "gamificacion"

urlpatterns = [
    path("", views.dashboard_estudiante, name="dashboard"),
    path("cursos/", views.mis_cursos, name="mis_cursos"),
    path("practicas/", views.practicas, name="practicas"),
    path("evaluaciones/", views.evaluaciones, name="evaluaciones"),
    path("logros/", views.mis_logros, name="mis_logros"),
    path("estadisticas/", views.estadisticas, name="estadisticas"),
    path("certificados/", views.mis_certificados, name="mis_certificados"),
    path("perfil/", views.mi_perfil, name="mi_perfil"),
    path("recomendados/", views.recomendados, name="recomendados"),
]

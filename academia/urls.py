from django.urls import path
from . import views

app_name = "academia"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("curso/<slug:slug>/", views.curso_detail, name="curso_detail"),
    path("curso/<int:curso_id>/lecciones/", views.course_lessons, name="course_lessons"),
    path("leccion/<int:pk>/", views.lesson_detail, name="lesson_detail"),
    path("leccion/slug/<slug:slug>/", views.leccion_detail, name="leccion_detail"),
]

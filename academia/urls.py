from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "curso/<int:curso_id>/lecciones/",
        views.course_lessons,
        name="course_lessons"
    ),

    path(
        "leccion/<int:pk>/",
        views.lesson_detail,
        name="lesson_detail"
    ),
]


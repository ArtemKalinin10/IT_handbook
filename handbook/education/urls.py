from django.urls import path
from . import views

app_name = "education"

urlpatterns = [
    path("courses/<slug:slug>/",
         views.course_detail,
         name="course_detail"
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/",
        views.lesson_detail,
        name="lesson_detail"
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/tasks/<slug:task_slug>/",
         views.task_detail,
         name="task_detail"
    ),
    path(
        "courses/<slug:course_slug>/lessons/<slug:lesson_slug>/tasks/<slug:task_slug>/submit/",
         views.send_submission,
         name="send_submission"
    )
]
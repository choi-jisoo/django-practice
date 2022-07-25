from django.urls import path
from . import views

app_name = "elections"
urlpatterns = [
    path("", views.index, name="home"),
    path("areas/<area>/", views.areas),
    path("areas/<area>/results", views.results),
    path("polls/<int:poll_pk>/", views.polls),
    path("candidates/<name>", views.candidates),
]

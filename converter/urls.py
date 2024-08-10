from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("oauth", views.oauth, name="oauth"),
    path("start", views.start, name="start"),
]
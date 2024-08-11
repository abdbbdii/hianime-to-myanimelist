from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("oauth", views.oauth, name="oauth"),
    path("get-hi", views.get_hi, name="get_hi"),
    path("prepare", views.prepare, name="prepare"),
    path("post-mal", views.post_mal, name="post_mal"),
]
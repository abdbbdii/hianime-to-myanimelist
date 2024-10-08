from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("oauth", views.oauth, name="oauth"),
    path("get-hi", views.get_hi, name="get_hi"),
    path("send-to-mal", views.send_to_mal, name="send_to_mal"),
    path("get_json_list", views.get_json_list, name="get_json_list"),
    path("delete_all_anime", views.delete_all_anime, name="delete_all_anime"),
]
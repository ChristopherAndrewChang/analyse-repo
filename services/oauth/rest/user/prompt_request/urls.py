from django.urls import path
from .views import ListView, DetailView


app_name = "prompt_request"


urlpatterns = [
    path(
        "",
        ListView.as_view(),
        name="list"),
    path(
        "<slug:subid>/",
        DetailView.as_view(),
        name="detail"),
]
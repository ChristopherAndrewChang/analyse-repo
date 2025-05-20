from django.urls import path
from .views import GenerateView, RetrieveView


app_name = "prompt"


urlpatterns = [
    path("request/", GenerateView.as_view(), name="request",),
    path("detail/<slug:subid>/", RetrieveView.as_view(), name="detail"),
]

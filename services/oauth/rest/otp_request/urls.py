from django.urls import path
from .views import GenerateView, VerifyView


app_name = "otp"


urlpatterns = [
    path("request/", GenerateView.as_view(), name="request",),
    path("verify/<slug:subid>/", VerifyView.as_view(), name="verify"),
]

from django.urls import path
from .views import EmailView, PhoneView


app_name = "enrollment"


urlpatterns = [
    path('email/', EmailView.as_view(), name='email'),
    path('phone/', PhoneView.as_view(), name='phone'),
]

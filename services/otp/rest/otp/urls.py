from django.urls import path
from .views import OtpView


app_name = "otp"


urlpatterns = [
    path('<slug:usage>/<slug:object_id>/', OtpView.as_view(), name='apply'),
]

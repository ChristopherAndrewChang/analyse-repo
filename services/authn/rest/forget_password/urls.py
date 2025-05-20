from django.urls import path
from .views import CreateView, ResetPasswordView


app_name = "forget_password"


urlpatterns = [
    path('', CreateView.as_view(), name='create'),
    path('<slug:subid>/', ResetPasswordView.as_view(), name='reset'),
]

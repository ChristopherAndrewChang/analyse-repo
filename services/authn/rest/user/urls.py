from django.urls import path
from .views import (
    CreateView,
    ChangePasswordView,
    ChangeEmailView,
    LoginMethodView,
    ProfileView,
)


app_name = "user"


urlpatterns = [
    path('change-password/',
         ChangePasswordView.as_view(), name='change-password'),
    path('change-email/',
         ChangeEmailView.as_view({"post": "create"}), name='change-email'),
    path('change-email/<slug:subid>/',
         ChangeEmailView.as_view({"post": "verify"}), name='change-email-verify'),
    path('login-methods/',
         LoginMethodView.as_view(), name='login-methods'),
    path('profile/',
         ProfileView.as_view(), name='profile'),
    path('<slug:subid>/',
         CreateView.as_view(), name='create'),
]

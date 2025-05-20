from django.urls import path
from .views import (
    LoginView,
    EmailLoginView,
    PhoneLoginView,
    PasskeyLoginView,
    TokenRefreshView,
    LogoutView,
)


app_name = "auth"

urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('login/email/', EmailLoginView.as_view(), name="login-email"),
    path('login/phone/', PhoneLoginView.as_view(), name="login-phone"),
    path('login/passkey/', PasskeyLoginView.as_view({
        "get": "challenge"
    }), name="login-passkey-challenge"),
    path('login/passkey/<slug:subid>/', PasskeyLoginView.as_view({
        "post": "verify"
    }), name="login-passkey"),
    path('refresh/', TokenRefreshView.as_view(), name="refresh"),
    path('logout/', LogoutView.as_view(), name="logout"),
]

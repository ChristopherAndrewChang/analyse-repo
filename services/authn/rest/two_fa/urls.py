from django.urls import path, include
from .views import (
    SummaryView,
    AuthenticatorView,
    ConfirmTOTPView,
    SecurityCodeView,
)


app_name = "2fa"


urlpatterns = [
    path('summary/', SummaryView.as_view(), name="summary"),
    path('authenticator/', include(([
        path('', AuthenticatorView.as_view(), name="generate"),
        path('<slug:subid>/', ConfirmTOTPView.as_view(), name="confirm"),
    ], "authenticator"))),
    path('security-code/', SecurityCodeView.as_view(), name="security_code"),
]

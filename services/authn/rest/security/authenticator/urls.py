from django.urls import path
from .views import (
    AuthenticatorViewSet,
)


app_name = "authenticator"

urlpatterns = [
    path('', AuthenticatorViewSet.as_view({
        "get": "generate",
        "delete": "disable",
    }), name="list"),
    path('<slug:subid>/', AuthenticatorViewSet.as_view({
        "put": "confirm",
    }), name="detail"),
]

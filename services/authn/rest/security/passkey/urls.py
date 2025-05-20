from django.urls import path, include
from .views import (
    RegistrationViewSet,
    PasskeyViewSet,
)


app_name = "passkey"


urlpatterns = [
    path('register/', include((
        [
            path(
                '',
                RegistrationViewSet.as_view({
                    "get": "challenge",
                }),
                name="challenge"),
            path(
                '<slug:subid>/',
                RegistrationViewSet.as_view({
                    "post": "verify",
                }),
                name="verify"),
        ],
        "registration"
    ))),
    path('', PasskeyViewSet.as_view({
        "get": "list"
    }), name="list"),
    path('<slug:subid>/', PasskeyViewSet.as_view({
        "delete": "destroy",
    }), name="detail")
]

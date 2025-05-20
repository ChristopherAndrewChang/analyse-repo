from django.urls import path, include
from .views import (
    SummaryViewSet,
    AuthenticatorViewSet,
    SecurityCodeViewSet,
    BackupCodeViewSet,
    EmailViewSet,
    MobileViewSet,
    PasskeyViewSet,
)


app_name = "multi_factor"


urlpatterns = [
    path(
        'summary/',
        SummaryViewSet.as_view({
            "get": "list",
        }),
        name="summary",
    ),
    path(
        'authenticator/',
        AuthenticatorViewSet.as_view({
            "post": "verify"
        }),
        name="authenticator",
    ),
    path(
        'security-code/',
        SecurityCodeViewSet.as_view({
            "post": "verify"
        }),
        name="security_code",
    ),
    path(
        'backup-code/',
        BackupCodeViewSet.as_view({
            "post": "verify"
        }),
        name="backup_code",
    ),
    path(
        'email/',
        EmailViewSet.as_view({
            "get": "challenge",
            "post": "verify"
        }),
        name="email",
    ),
    path(
        'mobile/', include(([
            path(
                '',
                MobileViewSet.as_view({
                    "post": "challenge",
                }),
                name="challenge",
            ),
            path(
                '<slug:subid>/',
                MobileViewSet.as_view({
                    "post": "verify"
                }),
                name="verify"
            )
        ], "mobile"))
    ),
    path(
        'passkey/', include(([
            path(
                '',
                PasskeyViewSet.as_view({
                    "get": "challenge",
                }),
                name="challenge"
            ),
            path(
                '<slug:subid>/',
                PasskeyViewSet.as_view({
                    "post": "verify"
                }),
                name="verify"
            ),
        ], "passkey"))
    ),
]

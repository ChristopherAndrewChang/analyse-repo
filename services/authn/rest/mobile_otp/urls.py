from django.urls import path
from .views import (
    MobileOtpViewSet,
)


app_name = "mobil_otp"


urlpatterns = [
    path(
        '',
        MobileOtpViewSet.as_view({
            "get": "list"
        }),
        name="list",
    ),
    path(
        '<slug:subid>/',
        MobileOtpViewSet.as_view({
            "post": "verify",
            "delete": "reject"
        }),
        name="detail",
    ),
]

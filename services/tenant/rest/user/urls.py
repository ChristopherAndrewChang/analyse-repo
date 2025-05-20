from django.urls import path
from .views import (
    UserViewSet,
)


app_name = "user"


urlpatterns = [
    path(
        '',
        UserViewSet.as_view({
            "get": "list"
        }),
        name="list"),
    path(
        '<slug:subid>/active-status/',
        UserViewSet.as_view({
            "post": "activate",
            "delete": "deactivate",
        }),
        name="active-status"
    ),
]

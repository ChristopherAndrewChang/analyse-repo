from django.urls import path
from .views import (
    RoleViewSet,
)


app_name = "role"


urlpatterns = [
    path(
        '',
        RoleViewSet.as_view({
            "get": "list",
            "post": "create",
        }),
        name="list"),
    path(
        '<slug:subid>/',
        RoleViewSet.as_view({
            "get": "retrieve",
            "put": "update",
        }),
        name="detail"),
]

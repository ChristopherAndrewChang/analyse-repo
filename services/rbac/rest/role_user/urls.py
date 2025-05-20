from django.urls import path
from .views import (
    RoleUserViewSet,
)


app_name = "role_user"


urlpatterns = [
    path(
        '',
        RoleUserViewSet.as_view({
            "post": "create"
        }),
        name="list"
    ),
    path(
        '<slug:subid>/',
        RoleUserViewSet.as_view({
            "delete": "destroy"
        }),
        name="detail"
    )
]

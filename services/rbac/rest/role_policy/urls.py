from django.urls import path
from .views import (
    RolePolicyViewSet,
)


app_name = "role_policy"


urlpatterns = [
    path(
        '',
        RolePolicyViewSet.as_view({
            "post": "create"
        }),
        name="list"
    ),
    path(
        '<slug:subid>/',
        RolePolicyViewSet.as_view({
            "delete": "destroy"
        }),
        name="detail"
    )
]

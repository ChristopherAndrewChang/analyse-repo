from django.urls import path, include
from .views import (
    UserViewSet,
)


app_name = "user"


urlpatterns = [
    path(
        'role/<slug:role>/',
        include(([
            path(
                '',
                UserViewSet.as_view({
                    "get": "list"
                }),
                name="list"
            ),
        ], "role"))
    )
]

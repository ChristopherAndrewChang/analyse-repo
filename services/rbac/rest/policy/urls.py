from django.urls import path, include
from .views import (
    PolicyViewSet,
)


app_name = "policy"


urlpatterns = [
    path(
        'role/<slug:role>/',
        include(([
            path(
                '',
                PolicyViewSet.as_view({
                    "get": "list"
                }),
                name="list"
            ),
        ], "role"))
    )
]

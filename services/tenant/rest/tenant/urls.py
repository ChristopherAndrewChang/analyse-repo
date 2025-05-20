from django.urls import path
from .views import (
    TenantViewSet,
)


app_name = "tenant"


urlpatterns = [
    path('', TenantViewSet.as_view({
        "get": "list"
    }), name="list")
]

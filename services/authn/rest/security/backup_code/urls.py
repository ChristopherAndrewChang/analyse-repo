from django.urls import path
from .views import (
    BackupCodeViewSet,
)


app_name = "backup_codes"


urlpatterns = [
    path('', BackupCodeViewSet.as_view({
        "get": "list",
        "put": "update",
    }), name="list"),
]

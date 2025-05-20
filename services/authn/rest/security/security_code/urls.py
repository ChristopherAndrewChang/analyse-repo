from django.urls import path
from .views import SecurityCodeViewSet


app_name = "security_code"


urlpatterns = [
    path('', SecurityCodeViewSet.as_view({
        "put": "update",
        "delete": "destroy",
    }), name="list")
]

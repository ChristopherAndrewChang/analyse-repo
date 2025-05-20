from django.urls import path

from .views import DeviceView, DeviceRevokeView

app_name = "device"

urlpatterns = [
    path(
        "",
        DeviceView.as_view(),
        name="list"
    ),
    path(
        "<slug:subid>/",
        DeviceRevokeView.as_view(),
        name="delete"
    )
]

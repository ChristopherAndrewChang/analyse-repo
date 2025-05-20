from django.urls import path, include

from .device import urls as device_urls

app_name = "device"


urlpatterns = [
    path('devices/', include(device_urls)),
]

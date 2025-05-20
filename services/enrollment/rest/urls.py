from django.urls import path, include
from .email import urls as email_urls


app_name = "enrollment"


urlpatterns = [
    path('email/', include(email_urls)),
]

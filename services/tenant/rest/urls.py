from django.urls import path, include
from .profile import urls as profile_urls
from .tenant import urls as tenant_urls
from .user import urls as user_urls


app_name = "tenant"


urlpatterns = [
    path('profile/', include(profile_urls)),
    path('tenants/', include(tenant_urls)),
    path('users/', include(user_urls)),
]

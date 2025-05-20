from django.urls import path, include

from .policy import urls as policy_urls
from .role import urls as role_urls
from .role_policy import urls as role_policy_urls
from .role_user import urls as role_user_urls
from .user import urls as user_urls


app_name = "rbac"


urlpatterns = [
    path('policies/', include(policy_urls)),
    path('roles/', include(role_urls)),
    path('users/', include(user_urls)),

    path('role-policy/', include(role_policy_urls)),
    path('role-user/', include(role_user_urls)),
]

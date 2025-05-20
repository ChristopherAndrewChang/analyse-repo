"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('o/', include('oauth2_provider.urls')),

    # path('enrollment/', include('enrollment.rest.urls')),
    path('otp/', include('otp.rest.urls')),
    # path('account/', include('account.rest.urls')),
    path('auth/', include('authn.rest.urls')),
    path('device/', include('device.rest.urls')),
    path('oauth/', include('oauth.rest.urls')),
    path('tenant/', include('tenant.rest.urls')),
    path('rbac/', include('rbac.rest.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('oauth/m/', include('oauth.urls')),
    ]
    if "silk" in settings.INSTALLED_APPS:
        urlpatterns.append(
            path('debug-silk/', include('silk.urls', namespace='silk'))
        )

    from oauth2_provider import urls as oauth2_provider_urls
    # urlpatterns += [
    #     path('oauth2-provider/', include(oauth2_provider_urls))
    # ]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

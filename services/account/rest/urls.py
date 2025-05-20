from django.urls import path, include
from .account import urls as account_urls
from .enrollment import urls as enrollment_urls


app_name = "account"


urlpatterns = [
    path('account/', include(account_urls)),
    path('enrollment/', include(enrollment_urls))
]

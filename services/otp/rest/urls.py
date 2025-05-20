from django.urls import path, include
# from .code import urls as code_urls
from .otp import urls as otp_urls


app_name = "otp"


urlpatterns = [
    # path('code/', include(code_urls)),
    path('apply/', include(otp_urls)),
]

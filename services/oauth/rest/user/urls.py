from django.urls import path, include
# from .views import OtpRequestListView, OtpRequestRetrieveView
from .authorize_views import AuthorizeView
from .otp_request import urls as otp_urls
from .prompt_request import urls as prompt_urls


app_name = "user"


urlpatterns = [
    path("otp-requests/", include(otp_urls)),
    path("prompt-requests/", include(prompt_urls)),
    path(
        "authorize/",
        AuthorizeView.as_view(),
        name="authorize"),
]

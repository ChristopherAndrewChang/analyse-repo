from django.urls import path, re_path, include

from oauth2_provider import views
# from .authorize_views import AuthorizeView
from .otp_request import urls as otp_urls
from .prompt_request import urls as prompt_urls
from .user import urls as user_urls


app_name = "oauth"


urlpatterns = [
    path(
        "token/",
        views.TokenView.as_view(),
        name="token"),
    path(
        "revoke_token/",
        views.RevokeTokenView.as_view(),
        name="revoke-token"),
    path(
        "introspect/",
        views.IntrospectTokenView.as_view(),
        name="introspect"),
    # .well-known/openid-configuration/ is deprecated
    # https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig
    # does not specify a trailing slash
    # Support for trailing slash shall be removed in a future release.
    re_path(
        r"^\.well-known/openid-configuration/?$",
        views.ConnectDiscoveryInfoView.as_view(),
        name="oidc-connect-discovery-info",
    ),
    path(".well-known/jwks.json", views.JwksInfoView.as_view(), name="jwks-info"),
    path("userinfo/", views.UserInfoView.as_view(), name="user-info"),
    path("logout/", views.RPInitiatedLogoutView.as_view(), name="rp-initiated-logout"),

    path("otp/", include(otp_urls)),
    path("prompt/", include(prompt_urls)),
    path("user/", include(user_urls)),
]

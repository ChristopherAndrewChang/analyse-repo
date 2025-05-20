from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import status as status_code
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from oauth2_provider.exceptions import OAuthToolkitError
from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.views.mixins import OAuthLibMixin

from evercore_jwt_auth.rest_framework.authentication import JWTStatelessUserAuthentication

from oauth.models import Application

from .serializers import AllowSerializer

if TYPE_CHECKING:
    from oauthlib.oauth2 import OAuth2Error
    from oauth2_provider.scopes import SettingsScopes


logger = logging.getLogger(__name__)
__all__ = ("AuthorizeView",)


class AuthorizeView(GenericAPIView, OAuthLibMixin):
    authentication_classes = (JWTStatelessUserAuthentication,)
    permission_classes = (
        IsAuthenticated,
    )
    serializer_class = AllowSerializer
    error_messages = {
        "client_id_required": _("client_id parameter required."),
        "invalid_client_id": _("Invalid client_id parameter value."),
        "redirect_uri_required": _("redirect_uri parameter required."),
        "redirect_uri_mismatch": _("Mismatching redirect URI."),
        "invalid_scope": _("Invalid scope parameter value."),
    }

    def invalid_request(self, key: str):
        return Response({
            "error": "invalid_request",
            "error_description": self.error_messages[key]
        })

    def get(self, request, *args, **kwargs) -> Response:
        params = request.query_params
        if not (client_id := params.get("client_id")):
            return self.invalid_request("client_id_required")
        if not (redirect_uri := params.get("redirect_uri")):
            return self.invalid_request("redirect_uri_required")
        try:
            client = Application.objects.get(
                client_id=client_id
            )  # type: Application
        except Application.DoesNotExist:
            return self.invalid_request("invalid_client_id")
        if redirect_uri not in client.redirect_uris.split():
            return self.invalid_request("redirect_uri_mismatch")
        scope_backend = get_scopes_backend()  # type: SettingsScopes
        scope = params.get("scope")
        scopes = (
            scope.strip().split(" ")
            if scope else
            scope_backend.get_default_scopes(application=client)
        )
        if not set(scopes).issubset(set(
                scope_backend.get_available_scopes(application=client))):
            return self.invalid_request("invalid_scope")
        all_scopes = scope_backend.get_all_scopes()
        return Response({
            "client_name": client.name,
            "scopes": [
                all_scopes[scope]
                for scope in scopes
            ]
        })

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credentials = serializer.validated_data
        try:
            uri, headers, body, status = self.create_authorization_response(
                request=self.request, scopes=credentials.pop("scope"), credentials=credentials, allow=True)
        except OAuthToolkitError as error:
            redirect, error_response = self.error_response(error)
            if not redirect:
                oauthlib_error = error_response["error"]
                return Response({
                    "error": oauthlib_error.error,
                    "error_description ": oauthlib_error.description,
                    "state  ": oauthlib_error.state,
                }, status=status_code.HTTP_400_BAD_REQUEST)
            return Response({
                "url": error_response["url"]
            })
        return Response({"url": uri})

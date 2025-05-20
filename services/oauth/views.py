from __future__ import annotations
from typing import TYPE_CHECKING

from django.urls import reverse_lazy

from oauth2_provider.models import get_application_model
from oauth2_provider.views import (
    application as application_view,
    token as token_view,
    base as base_view,
)

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from django.core.handlers.wsgi import WSGIRequest


class ApplicationOwnerMixin:
    request: HttpRequest | WSGIRequest

    def get_queryset(self):
        return get_application_model().objects.filter(
            user_id=self.request.user.pk)


class ApplicationRegistration(
        application_view.ApplicationRegistration):
    template_name = "oauth/application_registration_form.html"

    def form_valid(self, form):
        form.instance.user_id = self.request.user.pk
        return super().form_valid(form)


class ApplicationDetail(
        ApplicationOwnerMixin, application_view.ApplicationDetail):
    template_name = "oauth/application_detail.html"


class ApplicationList(
        ApplicationOwnerMixin, application_view.ApplicationList):
    template_name = "oauth/application_list.html"


class ApplicationDelete(
        ApplicationOwnerMixin, application_view.ApplicationDelete):
    success_url = reverse_lazy("oauth_management:list")
    template_name = "oauth/application_confirm_delete.html"


class ApplicationUpdate(
        ApplicationOwnerMixin, application_view.ApplicationUpdate):
    template_name = "oauth/application_form.html"


class AuthorizedTokensListView(
        token_view.AuthorizedTokensListView):
    template_name = "oauth/authorized-tokens.html"


class AuthorizedTokenDeleteView(
        token_view.AuthorizedTokenDeleteView):
    template_name = "oauth/authorized-token-delete.html"
    success_url = reverse_lazy("oauth_management:authorized-token-list")

    def get_queryset(self):
        return self.model.objects.filter(
            user_id=self.request.user.pk)


class AuthorizationView(base_view.AuthorizationView):
    pass
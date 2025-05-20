from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth import backends

from authn.models import User
from authn.settings import authn_settings

if TYPE_CHECKING:
    from django.http.request import HttpRequest
    from rest_framework.request import Request


logger = logging.getLogger(__name__)
__alL__ = ("AuthBackend",)


class AuthBackend(backends.ModelBackend):
    def authenticate(
            self, request: HttpRequest | Request, *, field: str = None,
            password: str = None, **kwargs
    ) -> User | None:
        if field is None:
            field = authn_settings.DEFAULT_USER_LOOKUP_FIELD
        lookup = kwargs.get(field)
        if lookup is None or password is None:
            return
        try:
            user = User.objects.get(**{field: lookup})
        except User.DoesNotExist:
            User().set_password(password)
        else:
            if (
                    user.check_password(password) and
                    self.user_can_authenticate(user)
            ):
                return user

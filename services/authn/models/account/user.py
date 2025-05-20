from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.contrib.auth.models import (
    UserManager as BaseUserManager,
    AbstractUser,
)
from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField

from idvalid_core.models import get_subid_model
from idvalid_core.validators import UnicodeUsernameValidator

from authn_sdk.constants import USER_USERNAME_MAX_LENGTH

from authn.models import constants
from authn.signals import (
    user_logged_in,
    user_post_active_flag_update,
)

if TYPE_CHECKING:
    from django.db.models.base import ModelState
    from rest_framework.request import Request
    from phonenumber_field.phonenumber import PhoneNumber
    from authn.models import (
        UserLog,
        UserMFA,
        UserProfile,

        ForgetPasswordState,

        SessionManager,
        Session,

        EmailOTPManager,
        MobileOTPManager,

        PasskeyManager,
        PasskeyChallengeManager,
    )


logger = logging.getLogger(__name__)
__all__ = (
    "UserQuerySet",
    "UserManager",
    "User",
)


class UserQuerySet(models.QuerySet):
    pass


_UserManagerBase = models.Manager.from_queryset(
    UserQuerySet
)  # type: type[UserQuerySet]


class UserManager(_UserManagerBase, BaseUserManager, BaseManager):
    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        raise NotImplementedError


class User(get_subid_model(), AbstractUser):
    _state: ModelState
    # one to one fields
    log: UserLog
    mfa: UserMFA
    profile: UserProfile

    # related fields
    # allowed_applications: UserApplicationManager
    fp_state: ForgetPasswordState
    sessions: SessionManager
    emailotp_set: EmailOTPManager
    mobileotp_set: MobileOTPManager
    passkeys: PasskeyManager
    passkey_challenges: PasskeyChallengeManager

    # disabled name fields
    first_name = None
    last_name = None
    date_joined = None
    last_login = None

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=USER_USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_(
            f"Required. {USER_USERNAME_MAX_LENGTH} characters "
            f"or fewer. Letters, digits and ./_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    email = models.EmailField(
        _("email address"), null=True, blank=True,
        unique=True)
    phone = PhoneNumberField(
        _("phone"), null=True, blank=True,
        unique=True)  # type: PhoneNumber | None
    password = models.CharField(
        _("password"), max_length=128)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    account_id = models.CharField(
        _("account id"), unique=True,
        max_length=constants.USER_ACCOUNT_ID_MAX_LENGTH,
        null=True, blank=True)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def activate(self, *, save: bool = True):
        self.update_active_flag(True, save=save)

    def deactivate(self, *, save: bool = True):
        self.update_active_flag(False, save=save)

    def update_active_flag(self, value: bool, *, save: bool):
        self.is_active = value
        if save:
            self.save(update_fields=["is_active"])
            user_post_active_flag_update.send(
                sender=self.__class__, instance=self)

    def login(self, request: Request) -> Session:
        session = self.sessions.login(
            self,
            request.platform,
            request.COOKIES.get("device_id"))
        request.idvalid_session = session
        self.log.update_last_login(
            current_time=session.last_auth_time)
        user_logged_in.send(
            sender=self.__class__, request=request, user=self)
        return session

    def update_password(self, value, *, save: bool = True):
        self.set_password(value)
        if save:
            self.save(update_fields=["password"])

    def has_email(self) -> bool:
        return self.email is not None

    def has_phone(self) -> bool:
        return self.phone is not None

    def get_mf_summary(self, request) -> dict:
        summary = self.mfa.summary
        summary.update({
            "email": self.has_email(),
            "phone": self.has_phone(),
        })
        if request.auth.is_mobile:
            # always disabled mobile mfa
            # if token platform type is mobile
            summary["mobile_logged_in"] = False

        return summary

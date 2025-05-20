from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.db import models
from django.db.models.signals import pre_save
from django.db.models.manager import BaseManager
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from idvalid_core.models import get_subid_model
from idvalid_core.validators import UnicodeUsernameValidator

from account.integration.rpc import create_user_auth

from . import constants

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "AccountQuerySet",
    "AccountManager",
    "Account",
)


class AccountQuerySet(models.QuerySet):
    def create(
            self, *, password: str, client_id: str, **kwargs) -> Account:
        obj = self.model(**kwargs)
        obj.auth_register_data = {
            "password": password,
            "client_id": client_id,
        }
        self._for_write = True
        obj.save(force_insert=True, using=self.db)
        return obj


_AccountManagerBase = models.Manager.from_queryset(
    AccountQuerySet
)  # type: type[AccountQuerySet]


class AccountManager(_AccountManagerBase, BaseManager):
    pass


class Account(get_subid_model()):
    auth_register_data: dict

    email = models.EmailField(_("email"), unique=True)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=constants.ACCOUNT_USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_(
            f"Required. {constants.ACCOUNT_USERNAME_MAX_LENGTH} characters "
            f"or fewer. Letters, digits and ./_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    name = models.CharField(
        _("name"), max_length=constants.ACCOUNT_NAME_MAX_LENGTH)

    auth_id = models.CharField(
        _("auth id"), max_length=constants.ACCOUNT_AUTH_ID,
        unique=True)

    # enrollment_id = models.CharField(
    #     _("enrollment id"), unique=True,
    #     max_length=constants.ENROLLMENT_ID_LENGTH)
    # auth_id = models.CharField(
    #     _("auth id"), unique=True,
    #     max_length=constants.AUTH_ID_LENGTH)
    # profile_id = models.CharField(
    #     _("profile id"), unique=True,
    #     max_length=constants.PROFILE_ID_LENGTH)
    # email = models.EmailField(
    #     _("email"), unique=True)

    objects = AccountManager()


@receiver(pre_save, sender=Account)
def on_account_pre_save(instance: Account, **kwargs):
    if not instance.auth_id:
        instance.auth_id = create_user_auth(
            instance, **instance.auth_register_data)

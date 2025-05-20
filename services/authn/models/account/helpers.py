from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

from authn.signals import account_post_create

from .user import User
from .log import UserLog
from .mfa import UserMFA
from .profile import UserProfile

if TYPE_CHECKING:
    from authn.models import Enrollment


__all__ = (
    "UserRegisterData",
    "create_account",
)


@dataclass
class UserRegisterData:
    username: str
    password: str
    name: str
    enrollment: "Enrollment"


def create_account(data: UserRegisterData):
    user_data = {
        "username": data.username,
        "password": data.password,
    }
    enrollment = data.enrollment
    if enrollment.email_id:
        user_data["email"] = enrollment.email.address
    if enrollment.phone_id:
        user_data["phone"] = enrollment.phone.number
    user = User.objects.create_user(**user_data)  # type: User
    user.profile = UserProfile.objects.create(
        user=user, name=data.name)
    user.mfa = UserMFA.objects.create(
        user=user)
    user.log = UserLog.objects.create(
        user=user)
    account_post_create.send(sender=user.__class__, user=user)
    return user

from __future__ import annotations
from typing import TYPE_CHECKING

import logging

if TYPE_CHECKING:
    from typing import Any


logger = logging.getLogger(__name__)
__all__ = (
    "TemporaryUser",
)


class _User:
    is_active = True
    is_anonymous = False
    is_authenticated = True

    def __init__(self, _id, **kwargs):
        self.id = _id
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    @property
    def pk(self):
        return self.id

    def __eq__(self, other):
        return self.pk == other.pk


class TemporaryUser:
    _user: "Any"
    user_id: "Any"
    default_user_class = _User

    @property
    def user(self):
        if not hasattr(self, "_user"):
            if user_id := self.user_id:
                self._user = self.default_user_class(user_id)
            else:
                self._user = None
        return self._user

    @user.setter
    def user(self, value):
        self.user_id = value.pk
        self._user = value

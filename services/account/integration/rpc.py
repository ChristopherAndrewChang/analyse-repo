from __future__ import annotations
from typing import TYPE_CHECKING

import logging

# from idvalid_integration.rpc.enrollment.email import (
#     GetEmailRequest,
#     get_email,)
from idvalid_integration.rpc.authn.user import (
    CreateUser,
    CreateRequest,
    create,
)

if TYPE_CHECKING:
    from account.models import Account


logger = logging.getLogger(__name__)
__all__ = (
    "create_user_auth",
    # "enrollment_email",
)


def create_user_auth(instance: Account, client_id: str, password: str) -> str:
    data = {
        "email": instance.email,
        "username": instance.username,
        "name": instance.name,
        "account_id": instance.subid,
        "client_id": client_id,
        "password": password
    }
    return create(message=CreateRequest(data=CreateUser(**data))).id


# def enrollment_email(enrollment_id: str, state: str) -> str:
#     data = {
#         "id": enrollment_id,
#         "state": state,
#     }
#     return get_email(message=GetEmailRequest(**data)).email

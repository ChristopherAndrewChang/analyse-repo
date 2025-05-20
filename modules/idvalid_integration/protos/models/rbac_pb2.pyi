from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RoleUser(_message.Message):
    __slots__ = ("tenant_id", "role_id", "user_id")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    tenant_id: int
    role_id: int
    user_id: int
    def __init__(self, tenant_id: _Optional[int] = ..., role_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

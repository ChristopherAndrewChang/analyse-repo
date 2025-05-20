from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Tenant(_message.Message):
    __slots__ = ("id", "subid", "name", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: int
    subid: str
    name: str
    is_active: bool
    def __init__(self, id: _Optional[int] = ..., subid: _Optional[str] = ..., name: _Optional[str] = ..., is_active: bool = ...) -> None: ...

class TenantUser(_message.Message):
    __slots__ = ("tenant_id", "user_id", "is_owner", "is_registered", "is_active")
    TENANT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_OWNER_FIELD_NUMBER: _ClassVar[int]
    IS_REGISTERED_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    tenant_id: int
    user_id: int
    is_owner: bool
    is_registered: bool
    is_active: bool
    def __init__(self, tenant_id: _Optional[int] = ..., user_id: _Optional[int] = ..., is_owner: bool = ..., is_registered: bool = ..., is_active: bool = ...) -> None: ...

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateUser(_message.Message):
    __slots__ = ("email", "username", "password", "name", "account_id", "client_id")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    email: str
    username: str
    password: str
    name: str
    account_id: str
    client_id: str
    def __init__(self, email: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., name: _Optional[str] = ..., account_id: _Optional[str] = ..., client_id: _Optional[str] = ...) -> None: ...

class UserLoggedIn(_message.Message):
    __slots__ = ("user_id", "platform_id", "device_id", "user_agent", "session_id", "ip_address")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    platform_id: int
    device_id: str
    user_agent: str
    session_id: int
    ip_address: str
    def __init__(self, user_id: _Optional[int] = ..., platform_id: _Optional[int] = ..., device_id: _Optional[str] = ..., user_agent: _Optional[str] = ..., session_id: _Optional[int] = ..., ip_address: _Optional[str] = ...) -> None: ...

class Platform(_message.Message):
    __slots__ = ("id", "subid", "name", "type")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    id: int
    subid: str
    name: str
    type: str
    def __init__(self, id: _Optional[int] = ..., subid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class Session(_message.Message):
    __slots__ = ("id", "subid", "user_id", "platform_id", "device_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    subid: str
    user_id: int
    platform_id: int
    device_id: str
    def __init__(self, id: _Optional[int] = ..., subid: _Optional[str] = ..., user_id: _Optional[int] = ..., platform_id: _Optional[int] = ..., device_id: _Optional[str] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("id", "subid", "is_active", "is_staff", "is_superuser")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_STAFF_FIELD_NUMBER: _ClassVar[int]
    IS_SUPERUSER_FIELD_NUMBER: _ClassVar[int]
    id: int
    subid: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
    def __init__(self, id: _Optional[int] = ..., subid: _Optional[str] = ..., is_active: bool = ..., is_staff: bool = ..., is_superuser: bool = ...) -> None: ...

class UserActiveFlag(_message.Message):
    __slots__ = ("user_id", "is_active")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    is_active: bool
    def __init__(self, user_id: _Optional[int] = ..., is_active: bool = ...) -> None: ...

class UserProfile(_message.Message):
    __slots__ = ("user_id", "name")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    name: str
    def __init__(self, user_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class Account(_message.Message):
    __slots__ = ("user", "profile")
    USER_FIELD_NUMBER: _ClassVar[int]
    PROFILE_FIELD_NUMBER: _ClassVar[int]
    user: User
    profile: UserProfile
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., profile: _Optional[_Union[UserProfile, _Mapping]] = ...) -> None: ...

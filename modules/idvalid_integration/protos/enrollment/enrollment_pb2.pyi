from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ConfirmRequest(_message.Message):
    __slots__ = ("id", "device_id", "user_agent", "signature")
    ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    id: str
    device_id: str
    user_agent: str
    signature: bytes
    def __init__(self, id: _Optional[str] = ..., device_id: _Optional[str] = ..., user_agent: _Optional[str] = ..., signature: _Optional[bytes] = ...) -> None: ...

class ConfirmResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class GetEmailRequest(_message.Message):
    __slots__ = ("id", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: str
    state: str
    def __init__(self, id: _Optional[str] = ..., state: _Optional[str] = ...) -> None: ...

class GetEmailResponse(_message.Message):
    __slots__ = ("email",)
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    email: str
    def __init__(self, email: _Optional[str] = ...) -> None: ...

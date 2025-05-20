from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateRequest(_message.Message):
    __slots__ = ("email", "sms", "app", "expires_in", "usage", "issuer", "ref_id", "suppress", "device_id")
    class EmailOtp(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    class SmsOtp(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    class AppOtp(_message.Message):
        __slots__ = ("value",)
        VALUE_FIELD_NUMBER: _ClassVar[int]
        value: str
        def __init__(self, value: _Optional[str] = ...) -> None: ...
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    SMS_FIELD_NUMBER: _ClassVar[int]
    APP_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    ISSUER_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    email: CreateRequest.EmailOtp
    sms: CreateRequest.SmsOtp
    app: CreateRequest.AppOtp
    expires_in: _duration_pb2.Duration
    usage: str
    issuer: str
    ref_id: str
    suppress: str
    device_id: str
    def __init__(self, email: _Optional[_Union[CreateRequest.EmailOtp, _Mapping]] = ..., sms: _Optional[_Union[CreateRequest.SmsOtp, _Mapping]] = ..., app: _Optional[_Union[CreateRequest.AppOtp, _Mapping]] = ..., expires_in: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., usage: _Optional[str] = ..., issuer: _Optional[str] = ..., ref_id: _Optional[str] = ..., suppress: _Optional[str] = ..., device_id: _Optional[str] = ...) -> None: ...

class CreateResponse(_message.Message):
    __slots__ = ("id", "key", "expires")
    ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    id: str
    key: bytes
    expires: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., key: _Optional[bytes] = ..., expires: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ConfirmRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ConfirmResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

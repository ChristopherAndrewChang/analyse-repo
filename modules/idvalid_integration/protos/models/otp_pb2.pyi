from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Method(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    METHOD_MAIL: _ClassVar[Method]
    METHOD_SMS: _ClassVar[Method]
    METHOD_WHATSAPP: _ClassVar[Method]
    METHOD_IDVALID: _ClassVar[Method]
METHOD_MAIL: Method
METHOD_SMS: Method
METHOD_WHATSAPP: Method
METHOD_IDVALID: Method

class CreateOtp(_message.Message):
    __slots__ = ("object_id", "usage", "ref_id", "method", "device_id", "user_agent", "expires", "email_address", "phone_number", "user_id", "owner_id")
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    EMAIL_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PHONE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    usage: str
    ref_id: str
    method: Method
    device_id: str
    user_agent: str
    expires: _timestamp_pb2.Timestamp
    email_address: str
    phone_number: str
    user_id: str
    owner_id: int
    def __init__(self, object_id: _Optional[str] = ..., usage: _Optional[str] = ..., ref_id: _Optional[str] = ..., method: _Optional[_Union[Method, str]] = ..., device_id: _Optional[str] = ..., user_agent: _Optional[str] = ..., expires: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., email_address: _Optional[str] = ..., phone_number: _Optional[str] = ..., user_id: _Optional[str] = ..., owner_id: _Optional[int] = ...) -> None: ...

class Otp(_message.Message):
    __slots__ = ("id", "object_id", "usage", "ref_id", "expires", "token", "applied", "applied_time", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    USAGE_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    APPLIED_FIELD_NUMBER: _ClassVar[int]
    APPLIED_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    object_id: str
    usage: str
    ref_id: str
    expires: _timestamp_pb2.Timestamp
    token: str
    applied: bool
    applied_time: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., object_id: _Optional[str] = ..., usage: _Optional[str] = ..., ref_id: _Optional[str] = ..., expires: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., token: _Optional[str] = ..., applied: bool = ..., applied_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

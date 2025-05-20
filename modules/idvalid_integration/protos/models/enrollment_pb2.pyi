from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Email(_message.Message):
    __slots__ = ("id", "email", "is_registered", "registered_date", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    IS_REGISTERED_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_DATE_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: str
    is_registered: bool
    registered_date: _timestamp_pb2.Timestamp
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., email: _Optional[str] = ..., is_registered: bool = ..., registered_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Enrollment(_message.Message):
    __slots__ = ("id", "email", "state", "device_id", "user_agent", "created")
    ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    email: Email
    state: str
    device_id: str
    user_agent: str
    created: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., email: _Optional[_Union[Email, _Mapping]] = ..., state: _Optional[str] = ..., device_id: _Optional[str] = ..., user_agent: _Optional[str] = ..., created: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

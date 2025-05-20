from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Enum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENUM_UNSPECIFIED: _ClassVar[Enum]
    ENUM_SPECIFIED: _ClassVar[Enum]
    ENUM_CUSTOM: _ClassVar[Enum]
ENUM_UNSPECIFIED: Enum
ENUM_SPECIFIED: Enum
ENUM_CUSTOM: Enum

class OtherMessage(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("double_value", "float_value", "int32_value", "int64_value", "uint32_value", "uint64_value", "sint32_value", "sint64_value", "fixed32_value", "fixed64_value", "sfixed32_value", "sfixed64_value", "bool_value", "string_value", "bytes_value", "enum_value", "other_message_value", "wkt_value", "repeated_bool_value", "repeated_enum_value", "repeated_other_message_value", "repeated_wkt_value", "oneof_one_value", "oneof_two_value", "oneof_three_value", "map_str_bool_value", "optional_double_value", "optional_float_value", "optional_int32_value", "optional_int64_value", "optional_uint32_value", "optional_uint64_value", "optional_sint32_value", "optional_sint64_value", "optional_fixed32_value", "optional_fixed64_value", "optional_sfixed32_value", "optional_sfixed64_value", "optional_bool_value", "optional_string_value", "optional_bytes_value")
    class MapStrBoolValueEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: bool
        def __init__(self, key: _Optional[str] = ..., value: bool = ...) -> None: ...
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    UINT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    UINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    SINT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    SINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    FIXED32_VALUE_FIELD_NUMBER: _ClassVar[int]
    FIXED64_VALUE_FIELD_NUMBER: _ClassVar[int]
    SFIXED32_VALUE_FIELD_NUMBER: _ClassVar[int]
    SFIXED64_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    ENUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    OTHER_MESSAGE_VALUE_FIELD_NUMBER: _ClassVar[int]
    WKT_VALUE_FIELD_NUMBER: _ClassVar[int]
    REPEATED_BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    REPEATED_ENUM_VALUE_FIELD_NUMBER: _ClassVar[int]
    REPEATED_OTHER_MESSAGE_VALUE_FIELD_NUMBER: _ClassVar[int]
    REPEATED_WKT_VALUE_FIELD_NUMBER: _ClassVar[int]
    ONEOF_ONE_VALUE_FIELD_NUMBER: _ClassVar[int]
    ONEOF_TWO_VALUE_FIELD_NUMBER: _ClassVar[int]
    ONEOF_THREE_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAP_STR_BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_INT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_UINT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_UINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_SINT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_SINT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIXED32_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_FIXED64_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_SFIXED32_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_SFIXED64_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_BYTES_VALUE_FIELD_NUMBER: _ClassVar[int]
    double_value: float
    float_value: float
    int32_value: int
    int64_value: int
    uint32_value: int
    uint64_value: int
    sint32_value: int
    sint64_value: int
    fixed32_value: int
    fixed64_value: int
    sfixed32_value: int
    sfixed64_value: int
    bool_value: bool
    string_value: str
    bytes_value: bytes
    enum_value: Enum
    other_message_value: OtherMessage
    wkt_value: _duration_pb2.Duration
    repeated_bool_value: _containers.RepeatedScalarFieldContainer[bool]
    repeated_enum_value: _containers.RepeatedScalarFieldContainer[Enum]
    repeated_other_message_value: _containers.RepeatedCompositeFieldContainer[OtherMessage]
    repeated_wkt_value: _containers.RepeatedCompositeFieldContainer[_duration_pb2.Duration]
    oneof_one_value: bool
    oneof_two_value: str
    oneof_three_value: bytes
    map_str_bool_value: _containers.ScalarMap[str, bool]
    optional_double_value: float
    optional_float_value: float
    optional_int32_value: int
    optional_int64_value: int
    optional_uint32_value: int
    optional_uint64_value: int
    optional_sint32_value: int
    optional_sint64_value: int
    optional_fixed32_value: int
    optional_fixed64_value: int
    optional_sfixed32_value: int
    optional_sfixed64_value: int
    optional_bool_value: bool
    optional_string_value: str
    optional_bytes_value: bytes
    def __init__(self, double_value: _Optional[float] = ..., float_value: _Optional[float] = ..., int32_value: _Optional[int] = ..., int64_value: _Optional[int] = ..., uint32_value: _Optional[int] = ..., uint64_value: _Optional[int] = ..., sint32_value: _Optional[int] = ..., sint64_value: _Optional[int] = ..., fixed32_value: _Optional[int] = ..., fixed64_value: _Optional[int] = ..., sfixed32_value: _Optional[int] = ..., sfixed64_value: _Optional[int] = ..., bool_value: bool = ..., string_value: _Optional[str] = ..., bytes_value: _Optional[bytes] = ..., enum_value: _Optional[_Union[Enum, str]] = ..., other_message_value: _Optional[_Union[OtherMessage, _Mapping]] = ..., wkt_value: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., repeated_bool_value: _Optional[_Iterable[bool]] = ..., repeated_enum_value: _Optional[_Iterable[_Union[Enum, str]]] = ..., repeated_other_message_value: _Optional[_Iterable[_Union[OtherMessage, _Mapping]]] = ..., repeated_wkt_value: _Optional[_Iterable[_Union[_duration_pb2.Duration, _Mapping]]] = ..., oneof_one_value: bool = ..., oneof_two_value: _Optional[str] = ..., oneof_three_value: _Optional[bytes] = ..., map_str_bool_value: _Optional[_Mapping[str, bool]] = ..., optional_double_value: _Optional[float] = ..., optional_float_value: _Optional[float] = ..., optional_int32_value: _Optional[int] = ..., optional_int64_value: _Optional[int] = ..., optional_uint32_value: _Optional[int] = ..., optional_uint64_value: _Optional[int] = ..., optional_sint32_value: _Optional[int] = ..., optional_sint64_value: _Optional[int] = ..., optional_fixed32_value: _Optional[int] = ..., optional_fixed64_value: _Optional[int] = ..., optional_sfixed32_value: _Optional[int] = ..., optional_sfixed64_value: _Optional[int] = ..., optional_bool_value: bool = ..., optional_string_value: _Optional[str] = ..., optional_bytes_value: _Optional[bytes] = ...) -> None: ...

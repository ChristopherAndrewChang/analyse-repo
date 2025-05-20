from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FieldTestData(_message.Message):
    __slots__ = ("boolean_field", "char_field", "email_field", "regex_field", "slug_field", "url_field", "uuid_field", "ipaddress_field", "integer_field", "float_field", "decimal_field", "datetime_field", "duration_field", "choice_field", "multiple_choice_field", "list_field", "dict_field")
    class Choice(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHOICE_UNSPECIFIED: _ClassVar[FieldTestData.Choice]
        CHOICE_FIRST: _ClassVar[FieldTestData.Choice]
        CHOICE_SECOND: _ClassVar[FieldTestData.Choice]
        CHOICE_THIRD: _ClassVar[FieldTestData.Choice]
    CHOICE_UNSPECIFIED: FieldTestData.Choice
    CHOICE_FIRST: FieldTestData.Choice
    CHOICE_SECOND: FieldTestData.Choice
    CHOICE_THIRD: FieldTestData.Choice
    class DictFieldEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BOOLEAN_FIELD_FIELD_NUMBER: _ClassVar[int]
    CHAR_FIELD_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_FIELD_NUMBER: _ClassVar[int]
    SLUG_FIELD_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_FIELD_NUMBER: _ClassVar[int]
    IPADDRESS_FIELD_FIELD_NUMBER: _ClassVar[int]
    INTEGER_FIELD_FIELD_NUMBER: _ClassVar[int]
    FLOAT_FIELD_FIELD_NUMBER: _ClassVar[int]
    DECIMAL_FIELD_FIELD_NUMBER: _ClassVar[int]
    DATETIME_FIELD_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_FIELD_NUMBER: _ClassVar[int]
    CHOICE_FIELD_FIELD_NUMBER: _ClassVar[int]
    MULTIPLE_CHOICE_FIELD_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_FIELD_NUMBER: _ClassVar[int]
    DICT_FIELD_FIELD_NUMBER: _ClassVar[int]
    boolean_field: bool
    char_field: str
    email_field: str
    regex_field: str
    slug_field: str
    url_field: str
    uuid_field: int
    ipaddress_field: str
    integer_field: int
    float_field: float
    decimal_field: str
    datetime_field: _timestamp_pb2.Timestamp
    duration_field: _duration_pb2.Duration
    choice_field: FieldTestData.Choice
    multiple_choice_field: _containers.RepeatedScalarFieldContainer[FieldTestData.Choice]
    list_field: _containers.RepeatedScalarFieldContainer[str]
    dict_field: _containers.ScalarMap[str, str]
    def __init__(self, boolean_field: bool = ..., char_field: _Optional[str] = ..., email_field: _Optional[str] = ..., regex_field: _Optional[str] = ..., slug_field: _Optional[str] = ..., url_field: _Optional[str] = ..., uuid_field: _Optional[int] = ..., ipaddress_field: _Optional[str] = ..., integer_field: _Optional[int] = ..., float_field: _Optional[float] = ..., decimal_field: _Optional[str] = ..., datetime_field: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration_field: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., choice_field: _Optional[_Union[FieldTestData.Choice, str]] = ..., multiple_choice_field: _Optional[_Iterable[_Union[FieldTestData.Choice, str]]] = ..., list_field: _Optional[_Iterable[str]] = ..., dict_field: _Optional[_Mapping[str, str]] = ...) -> None: ...

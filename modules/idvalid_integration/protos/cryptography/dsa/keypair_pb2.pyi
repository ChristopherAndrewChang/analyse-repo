from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Algorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALGORITHM_UNSPECIFIED: _ClassVar[Algorithm]
    ALGORITHM_ED25519: _ClassVar[Algorithm]
    ALGORITHM_ECDSA: _ClassVar[Algorithm]
    ALGORITHM_RSA: _ClassVar[Algorithm]
ALGORITHM_UNSPECIFIED: Algorithm
ALGORITHM_ED25519: Algorithm
ALGORITHM_ECDSA: Algorithm
ALGORITHM_RSA: Algorithm

class Pair(_message.Message):
    __slots__ = ("private_key", "public_key", "signature")
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    private_key: bytes
    public_key: bytes
    signature: bytes
    def __init__(self, private_key: _Optional[bytes] = ..., public_key: _Optional[bytes] = ..., signature: _Optional[bytes] = ...) -> None: ...

class GenerateRequest(_message.Message):
    __slots__ = ("algorithm", "size", "data")
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    algorithm: Algorithm
    size: int
    data: bytes
    def __init__(self, algorithm: _Optional[_Union[Algorithm, str]] = ..., size: _Optional[int] = ..., data: _Optional[bytes] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ("pair",)
    PAIR_FIELD_NUMBER: _ClassVar[int]
    pair: Pair
    def __init__(self, pair: _Optional[_Union[Pair, _Mapping]] = ...) -> None: ...

class SignRequest(_message.Message):
    __slots__ = ("algorithm", "private_key", "data")
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    algorithm: Algorithm
    private_key: bytes
    data: bytes
    def __init__(self, algorithm: _Optional[_Union[Algorithm, str]] = ..., private_key: _Optional[bytes] = ..., data: _Optional[bytes] = ...) -> None: ...

class SignResponse(_message.Message):
    __slots__ = ("signature",)
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    signature: bytes
    def __init__(self, signature: _Optional[bytes] = ...) -> None: ...

class VerifyRequest(_message.Message):
    __slots__ = ("algorithm", "public_key", "data", "signature")
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    algorithm: Algorithm
    public_key: bytes
    data: bytes
    signature: bytes
    def __init__(self, algorithm: _Optional[_Union[Algorithm, str]] = ..., public_key: _Optional[bytes] = ..., data: _Optional[bytes] = ..., signature: _Optional[bytes] = ...) -> None: ...

class VerifyResponse(_message.Message):
    __slots__ = ("valid",)
    VALID_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    def __init__(self, valid: bool = ...) -> None: ...

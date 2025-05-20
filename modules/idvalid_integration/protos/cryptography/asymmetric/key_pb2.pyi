from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Algorithm(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALGORITHM_UNSPECIFIED: _ClassVar[Algorithm]
    ALGORITHM_RSA: _ClassVar[Algorithm]
    ALGORITHM_DSA: _ClassVar[Algorithm]
    ALGORITHM_ECDSA: _ClassVar[Algorithm]
    ALGORITHM_ED25519: _ClassVar[Algorithm]
ALGORITHM_UNSPECIFIED: Algorithm
ALGORITHM_RSA: Algorithm
ALGORITHM_DSA: Algorithm
ALGORITHM_ECDSA: Algorithm
ALGORITHM_ED25519: Algorithm

class KeyPair(_message.Message):
    __slots__ = ("private_key", "public_key")
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    private_key: bytes
    public_key: bytes
    def __init__(self, private_key: _Optional[bytes] = ..., public_key: _Optional[bytes] = ...) -> None: ...

class GenerateRequest(_message.Message):
    __slots__ = ("data", "algorithm")
    DATA_FIELD_NUMBER: _ClassVar[int]
    ALGORITHM_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    algorithm: Algorithm
    def __init__(self, data: _Optional[bytes] = ..., algorithm: _Optional[_Union[Algorithm, str]] = ...) -> None: ...

class GenerateResponse(_message.Message):
    __slots__ = ("pair", "signature")
    PAIR_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    pair: KeyPair
    signature: bytes
    def __init__(self, pair: _Optional[_Union[KeyPair, _Mapping]] = ..., signature: _Optional[bytes] = ...) -> None: ...

class SignRequest(_message.Message):
    __slots__ = ("private_key", "data")
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    private_key: bytes
    data: bytes
    def __init__(self, private_key: _Optional[bytes] = ..., data: _Optional[bytes] = ...) -> None: ...

class SignResponse(_message.Message):
    __slots__ = ("signature",)
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    signature: bytes
    def __init__(self, signature: _Optional[bytes] = ...) -> None: ...

class VerifyRequest(_message.Message):
    __slots__ = ("public_key", "data", "signature")
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    data: bytes
    signature: bytes
    def __init__(self, public_key: _Optional[bytes] = ..., data: _Optional[bytes] = ..., signature: _Optional[bytes] = ...) -> None: ...

class VerifyResponse(_message.Message):
    __slots__ = ("valid",)
    VALID_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    def __init__(self, valid: bool = ...) -> None: ...

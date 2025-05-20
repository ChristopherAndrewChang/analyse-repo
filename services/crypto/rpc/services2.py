from __future__ import annotations
from typing import TYPE_CHECKING

import logging

import grpc

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, padding

from django_grpc_framework.services import Service

from idvalid_integration.protos.cryptography.asymmetric import key_pb2
from idvalid_integration.protos.cryptography.asymmetric import key_pb2_grpc

if TYPE_CHECKING:
    # type KeyTypes = Union[
    #     rsa.RSAPrivateKey, rsa.RSAPublicKey,
    #     dsa.DSAPrivateKey, dsa.DSAPublicKey,
    #     ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey,
    #     ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]
    type PrivateKeyTypes = Union[
        rsa.RSAPrivateKey,
        dsa.DSAPrivateKey,
        ec.EllipticCurvePrivateKey,
        ed25519.Ed25519PrivateKey
    ]
    type PublicKeyTypes = Union[
        rsa.RSAPublicKey,
        dsa.DSAPublicKey,
        ec.EllipticCurvePublicKey,
        ed25519.Ed25519PublicKey
    ]
    type KeyTypes = PrivateKeyTypes | PublicKeyTypes

    from typing import Union


logger = logging.getLogger(__name__)
__all__ = ("KeyService",)


def _generate_rsa_key_pair() -> tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def _generate_dsa_key_pair() -> tuple[dsa.DSAPrivateKey, dsa.DSAPublicKey]:
    private_key = dsa.generate_private_key(key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def _generate_ecdsa_key_pair() -> tuple[ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    return private_key, public_key


def _generate_ed25519_key_pair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def _serialize_key(key: KeyTypes, is_private: bool) -> bytes:
    if is_private:
        return key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption())
    else:
        return key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo)


def _load_key(raw_key: bytes, is_private: bool) -> KeyTypes:
    if is_private:
        return serialization.load_der_private_key(raw_key, password=None)
    else:
        return serialization.load_der_public_key(raw_key)


def _sign_data(
        private_key: PrivateKeyTypes, data: bytes) -> bytes:
    if isinstance(private_key, rsa.RSAPrivateKey):
        return private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())
    elif isinstance(private_key, dsa.DSAPrivateKey):
        return private_key.sign(data, hashes.SHA256())
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        return private_key.sign(data, ec.ECDSA(hashes.SHA256()))
    elif isinstance(private_key, ed25519.Ed25519PrivateKey):
        return private_key.sign(data)
    raise ValueError("Unsupported algorithm")


class KeyService(Service, key_pb2_grpc.KeyServicer):
    def Generate(self, request: key_pb2.GenerateRequest,
                 context: grpc.ServicerContext) -> key_pb2.GenerateResponse:
        algorithm = request.algorithm or key_pb2.ALGORITHM_ED25519  # Default to RSA if not specified

        if algorithm == key_pb2.ALGORITHM_RSA:
            private_key, public_key = _generate_rsa_key_pair()
        elif algorithm == key_pb2.ALGORITHM_DSA:
            private_key, public_key = _generate_dsa_key_pair()
        elif algorithm == key_pb2.ALGORITHM_ECDSA:
            private_key, public_key = _generate_ecdsa_key_pair()
        elif algorithm == key_pb2.ALGORITHM_ED25519:
            private_key, public_key = _generate_ed25519_key_pair()
        else:
            context.set_details('Unsupported algorithm')
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return key_pb2.GenerateResponse()

        private_key_pem = _serialize_key(private_key, is_private=True)
        public_key_pem = _serialize_key(public_key, is_private=False)

        # Optional: Sign data if provided in request
        signature: bytes | None = None
        if request.data:
            signature = _sign_data(private_key, request.data)

        return key_pb2.GenerateResponse(
            pair=key_pb2.KeyPair(
                private_key=private_key_pem,
                public_key=public_key_pem
            ),
            signature=signature
        )

    def Sign(self, request: key_pb2.SignRequest,
             context: grpc.ServicerContext) -> key_pb2.SignResponse:
        # private_key = serialization.load_pem_private_key(request.private_key, password=None)
        try:
            private_key = _load_key(request.private_key, is_private=True)
        except ValueError:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Missing required field.")
            raise Exception()
        data = request.data

        signature = _sign_data(private_key, data)

        return key_pb2.SignResponse(
            signature=signature
        )

    def Verify(self, request: key_pb2.VerifyRequest,
               context: grpc.ServicerContext) -> key_pb2.VerifyResponse:
        # public_key = serialization.load_pem_public_key(request.public_key)
        try:
            public_key = _load_key(request.public_key, is_private=False)
        except ValueError:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Missing required field.")
            raise Exception()
        data = request.data
        signature = request.signature

        try:
            public_key.verify(signature, data)
            valid = True
        except Exception as e:
            print("exc:", e, type(e))
            print(signature, data)
            valid = False

        return key_pb2.VerifyResponse(
            valid=valid
        )

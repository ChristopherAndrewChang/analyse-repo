
from cryptography.hazmat.primitives.asymmetric import ed25519, ec, rsa

import grpc

from django_grpc_framework.services import Service

from idvalid_integration.protos.cryptography.dsa import keypair_pb2_grpc, keypair_pb2


# TODO: Move to django settings
DEFAULT_RSA_PUBLIC_EXPONENT = 65537
DEFAULT_RSA_KEY_SIZE = 2048


class KeyPairServicer(Service, keypair_pb2_grpc.KeyPairServicer):
    def Generate(self, request: keypair_pb2.GenerateRequest, context: grpc.ServicerContext):
        # print("request", request, type(request), request.__dict__)
        # print("context", context)
        # print(context.auth_context())
        # print(context.invocation_metadata())
        size = request.size if request.HasField('size') else None
        if request.algorithm == keypair_pb2.Algorithm.ALGORITHM_RSA:
            private_key = rsa.generate_private_key(
                public_exponent=DEFAULT_RSA_PUBLIC_EXPONENT,
                key_size=DEFAULT_RSA_KEY_SIZE)
        elif request.algorithm == keypair_pb2.Algorithm.ALGORITHM_ECDSA:
            private_key = ec.generate_private_key
        elif request.algorithm == keypair_pb2.Algorithm.ALGORITHM_ED25519:
            # ED25519 has a fixed key size, so size is usually ignored
            private_key = ed25519.Ed25519PrivateKey.generate()
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Unsupported algorithm')
            return keypair_pb2.GenerateResponse()

        context.set_trailing_metadata(
            (
                ("checksum-bin", b"I agree"),
                ("retry", "false"),
            )
        )
        # context.

        pair = keypair_pb2.Pair(private_key=private_key, public_key=public_key)
        return keypair_pb2.GenerateResponse(pair=pair)

    def _generate_ed25519_private_key(self):
        private_key = ed25519.Ed25519PrivateKey.generate()
        return private_key

    def generate_rsa_key(self, size: int):
        # Replace with actual RSA key generation logic using the provided size
        private_key = b'\x01\x02\x03\x04\x05'  # Example private key bytes
        public_key = b'\x06\x07\x08\x09\x0a'  # Example public key bytes
        return private_key, public_key

    def generate_ecdsa_key(self, size):
        # Replace with actual ECDSA key generation logic using the provided size
        private_key = b'\x11\x12\x13\x14\x15'  # Example private key bytes
        public_key = b'\x16\x17\x18\x19\x1a'  # Example public key bytes
        return private_key, public_key

    def Sign(self, request, context):
        # Example implementation: sign data with a private key
        key_id = request.id
        data = request.data
        algorithm = request.algorithm

        # Placeholder for actual signing logic
        signature = b'signature_placeholder'

        return keys_pb2.SignResponse(signature=signature)

    def Verify(self, request, context):
        # Example implementation: verify a signature
        key_id = request.id
        data = request.data
        signature = request.signature
        algorithm = request.algorithm

        # Placeholder for actual verification logic
        valid = True

        return keys_pb2.VerifyResponse(valid=valid)
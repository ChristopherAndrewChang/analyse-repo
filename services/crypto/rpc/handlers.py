from idvalid_integration.protos.cryptography.dsa import keypair_pb2_grpc
from idvalid_integration.protos.cryptography.asymmetric import key_pb2_grpc
from .services import KeyPairServicer
from .services2 import KeyService


def grpc_handlers(server):
    keypair_pb2_grpc.add_KeyPairServicer_to_server(KeyPairServicer.as_servicer(), server)
    key_pb2_grpc.add_KeyServicer_to_server(KeyService.as_servicer(), server)

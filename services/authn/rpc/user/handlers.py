from idvalid_integration.protos.authn import user_pb2_grpc
from .services import UserService


def grpc_handlers(server):
    user_pb2_grpc.add_UserServicer_to_server(UserService.as_servicer(), server)

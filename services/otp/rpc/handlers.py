from idvalid_integration.protos.otp import code_pb2_grpc
from .services import CodeService


def grpc_handlers(server):
    code_pb2_grpc.add_CodeServicer_to_server(CodeService.as_servicer(), server)

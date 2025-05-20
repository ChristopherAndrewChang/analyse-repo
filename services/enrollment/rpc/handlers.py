from idvalid_integration.protos.enrollment import enrollment_pb2_grpc
from .services import EnrollmentServicer


def grpc_handlers(server):
    enrollment_pb2_grpc.add_EnrollmentServicer_to_server(EnrollmentServicer.as_servicer(), server)

# from crypto.rpc import handlers as crypto_handlers
# from otp.rpc import handlers as otp_handlers
# from enrollment.rpc import handlers as enrollment_handlers
from authn.rpc import handlers as authn_handlers


def grpc_handlers(server):
    # crypto_handlers.grpc_handlers(server)
    # otp_handlers.grpc_handlers(server)
    # enrollment_handlers.grpc_handlers(server)
    authn_handlers.grpc_handlers(server)

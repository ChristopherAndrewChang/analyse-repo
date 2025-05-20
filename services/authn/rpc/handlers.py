from .user import handlers as user_handlers


def grpc_handlers(server):
    user_handlers.grpc_handlers(server)

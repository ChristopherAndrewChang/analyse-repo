import grpc
from grpc import StatusCode


# Interceptor to catch unimplemented methods
class UnimplementedInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # print(continuation, handler_call_details)
        handler = continuation(handler_call_details)
        if handler is None:
            def unimplemented_handler(request, context):
                method_name = handler_call_details.method
                context.set_code(StatusCode.UNIMPLEMENTED)
                context.set_details(f'Method {method_name} is not implemented.')
                print(f"Unimplemented method called: {method_name}")
                return None
            return grpc.unary_unary_rpc_method_handler(unimplemented_handler)
        return handler

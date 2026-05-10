from concurrent import futures

import grpc

from app.core.config import settings
from app.grpc.auth_servicer import AuthServicer
from app.grpc.generated import auth_pb2_grpc


def create_grpc_server() -> grpc.Server:
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
    )

    auth_pb2_grpc.add_AuthServiceServicer_to_server(
        AuthServicer(),
        server,
    )

    server.add_insecure_port(
        settings.grpc_host + ":" + str(settings.grpc_port),
    )

    return server


def serve() -> None:
    server = create_grpc_server()
    server.start()

    print(
        "MS Auth gRPC server running on "
        + settings.grpc_host
        + ":"
        + str(settings.grpc_port)
    )

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
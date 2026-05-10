import uvicorn

from app.core.config import settings
from app.grpc.server import create_grpc_server


def start_services() -> None:
    grpc_server = create_grpc_server()
    grpc_server.start()

    print(
        "MS Auth gRPC server running on "
        + settings.grpc_host
        + ":"
        + str(settings.grpc_port)
    )

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.api_host,
            port=settings.api_port,
        )
    finally:
        grpc_server.stop(grace=0)


if __name__ == "__main__":
    start_services()
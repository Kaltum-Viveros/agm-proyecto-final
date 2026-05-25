import uvicorn
import threading
import asyncio

from app.core.config import settings
from app.grpc.server import create_grpc_server
from app.messaging.rabbit_worker import start_rabbit_worker

def _run_rabbit_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_rabbit_worker())

def start_services() -> None:
    # Iniciar RabbitMQ worker en background
    rabbit_thread = threading.Thread(target=_run_rabbit_worker, daemon=True)
    rabbit_thread.start()

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
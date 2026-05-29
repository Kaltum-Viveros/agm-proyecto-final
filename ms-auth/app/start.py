import uvicorn
import threading
import asyncio
import logging

from app.core.config import settings
from app.grpc.server import create_grpc_server
from app.messaging.rabbit_worker import start_rabbit_worker

def _run_rabbit_worker():
    # Configurar logging básico para este thread
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("rabbit_worker")
    logger.info("Thread de RabbitMQ worker iniciado.")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_rabbit_worker())
    except Exception as e:
        logger.error(f"Fallo critico irrecuperable en loop de RabbitMQ worker: {e}")

def start_services() -> None:
    # Configurar logging básico global al inicio
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logger = logging.getLogger("start")
    logger.info("Iniciando servicios unificados de MS-1 Auth...")

    # Iniciar RabbitMQ worker en background
    rabbit_thread = threading.Thread(target=_run_rabbit_worker, daemon=True)
    rabbit_thread.start()

    grpc_server = create_grpc_server()
    grpc_server.start()

    logger.info(
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
import asyncio
import sys
from pathlib import Path

import grpc

from app.core.config import settings

# Los archivos generados por grpc_tools usan imports absolutos como:
# import calificaciones_pb2
# Por eso agregamos app/grpc/generated al path antes de importarlos.
generated_path = Path(__file__).resolve().parent / "generated"
sys.path.append(str(generated_path))

from app.grpc.generated import calificaciones_pb2_grpc
from app.grpc.services.calificaciones_grpc_service import CalificacionesGrpcService


_server = None

async def start_grpc_server():
    global _server
    _server = grpc.aio.server()

    calificaciones_pb2_grpc.add_CalificacionesServiceServicer_to_server(
        CalificacionesGrpcService(),
        _server,
    )

    listen_addr = f"[::]:{settings.grpc_port}"
    _server.add_insecure_port(listen_addr)

    print(f"gRPC server running on {listen_addr}")

    await _server.start()
    return _server

async def stop_grpc_server():
    global _server
    if _server:
        await _server.stop(grace=5)
        print("gRPC server stopped")

async def serve():
    await start_grpc_server()
    await _server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
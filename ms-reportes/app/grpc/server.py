import asyncio
import sys
from pathlib import Path

import grpc

from app.core.config import settings

# Archivos generados usan imports absolutos. Añadimos al path.
generated_path = Path(__file__).resolve().parent / "generated"
sys.path.append(str(generated_path))

from app.grpc.generated import reportes_pb2_grpc
from app.grpc.reportes_servicer import ReportesServicer

_server = None

async def start_grpc_server():
    global _server
    _server = grpc.aio.server()

    reportes_pb2_grpc.add_ReportesServiceServicer_to_server(
        ReportesServicer(),
        _server,
    )

    listen_addr = f"[::]:{settings.GRPC_PORT}"
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

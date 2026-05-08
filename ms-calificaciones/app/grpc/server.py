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


async def serve():
    server = grpc.aio.server()

    calificaciones_pb2_grpc.add_CalificacionesServiceServicer_to_server(
        CalificacionesGrpcService(),
        server,
    )

    listen_addr = f"[::]:{settings.grpc_port}"
    server.add_insecure_port(listen_addr)

    print(f"gRPC server running on {listen_addr}")

    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
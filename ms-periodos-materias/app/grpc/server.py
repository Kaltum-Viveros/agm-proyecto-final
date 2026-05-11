import asyncio

import grpc

from app.core.config import settings
from app.grpc.generated import periodos_materias_pb2_grpc
from app.grpc.periodos_materias_service import PeriodosMateriasGrpcService


async def serve():
    server = grpc.aio.server()

    periodos_materias_pb2_grpc.add_PeriodosMateriasServiceServicer_to_server(
        PeriodosMateriasGrpcService(),
        server
    )

    listen_addr = f"{settings.GRPC_HOST}:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)

    await server.start()

    print(f"Servidor gRPC MS-2 escuchando en {listen_addr}", flush=True)

    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
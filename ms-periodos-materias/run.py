import asyncio

import uvicorn

from app.core.config import settings
from app.grpc.server import serve as serve_grpc


async def serve_rest():
    config = uvicorn.Config(
        "app.main:app",
        host=settings.rest_host,    
        port=settings.rest_port,
        reload=False,
    )

    server = uvicorn.Server(config)

    await server.serve()


async def main():
    print("Iniciando REST y gRPC de MS-2...")

    await asyncio.gather(
        serve_rest(),
        serve_grpc(),
    )


if __name__ == "__main__":
    asyncio.run(main())
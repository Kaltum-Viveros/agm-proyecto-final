import asyncio

import uvicorn

from app.core.config import settings
from app.grpc.server import serve as serve_grpc


async def serve_rest():
    config = uvicorn.Config(
        "app.main:app",
        host=getattr(settings, "API_HOST", "0.0.0.0"),
        port=int(getattr(settings, "API_PORT", 8002)),
        reload=False,
    )

    server = uvicorn.Server(config)

    await server.serve()


async def main():
    print("Iniciando REST y gRPC de MS-2...", flush=True)
    await asyncio.gather(
        serve_rest(),
        serve_grpc(),
    )


if __name__ == "__main__":
    asyncio.run(main())
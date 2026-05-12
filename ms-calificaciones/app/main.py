from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.grpc.server import start_grpc_server, stop_grpc_server

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar servidor gRPC en segundo plano
    await start_grpc_server()
    yield
    # Detener servidor gRPC
    await stop_grpc_server()


from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="AGM - MS Calificaciones & Ponderaciones",
    version="0.1.0",
    description="Microservicio de ponderaciones, actividades, calificaciones y concentrados.",
    lifespan=lifespan
)

# Configuración de CORS para el Frontend (Angular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se debe restringir a la URL de Angular (ej. https://frontend.com)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "success": True,
        "service": settings.service_name,
        "message": "MS Calificaciones & Ponderaciones",
    }
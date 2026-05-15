from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="MS-7 Reportes",
    description="Microservicio de Reportes y Estadísticas",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

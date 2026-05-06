from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="AGM - MS Calificaciones & Ponderaciones",
    version="0.1.0",
    description="Microservicio de ponderaciones, actividades, calificaciones y concentrados.",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "success": True,
        "service": settings.service_name,
        "message": "MS Calificaciones & Ponderaciones",
    }
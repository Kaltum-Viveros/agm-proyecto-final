from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="MS-7: Reportes & Estadísticas",
    description="Microservicio para la generación y consulta de reportes académicos.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
async def root_health():
    """Endpoint raíz de salud — no requiere BD."""
    return {"status": "ok", "service": settings.SERVICE_NAME}

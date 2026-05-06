from fastapi import FastAPI
from app.api.v1.endpoints import notificaciones
from app.core.database import init_db

app = FastAPI(title="MS Notificaciones")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(notificaciones.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Microservicio de Notificaciones funcionando"}
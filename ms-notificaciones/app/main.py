from fastapi import FastAPI

from app.api.v1.endpoints import notificaciones

app = FastAPI(title="MS Notificaciones")

app.include_router(notificaciones.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Microservicio de Notificaciones funcionando"}
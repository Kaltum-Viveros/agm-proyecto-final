from fastapi import FastAPI

app = FastAPI(
    title="AGM - MS Calificaciones & Ponderaciones",
    version="0.1.0",
    description="Microservicio de ponderaciones, actividades, calificaciones y concentrados."
)

@app.get("/health")
def health_check():
    return {
        "success": True,
        "service": "ms-calificaciones",
        "status": "ok"
    }
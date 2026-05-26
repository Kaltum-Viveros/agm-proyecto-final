import asyncio

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import notificaciones
from app.core.database import init_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.responses import error_response
from app.core.config import settings
from app.messaging.event_worker import start_event_worker

tags_metadata = [
    {
        "name": "Notificaciones",
        "description": "Operaciones con notificaciones. Creación, lectura, actualización y eliminación.",
    }
]

app = FastAPI(
    title=settings.APP_NAME,
    description="Microservicio encargado de gestionar las notificaciones para los usuarios del sistema. Permite el envío de correos, alertas y mensajes.",
    version="1.0.0",
    contact={
        "name": "Equipo de Desarrollo",
        "email": "soporte@tudominio.com",
    },
    openapi_tags=tags_metadata
)

@app.on_event("startup")
async def startup():
    init_db()
    app.state.notification_event_worker_task = asyncio.create_task(start_event_worker())


@app.on_event("shutdown")
async def shutdown():
    task = getattr(app.state, "notification_event_worker_task", None)
    if task:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errores = [f"{error['loc'][-1]}: {error['msg']}" for error in exc.errors()]
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response(
            message="Error de validación",
            error_code="VALIDATION_ERROR",
            data={"detalles": errores}
        )
    )

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.detail, error_code="NOT_FOUND")
    )

@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.detail, error_code="BAD_REQUEST")
    )

app.include_router(notificaciones.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Microservicio de Notificaciones funcionando"}

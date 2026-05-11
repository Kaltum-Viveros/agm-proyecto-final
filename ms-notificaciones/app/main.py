from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import notificaciones
from app.core.database import init_db
from app.core.exceptions import NotFoundException, BadRequestException
from app.core.responses import error_response
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
def startup():
    init_db()

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
from fastapi import APIRouter, status

from app.schemas.esquema_qr import GenerarQrRequest, GenerarQrResponse
from app.services.servicio_qr import ServicioQr

router = APIRouter(prefix="/qr", tags=["Generación de Códigos QR"])


@router.post(
    "/generar",
    response_model=GenerarQrResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar token QR dinámico para alumno",
)
def generar_qr(request: GenerarQrRequest):
    """
    Genera un token cifrado con los datos del alumno y la sesión.
    Este endpoint NO requiere base de datos porque la validación 
    ocurre cuando el docente escanea el QR.
    """
    resultado = ServicioQr.generar_token_qr(
        id_sesion=request.id_sesion,
        id_alumno=request.id_alumno,
        matricula=request.matricula,
    )
    return GenerarQrResponse(**resultado)

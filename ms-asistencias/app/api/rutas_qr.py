from fastapi import APIRouter, Depends, status, HTTPException
from app.core.security import requerir_alumno
from app.schemas.esquema_qr import GenerarQrRequest, GenerarQrResponse
from app.services.servicio_qr import ServicioQr

router = APIRouter(prefix="/qr", tags=["Generación de Códigos QR"])


@router.post(
    "/generar",
    response_model=GenerarQrResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generar token QR dinámico para alumno",
)
def generar_qr(
    request: GenerarQrRequest,
    claims: dict = Depends(requerir_alumno)
):
    """
    Genera un token cifrado con los datos del alumno y la sesión.
    Este endpoint NO requiere base de datos porque la validación 
    ocurre cuando el docente escanea el QR.
    """
    id_alumno_claim = claims.get("id_alumno") or claims.get("user_id")
    if str(request.id_alumno) != str(id_alumno_claim):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para generar un QR a nombre de otro alumno"
        )
        
    # TODO: Validar con MS-3 que el alumno está inscrito en la materia/sesión
    resultado = ServicioQr.generar_token_qr(
        id_sesion=request.id_sesion,
        id_alumno=request.id_alumno,
        matricula=request.matricula,
    )
    return GenerarQrResponse(**resultado)

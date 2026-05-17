from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
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
async def generar_qr(
    request: GenerarQrRequest,
    claims: dict = Depends(requerir_alumno),
    db: AsyncSession = Depends(get_db),
):
    """
    Genera un token cifrado con los datos del alumno y la sesión.
    Este endpoint requiere base de datos para validar el estado de la sesión
    y gRPC para comprobar las inscripciones.
    """
    id_alumno = claims.get("id_alumno") or claims.get("user_id")
    matricula = claims.get("matricula") or claims.get("correo") or "SIN_MATRICULA"

    if not id_alumno:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se encontró un ID de alumno válido en el token."
        )

    resultado = await ServicioQr.generar_token_qr(
        db=db,
        id_sesion=request.id_sesion,
        id_alumno=int(id_alumno),
        matricula=str(matricula),
    )
    return GenerarQrResponse(**resultado)

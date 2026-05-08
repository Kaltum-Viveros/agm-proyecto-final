from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.esquema_sesiones import IniciarSesionRequest, SesionResponse
from app.services.servicio_sesiones import ServicioSesiones

router = APIRouter(prefix="/sesiones", tags=["Sesiones de Asistencia"])


@router.post(
    "/iniciar",
    response_model=SesionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar una nueva sesión de asistencia",
)
async def iniciar_sesion(
    request: IniciarSesionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Abre una nueva sesión de asistencia para una materia específica.
    La sesión durará 10 minutos automáticamente.
    """
    nueva_sesion = await ServicioSesiones.iniciar_sesion(
        db=db,
        id_materia=request.id_materia,
        id_docente=request.id_docente,
    )
    # Convertir el modelo de SQLAlchemy a Pydantic y commitear
    await db.commit()
    return SesionResponse.model_validate(nueva_sesion)


@router.delete(
    "/{id_sesion}/cerrar",
    status_code=status.HTTP_200_OK,
    summary="Cerrar una sesión manualmente",
)
async def cerrar_sesion(
    id_sesion: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Permite al docente cerrar la sesión antes de que se acaben los 10 minutos.
    """
    resultado = await ServicioSesiones.cerrar_sesion(db=db, id_sesion=id_sesion)
    await db.commit()
    return resultado

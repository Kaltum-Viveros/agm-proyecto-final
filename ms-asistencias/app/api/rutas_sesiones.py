from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import requerir_docente, requerir_usuario
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
    claims: dict = Depends(requerir_docente),
    db: AsyncSession = Depends(get_db),
):
    """
    Abre una nueva sesión de asistencia para una materia específica.
    La sesión durará 10 minutos automáticamente.
    """
    # Validar propiedad (no iniciar sesión para otro docente)
    id_docente_claim = claims.get("id_docente") or claims.get("user_id")
    if str(request.id_docente) != str(id_docente_claim):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para iniciar una sesión a nombre de otro docente"
        )
        
    # TODO: Validar con MS-2/MS-3 que este docente pertenece a la materia
    # (Por ahora, como lo define la Fase 13, la lógica de validación se irá integrando)

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
    claims: dict = Depends(requerir_docente),
    db: AsyncSession = Depends(get_db),
):
    """
    Permite al docente cerrar la sesión antes de que se acaben los 10 minutos.
    """
    resultado = await ServicioSesiones.cerrar_sesion(db=db, id_sesion=id_sesion)
    await db.commit()
    return resultado


@router.get(
    "/{id_sesion}",
    response_model=SesionResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener los detalles de una sesión",
)
async def obtener_sesion(
    id_sesion: int,
    claims: dict = Depends(requerir_usuario),
    db: AsyncSession = Depends(get_db),
):
    """
    Retorna la información de una sesión específica.
    """
    sesion = await ServicioSesiones.obtener_sesion(db=db, id_sesion=id_sesion)
    return SesionResponse.model_validate(sesion)


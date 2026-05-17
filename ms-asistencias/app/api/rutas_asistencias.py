from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.repositorio_asistencias import RepositorioAsistencias
from app.schemas.esquema_asistencias import (
    DetalleAsistencia, 
    RegistrarAsistenciaRequest, 
    RegistroAsistenciaResponse,
    EstadisticasAsistenciaResponse
)
from app.services.servicio_asistencias import ServicioAsistencias

router = APIRouter(prefix="/asistencias", tags=["Registros de Asistencia"])


@router.post(
    "/registrar",
    response_model=RegistroAsistenciaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar la asistencia de un alumno validando su QR",
)
async def registrar_asistencia(
    request: RegistrarAsistenciaRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    El docente envía el token escaneado. 
    Se valida seguridad, tiempos y se guarda el pase de lista.
    """
    resultado = await ServicioAsistencias.registrar_asistencia(
        db=db, token_cifrado=request.token_cifrado
    )
    # Si todo salió bien en el servicio, guardamos los cambios físicos en BD.
    await db.commit()
    return RegistroAsistenciaResponse(**resultado)


@router.get(
    "/{id_sesion}/historial",
    response_model=List[DetalleAsistencia],
    status_code=status.HTTP_200_OK,
    summary="Obtener la lista de asistencias de una sesión específica",
)
async def listar_historial_sesion(
    id_sesion: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve a todos los alumnos que pasaron lista en una sesión dada.
    """
    registros = await RepositorioAsistencias.listar_asistencias_por_sesion(db=db, id_sesion=id_sesion)
    return registros


@router.get(
    "/{id_materia}/hoy",
    response_model=List[DetalleAsistencia],
    status_code=status.HTTP_200_OK,
    summary="Obtener las asistencias de una materia en el día de hoy",
)
async def listar_asistencias_hoy(
    id_materia: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve todos los registros de asistencia tomados hoy para una materia.
    """
    registros = await ServicioAsistencias.obtener_asistencias_hoy_materia(db=db, id_materia=id_materia)
    return registros


@router.get(
    "/sesion/{id_sesion}/estadisticas",
    response_model=EstadisticasAsistenciaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener las estadísticas de una sesión",
)
async def obtener_estadisticas_sesion(
    id_sesion: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Calcula y retorna presentes, retardos, ausentes y porcentaje de asistencia.
    """
    estadisticas = await ServicioAsistencias.obtener_estadisticas_sesion(db=db, id_sesion=id_sesion)
    return EstadisticasAsistenciaResponse(**estadisticas)


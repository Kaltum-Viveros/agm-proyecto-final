from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.reporte_repository import ReporteRepository
from app.services.reporte_service import ReporteService

router = APIRouter()

def get_reporte_service(db: AsyncSession = Depends(get_db)) -> ReporteService:
    repo = ReporteRepository(db)
    return ReporteService(repo)

@router.get("/docente/{docente_id}")
async def get_estadisticas_docente(
    docente_id: str,
    service: ReporteService = Depends(get_reporte_service)
):
    """
    Obtiene las estadísticas agrupadas por periodo y materia de un docente.
    """
    return service.obtener_estadisticas_docente(docente_id)

@router.get("/alumno/{alumno_id}")
async def get_estadisticas_alumno(
    alumno_id: str,
    service: ReporteService = Depends(get_reporte_service)
):
    """
    Obtiene el historial de un alumno. 
    (Limitado temporalmente por falta de GetMateriasByAlumno en MS-3).
    """
    return service.obtener_estadisticas_alumno(alumno_id)

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.reporte_repository import ReporteRepository
from app.services.reporte_service import ReporteService
from app.api.deps import require_authenticated_user

router = APIRouter()

def get_reporte_service(db: AsyncSession = Depends(get_db)) -> ReporteService:
    repo = ReporteRepository(db)
    return ReporteService(repo)

@router.get("/docente/{docente_id}")
async def get_estadisticas_docente(
    docente_id: str,
    service: ReporteService = Depends(get_reporte_service),
    _user: dict = Depends(require_authenticated_user)
):
    """
    Obtiene las estadísticas agrupadas por periodo y materia de un docente.
    """
    return await service.obtener_estadisticas_docente(docente_id)

@router.get("/alumno/{alumno_id}")
async def get_estadisticas_alumno(
    alumno_id: str,
    service: ReporteService = Depends(get_reporte_service),
    _user: dict = Depends(require_authenticated_user)
):
    """
    Obtiene el historial y estadísticas de un alumno. 
    Las materias del alumno se obtienen desde MS-3 (Docentes & Alumnos) mediante gRPC usando GetMateriasByAlumno.
    """
    return await service.obtener_estadisticas_alumno(alumno_id)

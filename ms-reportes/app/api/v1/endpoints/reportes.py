from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.reporte_repository import ReporteRepository
from app.services.reporte_service import ReporteService
from app.api.deps import require_authenticated_user

router = APIRouter()

def get_reporte_service(db: AsyncSession = Depends(get_db)) -> ReporteService:
    repo = ReporteRepository(db)
    return ReporteService(repo)

@router.get("/calificaciones/{materia_id}")
async def descargar_reporte_calificaciones(
    materia_id: str,
    formato: str = Query(..., description="Formato del reporte: pdf o xlsx"),
    service: ReporteService = Depends(get_reporte_service),
    _user: dict = Depends(require_authenticated_user)
):
    """
    Genera y descarga un reporte de calificaciones de una materia específica en PDF o XLSX.
    """
    formato = formato.lower()
    file_bytes, filename, content_type = await service.generar_reporte_calificaciones(materia_id, formato)
    
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

@router.get("/asistencias/{materia_id}")
async def descargar_reporte_asistencias(
    materia_id: str,
    formato: str = Query(..., description="Formato del reporte: pdf o xlsx"),
    service: ReporteService = Depends(get_reporte_service),
    _user: dict = Depends(require_authenticated_user)
):
    """
    Genera y descarga un reporte de asistencias de una materia específica en PDF o XLSX.
    """
    formato = formato.lower()
    file_bytes, filename, content_type = await service.generar_reporte_asistencias(materia_id, formato)
    
    return Response(
        content=file_bytes,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

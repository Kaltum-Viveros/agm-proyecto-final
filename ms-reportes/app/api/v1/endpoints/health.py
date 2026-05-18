from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db

router = APIRouter()


@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Verifica que el servicio y la base de datos estén operativos."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = str(exc)

    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "ok",
        "database": db_status,
    }

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reporte import ReporteGenerado

class ReporteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: dict) -> ReporteGenerado:
        reporte = ReporteGenerado(**data)
        self.db.add(reporte)
        await self.db.commit()
        await self.db.refresh(reporte)
        return reporte

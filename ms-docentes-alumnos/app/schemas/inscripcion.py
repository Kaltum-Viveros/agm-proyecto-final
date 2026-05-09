from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class InscripcionBase(BaseModel):
    docente_id: UUID
    alumno_id: UUID
    ciclo_escolar: str  # Ej: "2026-Primavera"
    estatus: bool = True

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionUpdate(BaseModel):
    ciclo_escolar: Optional[str] = None
    estatus: Optional[bool] = None

class InscripcionOut(InscripcionBase):
    inscripcion_id: UUID
    fecha_inscripcion: datetime

    model_config = ConfigDict(from_attributes=True)
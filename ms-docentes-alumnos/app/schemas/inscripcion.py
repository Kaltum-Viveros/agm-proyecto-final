from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class InscripcionBase(BaseModel):
    docente_id: UUID
    alumno_id: UUID
    materia_id: UUID
    periodo_id: UUID
    nrc_materia: str
    seccion_materia: Optional[str] = None
    
    activa: bool = True 

class InscripcionCreate(InscripcionBase):
    pass

class InscripcionOut(InscripcionBase):
    inscripcion_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class AlumnoBase(BaseModel):
    nombre_completo: str
    correo: EmailStr
    matricula: str
    estatus_academico: bool = True
    tipo_formacion: Optional[str] = None

# user_id NO se acepta desde el cliente REST; se obtiene desde MS-1 vía gRPC.
class AlumnoCreate(AlumnoBase):
    pass

class AlumnoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    promedio: Optional[float] = None
    estatus_academico: Optional[bool] = None

class AlumnoOut(AlumnoBase):
    alumno_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
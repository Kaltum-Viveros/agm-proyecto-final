# Esquemas
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# ---- Request Schemas (Peticiones REST) ----

class BienvenidaRequest(BaseModel):
    alumno_id: int = Field(..., gt=0, description="ID numérico del alumno registrado")

class BajaMateriaRequest(BaseModel):
    alumno_id: int = Field(..., gt=0, description="ID del alumno que se da de baja")
    docente_id: int = Field(..., gt=0, description="ID del docente responsable")
    materia_id: int = Field(..., gt=0, description="ID de la materia")

class CierreMateriaRequest(BaseModel):
    materia_id: int = Field(..., gt=0, description="ID de la materia que cerró actas")

class ResetPasswordRequest(BaseModel):
    usuario_id: int = Field(..., gt=0, description="ID del usuario (alumno o docente)")

# ---- Response Schemas (Salidas REST) ----

class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    email: str
    tipo: str
    asunto: str
    mensaje: str
    estado: str
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
# Esquemas
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# ---- Request Schemas (Peticiones REST) ----

class BienvenidaRequest(BaseModel):
    alumno_id: str = Field(..., description="ID (UUID) del alumno registrado")
    materia_id: str = Field("", description="ID (UUID) de la materia")
    password_temporal: str = Field(..., description="Contraseña temporal generada")

class BajaMateriaRequest(BaseModel):
    alumno_id: str = Field(..., description="ID (UUID) del alumno que se da de baja")
    docente_id: str = Field(..., description="ID (UUID) del docente responsable")
    materia_id: str = Field(..., description="ID (UUID) de la materia")

class CierreMateriaRequest(BaseModel):
    materia_id: str = Field(..., description="ID (UUID) de la materia que cerró actas")

class ResetPasswordRequest(BaseModel):
    usuario_id: str = Field(..., description="ID del usuario (UUID de ms-auth o numérico)")
    email: EmailStr = Field(..., description="Correo del usuario para enviar el token")
    reset_token: str = Field(..., description="Token seguro generado por ms-auth")

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
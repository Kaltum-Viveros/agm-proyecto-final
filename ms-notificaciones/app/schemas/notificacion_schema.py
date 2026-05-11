# Esquemas
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class NotificacionCreate(BaseModel):
    usuario_id: int = Field(..., gt=0, description="El ID de usuario debe ser mayor a 0")
    email: EmailStr = Field(..., description="Debe ser un correo electrónico válido")
    tipo: str = Field(..., min_length=2, max_length=50, description="Tipo de notificación (ej. alerta, mensaje)")
    asunto: str = Field(..., min_length=3, max_length=150, description="El asunto debe tener entre 3 y 150 caracteres")
    mensaje: str = Field(..., min_length=5, description="El mensaje debe contener al menos 5 caracteres")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usuario_id": 123,
                "email": "usuario@ejemplo.com",
                "tipo": "alerta",
                "asunto": "Cambio de contraseña",
                "mensaje": "Se ha solicitado un cambio de contraseña para tu cuenta."
            }
        }
    )

class NotificacionUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Debe ser un correo electrónico válido")
    tipo: Optional[str] = Field(None, min_length=2, max_length=50)
    asunto: Optional[str] = Field(None, min_length=3, max_length=150)
    mensaje: Optional[str] = Field(None, min_length=5)
    estado: Optional[str] = Field(None, pattern="^(pendiente|enviada|fallida)$", description="Estado de la notificación")
    fecha_envio: Optional[datetime] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "enviada",
                "fecha_envio": "2026-05-11T12:00:00Z"
            }
        }
    )

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

    class Config:
        from_attributes = True
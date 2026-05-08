# Esquemas
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificacionCreate(BaseModel):
    usuario_id: int
    email: str
    tipo: str
    asunto: str
    mensaje: str

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
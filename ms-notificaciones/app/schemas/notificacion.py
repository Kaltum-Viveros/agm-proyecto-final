# Esquemas
from pydantic import BaseModel
from datetime import datetime

class NotificacionCreate(BaseModel):
    usuario_id: int
    mensaje: str

class NotificacionResponse(BaseModel):
    id: int
    usuario_id: int
    mensaje: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True
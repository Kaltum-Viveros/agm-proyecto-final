# Esquemas
from pydantic import BaseModel
from datetime import datetime

class NotificacionCreate(BaseModel):
    usuario_id: int
    email: str
    tipo: str
    asunto: str
    mensaje: str

class NotificacionResponse(BaseModel):
    id: int
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True
# Modelo de base de datos
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.core.database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=False)
    email = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    asunto = Column(String, nullable=False)
    mensaje = Column(Text, nullable=False)
    estado = Column(String, default="pendiente")

    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_envio = Column(DateTime, nullable=True)
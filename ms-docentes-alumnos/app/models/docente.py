import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base 

class Docente(Base):
    __tablename__ = "docentes"
    docente_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    clave_docente = Column(String(20), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(150), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    cubiculo = Column(String(100), nullable=True)
    horario_atencion = Column(String(150), nullable=True)
    estatus_laboral = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    inscripciones = relationship("Inscripcion", back_populates="docente")
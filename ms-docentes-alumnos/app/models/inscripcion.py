import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base 

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    inscripcion_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alumno_id = Column(UUID(as_uuid=True), ForeignKey("alumnos.alumno_id"), nullable=False)
    docente_id = Column(UUID(as_uuid=True), ForeignKey("docentes.docente_id"), nullable=False)
    materia_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    periodo_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    nrc_materia = Column(String(10), nullable=False)
    seccion_materia = Column(String(10), nullable=True)
    activa = Column(Boolean, default=True, nullable=False)
    fecha_baja = Column(DateTime(timezone=True), nullable=True)
    motivo_baja = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    alumno = relationship("Alumno", back_populates="inscripciones")
    docente = relationship("Docente", back_populates="inscripciones")
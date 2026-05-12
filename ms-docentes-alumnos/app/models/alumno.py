import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base 

class Alumno(Base):
    __tablename__ = "alumnos"
    
    alumno_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    matricula = Column(String(20), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(200), nullable=False)
    correo = Column(String(150), unique=True, nullable=False)
    
    # Perfil del Alumno
    tipo_formacion = Column(String(50), nullable=True) # Ej: Licenciatura, Posgrado
    
    # Lógica de Proceso: Control de bienvenida y acceso
    clave_unica_enviada = Column(Boolean, default=False) # Para MS-Notificaciones
    estatus_academico = Column(Boolean, default=True)    # Para control de bajas
    
    # Auditoría
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con la tabla que une alumnos con docentes/materias
    inscripciones = relationship("Inscripcion", back_populates="alumno", cascade="all, delete-orphan")
from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base

class Plantilla(Base):
    __tablename__ = "plantillas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True) # ej: "bienvenida", "baja_materia"
    asunto_base = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)

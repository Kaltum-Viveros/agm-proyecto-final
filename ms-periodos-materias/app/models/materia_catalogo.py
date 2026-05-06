import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_ofertada import MateriaOfertada
    from app.models.materia_plan_estudio import MateriaPlanEstudio


class MateriaCatalogo(Base):
    __tablename__ = "materias_catalogo"

    materia_catalogo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    clave: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    planes_estudio: Mapped[list["MateriaPlanEstudio"]] = relationship(
        back_populates="materia_catalogo",
        cascade="all, delete-orphan",
    )

    materias_ofertadas: Mapped[list["MateriaOfertada"]] = relationship(
        back_populates="materia_catalogo",
    )
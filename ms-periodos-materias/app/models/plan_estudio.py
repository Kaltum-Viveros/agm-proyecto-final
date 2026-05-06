import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_plan_estudio import MateriaPlanEstudio


class PlanEstudio(Base):
    __tablename__ = "planes_estudio"

    plan_estudio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relación con MateriaPlanEstudio 1 a muchos
    materias: Mapped[list["MateriaPlanEstudio"]] = relationship(
        back_populates="plan_estudio",
        cascade="all, delete-orphan",
    )
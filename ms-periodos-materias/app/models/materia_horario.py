import uuid
from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_ofertada import MateriaOfertada


class MateriaHorario(Base):
    __tablename__ = "materia_horarios"

    materia_horario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    materia_ofertada_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materias_ofertadas.materia_ofertada_id", ondelete="CASCADE"),
        nullable=False,
    )

    dia: Mapped[str] = mapped_column(String(2), nullable=False)

    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)

    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    
    salon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    materia_ofertada: Mapped["MateriaOfertada"] = relationship(
        back_populates="horarios",
    )

    __table_args__ = (
        CheckConstraint(
            "hora_inicio < hora_fin",
            name="ck_materia_horarios_horas_validas",
        ),
        UniqueConstraint(
            "materia_ofertada_id",
            "dia",
            "hora_inicio",
            "hora_fin",
            "salon",
            name="uq_materia_horario_unico",
        ),
    )
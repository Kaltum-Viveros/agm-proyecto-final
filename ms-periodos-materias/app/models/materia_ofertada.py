import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_catalogo import MateriaCatalogo
    from app.models.materia_horario import MateriaHorario
    from app.models.periodo import Periodo


class MateriaOfertada(Base):
    __tablename__ = "materias_ofertadas"

    materia_ofertada_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    periodo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("periodos.periodo_id", ondelete="CASCADE"),
        nullable=False,
    )

    materia_catalogo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materias_catalogo.materia_catalogo_id", ondelete="RESTRICT"),
        nullable=False,
    )

    nrc: Mapped[str] = mapped_column(String(5), nullable=False)

    seccion: Mapped[str] = mapped_column(String(100), nullable=False)

    # este atributo se obtiene de otro microservicio, no es una relación directa en la base de datos 
    docente_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID(as_uuid=True),
    nullable=True,
    )
    
    docente_nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVA")

    periodo: Mapped["Periodo"] = relationship(
        back_populates="materias_ofertadas",
    )

    materia_catalogo: Mapped["MateriaCatalogo"] = relationship(
        back_populates="materias_ofertadas",
    )

    horarios: Mapped[list["MateriaHorario"]] = relationship(
        back_populates="materia_ofertada",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "periodo_id",
            "nrc",
            name="uq_materia_ofertada_periodo_nrc",
        ),
    )
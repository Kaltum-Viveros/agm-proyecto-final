import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_ofertada import MateriaOfertada


class Periodo(Base):
    __tablename__ = "periodos"

    periodo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)

    fecha_fin: Mapped[date] = mapped_column(Date, nullable=False)

    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relación con MateriaOfertada 1 a muchos
    materias_ofertadas: Mapped[list["MateriaOfertada"]] = relationship(
        back_populates="periodo",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "fecha_inicio <= fecha_fin",
            name="ck_periodos_fechas_validas",
        ),
        Index(
            "uq_periodos_unico_activo",
            "activo",
            unique=True,
            postgresql_where=(activo.is_(True)),
        ),
    )
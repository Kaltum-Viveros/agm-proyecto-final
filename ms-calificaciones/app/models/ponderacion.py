import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Ponderacion(Base):
    __tablename__ = "ponderaciones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Referencia lógica a MS-2. No es FK real.
    materia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    porcentaje: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    actividades = relationship(
        "Actividad",
        back_populates="ponderacion",
    )

    __table_args__ = (
        UniqueConstraint("materia_id", "nombre", name="uq_ponderacion_materia_nombre"),
        CheckConstraint("porcentaje > 0 AND porcentaje <= 100", name="chk_ponderacion_porcentaje"),
    )
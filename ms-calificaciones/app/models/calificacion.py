import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Calificacion(Base):
    __tablename__ = "calificaciones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # FK real dentro del MS-4.
    actividad_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("actividades.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Referencia lógica a MS-3. No es FK real.
    alumno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    calificacion: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
    )

    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

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

    actividad = relationship(
        "Actividad",
        back_populates="calificaciones",
    )

    __table_args__ = (
        UniqueConstraint("actividad_id", "alumno_id", name="uq_calificacion_actividad_alumno"),
        CheckConstraint("calificacion >= 0", name="chk_calificacion_minima"),
    )
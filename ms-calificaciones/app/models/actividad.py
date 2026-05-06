import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Actividad(Base):
    __tablename__ = "actividades"

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

    # FK real dentro del MS-4.
    ponderacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ponderaciones.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    valor_maximo: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=10,
    )

    fecha_aplicacion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="activa",
    )

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

    ponderacion = relationship(
        "Ponderacion",
        back_populates="actividades",
    )

    calificaciones = relationship(
        "Calificacion",
        back_populates="actividad",
    )

    __table_args__ = (
        UniqueConstraint("ponderacion_id", "nombre", name="uq_actividad_ponderacion_nombre"),
        CheckConstraint("valor_maximo > 0", name="chk_actividad_valor_maximo"),
        CheckConstraint("estado IN ('activa', 'cerrada', 'cancelada')", name="chk_actividad_estado"),
    )
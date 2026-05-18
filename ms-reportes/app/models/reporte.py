import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ReporteGenerado(Base):
    """
    Registro de cada reporte generado por el sistema.
    Las referencias a periodo_id, materia_id y docente_id son lógicas
    (no FK físicas) apuntando a MS-2 y MS-3 respectivamente.
    """

    __tablename__ = "reportes_generados"

    reporte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tipo_reporte: Mapped[str] = mapped_column(String(30), nullable=False)
    formato: Mapped[str] = mapped_column(String(10), nullable=False)

    # Referencias lógicas a otros microservicios (sin FK físicas)
    periodo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    materia_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    docente_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDIENTE",
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

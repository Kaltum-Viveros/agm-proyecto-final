from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EstadoAsistencia, MetodoRegistro


class RegistroAsistencia(Base):
    __tablename__ = "registros_asistencia"

    id_asistencia: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # FK real porque apunta a una tabla del mismo microservicio.
    id_sesion: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "sesiones_asistencia.id_sesion",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Referencia lógica al MS-3 Docentes/Alumnos.
    # No es FK real.
    id_alumno: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    matricula: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )

    estado_asistencia: Mapped[EstadoAsistencia] = mapped_column(
        Enum(
            EstadoAsistencia,
            name="estado_asistencia_enum",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        index=True,
    )

    identificador_qr: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    fecha_hora_emision_qr: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    fecha_hora_registro: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True,
    )

    metodo_registro: Mapped[MetodoRegistro] = mapped_column(
        Enum(
            MetodoRegistro,
            name="metodo_registro_enum",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=MetodoRegistro.QR,
    )

    observaciones: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
    )

    sesion = relationship(
        "SesionAsistencia",
        back_populates="registros_asistencia",
    )

    __table_args__ = (
        # Un alumno solo puede tener un registro por sesión.
        UniqueConstraint(
            "id_sesion",
            "id_alumno",
            name="uq_registro_asistencia_sesion_alumno",
        ),
    )

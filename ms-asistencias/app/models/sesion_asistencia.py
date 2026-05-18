from datetime import datetime

from sqlalchemy import DateTime, Enum, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import EstadoSesion


class SesionAsistencia(Base):
    __tablename__ = "sesiones_asistencia"

    id_sesion: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Referencia lógica al MS-2 Periodos/Materias.
    # No es FK real porque la materia pertenece a otro microservicio.
    id_materia: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    # Referencia lógica al MS-3 Docentes/Alumnos.
    # No es FK real porque el docente pertenece a otro microservicio.
    id_docente: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    estado_sesion: Mapped[EstadoSesion] = mapped_column(
        Enum(
            EstadoSesion,
            name="estado_sesion_enum",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        default=EstadoSesion.ACTIVA,
        index=True,
    )

    fecha_hora_inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_hora_limite_presente: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_hora_fin: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_hora_cierre: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    registros_asistencia = relationship(
        "RegistroAsistencia",
        back_populates="sesion",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tokens_qr_usados = relationship(
        "TokenQrUsado",
        back_populates="sesion",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# Regla de negocio:
# No debe existir más de una sesión ACTIVA para la misma materia.
Index(
    "idx_unica_sesion_activa_por_materia",
    SesionAsistencia.id_materia,
    unique=True,
    postgresql_where=text("estado_sesion = 'ACTIVA'"),
)

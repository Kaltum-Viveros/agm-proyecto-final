from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ResultadoValidacionQr


class TokenQrUsado(Base):
    __tablename__ = "tokens_qr_usados"

    id_token_qr_usado: Mapped[int] = mapped_column(
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

    # Identificador único que viaja dentro del QR cifrado.
    # Sirve para impedir reutilización del mismo QR.
    identificador_unico_qr: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    # Hash del token completo. No se guarda el token completo por seguridad.
    huella_token: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
    )

    fecha_hora_emision: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    fecha_hora_expiracion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    fecha_hora_uso: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    resultado_validacion: Mapped[ResultadoValidacionQr] = mapped_column(
        Enum(
            ResultadoValidacionQr,
            name="resultado_validacion_qr_enum",
            native_enum=False,
            length=20,
        ),
        nullable=False,
        index=True,
    )

    motivo_rechazo: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    sesion = relationship(
        "SesionAsistencia",
        back_populates="tokens_qr_usados",
    )

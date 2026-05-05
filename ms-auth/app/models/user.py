import uuid

from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    nombre_completo = Column(
        String(150),
        nullable=False,
    )
    email = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True,
    )
    contrasena_hash = Column(
        String(255),
        nullable=False,
    )
    rol = Column(
        Enum(
            UserRole,
            name="user_role_enum",
            native_enum=False,
        ),
        nullable=False,
    )
    activo = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    auth_tokens = relationship(
        "AuthToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
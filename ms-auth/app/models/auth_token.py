import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.enums import TokenStatus, TokenType


class AuthToken(Base):
    __tablename__ = "auth_tokens"

    auth_token_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_type = Column(
        Enum(
            TokenType,
            name="token_type_enum",
            native_enum=False,
        ),
        nullable=False,
    )
    token_hash = Column(
        String(255),
        nullable=True,
        index=True,
    )
    jti = Column(
        String(120),
        nullable=True,
        index=True,
    )
    expiracion = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    estado = Column(
        Enum(
            TokenStatus,
            name="token_status_enum",
            native_enum=False,
        ),
        nullable=False,
        default=TokenStatus.ACTIVE,
    )
    creacion = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    user = relationship(
        "User",
        back_populates="auth_tokens",
    )
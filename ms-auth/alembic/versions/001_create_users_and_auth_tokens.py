"""create users and auth_tokens tables

Revision ID: 001_create_users_and_auth_tokens
Revises: None
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Optional, Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "001_create_users_and_auth_tokens"
down_revision: Optional[str] = None
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "nombre_completo",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "contrasena_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "rol",
            sa.Enum(
                "ADMIN",
                "DOCENTE",
                "ALUMNO",
                name="user_role_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "activo",
            sa.Boolean(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_index(
        "ix_users_user_id",
        "users",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    op.create_table(
        "auth_tokens",
        sa.Column(
            "auth_token_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "token_type",
            sa.Enum(
                "REFRESH",
                "PASSWORD_RESET",
                "REVOKED_ACCESS",
                name="token_type_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "token_hash",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "jti",
            sa.String(length=120),
            nullable=True,
        ),
        sa.Column(
            "expiracion",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "ACTIVE",
                "USED",
                "REVOKED",
                "EXPIRED",
                name="token_status_enum",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "creacion",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("auth_token_id"),
    )

    op.create_index(
        "ix_auth_tokens_auth_token_id",
        "auth_tokens",
        ["auth_token_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_tokens_user_id",
        "auth_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_tokens_token_hash",
        "auth_tokens",
        ["token_hash"],
        unique=False,
    )

    op.create_index(
        "ix_auth_tokens_jti",
        "auth_tokens",
        ["jti"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_auth_tokens_jti",
        table_name="auth_tokens",
    )

    op.drop_index(
        "ix_auth_tokens_token_hash",
        table_name="auth_tokens",
    )

    op.drop_index(
        "ix_auth_tokens_user_id",
        table_name="auth_tokens",
    )

    op.drop_index(
        "ix_auth_tokens_auth_token_id",
        table_name="auth_tokens",
    )

    op.drop_table("auth_tokens")

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_index(
        "ix_users_user_id",
        table_name="users",
    )

    op.drop_table("users")
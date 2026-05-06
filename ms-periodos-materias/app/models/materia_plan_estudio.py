import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.materia_catalogo import MateriaCatalogo
    from app.models.plan_estudio import PlanEstudio


class MateriaPlanEstudio(Base):
    __tablename__ = "materia_plan_estudio"

    materia_plan_estudio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    materia_catalogo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("materias_catalogo.materia_catalogo_id", ondelete="CASCADE"),
        nullable=False,
    )

    plan_estudio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("planes_estudio.plan_estudio_id", ondelete="CASCADE"),
        nullable=False,
    )

    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    materia_catalogo: Mapped["MateriaCatalogo"] = relationship(
        back_populates="planes_estudio",
    )

    plan_estudio: Mapped["PlanEstudio"] = relationship(
        back_populates="materias",
    )

    __table_args__ = (
        UniqueConstraint(
            "materia_catalogo_id",
            "plan_estudio_id",
            name="uq_materia_plan_estudio",
        ),
    )
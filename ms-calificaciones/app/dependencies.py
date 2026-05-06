from collections.abc import Generator

from fastapi import HTTPException, status

from app.core.config import settings

from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository
from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository

from app.services.actividad_service import ActividadService
from app.services.calificacion_service import CalificacionService
from app.services.concentrado_service import ConcentradoService
from app.services.importacion_calificaciones_service import ImportacionCalificacionesService
from app.services.ponderacion_service import PonderacionService


ponderacion_memory_repository = PonderacionMemoryRepository()
actividad_memory_repository = ActividadMemoryRepository()
calificacion_memory_repository = CalificacionMemoryRepository()


def _validate_storage_mode() -> None:
    if settings.storage_mode not in ["memory", "database"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="STORAGE_MODE debe ser 'memory' o 'database'",
        )


def get_ponderacion_service() -> Generator[PonderacionService, None, None]:
    _validate_storage_mode()

    if settings.storage_mode == "database":
        from app.db.session import SessionLocal
        from app.repositories.sqlalchemy.actividad_repository import (
            ActividadRepository as SqlAlchemyActividadRepository,
        )
        from app.repositories.sqlalchemy.ponderacion_repository import (
            PonderacionRepository as SqlAlchemyPonderacionRepository,
        )

        db = SessionLocal()

        try:
            yield PonderacionService(
                repository=SqlAlchemyPonderacionRepository(db),
                actividad_repository=SqlAlchemyActividadRepository(db),
            )
        finally:
            db.close()

        return

    yield PonderacionService(
        repository=ponderacion_memory_repository,
        actividad_repository=actividad_memory_repository,
    )


def get_actividad_service() -> Generator[ActividadService, None, None]:
    _validate_storage_mode()

    if settings.storage_mode == "database":
        from app.db.session import SessionLocal
        from app.repositories.sqlalchemy.actividad_repository import (
            ActividadRepository as SqlAlchemyActividadRepository,
        )
        from app.repositories.sqlalchemy.calificacion_repository import (
            CalificacionRepository as SqlAlchemyCalificacionRepository,
        )
        from app.repositories.sqlalchemy.ponderacion_repository import (
            PonderacionRepository as SqlAlchemyPonderacionRepository,
        )

        db = SessionLocal()

        try:
            yield ActividadService(
                actividad_repository=SqlAlchemyActividadRepository(db),
                ponderacion_repository=SqlAlchemyPonderacionRepository(db),
                calificacion_repository=SqlAlchemyCalificacionRepository(db),
            )
        finally:
            db.close()

        return

    yield ActividadService(
        actividad_repository=actividad_memory_repository,
        ponderacion_repository=ponderacion_memory_repository,
        calificacion_repository=calificacion_memory_repository,
    )


def get_calificacion_service() -> Generator[CalificacionService, None, None]:
    _validate_storage_mode()

    if settings.storage_mode == "database":
        from app.db.session import SessionLocal
        from app.repositories.sqlalchemy.actividad_repository import (
            ActividadRepository as SqlAlchemyActividadRepository,
        )
        from app.repositories.sqlalchemy.calificacion_repository import (
            CalificacionRepository as SqlAlchemyCalificacionRepository,
        )

        db = SessionLocal()

        try:
            yield CalificacionService(
                calificacion_repository=SqlAlchemyCalificacionRepository(db),
                actividad_repository=SqlAlchemyActividadRepository(db),
            )
        finally:
            db.close()

        return

    yield CalificacionService(
        calificacion_repository=calificacion_memory_repository,
        actividad_repository=actividad_memory_repository,
    )


def get_importacion_calificaciones_service() -> Generator[ImportacionCalificacionesService, None, None]:
    _validate_storage_mode()

    if settings.storage_mode == "database":
        from app.db.session import SessionLocal
        from app.repositories.sqlalchemy.actividad_repository import (
            ActividadRepository as SqlAlchemyActividadRepository,
        )
        from app.repositories.sqlalchemy.calificacion_repository import (
            CalificacionRepository as SqlAlchemyCalificacionRepository,
        )

        db = SessionLocal()

        try:
            yield ImportacionCalificacionesService(
                calificacion_repository=SqlAlchemyCalificacionRepository(db),
                actividad_repository=SqlAlchemyActividadRepository(db),
            )
        finally:
            db.close()

        return

    yield ImportacionCalificacionesService(
        calificacion_repository=calificacion_memory_repository,
        actividad_repository=actividad_memory_repository,
    )


def get_concentrado_service() -> Generator[ConcentradoService, None, None]:
    _validate_storage_mode()

    if settings.storage_mode == "database":
        from app.db.session import SessionLocal
        from app.repositories.sqlalchemy.actividad_repository import (
            ActividadRepository as SqlAlchemyActividadRepository,
        )
        from app.repositories.sqlalchemy.calificacion_repository import (
            CalificacionRepository as SqlAlchemyCalificacionRepository,
        )
        from app.repositories.sqlalchemy.ponderacion_repository import (
            PonderacionRepository as SqlAlchemyPonderacionRepository,
        )

        db = SessionLocal()

        try:
            yield ConcentradoService(
                ponderacion_repository=SqlAlchemyPonderacionRepository(db),
                actividad_repository=SqlAlchemyActividadRepository(db),
                calificacion_repository=SqlAlchemyCalificacionRepository(db),
            )
        finally:
            db.close()

        return

    yield ConcentradoService(
        ponderacion_repository=ponderacion_memory_repository,
        actividad_repository=actividad_memory_repository,
        calificacion_repository=calificacion_memory_repository,
    )
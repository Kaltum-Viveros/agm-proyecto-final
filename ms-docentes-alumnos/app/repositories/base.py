from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        # Esta línea busca dinámicamente la llave primaria del modelo (docente_id, alumno_id, etc.)
        pk_name = inspect(self.model).primary_key[0].name
        return db.query(self.model).filter(getattr(self.model, pk_name) == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
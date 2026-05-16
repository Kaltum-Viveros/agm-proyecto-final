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

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> ModelType:
        pk_name = inspect(self.model).primary_key[0].name
        obj = db.query(self.model).filter(getattr(self.model, pk_name) == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
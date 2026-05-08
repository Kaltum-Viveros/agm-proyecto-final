from typing import Any

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, instance: Any) -> Any:
        try:
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception:
            self.db.rollback()
            raise

    def commit_changes(self, instance: Any) -> Any:
        try:
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception:
            self.db.rollback()
            raise
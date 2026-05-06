# Acceso a datos
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion

def crear_notificacion(db: Session, data):
    nueva = Notificacion(**data.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva
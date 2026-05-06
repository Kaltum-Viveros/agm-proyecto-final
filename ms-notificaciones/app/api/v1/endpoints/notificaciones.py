from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.notificacion import NotificacionCreate, NotificacionResponse
from app.services import notificacion_service
from app.core.database import SessionLocal

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NotificacionResponse)
def crear_notificacion(data: NotificacionCreate, db: Session = Depends(get_db)):
    return notificacion_service.crear_notificacion(db, data)
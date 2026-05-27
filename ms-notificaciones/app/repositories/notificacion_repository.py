# Acceso a datos
from sqlalchemy.orm import Session
from app.models.notificacion import Notificacion

def crear_notificacion(
    db: Session, 
    usuario_id: int, 
    email: str, 
    tipo: str, 
    asunto: str, 
    mensaje: str,
    estado: str = "pendiente"
):
    nueva = Notificacion(
        usuario_id=usuario_id,
        email=email,
        tipo=tipo,
        asunto=asunto,
        mensaje=mensaje,
        estado=estado
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

def obtener_notificaciones(db: Session):
    return db.query(Notificacion).all()

def obtener_por_usuario(db: Session, usuario_id: int):
    return db.query(Notificacion).filter(Notificacion.usuario_id == usuario_id).all()

def obtener_por_id(db: Session, notificacion_id: int):
    return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()

def existe_enviada_por_email_y_tipo(db: Session, email: str, tipos: list[str]):
    if not email:
        return False
    return db.query(Notificacion).filter(
        Notificacion.email == email,
        Notificacion.tipo.in_(tipos),
        Notificacion.estado == "enviada",
    ).first() is not None

def actualizar_estado(db: Session, db_notificacion: Notificacion, estado: str, fecha_envio=None):
    db_notificacion.estado = estado
    if fecha_envio:
        db_notificacion.fecha_envio = fecha_envio
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion

def marcar_enviada(db: Session, notificacion_id: int):
    """Marca la notificación como enviada con fecha/hora actual."""
    from datetime import datetime, timezone
    notif = obtener_por_id(db, notificacion_id)
    if notif:
        return actualizar_estado(db, notif, "enviada", datetime.now(timezone.utc))
    return None

def marcar_fallida(db: Session, notificacion_id: int):
    """Marca la notificación como fallida."""
    notif = obtener_por_id(db, notificacion_id)
    if notif:
        return actualizar_estado(db, notif, "fallida")
    return None

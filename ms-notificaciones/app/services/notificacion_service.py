# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest
from app.services.email_service import enviar_correo_background
from app.models.plantilla import Plantilla

from app.grpc.clients.alumnos_client import alumnos_client
from app.grpc.clients.materias_client import materias_client

def renderizar_plantilla(db: Session, slug: str, contexto: dict) -> tuple[str, str]:
    """Busca la plantilla en BD y reemplaza las variables dinámicas {{llave}}"""
    plantilla = db.query(Plantilla).filter(Plantilla.slug == slug).first()
    
    if not plantilla:
        # Fallback genérico si no hay plantilla en DB para no crashear
        return f"Notificación: {slug}", f"<p>Alerta: {slug}</p><p>{str(contexto)}</p>"
        
    html = plantilla.html_content
    asunto = plantilla.asunto_base
    for llave, valor in contexto.items():
        html = html.replace(f"{{{{{llave}}}}}", str(valor))
        asunto = asunto.replace(f"{{{{{llave}}}}}", str(valor))
        
    return asunto, html

def procesar_bienvenida(db: Session, data: BienvenidaRequest):
    # 1 y 2: Llamar al cliente gRPC del MS-3 para obtener el email y nombre del alumno
    alumno_data = alumnos_client.obtener_alumno(data.alumno_id)
    email_obtenido = alumno_data.get("email") or "correo_por_defecto@ejemplo.com"
    nombre_obtenido = alumno_data.get("nombre") or "Estudiante"
    
    # 3. Construir HTML dinámico
    asunto, html = renderizar_plantilla(db, "bienvenida", {
        "nombre_obtenido": nombre_obtenido
    })
    
    # 4. Enviar correo en segundo plano
    enviar_correo_background(
        destinatario=email_obtenido,
        asunto=asunto,
        mensaje_html=html
    )
    
    # 5. Guardar en base de datos
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.alumno_id,
        email=email_obtenido,
        tipo="bienvenida",
        asunto=asunto,
        mensaje=f"Plantilla 'bienvenida' procesada para {nombre_obtenido}."
    )
    return notificacion

def procesar_baja(db: Session, data: BajaMateriaRequest):
    # Llamadas a MS-2 y MS-3
    alumno_data = alumnos_client.obtener_alumno(data.alumno_id)
    materia_data = materias_client.obtener_materia(data.materia_id)
    docente_data = alumnos_client.obtener_alumno(data.docente_id) # Suponiendo que MS-3 maneja docentes también
    
    email_docente = docente_data.get("email") or "correo_por_defecto@ejemplo.com"
    nombre_alumno = alumno_data.get("nombre") or str(data.alumno_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    
    asunto, html = renderizar_plantilla(db, "baja_materia", {
        "nombre_alumno": nombre_alumno,
        "nombre_materia": nombre_materia
    })
    
    enviar_correo_background(email_docente, asunto, html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.docente_id,
        email=email_docente,
        tipo="baja_materia",
        asunto=asunto,
        mensaje=f"El alumno {nombre_alumno} se ha dado de baja de la materia {nombre_materia}."
    )
    return notificacion

def procesar_cierre_materia(db: Session, data: CierreMateriaRequest):
    # Llamada a MS-2
    materia_data = materias_client.obtener_materia(data.materia_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    
    # TODO: gRPC para obtener la lista de correos de los alumnos (MS-3) inscritos en la materia (MS-4)
    # TODO: Iterar sobre la lista real cuando esté disponible desde MS-4
    email_mock = "rinava404@gmail.com"
    
    asunto, html = renderizar_plantilla(db, "cierre_materia", {
        "nombre_materia": nombre_materia
    })
    enviar_correo_background(email_mock, asunto, html)

    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=999, # id genérico
        email=email_mock,
        tipo="cierre_materia",
        asunto=asunto,
        mensaje=f"Las notas de la materia {nombre_materia} ya están disponibles."
    )
    return notificacion

def procesar_reset_password(db: Session, data: ResetPasswordRequest):
    asunto, html = renderizar_plantilla(db, "reset_password", {
        "token_simulado": data.reset_token
    })
    enviar_correo_background(data.email, asunto, html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.usuario_id,
        email=data.email,
        tipo="reset_password",
        asunto=asunto,
        mensaje=f"Se envió un token de recuperación a {data.email}."
    )
    return notificacion
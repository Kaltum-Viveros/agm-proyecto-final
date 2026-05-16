# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest
from app.services.email_service import enviar_correo_background
from app.models.plantilla import Plantilla
from app.utils.email_templates import get_default_template

from app.grpc.clients.alumnos_client import alumnos_client
from app.grpc.clients.materias_client import materias_client

def renderizar_plantilla(db: Session, slug: str, contexto: dict) -> tuple[str, str]:
    """Busca la plantilla en BD y reemplaza las variables dinámicas {{llave}}"""
    plantilla = db.query(Plantilla).filter(Plantilla.slug == slug).first()
    
    if not plantilla:
        asunto, html = get_default_template(slug)
    else:
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
    
    # 3. Preparar mensaje dinámico para la contraseña
    if data.password_temporal:
        mensaje_password = f"""
        <div style="margin: 20px 0; padding: 20px; background-color: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;">
            <p style="margin: 0; color: #0369a1; font-size: 15px;">Tu contraseña provisional de acceso es:</p>
            <p style="margin: 10px 0 0 0; color: #0c4a6e; font-size: 26px; font-weight: bold; letter-spacing: 3px;">{data.password_temporal}</p>
            <p style="margin: 10px 0 0 0; color: #0284c7; font-size: 13px;">Te recomendamos cambiarla en cuanto inicies sesión por primera vez.</p>
        </div>
        """
    else:
        mensaje_password = """
        <div style="margin: 20px 0; padding: 15px; background-color: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;">
            <p style="margin: 0; color: #166534; font-size: 15px;"><strong>¡Aviso!</strong> Notamos que ya cuentas con una cuenta activa en la plataforma. Puedes seguir utilizando tu contraseña habitual para iniciar sesión y acceder a esta nueva materia.</p>
        </div>
        """

    # 4. Construir HTML dinámico
    asunto, html = renderizar_plantilla(db, "bienvenida", {
        "nombre_obtenido": nombre_obtenido,
        "mensaje_password": mensaje_password
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
    docente_data = alumnos_client.obtener_docente(data.docente_id)
    
    email_alumno = alumno_data.get("email") or "correo_por_defecto@ejemplo.com"
    nombre_alumno = alumno_data.get("nombre") or str(data.alumno_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    nombre_docente = docente_data.get("nombre") or "Tu docente"
    
    asunto, html = renderizar_plantilla(db, "baja_materia", {
        "nombre_alumno": nombre_alumno,
        "nombre_materia": nombre_materia,
        "nombre_docente": nombre_docente
    })
    
    enviar_correo_background(email_alumno, asunto, html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.alumno_id,
        email=email_alumno,
        tipo="baja_materia",
        asunto=asunto,
        mensaje=f"El alumno {nombre_alumno} se ha dado de baja de la materia {nombre_materia}."
    )
    return notificacion

def procesar_cierre_materia(db: Session, data: CierreMateriaRequest):
    # Llamada a MS-2
    materia_data = materias_client.obtener_materia(data.materia_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    
    # Obtener la lista de correos de los alumnos (MS-3) inscritos en la materia (MS-4)
    alumnos = alumnos_client.obtener_alumnos_por_materia(data.materia_id)
    
    asunto, html = renderizar_plantilla(db, "cierre_materia", {
        "nombre_materia": nombre_materia
    })
    
    for alumno in alumnos:
        enviar_correo_background(alumno["email"], asunto, html)

    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id="00000000-0000-0000-0000-000000000000", # id genérico para cierres masivos
        email="multiple_alumnos",
        tipo="cierre_materia",
        asunto=asunto,
        mensaje=f"Las notas de la materia {nombre_materia} ya están disponibles. Notificados {len(alumnos)} alumnos."
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
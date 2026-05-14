# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest
from app.services.email_service import enviar_correo_background

from app.grpc.clients.alumnos_client import alumnos_client
from app.grpc.clients.materias_client import materias_client

def procesar_bienvenida(db: Session, data: BienvenidaRequest):
    # 1 y 2: Llamar al cliente gRPC del MS-3 para obtener el email y nombre del alumno
    alumno_data = alumnos_client.obtener_alumno(data.alumno_id)
    email_obtenido = alumno_data.get("email") or "correo_por_defecto@ejemplo.com"
    nombre_obtenido = alumno_data.get("nombre") or "Estudiante"
    
    # 3. Construir HTML
    html = f"<h1>¡Bienvenido a AGM, {nombre_obtenido}!</h1><p>Tu cuenta ha sido creada exitosamente. Esperamos que disfrutes la plataforma.</p>"
    
    # 4. Enviar correo en segundo plano
    enviar_correo_background(
        destinatario=email_obtenido,
        asunto="¡Bienvenido a AGM!",
        mensaje_html=html
    )
    
    # 5. Guardar en base de datos
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.alumno_id,
        email=email_obtenido,
        tipo="bienvenida",
        asunto="¡Bienvenido a AGM!",
        mensaje="Tu cuenta ha sido creada exitosamente."
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
    
    html = f"<h3>Baja de Alumno</h3><p>Estimado Docente, el alumno <b>{nombre_alumno}</b> se ha dado de baja de la materia <b>{nombre_materia}</b>.</p>"
    
    enviar_correo_background(email_docente, "Baja de Alumno en tu Materia", html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.docente_id,
        email=email_docente,
        tipo="baja_materia",
        asunto="Baja de Alumno en tu Materia",
        mensaje=f"El alumno {nombre_alumno} se ha dado de baja de la materia {nombre_materia}."
    )
    return notificacion

def procesar_cierre_materia(db: Session, data: CierreMateriaRequest):
    # Llamada a MS-2
    materia_data = materias_client.obtener_materia(data.materia_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    
    # TODO: gRPC para obtener la lista de correos de los alumnos (MS-3) inscritos en la materia (MS-4)
    # Por ahora simulamos 1 solo correo (Se reemplaza por un ciclo for cuando tengamos la lista real)
    email_mock = "rinava404@gmail.com"
    
    html = f"<h2>Cierre de Actas Oficial</h2><p>Estimado Alumno, las calificaciones de la materia <b>{nombre_materia}</b> han sido publicadas en el sistema.</p>"
    enviar_correo_background(email_mock, "Cierre de Actas - Materia", html)

    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=999, # id genérico
        email=email_mock,
        tipo="cierre_materia",
        asunto="Cierre de Actas - Materia",
        mensaje=f"Las notas de la materia {nombre_materia} ya están disponibles."
    )
    return notificacion

def procesar_reset_password(db: Session, data: ResetPasswordRequest):
    # TODO: gRPC para obtener email del usuario
    email_usuario = "rinava404@gmail.com"
    token_simulado = "abc-123-xyz"
    
    html = f"<h2>Recuperación de Acceso</h2><p>Haz solicitado un cambio de contraseña. Usa este token para restaurarla: <br><br><b>{token_simulado}</b></p>"
    enviar_correo_background(email_usuario, "Recuperación de Contraseña", html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.usuario_id,
        email=email_usuario,
        tipo="reset_password",
        asunto="Recuperación de Contraseña",
        mensaje=f"Usa este token para recuperar tu contraseña: {token_simulado}"
    )
    return notificacion
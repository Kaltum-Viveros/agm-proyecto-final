# Lógica de negocio 
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest
from app.services.email_service import enviar_correo_background

# TODO: Importar los clientes gRPC

def procesar_bienvenida(db: Session, data: BienvenidaRequest):
    # TODO: 1. Llamar al cliente gRPC del MS-3 para obtener el email y nombre del alumno
    # TODO: 2. Construir el mensaje de bienvenida
    # TODO: 3. Llamar al EmailService para enviar el correo (en background)
    # Mock momentáneo:
    email_obtenido = "rinava404@gmail.com" # TODO: Quitar cuando gRPC MS-3 funcione
    nombre_obtenido = "Estudiante Nuevo"
    
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
    # TODO: gRPC para obtener nombre del alumno (MS-3), materia (MS-2) y email del docente (MS-3/Docentes)
    email_docente = "rinava404@gmail.com" # TODO: Quitar cuando gRPC funcione
    
    html = f"<h3>Baja de Alumno</h3><p>Estimado Docente, el alumno con ID <b>{data.alumno_id}</b> se ha dado de baja de la materia <b>{data.materia_id}</b>.</p>"
    
    enviar_correo_background(email_docente, "Baja de Alumno en tu Materia", html)
    
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.docente_id,
        email=email_docente,
        tipo="baja_materia",
        asunto="Baja de Alumno en tu Materia",
        mensaje=f"El alumno {data.alumno_id} se ha dado de baja de la materia {data.materia_id}."
    )
    return notificacion

def procesar_cierre_materia(db: Session, data: CierreMateriaRequest):
    # TODO: gRPC para obtener la lista de correos de los alumnos (MS-3) inscritos en la materia (MS-4)
    # Por cada alumno se debería enviar un correo y guardar el registro.
    # Aquí simularemos que le llega a 1 alumno representativo para el endpoint de prueba.
    email_mock = "rinava404@gmail.com"
    
    html = f"<h2>Cierre de Actas Oficial</h2><p>Estimado Alumno, las calificaciones de la materia <b>{data.materia_id}</b> han sido publicadas en el sistema.</p>"
    enviar_correo_background(email_mock, "Cierre de Actas - Materia", html)

    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=999, # id genérico simulado
        email=email_mock,
        tipo="cierre_materia",
        asunto="Cierre de Actas - Materia",
        mensaje=f"Las notas de la materia {data.materia_id} ya están disponibles."
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
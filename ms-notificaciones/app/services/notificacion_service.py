# Lógica de negocio
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import BienvenidaRequest, BajaMateriaRequest, CierreMateriaRequest, ResetPasswordRequest
from app.services.email_service import enviar_correo_con_callback
from app.models.plantilla import Plantilla
from app.utils.email_templates import get_default_template
from app.core.database import SessionLocal

from app.messaging.clients.docentes_hybrid_client import alumnos_client
from app.messaging.clients.periodos_hybrid_client import materias_client


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


def _callback_actualizar_estado(notificacion_id: int, exito: bool):
    """
    Callback invocado en el hilo de envío SMTP para actualizar el estado de la notificación.
    Abre su propia sesión de BD para no compartir la sesión original (ya cerrada).
    """
    estado = "enviada" if exito else "fallida"
    try:
        db = SessionLocal()
        notif = notificacion_repository.obtener_por_id(db, notificacion_id)
        if notif:
            notificacion_repository.actualizar_estado(
                db=db,
                db_notificacion=notif,
                estado=estado,
                fecha_envio=datetime.now(timezone.utc) if exito else None
            )
        db.close()
    except Exception as ex:
        logging.error(f"[MS-6] Error actualizando estado de notificación {notificacion_id}: {ex}")


def procesar_bienvenida(db: Session, data: BienvenidaRequest):
    # 1 y 2: Llamar al cliente gRPC del MS-3 para obtener el email y nombre del alumno
    alumno_data = alumnos_client.obtener_alumno(data.alumno_id)
    email_obtenido = alumno_data.get("email") or "correo_por_defecto@ejemplo.com"
    nombre_obtenido = alumno_data.get("nombre") or "Estudiante"

    # 3. Preparar mensaje dinámico para la contraseña (no se loggea en claro)
    if data.password_temporal:
        mensaje_password = """
        <div style="margin: 20px 0; padding: 20px; background-color: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;">
            <p style="margin: 0; color: #0369a1; font-size: 15px;">Tu contraseña provisional de acceso está disponible en el portal.</p>
            <p style="margin: 10px 0 0 0; color: #0284c7; font-size: 13px;">Te recomendamos cambiarla en cuanto inicies sesión por primera vez.</p>
        </div>
        """
    else:
        mensaje_password = """
        <div style="margin: 20px 0; padding: 15px; background-color: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;">
            <p style="margin: 0; color: #166534; font-size: 15px;"><strong>¡Aviso!</strong> Notamos que ya cuentas con una cuenta activa en la plataforma. Puedes seguir utilizando tu contraseña habitual.</p>
        </div>
        """

    # 4. Construir HTML dinámico
    asunto, html = renderizar_plantilla(db, "bienvenida", {
        "nombre_obtenido": nombre_obtenido,
        "mensaje_password": mensaje_password
    })

    # 5. Guardar en base de datos (estado inicial: pendiente)
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.alumno_id,
        email=email_obtenido,
        tipo="bienvenida",
        asunto=asunto,
        mensaje=f"Plantilla 'bienvenida' procesada para {nombre_obtenido}."
    )

    # 6. Enviar correo en segundo plano, actualizando estado al terminar
    notificacion_id = notificacion.id
    enviar_correo_con_callback(
        destinatario=email_obtenido,
        asunto=asunto,
        mensaje_html=html,
        callback=lambda exito: _callback_actualizar_estado(notificacion_id, exito)
    )

    return notificacion


def procesar_baja(
    db: Session,
    data: BajaMateriaRequest,
    materia_data: dict | None = None,
    alumno_data: dict | None = None,
    docente_data: dict | None = None,
):
    """
    Notifica al alumno cuando se registra su baja de una materia.
    El docente se usa solo como contexto del mensaje.
    """
    # Obtener datos desde MS-3 y MS-2
    alumno_data = alumno_data or alumnos_client.obtener_alumno(data.alumno_id)
    materia_data = materia_data or materias_client.obtener_materia(data.materia_id)
    docente_data = docente_data or alumnos_client.obtener_docente(data.docente_id)

    nombre_alumno = alumno_data.get("nombre") or str(data.alumno_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)
    nombre_docente = docente_data.get("nombre") or "Docente"
    email_alumno = alumno_data.get("email") or alumno_data.get("correo")

    asunto, html = renderizar_plantilla(db, "baja_materia", {
        "nombre_alumno": nombre_alumno,
        "nombre_materia": nombre_materia,
        "nombre_docente": nombre_docente
    })

    if not email_alumno:
        logging.error("No se pudo enviar notificación de baja: alumno sin correo")
        return notificacion_repository.crear_notificacion(
            db=db,
            usuario_id=data.alumno_id,
            email="",
            tipo="baja_materia",
            asunto=asunto,
            mensaje=(
                "No se pudo enviar notificación de baja: alumno sin correo. "
                f"alumno_id={data.alumno_id}, materia_id={data.materia_id}"
            ),
            estado="fallida"
        )

    # Guardar en BD con el email del alumno como destinatario (estado inicial: pendiente)
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.alumno_id,
        email=email_alumno,
        tipo="baja_materia",
        asunto=asunto,
        mensaje=f"El alumno {nombre_alumno} se dio de baja de la materia {nombre_materia} impartida por {nombre_docente}."
    )

    # Enviar correo al alumno en segundo plano, actualizando estado al terminar
    notificacion_id = notificacion.id
    enviar_correo_con_callback(
        destinatario=email_alumno,
        asunto=asunto,
        mensaje_html=html,
        callback=lambda exito: _callback_actualizar_estado(notificacion_id, exito)
    )

    return notificacion


async def procesar_baja_async(db: Session, data: BajaMateriaRequest):
    materia_data = await materias_client.obtener_materia_async(data.materia_id)
    alumno_data = await alumnos_client.obtener_alumno_async(data.alumno_id)
    docente_data = await alumnos_client.obtener_docente_async(data.docente_id)
    return procesar_baja(
        db,
        data,
        materia_data=materia_data,
        alumno_data=alumno_data,
        docente_data=docente_data,
    )


def procesar_cierre_materia(
    db: Session,
    data: CierreMateriaRequest,
    materia_data: dict | None = None,
    alumnos: list | None = None,
):
    # Llamada a MS-2
    materia_data = materia_data or materias_client.obtener_materia(data.materia_id)
    nombre_materia = materia_data.get("nombre") or str(data.materia_id)

    # Obtener la lista de correos de los alumnos (MS-3) inscritos en la materia (MS-2)
    alumnos = alumnos if alumnos is not None else alumnos_client.obtener_alumnos_por_materia(data.materia_id)

    asunto, html = renderizar_plantilla(db, "cierre_materia", {
        "nombre_materia": nombre_materia
    })

    # Guardar registro de la notificación masiva (estado inicial: pendiente)
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id="00000000-0000-0000-0000-000000000000",  # id genérico para cierres masivos
        email="multiple_alumnos",
        tipo="cierre_materia",
        asunto=asunto,
        mensaje=f"Las notas de la materia {nombre_materia} ya están disponibles. Notificados {len(alumnos)} alumnos."
    )

    # Enviar correo a cada alumno en segundo plano (sin callback individual por ser masivo)
    for alumno in alumnos:
        enviar_correo_con_callback(
            destinatario=alumno["email"],
            asunto=asunto,
            mensaje_html=html,
            callback=None
        )

    # Marcar como enviada después de disparar todos los hilos
    notificacion_id = notificacion.id
    _callback_actualizar_estado(notificacion_id, True)

    return notificacion


async def procesar_cierre_materia_async(db: Session, data: CierreMateriaRequest):
    materia_data = await materias_client.obtener_materia_async(data.materia_id)
    alumnos = await alumnos_client.obtener_alumnos_por_materia_async(data.materia_id)
    return procesar_cierre_materia(db, data, materia_data=materia_data, alumnos=alumnos)


def procesar_reset_password(db: Session, data: ResetPasswordRequest):
    # El token real va al cuerpo del correo, pero no se loggea en claro en logs del sistema
    asunto, html = renderizar_plantilla(db, "reset_password", {
        "token_simulado": data.reset_token
    })

    # Guardar en BD (estado inicial: pendiente)
    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.usuario_id,
        email=data.email,
        tipo="reset_password",
        asunto=asunto,
        mensaje=f"Se envió un token de recuperación a {data.email}."  # No se loggea el token
    )

    notificacion_id = notificacion.id
    enviar_correo_con_callback(
        destinatario=data.email,
        asunto=asunto,
        mensaje_html=html,
        callback=lambda exito: _callback_actualizar_estado(notificacion_id, exito)
    )

    return notificacion

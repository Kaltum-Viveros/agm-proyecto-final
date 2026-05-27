# Lógica de negocio
import asyncio
import logging
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.repositories import notificacion_repository
from app.schemas.notificacion_schema import (
    BajaMateriaRequest,
    BienvenidaDocenteRequest,
    BienvenidaRequest,
    CierreMateriaRequest,
    ResetPasswordRequest,
)
from app.services.email_service import enviar_correo_con_callback, enviar_correo_sincrono
from app.models.plantilla import Plantilla
from app.utils.email_templates import get_default_template
from app.core.database import SessionLocal

from app.messaging.clients.docentes_hybrid_client import alumnos_client
from app.messaging.clients.auth_hybrid_client import auth_client
from app.messaging.clients.periodos_hybrid_client import materias_client


def _extraer_nombre_materia(materia_data: dict | None) -> str:
    if not materia_data:
        return ""

    nested_materia = materia_data.get("materia") or {}
    nombre = (
        materia_data.get("nombre")
        or nested_materia.get("nombre")
        or materia_data.get("materia_nombre")
        or ""
    )
    nombre = str(nombre).strip()
    if "mock" in nombre.lower() or nombre == "Materia Prueba (Mock)":
        logging.error("MS-6 recibio nombre de materia mock desde cliente Periodos: %s", nombre)
        return ""
    return nombre


async def _obtener_contexto_baja(
    data: BajaMateriaRequest,
    materia_data: dict | None,
    alumno_data: dict | None,
    docente_data: dict | None,
) -> tuple[dict, dict, dict]:
    if alumno_data is None:
        alumno_data = await alumnos_client.obtener_alumno_async(data.alumno_id)
    if materia_data is None:
        materia_data = await materias_client.obtener_materia_async(data.materia_id)
    if docente_data is None:
        docente_data = await alumnos_client.obtener_docente_async(data.docente_id)
    return alumno_data or {}, materia_data or {}, docente_data or {}


def _email_real(data: dict | None) -> str:
    if not data:
        return ""
    email = str(data.get("email") or data.get("correo") or "").strip()
    if not email:
        return ""
    invalidos = {
        "correo_por_defecto@ejemplo.com",
        "error@ejemplo.com",
    }
    if email.lower() in invalidos:
        return ""
    return email


def _obtener_token_reset_inicial(email: str, tipo: str) -> str:
    try:
        token_data = asyncio.run(auth_client.create_password_reset_token(email))
    except Exception as exc:
        logging.warning(
            "No se pudo generar token inicial de bienvenida %s para %s: %s",
            tipo,
            email,
            exc,
        )
        return ""

    token = str((token_data or {}).get("token") or "").strip()
    if token:
        logging.info("Token inicial de bienvenida %s generado para %s", tipo, email)
    return token


def _obtener_token_si_primera_bienvenida(
    db: Session,
    email: str,
    tipos: list[str],
    tipo_log: str,
) -> str:
    ya_enviada = notificacion_repository.existe_enviada_por_email_y_tipo(
        db=db,
        email=email,
        tipos=tipos,
    )
    if ya_enviada:
        logging.info(
            "Bienvenida previa encontrada para %s; no se generara token inicial",
            email,
        )
        return ""
    return _obtener_token_reset_inicial(email, tipo_log)


def _mensaje_password_bienvenida(password_temporal: str, reset_token: str = "") -> str:
    if reset_token:
        return f"""
        <div style="margin: 20px 0; padding: 20px; background-color: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;">
            <p style="margin: 0; color: #0369a1; font-size: 15px;">Para configurar tu contraseña inicial, entra al login y usa el flujo de recuperación o restablecimiento de contraseña indicado por el sistema.</p>
            <p style="margin: 10px 0 0 0; color: #0284c7; font-size: 14px;"><strong>Token de recuperación:</strong> {reset_token}</p>
            <p style="margin: 10px 0 0 0; color: #0284c7; font-size: 13px;">Ingresa este token y tu nueva contraseña. No compartas este token.</p>
        </div>
        """

    if password_temporal:
        return ""

    return """
    <div style="margin: 20px 0; padding: 15px; background-color: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;">
        <p style="margin: 0; color: #166534; font-size: 15px;"><strong>¡Aviso!</strong> Notamos que ya cuentas con una cuenta activa en la plataforma. Puedes seguir utilizando tu contraseña habitual.</p>
    </div>
    """


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


def _callback_actualizar_estado(notificacion_id: int, exito: bool, log_success: bool = False):
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
            if exito and log_success:
                mensaje_log = (
                    f"Correo enviado exitosamente a {notif.email} | Asunto: {notif.asunto}"
                )
                logging.info(
                    mensaje_log,
                )
                print(mensaje_log, flush=True)
        db.close()
    except Exception as ex:
        logging.error(f"[MS-6] Error actualizando estado de notificación {notificacion_id}: {ex}")


def procesar_bienvenida(db: Session, data: BienvenidaRequest):
    # 1 y 2: Llamar al cliente gRPC del MS-3 para obtener el email y nombre del alumno
    alumno_data = alumnos_client.obtener_alumno(data.alumno_id)
    email_obtenido = _email_real(alumno_data)
    if not email_obtenido:
        docente_data = alumnos_client.obtener_docente(data.alumno_id)
        if _email_real(docente_data):
            logging.info(
                "SendBienvenida recibio un ID de docente; procesando bienvenida_docente. docente_id=%s",
                data.alumno_id,
            )
            return procesar_bienvenida_docente(
                db,
                BienvenidaDocenteRequest(
                    docente_id=data.alumno_id,
                    password_temporal=data.password_temporal,
                ),
                docente_data=docente_data,
            )

        logging.error(
            "No se pudo enviar bienvenida de alumno: alumno sin correo real. alumno_id=%s",
            data.alumno_id,
        )
        return notificacion_repository.crear_notificacion(
            db=db,
            usuario_id=data.alumno_id,
            email="",
            tipo="bienvenida",
            asunto="Bienvenido a AGM",
            mensaje=f"No se pudo enviar bienvenida: alumno sin correo real. alumno_id={data.alumno_id}",
            estado="fallida",
        )
    nombre_obtenido = alumno_data.get("nombre") or "Estudiante"
    reset_token = _obtener_token_si_primera_bienvenida(
        db=db,
        email=email_obtenido,
        tipos=["bienvenida", "bienvenida_alumno"],
        tipo_log="alumno",
    )

    # 3. Preparar mensaje dinámico para la contraseña (no se loggea en claro)
    if data.password_temporal:
        mensaje_password = ""
    else:
        mensaje_password = """
        <div style="margin: 20px 0; padding: 15px; background-color: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;">
            <p style="margin: 0; color: #166534; font-size: 15px;"><strong>¡Aviso!</strong> Notamos que ya cuentas con una cuenta activa en la plataforma. Puedes seguir utilizando tu contraseña habitual.</p>
        </div>
        """

    # 4. Construir HTML dinámico
    mensaje_password = _mensaje_password_bienvenida(
        data.password_temporal,
        reset_token=reset_token,
    )

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
        mensaje=(
            f"Plantilla 'bienvenida' procesada para {nombre_obtenido}."
            + (f" Token de recuperacion inicial: {reset_token}" if reset_token else "")
        )
    )

    # 6. Enviar correo en segundo plano, actualizando estado al terminar
    notificacion_id = notificacion.id
    enviar_correo_con_callback(
        destinatario=email_obtenido,
        asunto=asunto,
        mensaje_html=html,
        callback=lambda exito: _callback_actualizar_estado(
            notificacion_id,
            exito,
            log_success=True,
        )
    )

    return notificacion


def procesar_bienvenida_docente(
    db: Session,
    data: BienvenidaDocenteRequest,
    docente_data: dict | None = None,
):
    docente_data = docente_data or alumnos_client.obtener_docente(data.docente_id)
    email_docente = _email_real(docente_data)
    nombre_docente = docente_data.get("nombre") or "Docente"

    if not email_docente:
        logging.error(
            "No se pudo enviar bienvenida de docente: docente sin correo real. docente_id=%s",
            data.docente_id,
        )
        return notificacion_repository.crear_notificacion(
            db=db,
            usuario_id=data.docente_id,
            email="",
            tipo="bienvenida_docente",
            asunto="Bienvenido a AGM",
            mensaje=f"No se pudo enviar bienvenida docente: docente sin correo real. docente_id={data.docente_id}",
            estado="fallida",
        )

    reset_token = _obtener_token_si_primera_bienvenida(
        db=db,
        email=email_docente,
        tipos=["bienvenida_docente"],
        tipo_log="docente",
    )

    asunto, html = renderizar_plantilla(db, "bienvenida_docente", {
        "nombre_docente": nombre_docente,
        "nombre_obtenido": nombre_docente,
        "mensaje_password": _mensaje_password_bienvenida(
            data.password_temporal,
            reset_token=reset_token,
        ),
    })

    notificacion = notificacion_repository.crear_notificacion(
        db=db,
        usuario_id=data.docente_id,
        email=email_docente,
        tipo="bienvenida_docente",
        asunto=asunto,
        mensaje=(
            f"Plantilla 'bienvenida_docente' procesada para {nombre_docente}."
            + (f" Token de recuperacion inicial: {reset_token}" if reset_token else "")
        )
    )

    notificacion_id = notificacion.id
    enviar_correo_con_callback(
        destinatario=email_docente,
        asunto=asunto,
        mensaje_html=html,
        callback=lambda exito: _callback_actualizar_estado(
            notificacion_id,
            exito,
            log_success=True,
        )
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
    # Obtener datos desde MS-3 y MS-2. En el flujo gRPC sincronico se resuelven
    # en un solo event loop para no reutilizar conexiones RabbitMQ cerradas.
    if alumno_data is None or materia_data is None or docente_data is None:
        alumno_data, materia_data, docente_data = asyncio.run(
            _obtener_contexto_baja(data, materia_data, alumno_data, docente_data)
        )

    nombre_alumno = alumno_data.get("nombre") or str(data.alumno_id)
    nombre_materia = _extraer_nombre_materia(materia_data)
    nombre_docente = docente_data.get("nombre") or "Docente"
    email_alumno = alumno_data.get("email") or alumno_data.get("correo")

    if not nombre_materia:
        logging.error(
            "No se pudo enviar notificacion de baja: materia no encontrada o sin nombre. materia_id=%s",
            data.materia_id,
        )
        return notificacion_repository.crear_notificacion(
            db=db,
            usuario_id=data.alumno_id,
            email=email_alumno or "",
            tipo="baja_materia",
            asunto="Notificacion de Baja de Materia",
            mensaje=(
                "No se pudo enviar notificacion de baja: materia no encontrada o sin nombre. "
                f"alumno_id={data.alumno_id}, materia_id={data.materia_id}"
            ),
            estado="fallida",
        )

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
        callback=lambda exito: _callback_actualizar_estado(
            notificacion_id,
            exito,
            log_success=True,
        )
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
    materia_data = materia_data or materias_client.obtener_materia(data.materia_id)
    nombre_materia = _extraer_nombre_materia(materia_data) or "Materia no encontrada"

    alumnos = alumnos if alumnos is not None else alumnos_client.obtener_alumnos_por_materia(data.materia_id)

    asunto, html = renderizar_plantilla(db, "cierre_materia", {
        "nombre_materia": nombre_materia
    })

    total = len(alumnos)
    enviados = 0
    fallidos = 0
    primera_notificacion = None

    for indice, alumno in enumerate(alumnos):
        email_alumno = _email_real(alumno)
        nombre_alumno = alumno.get("nombre") or "Alumno"

        notificacion = notificacion_repository.crear_notificacion(
            db=db,
            usuario_id="00000000-0000-0000-0000-000000000000",
            email=email_alumno,
            tipo="cierre_materia",
            asunto=asunto,
            mensaje=(
                f"Las notas de la materia {nombre_materia} ya están disponibles "
                f"para {nombre_alumno}."
            ),
        )
        primera_notificacion = primera_notificacion or notificacion

        if not email_alumno:
            fallidos += 1
            logging.error(
                "No se pudo enviar cierre_materia: alumno sin correo real. materia_id=%s",
                data.materia_id,
            )
            _callback_actualizar_estado(notificacion.id, False)
        else:
            exito = enviar_correo_sincrono(
                destinatario=email_alumno,
                asunto=asunto,
                mensaje_html=html,
            )
            _callback_actualizar_estado(
                notificacion.id,
                exito,
                log_success=exito,
            )
            if exito:
                enviados += 1
            else:
                fallidos += 1

        if indice < total - 1:
            time.sleep(0.75)

    if primera_notificacion is None:
        primera_notificacion = notificacion_repository.crear_notificacion(
            db=db,
            usuario_id="00000000-0000-0000-0000-000000000000",
            email="multiple_alumnos",
            tipo="cierre_materia",
            asunto=asunto,
            mensaje=f"No se encontraron alumnos para notificar en {nombre_materia}.",
            estado="enviada",
        )

    resumen = (
        f"Resumen cierre_materia total={total} enviados={enviados} fallidos={fallidos} "
        f"materia_id={data.materia_id}"
    )
    logging.info(resumen)
    print(resumen, flush=True)

    return primera_notificacion


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

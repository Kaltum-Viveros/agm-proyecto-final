import logging
import smtplib
import threading
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Callable, Optional

from app.core.config import settings


SMTP_BACKOFF_SECONDS = (0, 3, 8)


def _es_error_temporal_smtp(error: Exception) -> bool:
    if isinstance(error, smtplib.SMTPResponseException):
        return int(error.smtp_code) == 421
    return isinstance(
        error,
        (
            smtplib.SMTPServerDisconnected,
            TimeoutError,
            ConnectionError,
            OSError,
        ),
    )


def _enviar_correo_una_vez(destinatario: str, asunto: str, mensaje_html: str) -> None:
    msg = MIMEMultipart("alternative", _charset="utf-8")
    msg["Subject"] = Header(asunto, "utf-8")
    msg["From"] = settings.SMTP_USER
    msg["To"] = destinatario

    parte_html = MIMEText(mensaje_html, "html", "utf-8")
    msg.attach(parte_html)

    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
    try:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, destinatario, msg.as_string())
    finally:
        try:
            server.quit()
        except Exception:
            pass


def enviar_correo_sincrono(destinatario: str, asunto: str, mensaje_html: str) -> bool:
    """
    Envia un correo de forma bloqueante.

    Reintenta solamente errores SMTP temporales. Los errores permanentes 5xx
    no se reintentan.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logging.warning(
            "[MS-6] No se ha configurado SMTP_USER o SMTP_PASSWORD. "
            "Simulacion de envio de correo."
        )
        logging.info(f"[MS-6] SIMULACION -> Correo a: {destinatario} | Asunto: {asunto}")
        return True

    ultimo_error: Exception | None = None
    for intento, espera in enumerate(SMTP_BACKOFF_SECONDS, start=1):
        if espera:
            time.sleep(espera)

        try:
            _enviar_correo_una_vez(destinatario, asunto, mensaje_html)
            logging.info(f"[MS-6] Correo enviado exitosamente a {destinatario} | Asunto: {asunto}")
            return True
        except Exception as exc:
            ultimo_error = exc
            temporal = _es_error_temporal_smtp(exc)
            if not temporal or intento == len(SMTP_BACKOFF_SECONDS):
                break
            logging.warning(
                "[MS-6] Error SMTP temporal enviando a %s; reintento %s/%s en %ss: %s",
                destinatario,
                intento + 1,
                len(SMTP_BACKOFF_SECONDS),
                SMTP_BACKOFF_SECONDS[intento],
                exc,
            )

    logging.error(f"[MS-6] Fallo al enviar correo a {destinatario}: {str(ultimo_error)}")
    return False


def _worker_con_callback(
    destinatario: str,
    asunto: str,
    mensaje_html: str,
    callback: Optional[Callable[[bool], None]],
):
    exito = enviar_correo_sincrono(destinatario, asunto, mensaje_html)
    if callback:
        try:
            callback(exito)
        except Exception as exc:
            logging.error(f"[MS-6] Error en callback post-envio para {destinatario}: {exc}")


def enviar_correo_con_callback(
    destinatario: str,
    asunto: str,
    mensaje_html: str,
    callback: Optional[Callable[[bool], None]] = None,
):
    """
    Envia el correo en un hilo de fondo.

    Si se provee un callback, se invoca con True/False segun el resultado.
    """
    hilo = threading.Thread(
        target=_worker_con_callback,
        args=(destinatario, asunto, mensaje_html, callback),
        daemon=True,
    )
    hilo.start()


def enviar_correo_background(destinatario: str, asunto: str, mensaje_html: str):
    enviar_correo_con_callback(destinatario, asunto, mensaje_html, callback=None)

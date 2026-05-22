import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Callable, Optional
from app.core.config import settings


def enviar_correo_sincrono(destinatario: str, asunto: str, mensaje_html: str) -> bool:
    """
    Función base que se conecta al servidor SMTP y envía el correo.
    Bloquea el hilo en el que se ejecuta.
    Retorna True si el envío fue exitoso, False si falló.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logging.warning("[MS-6] No se ha configurado SMTP_USER o SMTP_PASSWORD. Simulación de envío de correo.")
        logging.info(f"[MS-6] SIMULACIÓN -> Correo a: {destinatario} | Asunto: {asunto}")
        return True

    try:
        # Configurar el mensaje
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"] = settings.SMTP_USER
        msg["To"] = destinatario

        # Adjuntar la plantilla HTML
        parte_html = MIMEText(mensaje_html, "html")
        msg.attach(parte_html)

        # Conectar al servidor SMTP y enviar
        # NOTA DE SEGURIDAD: Se usa STARTTLS para la conexión SMTP. Esto cifra la transmisión
        # hacia el servidor de correo. Para redes completamente internas y pruebas, esto es
        # suficiente. En producción real se debe asegurar que las credenciales SMTP sean
        # variables de entorno seguras (no hardcodeadas).
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()  # Asegurar la conexión
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, destinatario, msg.as_string())
        server.quit()

        logging.info(f"[MS-6] Correo enviado exitosamente a {destinatario} | Asunto: {asunto}")
        return True
    except Exception as e:
        logging.error(f"[MS-6] Fallo al enviar correo a {destinatario}: {str(e)}")
        return False


def _worker_con_callback(destinatario: str, asunto: str, mensaje_html: str, callback: Optional[Callable[[bool], None]]):
    """Worker privado que ejecuta el envío y luego llama al callback con el resultado."""
    exito = enviar_correo_sincrono(destinatario, asunto, mensaje_html)
    if callback:
        try:
            callback(exito)
        except Exception as e:
            logging.error(f"[MS-6] Error en callback post-envío para {destinatario}: {e}")


def enviar_correo_con_callback(
    destinatario: str,
    asunto: str,
    mensaje_html: str,
    callback: Optional[Callable[[bool], None]] = None
):
    """
    Envía el correo en un hilo de fondo (no bloquea la respuesta REST/gRPC).
    Si se provee un callback, es invocado con True/False según éxito del envío.
    Esto permite actualizar el estado de la notificación en BD sin acceder a la sesión original.

    Funciona tanto para FastAPI (REST) como para gRPC.
    """
    hilo = threading.Thread(
        target=_worker_con_callback,
        args=(destinatario, asunto, mensaje_html, callback),
        daemon=True  # El hilo no bloquea el shutdown del proceso
    )
    hilo.start()


# Alias de compatibilidad hacia atrás por si se usa en el servidor gRPC
def enviar_correo_background(destinatario: str, asunto: str, mensaje_html: str):
    """Alias de compatibilidad. Llama a enviar_correo_con_callback sin callback."""
    enviar_correo_con_callback(destinatario, asunto, mensaje_html, callback=None)

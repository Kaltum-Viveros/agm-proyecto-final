import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def enviar_correo_sincrono(destinatario: str, asunto: str, mensaje_html: str):
    """
    Función base que se conecta al servidor SMTP y envía el correo.
    Bloquea el hilo en el que se ejecuta.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logging.warning("No se ha configurado SMTP_USER o SMTP_PASSWORD. Simulación de envío de correo.")
        logging.info(f"SIMULACIÓN -> Correo a: {destinatario} | Asunto: {asunto}")
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
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls() # Asegurar la conexión
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, destinatario, msg.as_string())
        server.quit()
        
        logging.info(f"Correo enviado exitosamente a {destinatario}")
        return True
    except Exception as e:
        logging.error(f"Fallo al enviar correo a {destinatario}: {str(e)}")
        # Aquí idealmente se actualizaría el estado en base de datos a "fallida"
        return False

def enviar_correo_background(destinatario: str, asunto: str, mensaje_html: str):
    """
    Envía el correo usando un Thread para no bloquear el servicio principal.
    Funciona tanto para FastAPI (REST) como para gRPC.
    """
    hilo = threading.Thread(
        target=enviar_correo_sincrono,
        args=(destinatario, asunto, mensaje_html)
    )
    hilo.start()

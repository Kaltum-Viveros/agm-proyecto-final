import os
from app.services.email_service import enviar_correo_sincrono
from app.core.config import settings

def ejecutar_prueba():
    print("Iniciando prueba de envío de correo...")
    print(f"Servidor SMTP configurado: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"Usuario remitente: {settings.SMTP_USER}")
    
    if not settings.SMTP_PASSWORD:
        print("ADVERTENCIA: No se detectó SMTP_PASSWORD en tu archivo .env")
        print("Asegúrate de haber creado tu archivo .env y puesto tu 'App Password' de Gmail.")
        return

    destinatario = "rinava404@gmail.com"
    asunto = "Prueba de Integración: MS-Notificaciones (AGM)"
    
    # Una plantilla bonita y básica para la prueba
    html = """
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="border: 1px solid #ddd; padding: 20px; border-radius: 8px; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2b6cb0;">¡Prueba Exitosa del Microservicio!</h2>
                <p>Hola,</p>
                <p>Este es un correo automático generado desde el <b>MS-6 (Notificaciones)</b> del sistema AGM.</p>
                <p>Si estás leyendo esto, significa que:</p>
                <ul>
                    <li>✅ El servidor SMTP está bien configurado.</li>
                    <li>✅ Las variables de entorno son correctas.</li>
                    <li>✅ El módulo de plantillas HTML funciona a la perfección.</li>
                </ul>
                <p>¡Gran trabajo en equipo!</p>
            </div>
        </body>
    </html>
    """

    print(f"Intentando enviar correo a: {destinatario}...")
    exito = enviar_correo_sincrono(destinatario, asunto, html)
    
    if exito:
        print("🎉 ¡Prueba superada! Revisa la bandeja de entrada de rinava404@gmail.com")
    else:
        print("❌ La prueba falló. Revisa los logs arriba para ver el error.")

if __name__ == "__main__":
    ejecutar_prueba()

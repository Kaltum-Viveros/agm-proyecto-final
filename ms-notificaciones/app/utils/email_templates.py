def get_default_template(slug: str) -> tuple[str, str]:
    """
    Retorna asunto y contenido HTML hermoso por defecto si no existe en la BD.
    """
    
    BASE_HTML_START = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #f1f5f9;
                margin: 0;
                padding: 0;
                color: #334155;
            }
            .container {
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }
            .header {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
                padding: 30px 20px;
                text-align: center;
                color: white;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }
            .content {
                padding: 40px 30px;
            }
            .greeting {
                font-size: 20px;
                font-weight: 600;
                color: #0f172a;
                margin-bottom: 20px;
            }
            .text {
                font-size: 16px;
                line-height: 1.6;
                color: #475569;
                margin-bottom: 25px;
            }
            .footer {
                background-color: #f8fafc;
                padding: 20px;
                text-align: center;
                font-size: 13px;
                color: #94a3b8;
                border-top: 1px solid #e2e8f0;
            }
            .btn {
                display: inline-block;
                background-color: #2563eb;
                color: white !important;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                margin-top: 10px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
    """

    BASE_HTML_END = """
        </div>
    </body>
    </html>
    """

    if slug == "bienvenida":
        asunto = "¡Bienvenido al Sistema de Gestión Académica!"
        html = BASE_HTML_START + """
            <div class="header">
                <h1>Bienvenido al Sistema Académico</h1>
            </div>
            <div class="content">
                <div class="greeting">Hola, {{nombre_obtenido}}</div>
                <div class="text">
                    Has sido dado de alta exitosamente en nuestro sistema. Estamos muy emocionados de tenerte con nosotros.
                </div>
                
                {{mensaje_password}}

                <div class="text">
                    Si tienes algún problema para acceder, no dudes en contactar al soporte técnico de tu facultad.
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:4200" class="btn">Ir al Portal Educativo</a>
                </div>
            </div>
            <div class="footer">
                Este es un mensaje automático del Sistema de Gestión y Automatización de Calificaciones (AGM). Por favor, no respondas a este correo.
            </div>
        """ + BASE_HTML_END
        return asunto, html

    if slug == "bienvenida_docente":
        asunto = "Bienvenido a AGM"
        html = BASE_HTML_START + """
            <div class="header">
                <h1>Bienvenido al Sistema AcadÃ©mico</h1>
            </div>
            <div class="content">
                <div class="greeting">Hola, {{nombre_docente}}</div>
                <div class="text">
                    Tu cuenta docente ha sido creada exitosamente en AGM. Ya puedes acceder al portal para gestionar tus materias y consultar la informaciÃ³n acadÃ©mica asignada.
                </div>

                {{mensaje_password}}

                <div class="text">
                    Si tienes algÃºn problema para acceder, contacta al soporte tÃ©cnico de tu facultad.
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:4200" class="btn">Ir al Portal Docente</a>
                </div>
            </div>
            <div class="footer">
                Este es un mensaje automÃ¡tico del Sistema AGM. Por favor, no respondas a este correo.
            </div>
        """ + BASE_HTML_END
        return asunto, html

    if slug == "baja_materia":
        asunto = "Notificación de Baja de Materia"
        html = BASE_HTML_START + """
            <div class="header" style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);">
                <h1>Notificación de Baja</h1>
            </div>
            <div class="content">
                <div class="greeting">Hola, {{nombre_alumno}}</div>
                <div class="text">
                    Te informamos que has sido <strong>dado de baja</strong> de la materia <strong>{{nombre_materia}}</strong> impartida por el docente {{nombre_docente}}.
                </div>
                <div class="text">
                    Nuestros registros han sido actualizados automáticamente. Si consideras que esto es un error, por favor contacta a la administración de tu facultad a la brevedad posible.
                </div>
            </div>
            <div class="footer">
                Sistema AGM - Notificaciones Automáticas
            </div>
        """ + BASE_HTML_END
        return asunto, html

    if slug == "cierre_materia":
        asunto = "Cierre de Actas: {{nombre_materia}}"
        html = BASE_HTML_START + """
            <div class="header" style="background: linear-gradient(135deg, #059669 0%, #047857 100%);">
                <h1>Cierre de Materia Finalizado</h1>
            </div>
            <div class="content">
                <div class="greeting">¡Hola!</div>
                <div class="text">
                    Te informamos que las actas y calificaciones finales de la materia <strong>{{nombre_materia}}</strong> han sido cerradas oficialmente por tu docente.
                </div>
                <div class="text">
                    Ya puedes consultar tu promedio final y el concentrado de calificaciones en el portal.
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:4200" class="btn" style="background-color: #059669;">Ver mis Calificaciones</a>
                </div>
            </div>
            <div class="footer">
                Sistema AGM - Notificaciones Automáticas
            </div>
        """ + BASE_HTML_END
        return asunto, html

    if slug == "reset_password":
        asunto = "Recuperación de Contraseña"
        html = BASE_HTML_START + """
            <div class="header" style="background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);">
                <h1>Recuperación de Acceso</h1>
            </div>
            <div class="content">
                <div class="greeting">Hola,</div>
                <div class="text">
                    Hemos recibido una solicitud para restablecer tu contraseña. Utiliza el siguiente token de recuperación de forma confidencial.
                </div>
                <div style="margin: 25px 0; padding: 20px; background-color: #f5f3ff; border-radius: 8px; text-align: center; border: 1px dashed #a78bfa;">
                    <p style="margin: 0; color: #5b21b6; font-size: 20px; font-weight: bold; letter-spacing: 2px;">{{token_simulado}}</p>
                </div>
                <div class="text" style="font-size: 14px; color: #64748b;">
                    Si no solicitaste este cambio, puedes ignorar este correo de forma segura.
                </div>
            </div>
            <div class="footer">
                Sistema AGM - Seguridad
            </div>
        """ + BASE_HTML_END
        return asunto, html

    # Fallback genérico final
    return f"Notificación: {slug}", f"<h1>Alerta del Sistema</h1><p>{slug}</p>"

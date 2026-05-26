import os
import sys

# Asegurar que Python reconozca el módulo 'app' al correr el script directamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.plantilla import Plantilla

def seed():
    db = SessionLocal()
    print("Conectando a la base de datos...")
    
    plantillas_data = [
        Plantilla(
            slug="bienvenida",
            asunto_base="¡Bienvenido a AGM, {{nombre_obtenido}}!",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h1 style="color: #2b6cb0; text-align: center;">¡Bienvenido al Sistema AGM!</h1>
                <p>Hola <strong>{{nombre_obtenido}}</strong>,</p>
                <p>Tu cuenta ha sido creada exitosamente. Estamos muy emocionados de tenerte en nuestra plataforma académica.</p>
                <p>Por favor, no compartas tus credenciales con nadie por seguridad.</p>
                <hr style="border-top: 1px solid #eee; margin-top: 30px;" />
                <p style="font-size: 12px; color: #888; text-align: center;">AGM Microservicios - 2026</p>
            </div>
            """
        ),
        Plantilla(
            slug="baja_materia",
            asunto_base="Notificación de Baja de Materia",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #c53030;">Aviso Oficial de Baja</h2>
                <p>Hola <strong>{{nombre_alumno}}</strong>,</p>
                <p>Te informamos que has sido dado de baja de la materia <strong>{{nombre_materia}}</strong> impartida por el docente {{nombre_docente}}.</p>
                <p>El sistema ha actualizado tu registro académico de forma automática.</p>
                <hr style="border-top: 1px solid #eee; margin-top: 30px;" />
                <p style="font-size: 12px; color: #888; text-align: center;">AGM Microservicios</p>
            </div>
            """
        ),
        Plantilla(
            slug="cierre_materia",
            asunto_base="Cierre de Actas - Materia {{nombre_materia}}",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2c5282; text-align: center;">Cierre de Actas Oficial</h2>
                <p>Estimado Alumno,</p>
                <p>Las calificaciones finales de la materia <strong>{{nombre_materia}}</strong> han sido publicadas oficialmente en el sistema.</p>
                <p>Puedes consultar tu kardex ingresando al portal web de estudiantes.</p>
                <hr style="border-top: 1px solid #eee; margin-top: 30px;" />
                <p style="font-size: 12px; color: #888; text-align: center;">AGM Microservicios</p>
            </div>
            """
        ),
        Plantilla(
            slug="reset_password",
            asunto_base="Recuperación de Contraseña - AGM",
            html_content="""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #2b6cb0;">Recuperación de Acceso</h2>
                <p>Hemos recibido una solicitud para restablecer tu contraseña en la plataforma.</p>
                <p>Utiliza el siguiente código de seguridad temporal para recuperar tu acceso:</p>
                <div style="background-color: #f7fafc; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; border-radius: 5px; color: #2d3748; margin: 20px 0;">
                    {{token_simulado}}
                </div>
                <p style="color: #e53e3e; font-size: 14px;">Si no solicitaste este cambio, ignora este correo y contacta a soporte.</p>
                <hr style="border-top: 1px solid #eee; margin-top: 30px;" />
                <p style="font-size: 12px; color: #888; text-align: center;">AGM Microservicios</p>
            </div>
            """
        )
    ]
    
    for plantilla in plantillas_data:
        existente = db.query(Plantilla).filter(Plantilla.slug == plantilla.slug).first()
        if not existente:
            db.add(plantilla)
            print(f"✅ Plantilla '{plantilla.slug}' inyectada exitosamente.")
        else:
            print(f"⚠️ La plantilla '{plantilla.slug}' ya existe en la base de datos.")
            
    db.commit()
    db.close()
    print("🎉 ¡Proceso finalizado! Tu base de datos ya tiene las plantillas hermosas.")

if __name__ == "__main__":
    seed()

from app.db.session import engine
from app.db.base import Base
# Importamos los modelos para que Base los conozca
from app.models.docente import Docente
from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion

def test_connection():
    try:
        print("🔍 Intentando conectar a la base de datos...")
        # Esto intentará crear las tablas físicamente si no existen
        Base.metadata.create_all(bind=engine)
        print("✅ ¡Conexión exitosa y tablas creadas (si no existían)!")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()
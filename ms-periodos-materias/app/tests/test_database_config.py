from app.core.config import get_settings

# test para verificar que las configuraciones de la base de datos se cargan correctamente desde el archivo .env o los valores predeterminados
def test_database_settings_are_loaded():
    settings = get_settings()

    assert settings.database_url.startswith("postgresql+asyncpg://")
    assert settings.db_echo is True
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# prueba que el archivo alembic.ini existe
def test_alembic_ini_exists():
    alembic_ini = PROJECT_ROOT / "alembic.ini"

    assert alembic_ini.exists()

# prueba que el directorio de migraciones de Alembic existe
def test_alembic_directory_exists():
    alembic_dir = PROJECT_ROOT / "alembic"
    versions_dir = alembic_dir / "versions"

    assert alembic_dir.exists()
    assert versions_dir.exists()

# prueba que alembic puede cargar el directorio de migraciones correctamente
def test_alembic_config_can_load_script_directory():
    alembic_ini = PROJECT_ROOT / "alembic.ini"

    config = Config(str(alembic_ini))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))

    script = ScriptDirectory.from_config(config)

    assert script.dir == str(PROJECT_ROOT / "alembic")

# prueba que el archivo env.py de Alembic importa correctamente el metadata del proyecto y la configuración de la base de datos
def test_alembic_env_uses_project_metadata():
    env_file = PROJECT_ROOT / "alembic" / "env.py"

    content = env_file.read_text(encoding="utf-8")

    assert "from app.db.base import Base" in content
    assert "target_metadata = Base.metadata" in content
    assert "settings.database_url" in content
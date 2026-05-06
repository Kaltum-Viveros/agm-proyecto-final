from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.db.base import Base


BASE_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI_PATH = BASE_DIR / "alembic.ini"


def test_alembic_ini_exists() -> None:
    assert ALEMBIC_INI_PATH.exists()


def test_alembic_script_directory_is_configured() -> None:
    alembic_config = Config(str(ALEMBIC_INI_PATH))
    script_directory = ScriptDirectory.from_config(alembic_config)

    expected_path = (BASE_DIR / "alembic").resolve()
    actual_path = Path(script_directory.dir).resolve()

    assert actual_path == expected_path


def test_alembic_has_initial_revision() -> None:
    alembic_config = Config(str(ALEMBIC_INI_PATH))
    script_directory = ScriptDirectory.from_config(alembic_config)

    heads = script_directory.get_heads()

    assert "001_create_users_and_auth_tokens" in heads


def test_base_metadata_has_users_and_auth_tokens_tables() -> None:
    assert "users" in Base.metadata.tables
    assert "auth_tokens" in Base.metadata.tables


def test_initial_revision_contains_expected_tables() -> None:
    migration_path = (
        BASE_DIR
        / "alembic"
        / "versions"
        / "001_create_users_and_auth_tokens.py"
    )

    migration_content = migration_path.read_text(encoding="utf-8")

    assert '"users"' in migration_content
    assert '"auth_tokens"' in migration_content
    assert '"ix_users_email"' in migration_content
    assert '"ix_auth_tokens_user_id"' in migration_content
from app.core.config import settings
from app.db.session import engine, SessionLocal


def test_database_url_is_configured() -> None:
    assert settings.database_url.startswith("postgresql://")


def test_sqlalchemy_engine_uses_postgresql() -> None:
    assert engine.url.get_backend_name() == "postgresql"


def test_session_local_is_configured() -> None:
    db = SessionLocal()

    try:
        assert db is not None
    finally:
        db.close()
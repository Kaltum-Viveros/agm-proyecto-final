import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db.session import AsyncSessionLocal, engine, get_db

# Se construyen hasta este punto sesiones sqlalchemy para la conexión a la base de datos
#test para verificar que se ha creado un motor de base de datos asíncrono utilizando SQLAlchemy
def test_engine_is_created():
    assert isinstance(engine, AsyncEngine)


@pytest.mark.asyncio
#test para verificar que se puede crear una sesión asíncrona utilizando el AsyncSessionLocal
async def test_async_session_can_be_created():
    session = AsyncSessionLocal()

    try:
        assert isinstance(session, AsyncSession)
    finally:
        await session.close()


@pytest.mark.asyncio
#test para verificar que la función get_db devuelve un generador asíncrono que produce sesiones de base de datos
async def test_get_db_yields_async_session():
    db_generator = get_db()
    session = await db_generator.__anext__()

    try:
        assert isinstance(session, AsyncSession)
    finally:
        await db_generator.aclose()
# Conexión a base de datos
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"options": "-c client_encoding=utf8"})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

def init_db():
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)
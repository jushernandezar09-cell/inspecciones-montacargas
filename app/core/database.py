"""
Conexión a la base de datos con SQLAlchemy.

Con SQLite (el default local), esto crea un solo archivo en data/app.db.
En producción, DATABASE_URL apunta a Supabase (Postgres) y este archivo
no necesita tocarse — exactamente el mismo patrón que usa "asistente".
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite necesita este flag extra para trabajar bien con FastAPI (multi-hilo)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

if settings.database_url.startswith("sqlite:///./"):
    os.makedirs("data", exist_ok=True)

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de base de datos por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

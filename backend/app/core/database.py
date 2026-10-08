"""
Configuración del motor de base de datos y gestión de sesiones SQLAlchemy.
"""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from app.core.config import settings

# Normalizar URL de conexión para compatibilidad con PostgreSQL / Supabase
# (Supabase/Render suelen proveer URLs iniciando con "postgres://", pero SQLAlchemy 2.0 requiere "postgresql://")
raw_url = settings.DATABASE_URL
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql://", 1)

# Configuración específica por motor (SQLite vs PostgreSQL)
engine_kwargs = {"echo": False}
if raw_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Optimización para conexiones en la nube (Supabase / Render / Railway)
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

engine = create_engine(raw_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """Generador de sesión de base de datos para inyección de dependencias en FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


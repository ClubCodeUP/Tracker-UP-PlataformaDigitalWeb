"""
Inicializador de base de datos y carga de datos semilla para funcionamiento 100% autocontenido.
"""
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.curriculum_loader import CurriculumLoader


def seed_database(db: Session) -> None:
    """Carga los datos maestros de las mallas curriculares mediante CurriculumLoader."""
    CurriculumLoader.load_all_curricula(db)


def init_database() -> None:
    """Crea las tablas en la base de datos y ejecuta la siembra inicial."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)

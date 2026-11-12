"""
Inicializador de base de datos y carga de datos semilla para funcionamiento 100% autocontenido.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.curriculum_loader import CurriculumLoader
from app.core.security import hash_password
from app.infrastructure.models.user_model import UsuarioModel, CarreraModel


def migrate_schema() -> None:
    """Verifica y aplica migraciones ligeras para tablas existentes en SQLite."""
    with engine.connect() as conn:
        try:
            res = conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()
            col_names = [r[1] for r in res]
            if "rol" not in col_names and len(col_names) > 0:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) DEFAULT 'ESTUDIANTE'"))
                conn.commit()
        except Exception:
            pass


def migrate_sqlite_columns(eng) -> None:
    """Añade columnas nuevas a tablas existentes en SQLite si aún no existen."""
    if eng.dialect.name != "sqlite":
        return
    try:
        with eng.connect() as conn:
            # Concentraciones
            res = conn.exec_driver_sql("PRAGMA table_info(concentraciones)").fetchall()
            col_names = [r[1] for r in res] if res else []
            if col_names:
                if "creditos_minimos" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN creditos_minimos INTEGER NOT NULL DEFAULT 12")
                if "carreras_excluidas" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN carreras_excluidas TEXT")
                if "carreras_exclusivas" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN carreras_exclusivas TEXT")
                if "creditos_por_carrera" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN creditos_por_carrera TEXT")
                if "notas_reglamento" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN notas_reglamento TEXT")
                if "cursos_info" not in col_names:
                    conn.exec_driver_sql("ALTER TABLE concentraciones ADD COLUMN cursos_info TEXT")
                conn.commit()

            # Usuarios
            res_u = conn.exec_driver_sql("PRAGMA table_info(usuarios)").fetchall()
            col_names_u = [r[1] for r in res_u] if res_u else []
            if col_names_u:
                if "concentracion_secundaria_id" not in col_names_u:
                    conn.exec_driver_sql("ALTER TABLE usuarios ADD COLUMN concentracion_secundaria_id INTEGER")
                conn.commit()
    except Exception:
        pass


def sync_postgres_sequences(eng) -> None:
    """Sincroniza las secuencias autoincrementales en PostgreSQL con los IDs existentes."""
    if eng.dialect.name != "postgresql":
        return
    try:
        from sqlalchemy import text
        with eng.connect() as conn:
            for tbl in ["carreras", "concentraciones", "asignaturas", "malla_curricular", "prerrequisitos", "usuarios", "historial_academico"]:
                try:
                    conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE((SELECT max(id) FROM {tbl}), 1));"))
                except Exception:
                    pass
            conn.commit()
    except Exception:
        pass


def seed_database(db: Session) -> None:
    """Carga los datos maestros de las mallas curriculares, concentraciones oficiales y usuarios semilla."""
    should_load_curricula = True
    try:
        if db.query(CarreraModel).count() >= 12:
            should_load_curricula = False
    except Exception:
        pass
    if should_load_curricula:
        CurriculumLoader.load_all_curricula(db)

    # Crear usuario administrador oficial si no existe
    admin_user = db.query(UsuarioModel).filter(UsuarioModel.email == "admin@up.edu.pe").first()
    if not admin_user:
        first_career = db.query(CarreraModel).first()
        career_id = first_career.id if first_career else 1
        admin_user = UsuarioModel(
            email="admin@up.edu.pe",
            password_hash=hash_password("admin1234"),
            nombres="Administrador",
            apellidos="Académico UP",
            carrera_id=career_id,
            periodo_ingreso="2020-1",
            rol="ADMIN",
            activo=True,
        )
        db.add(admin_user)
        db.commit()


def init_database() -> None:
    """Crea las tablas en la base de datos y ejecuta la siembra inicial."""
    migrate_sqlite_columns(engine)
    migrate_schema()
    Base.metadata.create_all(bind=engine)
    sync_postgres_sequences(engine)
    with SessionLocal() as session:
        seed_database(session)

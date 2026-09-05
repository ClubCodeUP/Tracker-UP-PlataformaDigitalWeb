"""
Pruebas automatizadas para el cargador de mallas JSON ("Curriculum as Code") y validación de DAG.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.curriculum_loader import CurriculumLoader, CurriculumCycleException
from app.infrastructure.models import CarreraModel, AsignaturaModel, MallaCurricularModel, PrerrequisitoModel

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_curriculum_loader_loads_all_files(db_session):
    """Verifica que CurriculumLoader procese los JSONs de mallas sin errores."""
    results = CurriculumLoader.load_all_curricula(db_session)
    assert len(results) >= 2

    # Verificar que existan las carreras cargadas
    codigos = [r["carrera_codigo"] for r in results]
    assert "INF" in codigos
    assert "MKT" in codigos
    assert "ADM" in codigos

    # Verificar asignaturas de Marketing
    mkt = db_session.query(CarreraModel).filter(CarreraModel.codigo == "MKT").first()
    assert mkt is not None
    malla_mkt = db_session.query(MallaCurricularModel).filter(MallaCurricularModel.carrera_id == mkt.id).all()
    assert len(malla_mkt) >= 40

    # Verificar existencia de prerrequisitos
    prereqs = db_session.query(PrerrequisitoModel).all()
    assert len(prereqs) > 0


def test_curriculum_loader_detects_cycle(db_session):
    """Verifica que el validador lance CurriculumCycleException si hay un ciclo en los prerrequisitos."""
    # Crear asignaturas cíclicas
    a1 = AsignaturaModel(codigo="TEST-1", nombre="Curso 1", creditos=4.0, tipo="OBLIGATORIA")
    a2 = AsignaturaModel(codigo="TEST-2", nombre="Curso 2", creditos=4.0, tipo="OBLIGATORIA")
    db_session.add_all([a1, a2])
    db_session.flush()

    # a1 requiere a2 y a2 requiere a1 (ciclo)
    p1 = PrerrequisitoModel(asignatura_id=a1.id, prerrequisito_asignatura_id=a2.id)
    p2 = PrerrequisitoModel(asignatura_id=a2.id, prerrequisito_asignatura_id=a1.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    with pytest.raises(CurriculumCycleException):
        CurriculumLoader.validate_dag_acyclic(db_session)


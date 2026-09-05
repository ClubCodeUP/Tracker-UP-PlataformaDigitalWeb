"""
Inicializador de base de datos y carga de datos semilla para funcionamiento 100% autocontenido.
"""
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.infrastructure.models import (
    CarreraModel, ConcentracionModel, AsignaturaModel, MallaCurricularModel, PrerrequisitoModel
)


def seed_database(db: Session) -> None:
    """Carga los datos maestros de la carrera de Ingeniería de la Información (UP) si no existen."""
    if db.query(CarreraModel).first():
        return  # Ya fue inicializada

    # 1. Carreras
    carrera_info = CarreraModel(
        id=1,
        codigo="INF",
        nombre="Ingeniería de la Información",
        total_creditos_graduacion=205,
        total_ciclos=10,
        max_creditos_ciclo_regular=22.0
    )
    carrera_emp = CarreraModel(
        id=2,
        codigo="EMP",
        nombre="Ingeniería Empresarial",
        total_creditos_graduacion=205,
        total_ciclos=10,
        max_creditos_ciclo_regular=22.0
    )
    db.add_all([carrera_info, carrera_emp])
    db.flush()

    # 2. Concentraciones
    conc_swe = ConcentracionModel(
        id=1,
        carrera_id=1,
        codigo="CONC-SWE",
        nombre="Ingeniería de Software y Sistemas Cloud",
        descripcion="Arquitecturas distribuidas, desarrollo web/móvil y DevOps."
    )
    conc_ds = ConcentracionModel(
        id=2,
        carrera_id=1,
        codigo="CONC-DS",
        nombre="Ciencia de Datos e Inteligencia Artificial",
        descripcion="Modelado estadístico, machine learning y procesamiento big data."
    )
    db.add_all([conc_swe, conc_ds])
    db.flush()

    # 3. Asignaturas de Ingeniería
    asignaturas_data = [
        # Ciclo 1
        (1, "MAT-1101", "Álgebra y Geometría Analítica", 4.0, "OBLIGATORIA", False),
        (2, "PRO-1101", "Fundamentos de Programación", 4.0, "OBLIGATORIA", False),
        (3, "COM-1101", "Comunicación Académica", 3.0, "OBLIGATORIA", False),
        (4, "ADM-1101", "Administración y Organizaciones", 3.0, "OBLIGATORIA", False),
        (5, "ECO-1101", "Economía General", 4.0, "OBLIGATORIA", False),
        # Ciclo 2
        (6, "MAT-1102", "Cálculo Diferencial e Integral", 4.0, "OBLIGATORIA", False),
        (7, "PRO-1102", "Algoritmos y Estructuras de Datos", 4.0, "OBLIGATORIA", True),  # Cuello de botella
        (8, "EST-1101", "Estadística y Probabilidades", 4.0, "OBLIGATORIA", False),
        (9, "CON-1101", "Contabilidad Financiera", 3.0, "OBLIGATORIA", False),
        # Ciclo 3
        (10, "MAT-1103", "Álgebra Lineal Computacional", 4.0, "OBLIGATORIA", False),
        (11, "BD-1101", "Fundamentos de Bases de Datos", 4.0, "OBLIGATORIA", True),  # Cuello de botella
        (12, "ARQ-1101", "Arquitectura de Computadoras", 4.0, "OBLIGATORIA", False),
        (13, "EST-1102", "Estadística Inferencial", 4.0, "OBLIGATORIA", False),
        # Ciclo 4
        (14, "SOF-1101", "Ingeniería de Software I", 4.0, "OBLIGATORIA", True),  # Cuello de botella
        (15, "BD-1102", "Bases de Datos NoSQL y Big Data", 4.0, "OBLIGATORIA", False),
        (16, "RED-1101", "Redes y Comunicaciones", 4.0, "OBLIGATORIA", False),
        # Ciclo 5 (Electivos)
        (17, "ELE-SW01", "Arquitecturas Cloud y DevOps", 4.0, "ELECTIVA", False),
        (18, "ELE-DS01", "Machine Learning Supervisado", 4.0, "ELECTIVA", False),
    ]

    for aid, cod, nom, cred, tip, cb in asignaturas_data:
        db.add(AsignaturaModel(
            id=aid,
            codigo=cod,
            nombre=nom,
            creditos=cred,
            tipo=tip,
            es_cuello_botella=cb
        ))
    db.flush()

    # 4. Malla Curricular
    malla_data = [
        # Ciclo 1
        (1, 1, 1, None, 0.0), (1, 2, 1, None, 0.0), (1, 3, 1, None, 0.0), (1, 4, 1, None, 0.0), (1, 5, 1, None, 0.0),
        # Ciclo 2
        (1, 6, 2, None, 0.0), (1, 7, 2, None, 0.0), (1, 8, 2, None, 0.0), (1, 9, 2, None, 0.0),
        # Ciclo 3
        (1, 10, 3, None, 0.0), (1, 11, 3, None, 0.0), (1, 12, 3, None, 0.0), (1, 13, 3, None, 0.0),
        # Ciclo 4
        (1, 14, 4, None, 0.0), (1, 15, 4, None, 0.0), (1, 16, 4, None, 0.0),
        # Ciclo 5
        (1, 17, 5, 1, 50.0),
        (1, 18, 5, 2, 50.0),
    ]
    for cid, aid, ciclo, conc_id, req_cred in malla_data:
        db.add(MallaCurricularModel(
            carrera_id=cid,
            asignatura_id=aid,
            ciclo_sugerido=ciclo,
            concentracion_id=conc_id,
            creditos_minimos_requeridos=req_cred
        ))
    db.flush()

    # 5. Prerrequisitos
    prerreq_data = [
        (6, 1),   # Cálculo -> Álgebra
        (7, 2),   # Estructuras de Datos -> Fundamentos Prog
        (8, 1),   # Estadística -> Álgebra
        (9, 4),   # Contabilidad -> Administración
        (10, 6),  # Álgebra Computacional -> Cálculo
        (11, 7),  # Bases de Datos -> Estructuras de Datos
        (12, 7),  # Arquitectura -> Estructuras de Datos
        (13, 8),  # Estadística Inferencial -> Estadística
        (14, 11), # Ing. Software -> Bases de Datos
        (15, 11), # NoSQL -> Bases de Datos
        (16, 12), # Redes -> Arquitectura
        (17, 14), # Cloud -> Ing. Software
        (18, 13), # Machine Learning -> Estadística Inferencial
    ]
    for obj_id, req_id in prerreq_data:
        db.add(PrerrequisitoModel(
            asignatura_id=obj_id,
            prerrequisito_asignatura_id=req_id,
            nota_minima_aprobatoria=11.00
        ))

    db.commit()


def init_database() -> None:
    """Crea las tablas en la base de datos y ejecuta la siembra inicial."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_database(session)


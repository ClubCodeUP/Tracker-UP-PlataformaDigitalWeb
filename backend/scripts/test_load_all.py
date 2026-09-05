from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.core.curriculum_loader import CurriculumLoader

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()

print('Loading all curricula into SQLite in-memory...')
res = CurriculumLoader.load_all_curricula(db)
print('Result of load_all_curricula:')
for r in res:
    print(f"  - [{r['carrera_codigo']}] {r['carrera_nombre']}: {r['cursos_procesados']} cursos, {r['prerrequisitos_nuevos']} prerreqs")
print(f"Total carreras cargadas: {len(res)}")

CurriculumLoader.validate_dag_acyclic(db)
print('[OK] Entire multi-career graph is a 100% acyclic valid DAG!')

"""
Repositorio para acceso y consulta de asignaturas, malla curricular y prerrequisitos.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.infrastructure.models.course_model import AsignaturaModel, MallaCurricularModel, PrerrequisitoModel


class CourseRepository:
    @staticmethod
    def get_by_id(db: Session, course_id: int) -> Optional[AsignaturaModel]:
        return db.query(AsignaturaModel).filter(AsignaturaModel.id == course_id).first()

    @staticmethod
    def get_by_code(db: Session, codigo: str) -> Optional[AsignaturaModel]:
        return db.query(AsignaturaModel).filter(AsignaturaModel.codigo == codigo.upper()).first()

    @staticmethod
    def get_all(db: Session) -> List[AsignaturaModel]:
        return db.query(AsignaturaModel).all()

    @staticmethod
    def get_malla_by_carrera(db: Session, carrera_id: int) -> List[MallaCurricularModel]:
        return db.query(MallaCurricularModel).options(
            joinedload(MallaCurricularModel.asignatura),
            joinedload(MallaCurricularModel.concentracion)
        ).filter(MallaCurricularModel.carrera_id == carrera_id).order_by(MallaCurricularModel.ciclo_sugerido).all()

    @staticmethod
    def get_prerrequisitos(db: Session, asignatura_id: int) -> List[PrerrequisitoModel]:
        return db.query(PrerrequisitoModel).options(
            joinedload(PrerrequisitoModel.asignatura_requisito)
        ).filter(PrerrequisitoModel.asignatura_id == asignatura_id).all()


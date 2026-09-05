"""
Repositorio para acceso, persistencia y consulta del historial académico del estudiante.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.infrastructure.models.history_model import HistorialAcademicoModel


class HistoryRepository:
    @staticmethod
    def get_by_id(db: Session, history_id: int) -> Optional[HistorialAcademicoModel]:
        return db.query(HistorialAcademicoModel).options(
            joinedload(HistorialAcademicoModel.asignatura)
        ).filter(HistorialAcademicoModel.id == history_id).first()

    @staticmethod
    def get_by_user_and_course_and_period(
        db: Session, user_id: int, asignatura_id: int, periodo: str
    ) -> Optional[HistorialAcademicoModel]:
        return db.query(HistorialAcademicoModel).filter(
            HistorialAcademicoModel.usuario_id == user_id,
            HistorialAcademicoModel.asignatura_id == asignatura_id,
            HistorialAcademicoModel.periodo_academico == periodo
        ).first()

    @staticmethod
    def get_all_by_user(db: Session, user_id: int) -> List[HistorialAcademicoModel]:
        return db.query(HistorialAcademicoModel).options(
            joinedload(HistorialAcademicoModel.asignatura)
        ).filter(
            HistorialAcademicoModel.usuario_id == user_id
        ).order_by(HistorialAcademicoModel.periodo_academico.asc()).all()

    @staticmethod
    def create(db: Session, entry: HistorialAcademicoModel) -> HistorialAcademicoModel:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def update(db: Session, entry: HistorialAcademicoModel) -> HistorialAcademicoModel:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def delete(db: Session, entry: HistorialAcademicoModel) -> None:
        db.delete(entry)
        db.commit()


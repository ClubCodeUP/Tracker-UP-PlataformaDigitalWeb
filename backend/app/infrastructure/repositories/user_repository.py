"""
Repositorio para acceso y persistencia de usuarios y carreras.
"""
from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.infrastructure.models.user_model import UsuarioModel, CarreraModel, ConcentracionModel


class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[UsuarioModel]:
        return db.query(UsuarioModel).options(
            joinedload(UsuarioModel.carrera),
            joinedload(UsuarioModel.concentracion)
        ).filter(UsuarioModel.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UsuarioModel]:
        return db.query(UsuarioModel).options(
            joinedload(UsuarioModel.carrera),
            joinedload(UsuarioModel.concentracion)
        ).filter(UsuarioModel.email == email.lower()).first()

    @staticmethod
    def create(db: Session, user: UsuarioModel) -> UsuarioModel:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update(db: Session, user: UsuarioModel) -> UsuarioModel:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_carrera_by_id(db: Session, carrera_id: int) -> Optional[CarreraModel]:
        return db.query(CarreraModel).filter(CarreraModel.id == carrera_id).first()

    @staticmethod
    def get_concentracion_by_id(db: Session, concentracion_id: int) -> Optional[ConcentracionModel]:
        return db.query(ConcentracionModel).filter(ConcentracionModel.id == concentracion_id).first()


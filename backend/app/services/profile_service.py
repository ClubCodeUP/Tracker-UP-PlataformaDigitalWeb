"""
Servicio para la configuración y actualización del perfil del estudiante (RF-02).
"""
from sqlalchemy.orm import Session
from app.domain.exceptions import EntityNotFoundException
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas.user import UserProfileUpdate, UserProfileResponse


class ProfileService:
    @staticmethod
    def get_profile(user: UsuarioModel) -> UserProfileResponse:
        """Obtiene la información base del perfil del estudiante autenticado."""
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            nombres=user.nombres,
            apellidos=user.apellidos,
            carrera_id=user.carrera_id,
            carrera_nombre=user.carrera.nombre if user.carrera else None,
            carrera_codigo=user.carrera.codigo if user.carrera else None,
            concentracion_id=user.concentracion_id,
            concentracion_nombre=user.concentracion.nombre if user.concentracion else None,
            periodo_ingreso=user.periodo_ingreso,
            activo=user.activo
        )

    @staticmethod
    def update_profile(db: Session, user: UsuarioModel, update_data: UserProfileUpdate) -> UserProfileResponse:
        """Actualiza la carrera, concentración y periodo de ingreso del estudiante."""
        if update_data.carrera_id is not None:
            carrera = UserRepository.get_carrera_by_id(db, update_data.carrera_id)
            if not carrera:
                raise EntityNotFoundException("Carrera", update_data.carrera_id)
            user.carrera_id = update_data.carrera_id

        if update_data.concentracion_id is not None:
            concentracion = UserRepository.get_concentracion_by_id(db, update_data.concentracion_id)
            if not concentracion or concentracion.carrera_id != user.carrera_id:
                raise EntityNotFoundException("Concentración válida para la carrera", update_data.concentracion_id)
            user.concentracion_id = update_data.concentracion_id

        if update_data.periodo_ingreso is not None:
            user.periodo_ingreso = update_data.periodo_ingreso.strip()

        updated_user = UserRepository.update(db, user)
        # Recargar relaciones
        refreshed = UserRepository.get_by_id(db, updated_user.id)
        return ProfileService.get_profile(refreshed or updated_user)


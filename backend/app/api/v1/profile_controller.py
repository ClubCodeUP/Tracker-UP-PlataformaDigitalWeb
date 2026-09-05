"""
Controlador CRUD para la configuración del perfil del estudiante (RF-02).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.exceptions import EntityNotFoundException
from app.infrastructure.models.user_model import UsuarioModel
from app.schemas.user import UserProfileUpdate, UserProfileResponse
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Perfil del Estudiante"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Consultar perfil del estudiante autenticado",
    description="Devuelve los datos de carrera, periodo de ingreso y concentración seleccionada."
)
def get_my_profile(current_user: UsuarioModel = Depends(get_current_user)):
    return ProfileService.get_profile(current_user)


@router.put(
    "/me",
    response_model=UserProfileResponse,
    summary="Actualizar perfil del estudiante",
    description="Permite al estudiante actualizar su carrera, periodo de ingreso y concentración electiva."
)
def update_my_profile(
    update_data: UserProfileUpdate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return ProfileService.update_profile(db, current_user, update_data)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


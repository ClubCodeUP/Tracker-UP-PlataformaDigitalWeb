"""
Controlador CRUD para la configuración del perfil del estudiante (RF-02).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.exceptions import EntityNotFoundException, ConcentrationEligibilityException
from app.infrastructure.models.user_model import UsuarioModel, CarreraModel, SolicitudCambioCarreraModel
from app.schemas.user import UserProfileUpdate, UserProfileResponse
from app.schemas.admin import CareerChangeRequestCreate, CareerChangeRequestResponse
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Perfil del Estudiante"])


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Consultar perfil del estudiante autenticado",
    description="Devuelve los datos de carrera, periodo de ingreso y concentración seleccionada."
)
def get_my_profile(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ProfileService.get_profile(current_user, db)


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
    except ConcentrationEligibilityException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/career-change-request",
    response_model=CareerChangeRequestResponse,
    summary="Crear solicitud de cambio de carrera",
    description="Permite al estudiante enviar una solicitud formal de cambio de carrera hacia otra carrera de la UP."
)
def create_career_change_request(
    data: CareerChangeRequestCreate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.carrera_destino_id == current_user.carrera_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La carrera de destino seleccionada es la misma carrera actual del estudiante."
        )

    target_career = db.query(CarreraModel).filter(CarreraModel.id == data.carrera_destino_id).first()
    if not target_career:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrera de destino no encontrada.")

    # Verificar si ya tiene una solicitud pendiente
    existing_pending = db.query(SolicitudCambioCarreraModel).filter(
        SolicitudCambioCarreraModel.usuario_id == current_user.id,
        SolicitudCambioCarreraModel.estado == "PENDIENTE"
    ).first()
    if existing_pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya cuentas con una solicitud de cambio de carrera pendiente de evaluación."
        )

    new_req = SolicitudCambioCarreraModel(
        usuario_id=current_user.id,
        carrera_actual_id=current_user.carrera_id,
        carrera_destino_id=data.carrera_destino_id,
        motivo=data.motivo,
        estado="PENDIENTE"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return CareerChangeRequestResponse(
        id=new_req.id,
        usuario_id=new_req.usuario_id,
        estudiante_nombres=current_user.nombres,
        estudiante_apellidos=current_user.apellidos,
        estudiante_email=current_user.email,
        carrera_actual_id=new_req.carrera_actual_id,
        carrera_actual_nombre=current_user.carrera.nombre if current_user.carrera else "N/A",
        carrera_destino_id=new_req.carrera_destino_id,
        carrera_destino_nombre=target_career.nombre,
        motivo=new_req.motivo,
        estado=new_req.estado,
        respuesta_admin=new_req.respuesta_admin,
        creado_en=new_req.creado_en
    )


@router.get(
    "/career-change-requests",
    response_model=List[CareerChangeRequestResponse],
    summary="Listar mis solicitudes de cambio de carrera",
    description="Retorna el historial de solicitudes de cambio de carrera realizadas por el alumno."
)
def list_my_career_change_requests(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(SolicitudCambioCarreraModel).filter(
        SolicitudCambioCarreraModel.usuario_id == current_user.id
    ).order_by(SolicitudCambioCarreraModel.creado_en.desc()).all()

    results = []
    for r in requests:
        results.append(CareerChangeRequestResponse(
            id=r.id,
            usuario_id=r.usuario_id,
            estudiante_nombres=current_user.nombres,
            estudiante_apellidos=current_user.apellidos,
            estudiante_email=current_user.email,
            carrera_actual_id=r.carrera_actual_id,
            carrera_actual_nombre=r.carrera_actual.nombre if r.carrera_actual else "N/A",
            carrera_destino_id=r.carrera_destino_id,
            carrera_destino_nombre=r.carrera_destino.nombre if r.carrera_destino else "N/A",
            motivo=r.motivo,
            estado=r.estado,
            respuesta_admin=r.respuesta_admin,
            creado_en=r.creado_en
        ))
    return results


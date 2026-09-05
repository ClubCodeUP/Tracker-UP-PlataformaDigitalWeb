"""
Controlador CRUD para el historial de asignaturas del estudiante (RF-03, RF-07).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.exceptions import EntityNotFoundException, InvalidAcademicRecordException
from app.infrastructure.models.user_model import UsuarioModel
from app.schemas.history import CourseHistoryCreate, CourseHistoryUpdate, CourseHistoryResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["Historial Académico"])


@router.get(
    "",
    response_model=List[CourseHistoryResponse],
    summary="Listar historial académico",
    description="Devuelve el conjunto de asignaturas registradas por el estudiante con sus calificaciones y matrículas."
)
def get_history(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return HistoryService.get_history(db, current_user.id)


@router.post(
    "",
    response_model=CourseHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asignatura en el historial",
    description="Permite registrar una asignatura como aprobada, desaprobada, en curso o pendiente con su nota y veces cursada."
)
def add_course_history(
    data: CourseHistoryCreate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return HistoryService.add_entry(db, current_user.id, data)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidAcademicRecordException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/{history_id}",
    response_model=CourseHistoryResponse,
    summary="Actualizar estado o calificación de asignatura",
    description="Actualiza el estado (aprobada/en curso/pendiente), calificación o número de matrícula de una asignatura."
)
def update_course_history(
    history_id: int,
    data: CourseHistoryUpdate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return HistoryService.update_entry(db, current_user.id, history_id, data)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar registro del historial",
    description="Elimina una entrada de asignatura del historial académico del estudiante."
)
def delete_course_history(
    history_id: int,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        HistoryService.delete_entry(db, current_user.id, history_id)
        return None
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


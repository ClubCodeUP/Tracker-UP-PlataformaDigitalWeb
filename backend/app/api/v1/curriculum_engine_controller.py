"""
Controlador RESTful para el motor de recomendaciones y evaluación de riesgos curriculares (RF-10 al RF-16).
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.infrastructure.models.user_model import UsuarioModel
from app.schemas.rules_engine import (
    CurriculumEvaluationResponse,
    RecommendationResponse,
    RiskAlertResponse
)
from app.services.curriculum_engine_service import CurriculumEngineService

router = APIRouter(prefix="/curriculum", tags=["Motor Curricular y Alertas"])


@router.get(
    "/evaluate",
    response_model=CurriculumEvaluationResponse,
    summary="Evaluación integral curricular (Recomendación + Riesgos)",
    description=(
        "Ejecuta el motor determinístico completo: evalúa el avance del estudiante, "
        "recomienda el bloque de asignaturas para el siguiente ciclo y emite todas las alertas "
        "de riesgo académico (reiteración de matrícula, prerrequisitos límite, rezago y cuellos de botella)."
    )
)
def evaluate_curriculum(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.evaluate_full_curriculum(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/recommendation",
    response_model=RecommendationResponse,
    summary="Obtener recomendación de bloque de matrícula",
    description=(
        "Genera determinísticamente la propuesta de asignaturas a matricular para el siguiente periodo, "
        "respetando prerrequisitos cumplidos, bolsa de créditos y el rango regular de créditos de la carrera."
    )
)
def get_course_recommendations(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.generate_recommendations(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/risks",
    response_model=List[RiskAlertResponse],
    summary="Diagnóstico de alertas de riesgo académico",
    description=(
        "Emite la lista de alertas codificadas: asignaturas en 2ª/3ª matrícula, prerrequisitos aprobados "
        "con nota en límite (11.00), rezago por permanencia y asignaturas cuello de botella pendientes."
    )
)
def get_risk_alerts(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.evaluate_risks(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


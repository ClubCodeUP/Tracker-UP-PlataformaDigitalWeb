"""
Controlador para la consulta y cálculo dinámico de métricas académicas (RF-04, RF-08).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.infrastructure.models.user_model import UsuarioModel
from app.schemas.metrics import AcademicMetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Métricas de Avance"])


@router.get(
    "/me",
    response_model=AcademicMetricsResponse,
    summary="Calcular métricas de avance curricular",
    description="Calcula en tiempo real el porcentaje de avance, créditos acumulados/en curso y ciclo referencial."
)
def get_my_metrics(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return MetricsService.calculate_metrics(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


"""
Esquemas Pydantic para el motor determinístico de recomendaciones y alertas de riesgo.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domain.entities import TipoAlerta, SeveridadAlerta


class RiskAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tipo_alerta: TipoAlerta
    nivel_severidad: SeveridadAlerta
    codigo_asignatura: Optional[str] = None
    nombre_asignatura: Optional[str] = None
    mensaje: str
    detalles: Dict[str, Any] = Field(default_factory=dict)


class SuggestedCourseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    asignatura_id: int
    codigo: str
    nombre: str
    creditos: float
    ciclo_sugerido: int
    tipo: str
    es_cuello_botella: bool
    es_reiteracion: bool
    numero_matricula_proyectada: int
    prioridad_score: float
    motivo_prioridad: str


class CreditRange(BaseModel):
    minimo_regular: float = 12.0
    maximo_regular: float = 22.0


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    carrera: str
    concentracion: Optional[str] = None
    periodo_proyectado: str
    creditos_totales_sugeridos: float
    rango_creditos_permitido: CreditRange
    cantidad_cursos_sugeridos: int
    cursos_sugeridos: List[SuggestedCourseItem]
    resumen_criterios_deterministicos: List[str]


class CurriculumEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    estudiante: str
    recomendacion_matricula: RecommendationResponse
    alertas_riesgo: List[RiskAlertResponse]
    resumen_alertas: Dict[str, int]


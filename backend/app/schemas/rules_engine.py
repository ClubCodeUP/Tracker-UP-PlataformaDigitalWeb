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
    concentracion_secundaria: Optional[str] = None
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


class OfficialConcentrationCourseItem(BaseModel):
    codigo: str
    nombre: str
    departamento: str
    creditos: float
    es_obligatorio_concentracion: bool = False
    horas_teoria: int = 0
    horas_practica: int = 0


class OfficialConcentrationResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    creditos_minimos: int
    carreras_excluidas: List[str] = Field(default_factory=list)
    carreras_exclusivas: List[str] = Field(default_factory=list)
    notas_reglamento: str
    aplica_a_carrera_estudiante: bool = True
    motivo_exclusion: Optional[str] = None
    total_cursos: int
    cursos_obligatorios: List[OfficialConcentrationCourseItem] = Field(default_factory=list)
    cursos_electivos: List[OfficialConcentrationCourseItem] = Field(default_factory=list)


class ConcentrationTrackingProgress(BaseModel):
    concentracion_id: int
    codigo: str
    nombre: str
    creditos_minimos: int
    creditos_completados: float
    porcentaje_avance: float
    esta_completada: bool
    cursos_aprobados_computados: List[Dict[str, Any]] = Field(default_factory=list)
    cursos_obligatorios_pendientes: List[Dict[str, Any]] = Field(default_factory=list)
    cursos_electivos_disponibles: List[Dict[str, Any]] = Field(default_factory=list)


class StudentConcentrationsStatusResponse(BaseModel):
    usuario_id: int
    carrera_id: int
    carrera_codigo: str
    carrera_nombre: str
    creditos_aprobados_totales: float
    creditos_minimos_requeridos_acceso: float = 110.0
    puede_declarar_concentracion: bool
    mensaje_estado: str
    concentracion_primaria: Optional[ConcentrationTrackingProgress] = None
    concentracion_secundaria: Optional[ConcentrationTrackingProgress] = None
    total_concentraciones_declaradas: int
    concentraciones_elegibles_count: int


class DeclareConcentrationsRequest(BaseModel):
    concentracion_id: Optional[int] = Field(None, description="ID de la concentración primaria (o null para retirar)")
    concentracion_secundaria_id: Optional[int] = Field(None, description="ID de la concentración secundaria (opcional, o null)")


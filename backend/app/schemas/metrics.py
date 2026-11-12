"""
Esquemas Pydantic para métricas consolidadas de avance y desempeño académico.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AcademicMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    estudiante: str
    carrera: str
    total_creditos_carrera: int
    creditos_aprobados: float
    creditos_en_curso: float
    creditos_pendientes: float
    porcentaje_avance: float
    ciclo_referencial: int
    promedio_ponderado: Optional[float] = None
    cursos_aprobados_count: int
    cursos_en_curso_count: int
    cursos_en_riesgo_count: int


class CohortBenchmarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    periodo_ingreso: str
    semestres_transcurridos: int
    estudiante_creditos_aprobados: float
    estudiante_promedio_ponderado: Optional[float] = None
    estudiante_porcentaje_avance: float

    # 1. Comparación con cohorte/promoción real
    cohorte_tamano: int
    cohorte_media_creditos: float
    cohorte_media_promedio: Optional[float] = None
    cohorte_media_avance: float
    diferencia_creditos_cohorte: float

    # 2. Comparación con la trayectoria teórica de la malla
    malla_creditos_esperados: float
    malla_avance_esperado: float
    diferencia_creditos_malla: float

    # Diagnóstico constructivo / positivo
    estado_ritmo: str  # ADELANTADO | AL_DIA | EN_PROGRESO
    mensaje_evaluacion: str
    recomendacion_constructiva: str


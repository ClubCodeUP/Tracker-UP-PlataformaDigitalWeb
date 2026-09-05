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


"""
Esquemas Pydantic para el registro y gestión del historial académico.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.domain.entities import EstadoAsignatura


class CourseHistoryCreate(BaseModel):
    asignatura_id: int = Field(..., examples=[7], description="ID de la asignatura cursada")
    periodo_academico: str = Field(..., pattern=r"^[0-9]{4}-(0|1|2)$", examples=["2023-1"])
    estado: EstadoAsignatura = Field(default=EstadoAsignatura.EN_CURSO, examples=[EstadoAsignatura.APROBADA])
    calificacion: Optional[float] = Field(None, ge=0.0, le=20.0, examples=[15.5])
    numero_matricula: int = Field(default=1, ge=1, le=3, examples=[1], description="1ª, 2ª o 3ª matrícula")

    @model_validator(mode="after")
    def validate_grade_and_state(self) -> "CourseHistoryCreate":
        if self.estado == EstadoAsignatura.APROBADA:
            if self.calificacion is None or self.calificacion < 11.0:
                raise ValueError("Una asignatura APROBADA debe tener una calificación mayor o igual a 11.00.")
        elif self.estado == EstadoAsignatura.DESAPROBADA:
            if self.calificacion is None or self.calificacion >= 11.0:
                raise ValueError("Una asignatura DESAPROBADA debe tener una calificación menor a 11.00.")
        elif self.estado in (EstadoAsignatura.PENDIENTE, EstadoAsignatura.EN_CURSO):
            if self.calificacion is not None:
                raise ValueError("Una asignatura PENDIENTE o EN_CURSO no puede tener calificación registrada.")
        return self


class CourseHistoryUpdate(BaseModel):
    estado: Optional[EstadoAsignatura] = None
    calificacion: Optional[float] = Field(None, ge=0.0, le=20.0)
    numero_matricula: Optional[int] = Field(None, ge=1, le=3)

    @model_validator(mode="after")
    def validate_update(self) -> "CourseHistoryUpdate":
        if self.estado == EstadoAsignatura.APROBADA and self.calificacion is not None:
            if self.calificacion < 11.0:
                raise ValueError("Una asignatura APROBADA debe tener una calificación mayor o igual a 11.00.")
        elif self.estado == EstadoAsignatura.DESAPROBADA and self.calificacion is not None:
            if self.calificacion >= 11.0:
                raise ValueError("Una asignatura DESAPROBADA debe tener una calificación menor a 11.00.")
        elif self.estado in (EstadoAsignatura.PENDIENTE, EstadoAsignatura.EN_CURSO):
            if self.calificacion is not None:
                raise ValueError("Una asignatura PENDIENTE o EN_CURSO no puede tener calificación registrada.")
        return self


class CourseHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    asignatura_id: int
    codigo_asignatura: str
    nombre_asignatura: str
    creditos: float
    tipo_asignatura: str
    periodo_academico: str
    estado: EstadoAsignatura
    calificacion: Optional[float] = None
    numero_matricula: int
    es_cuello_botella: bool


"""
Esquemas Pydantic para el panel de administración y gestión académica.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CareerChangeRequestCreate(BaseModel):
    carrera_destino_id: int = Field(..., description="ID de la carrera a la que solicita el cambio")
    motivo: Optional[str] = Field(None, max_length=500, description="Explicación o fundamento del cambio")


class CareerChangeRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    estudiante_nombres: str
    estudiante_apellidos: str
    estudiante_email: str
    carrera_actual_id: int
    carrera_actual_nombre: str
    carrera_destino_id: int
    carrera_destino_nombre: str
    motivo: Optional[str] = None
    estado: str  # PENDIENTE / APROBADA / RECHAZADA
    respuesta_admin: Optional[str] = None
    creado_en: datetime


class CareerChangeAction(BaseModel):
    accion: str = Field(..., pattern="^(APROBAR|RECHAZAR)$", description="Acción administrativa a ejecutar")
    respuesta_admin: Optional[str] = Field(None, max_length=500, description="Observaciones o respuesta al alumno")


class CurriculumUploadResponse(BaseModel):
    archivo: str
    carrera_codigo: str
    carrera_nombre: str
    cursos_cargados: int
    prerrequisitos_procesados: int
    estado: str = "EXITOSO"

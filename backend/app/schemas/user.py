"""
Esquemas Pydantic para el perfil del estudiante.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class UserProfileUpdate(BaseModel):
    carrera_id: Optional[int] = Field(None, examples=[1])
    concentracion_id: Optional[int] = Field(None, examples=[2])
    periodo_ingreso: Optional[str] = Field(None, pattern=r"^[0-9]{4}-(0|1|2)$", examples=["2023-1"])


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    nombres: str
    apellidos: str
    carrera_id: int
    carrera_nombre: Optional[str] = None
    carrera_codigo: Optional[str] = None
    concentracion_id: Optional[int] = None
    concentracion_nombre: Optional[str] = None
    periodo_ingreso: str
    activo: bool


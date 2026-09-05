"""
Esquemas Pydantic para validación de especificaciones curriculares en JSON ("Curriculum as Code").
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ConcentrationDefinitionSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID opcional para fijar la concentración")
    codigo: str = Field(..., description="Código único de la concentración (ej. CONC-SWE)")
    nombre: str = Field(..., description="Nombre de la concentración")
    descripcion: Optional[str] = Field(None, description="Descripción de la línea de especialización")


class CourseDefinitionSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID numérico opcional para preservar consistencia histórica")
    codigo: str = Field(..., description="Código oficial UP del curso (ej. MAT-1101 o 138649)")
    nombre: str = Field(..., description="Nombre de la asignatura")
    creditos: float = Field(..., ge=0, description="Créditos académicos del curso")
    ciclo_sugerido: int = Field(..., ge=0, le=12, description="Semestre académico en que se sugiere cursar (0 a 12)")
    tipo: str = Field("OBLIGATORIA", description="OBLIGATORIA o ELECTIVA")
    concentracion_codigo: Optional[str] = Field(None, description="Código de la concentración si es electiva")
    es_cuello_botella: bool = Field(False, description="Marca formal si es cuello de botella crítico")
    creditos_minimos_requeridos: float = Field(0.0, ge=0, description="Bolsa mínima de créditos acumulados requerida")
    prerrequisitos: List[str] = Field(default_factory=list, description="Lista de códigos de asignaturas que actúan como prerrequisito")


class CareerDefinitionSchema(BaseModel):
    id: Optional[int] = Field(None, description="ID numérico opcional de la carrera (ej. 1 para INF)")
    codigo: str = Field(..., description="Código identificador de la carrera (ej. INF, MKT, ADM)")
    nombre: str = Field(..., description="Nombre oficial del programa académico")
    facultad: Optional[str] = Field(None, description="Facultad a la que pertenece")
    plan: Optional[str] = Field("2022", description="Año o versión del plan de estudios")
    total_creditos_graduacion: int = Field(205, gt=0, description="Total de créditos necesarios para egresar")
    total_ciclos: int = Field(10, ge=8, le=14, description="Número de ciclos regulares del programa")
    max_creditos_ciclo_regular: float = Field(22.0, gt=0, description="Límite máximo regular de créditos por ciclo")


class CurriculumFileSchema(BaseModel):
    carrera: CareerDefinitionSchema
    concentraciones: List[ConcentrationDefinitionSchema] = Field(default_factory=list)
    cursos: List[CourseDefinitionSchema] = Field(..., min_length=1)


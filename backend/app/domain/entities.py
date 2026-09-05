"""
Constantes, enumeraciones y entidades puras del dominio académico.
"""
from enum import Enum


class EstadoAsignatura(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_CURSO = "EN_CURSO"
    APROBADA = "APROBADA"
    DESAPROBADA = "DESAPROBADA"


class TipoAsignatura(str, Enum):
    OBLIGATORIA = "OBLIGATORIA"
    ELECTIVA = "ELECTIVA"


class TipoAlerta(str, Enum):
    REITERACION_MATRICULA = "REITERACION_MATRICULA"
    PRERREQUISITO_NOTA_LIMITE = "PRERREQUISITO_NOTA_LIMITE"
    REZAGO_PERMANENCIA = "REZAGO_PERMANENCIA"
    CUELLO_DE_BOTELLA = "CUELLO_DE_BOTELLA"


class SeveridadAlerta(str, Enum):
    CRITICA = "CRITICA"
    ADVERTENCIA = "ADVERTENCIA"
    INFORMATIVA = "INFORMATIVA"


"""
Esquemas Pydantic para autenticación, registro y gestión de tokens.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., examples=["20230145@up.edu.pe"], description="Correo institucional @up.edu.pe")
    password: str = Field(..., min_length=6, examples=["ClaveSegura2026!"], description="Contraseña de acceso")
    nombres: str = Field(..., examples=["Carlos"], min_length=2)
    apellidos: str = Field(..., examples=["Gutiérrez Mendoza"], min_length=2)
    carrera_id: int = Field(..., examples=[1])
    concentracion_id: Optional[int] = Field(None, examples=[1])
    periodo_ingreso: str = Field(..., pattern=r"^[0-9]{4}-(0|1|2)$", examples=["2023-1"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["20230145@up.edu.pe"])
    password: str = Field(..., examples=["ClaveSegura2026!"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    nombres: str
    apellidos: str


class TokenPayload(BaseModel):
    sub: str
    exp: int


"""
Controlador de autenticación y registro de estudiantes con restricción de dominio institucional UP.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domain.exceptions import InvalidEmailDomainException, UserAlreadyExistsException, EntityNotFoundException
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo estudiante",
    description="Crea la cuenta de un estudiante validando obligatoriamente el dominio institucional (@up.edu.pe)."
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.register(db, request)
    except InvalidEmailDomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica a un estudiante con su correo institucional UP y contraseña, devolviendo el JWT de acceso."
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.login(db, request)
    except InvalidEmailDomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


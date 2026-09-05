"""
Inyección de dependencias de seguridad y contexto para los controladores de FastAPI.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.user_repository import UserRepository

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UsuarioModel:
    """Extrae, decodifica y valida el token JWT Bearer, retornando la instancia del usuario autenticado."""
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = UserRepository.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario asociado al token ya no existe.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta del usuario está inactiva."
        )

    return user


security_optional = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security_optional),
    db: Session = Depends(get_db)
) -> UsuarioModel:
    """Retorna el usuario autenticado si el token existe y es válido, o None si no hay sesión."""
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload.get("sub"))
        return UserRepository.get_by_id(db, user_id)
    except Exception:
        return None


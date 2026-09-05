"""
Servicio de autenticación y validación de correos institucionales UP.
"""
import re
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.domain.exceptions import InvalidEmailDomainException, UserAlreadyExistsException, EntityNotFoundException
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    @staticmethod
    def validate_institutional_email(email: str) -> None:
        """Verifica que el correo cumpla estrictamente con el dominio institucional UP (@up.edu.pe)."""
        pattern = re.compile(settings.INSTITUTIONAL_EMAIL_REGEX, re.IGNORECASE)
        if not pattern.match(email):
            raise InvalidEmailDomainException(email)

    @classmethod
    def register(cls, db: Session, request: RegisterRequest) -> TokenResponse:
        """Registra a un estudiante nuevo tras validar el correo institucional y genera su token JWT."""
        # 1. Validar dominio institucional obligatorio (RF-01)
        cls.validate_institutional_email(request.email)

        # 2. Verificar existencia previa
        existing = UserRepository.get_by_email(db, request.email)
        if existing:
            raise UserAlreadyExistsException(request.email)

        # 3. Validar que la carrera exista
        carrera = UserRepository.get_carrera_by_id(db, request.carrera_id)
        if not carrera:
            raise EntityNotFoundException("Carrera", request.carrera_id)

        # 4. Validar concentración si fue provista
        if request.concentracion_id:
            concentracion = UserRepository.get_concentracion_by_id(db, request.concentracion_id)
            if not concentracion or concentracion.carrera_id != request.carrera_id:
                raise EntityNotFoundException("Concentración válida para la carrera", request.concentracion_id)

        # 5. Crear usuario
        user = UsuarioModel(
            email=request.email.lower().strip(),
            password_hash=hash_password(request.password),
            nombres=request.nombres.strip(),
            apellidos=request.apellidos.strip(),
            carrera_id=request.carrera_id,
            concentracion_id=request.concentracion_id,
            periodo_ingreso=request.periodo_ingreso.strip(),
            activo=True
        )
        saved_user = UserRepository.create(db, user)

        # 6. Generar JWT
        token = create_access_token(
            subject=saved_user.id,
            claims={"email": saved_user.email, "carrera_id": saved_user.carrera_id}
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=saved_user.id,
            email=saved_user.email,
            nombres=saved_user.nombres,
            apellidos=saved_user.apellidos
        )

    @classmethod
    def login(cls, db: Session, request: LoginRequest) -> TokenResponse:
        """Autentica a un estudiante y retorna el token de sesión JWT."""
        # 1. Validar dominio institucional
        cls.validate_institutional_email(request.email)

        # 2. Buscar usuario
        user = UserRepository.get_by_email(db, request.email)
        if not user or not verify_password(request.password, user.password_hash):
            raise ValueError("Credenciales inválidas")

        if not user.activo:
            raise ValueError("La cuenta se encuentra inactiva")

        # 3. Generar token
        token = create_access_token(
            subject=user.id,
            claims={"email": user.email, "carrera_id": user.carrera_id}
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            nombres=user.nombres,
            apellidos=user.apellidos
        )


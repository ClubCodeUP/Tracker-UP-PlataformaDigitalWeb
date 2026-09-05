"""
Configuración central de la aplicación Tracker UP utilizando Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tracker UP API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Seguridad y JWT
    SECRET_KEY: str = "tracker-up-super-secret-key-development-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas para conveniencia en MVP
    
    # Restricción institucional para alumnos y docentes (RF-01)
    INSTITUTIONAL_DOMAIN: str = "@alum.up.edu.pe"
    INSTITUTIONAL_EMAIL_REGEX: str = r"^[a-zA-Z0-9._%+-]+@(alum\.)?up\.edu\.pe$"
    
    # Base de Datos: SQLite por defecto para desarrollo autocontenido, configurable a PostgreSQL
    DATABASE_URL: str = "sqlite:///./tracker_up.db"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()


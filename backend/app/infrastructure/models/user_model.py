"""
Modelos ORM para usuarios, carreras y concentraciones temáticas.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class CarreraModel(Base):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
    total_creditos_graduacion = Column(Integer, nullable=False, default=205)
    total_ciclos = Column(Integer, nullable=False, default=10)
    max_creditos_ciclo_regular = Column(Numeric(3, 1), nullable=False, default=22.0)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    concentraciones = relationship("ConcentracionModel", back_populates="carrera", cascade="all, delete-orphan")
    usuarios = relationship("UsuarioModel", back_populates="carrera")
    malla = relationship("MallaCurricularModel", back_populates="carrera")


class ConcentracionModel(Base):
    __tablename__ = "concentraciones"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False)
    codigo = Column(String(30), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    carrera = relationship("CarreraModel", back_populates="concentraciones")
    usuarios = relationship("UsuarioModel", back_populates="concentracion")


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False)
    concentracion_id = Column(Integer, ForeignKey("concentraciones.id"), nullable=True)
    periodo_ingreso = Column(String(10), nullable=False)  # Ej: '2023-1'
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    carrera = relationship("CarreraModel", back_populates="usuarios")
    concentracion = relationship("ConcentracionModel", back_populates="usuarios")
    historial = relationship("HistorialAcademicoModel", back_populates="usuario", cascade="all, delete-orphan")


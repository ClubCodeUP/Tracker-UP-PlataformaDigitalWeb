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

    concentraciones = relationship("ConcentracionModel", back_populates="carrera")
    usuarios = relationship("UsuarioModel", back_populates="carrera")
    malla = relationship("MallaCurricularModel", back_populates="carrera")


class ConcentracionModel(Base):
    __tablename__ = "concentraciones"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="SET NULL"), nullable=True)
    codigo = Column(String(30), nullable=False, unique=True, index=True)
    nombre = Column(String(150), nullable=False)
    creditos_minimos = Column(Integer, nullable=False, default=12)
    carreras_excluidas = Column(Text, nullable=True)  # JSON list ej: '["INF"]'
    carreras_exclusivas = Column(Text, nullable=True)  # JSON list ej: '["DER"]'
    creditos_por_carrera = Column(Text, nullable=True)  # JSON dict ej: '{"ADM": 12, "CON": 12}'
    notas_reglamento = Column(Text, nullable=True)
    cursos_info = Column(Text, nullable=True)  # JSON con lista oficial de cursos obligatorios y electivos
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    carrera = relationship("CarreraModel", back_populates="concentraciones")


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False)
    concentracion_id = Column(Integer, ForeignKey("concentraciones.id", ondelete="SET NULL"), nullable=True)
    concentracion_secundaria_id = Column(Integer, ForeignKey("concentraciones.id", ondelete="SET NULL"), nullable=True)
    periodo_ingreso = Column(String(10), nullable=False)  # Ej: '2023-1'
    activo = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    carrera = relationship("CarreraModel", back_populates="usuarios")
    concentracion = relationship("ConcentracionModel", foreign_keys=[concentracion_id])
    concentracion_secundaria = relationship("ConcentracionModel", foreign_keys=[concentracion_secundaria_id])
    historial = relationship("HistorialAcademicoModel", back_populates="usuario", cascade="all, delete-orphan")


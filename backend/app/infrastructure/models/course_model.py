"""
Modelos ORM para catálogo de asignaturas, malla curricular y prerrequisitos.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class AsignaturaModel(Base):
    __tablename__ = "asignaturas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    creditos = Column(Numeric(3, 1), nullable=False)
    tipo = Column(String(20), nullable=False, default="OBLIGATORIA")  # OBLIGATORIA / ELECTIVA
    es_cuello_botella = Column(Boolean, default=False, nullable=False)
    descripcion = Column(Text, nullable=True)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    malla_entries = relationship("MallaCurricularModel", back_populates="asignatura")
    historial_entries = relationship("HistorialAcademicoModel", back_populates="asignatura")
    
    # Prerrequisitos donde este curso es el curso objetivo (los requisitos que exige)
    prerrequisitos_exigidos = relationship(
        "PrerrequisitoModel",
        foreign_keys="PrerrequisitoModel.asignatura_id",
        back_populates="asignatura_objetivo",
        cascade="all, delete-orphan"
    )
    # Prerrequisitos donde este curso es el requisito exigido por otros cursos
    cursos_dependientes = relationship(
        "PrerrequisitoModel",
        foreign_keys="PrerrequisitoModel.prerrequisito_asignatura_id",
        back_populates="asignatura_requisito"
    )


class MallaCurricularModel(Base):
    __tablename__ = "malla_curricular"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id", ondelete="CASCADE"), nullable=False)
    asignatura_id = Column(Integer, ForeignKey("asignaturas.id", ondelete="RESTRICT"), nullable=False)
    ciclo_sugerido = Column(Integer, nullable=False)
    concentracion_id = Column(Integer, ForeignKey("concentraciones.id", ondelete="SET NULL"), nullable=True)
    creditos_minimos_requeridos = Column(Numeric(4, 1), nullable=False, default=0.0)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    carrera = relationship("CarreraModel", back_populates="malla")
    asignatura = relationship("AsignaturaModel", back_populates="malla_entries")
    concentracion = relationship("ConcentracionModel")


class PrerrequisitoModel(Base):
    __tablename__ = "prerrequisitos"

    id = Column(Integer, primary_key=True, index=True)
    asignatura_id = Column(Integer, ForeignKey("asignaturas.id", ondelete="CASCADE"), nullable=False)
    prerrequisito_asignatura_id = Column(Integer, ForeignKey("asignaturas.id", ondelete="RESTRICT"), nullable=False)
    grupo_logico = Column(Integer, default=1, nullable=False)
    operador_intra_grupo = Column(String(10), default="AND", nullable=False)
    nota_minima_aprobatoria = Column(Numeric(4, 2), default=11.00, nullable=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    asignatura_objetivo = relationship("AsignaturaModel", foreign_keys=[asignatura_id], back_populates="prerrequisitos_exigidos")
    asignatura_requisito = relationship("AsignaturaModel", foreign_keys=[prerrequisito_asignatura_id], back_populates="cursos_dependientes")


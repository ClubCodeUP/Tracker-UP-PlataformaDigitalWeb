"""
Modelo ORM para el registro de historial académico de los estudiantes.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class HistorialAcademicoModel(Base):
    __tablename__ = "historial_academico"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    asignatura_id = Column(Integer, ForeignKey("asignaturas.id", ondelete="RESTRICT"), nullable=False, index=True)
    periodo_academico = Column(String(10), nullable=False)  # Ej: '2023-1', '2023-2'
    estado = Column(String(20), nullable=False, default="PENDIENTE")  # PENDIENTE, EN_CURSO, APROBADA, DESAPROBADA
    calificacion = Column(Numeric(4, 2), nullable=True)  # Escala 0 a 20
    numero_matricula = Column(Integer, nullable=False, default=1)  # 1, 2, 3
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("usuario_id", "asignatura_id", "periodo_academico", name="uq_usuario_asignatura_periodo"),
    )

    usuario = relationship("UsuarioModel", back_populates="historial")
    asignatura = relationship("AsignaturaModel", back_populates="historial_entries")


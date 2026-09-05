"""
Servicio para la gestión del historial de asignaturas del estudiante (RF-03, RF-07).
"""
from typing import List
from sqlalchemy.orm import Session
from app.domain.exceptions import EntityNotFoundException, InvalidAcademicRecordException
from app.domain.entities import EstadoAsignatura
from app.infrastructure.models.history_model import HistorialAcademicoModel
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.infrastructure.repositories.course_repository import CourseRepository
from app.schemas.history import CourseHistoryCreate, CourseHistoryUpdate, CourseHistoryResponse


class HistoryService:
    @staticmethod
    def _to_response(entry: HistorialAcademicoModel) -> CourseHistoryResponse:
        return CourseHistoryResponse(
            id=entry.id,
            usuario_id=entry.usuario_id,
            asignatura_id=entry.asignatura_id,
            codigo_asignatura=entry.asignatura.codigo,
            nombre_asignatura=entry.asignatura.nombre,
            creditos=float(entry.asignatura.creditos),
            tipo_asignatura=entry.asignatura.tipo,
            periodo_academico=entry.periodo_academico,
            estado=EstadoAsignatura(entry.estado),
            calificacion=float(entry.calificacion) if entry.calificacion is not None else None,
            numero_matricula=entry.numero_matricula,
            es_cuello_botella=entry.asignatura.es_cuello_botella
        )

    @classmethod
    def get_history(cls, db: Session, user_id: int) -> List[CourseHistoryResponse]:
        """Recupera todas las materias registradas en el historial del estudiante."""
        entries = HistoryRepository.get_all_by_user(db, user_id)
        return [cls._to_response(entry) for entry in entries]

    @classmethod
    def add_entry(cls, db: Session, user_id: int, data: CourseHistoryCreate) -> CourseHistoryResponse:
        """Registra una nueva asignatura en el historial del estudiante."""
        # 1. Verificar existencia de la asignatura
        course = CourseRepository.get_by_id(db, data.asignatura_id)
        if not course:
            raise EntityNotFoundException("Asignatura", data.asignatura_id)

        # 2. Si ya existe un registro previo de la materia para este estudiante, actualizarlo
        existing = HistoryRepository.get_by_user_and_course(db, user_id, data.asignatura_id)
        if existing:
            existing.estado = data.estado.value
            existing.calificacion = data.calificacion
            existing.numero_matricula = data.numero_matricula
            existing.periodo_academico = data.periodo_academico
            updated = HistoryRepository.update(db, existing)
            refreshed = HistoryRepository.get_by_id(db, updated.id)
            return cls._to_response(refreshed or updated)

        # 3. Crear modelo
        entry = HistorialAcademicoModel(
            usuario_id=user_id,
            asignatura_id=data.asignatura_id,
            periodo_academico=data.periodo_academico,
            estado=data.estado.value,
            calificacion=data.calificacion,
            numero_matricula=data.numero_matricula
        )
        saved = HistoryRepository.create(db, entry)
        refreshed = HistoryRepository.get_by_id(db, saved.id)
        return cls._to_response(refreshed or saved)

    @classmethod
    def update_entry(
        cls, db: Session, user_id: int, history_id: int, data: CourseHistoryUpdate
    ) -> CourseHistoryResponse:
        """Actualiza el estado, calificación o matrícula de un curso existente."""
        entry = HistoryRepository.get_by_id(db, history_id)
        if not entry or entry.usuario_id != user_id:
            raise EntityNotFoundException("Registro de Historial Académico", history_id)

        if data.estado is not None:
            entry.estado = data.estado.value
        if data.calificacion is not None:
            entry.calificacion = data.calificacion
        elif data.estado in (EstadoAsignatura.PENDIENTE, EstadoAsignatura.EN_CURSO):
            entry.calificacion = None

        if data.numero_matricula is not None:
            entry.numero_matricula = data.numero_matricula

        updated = HistoryRepository.update(db, entry)
        refreshed = HistoryRepository.get_by_id(db, updated.id)
        return cls._to_response(refreshed or updated)

    @classmethod
    def delete_entry(cls, db: Session, user_id: int, history_id: int) -> None:
        """Elimina un registro erróneo del historial."""
        entry = HistoryRepository.get_by_id(db, history_id)
        if not entry or entry.usuario_id != user_id:
            raise EntityNotFoundException("Registro de Historial Académico", history_id)

        HistoryRepository.delete(db, entry)


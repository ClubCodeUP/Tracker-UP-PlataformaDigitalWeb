"""
Servicio optimizado para el cálculo dinámico de métricas curriculares (RF-04, RF-08).
"""
from typing import Dict, Set
from sqlalchemy.orm import Session
from app.domain.entities import EstadoAsignatura
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.infrastructure.repositories.course_repository import CourseRepository
from app.schemas.metrics import AcademicMetricsResponse


class MetricsService:
    @classmethod
    def calculate_metrics(cls, db: Session, user: UsuarioModel) -> AcademicMetricsResponse:
        """Calcula en tiempo real las métricas consolidadas de progreso académico del estudiante."""
        # 1. Obtener información de carrera y total de créditos
        total_creditos_carrera = user.carrera.total_creditos_graduacion if user.carrera else 205

        # 2. Obtener historial del estudiante
        history_entries = HistoryRepository.get_all_by_user(db, user.id)

        # 3. Mapear materias aprobadas únicas (evitando doble conteo en caso de repetición de registros)
        approved_courses: Dict[int, Dict] = {}
        in_progress_courses: Dict[int, Dict] = {}
        risk_courses_count = 0

        # Para cálculo de promedio ponderado:
        suma_calificaciones_ponderadas = 0.0
        suma_creditos_ponderados = 0.0

        # Identificar materias aprobadas y en curso
        for entry in history_entries:
            asignatura = entry.asignatura
            creditos = float(asignatura.creditos)
            
            # Evaluación de cursos en riesgo (RF-13: 2ª o 3ª matrícula)
            if entry.numero_matricula >= 2 and entry.estado in (EstadoAsignatura.EN_CURSO.value, EstadoAsignatura.PENDIENTE.value):
                risk_courses_count += 1

            if entry.estado == EstadoAsignatura.APROBADA.value:
                # Tomar la última nota de aprobación
                approved_courses[entry.asignatura_id] = {
                    "creditos": creditos,
                    "calificacion": float(entry.calificacion) if entry.calificacion is not None else 11.0,
                    "es_cuello_botella": asignatura.es_cuello_botella
                }
            elif entry.estado == EstadoAsignatura.EN_CURSO.value:
                in_progress_courses[entry.asignatura_id] = {
                    "creditos": creditos,
                    "es_cuello_botella": asignatura.es_cuello_botella
                }

        # 4. Sumar créditos únicos aprobados
        creditos_aprobados = sum(c["creditos"] for c in approved_courses.values())
        creditos_en_curso = sum(c["creditos"] for c in in_progress_courses.values())
        creditos_pendientes = max(0.0, float(total_creditos_carrera) - creditos_aprobados)

        # 5. Calcular porcentaje de avance curricular (RF-04, RF-08)
        porcentaje_avance = round((creditos_aprobados / float(total_creditos_carrera)) * 100, 2)

        # 6. Calcular promedio ponderado acumulado de materias aprobadas
        for c in approved_courses.values():
            suma_calificaciones_ponderadas += c["calificacion"] * c["creditos"]
            suma_creditos_ponderados += c["creditos"]

        promedio_ponderado = (
            round(suma_calificaciones_ponderadas / suma_creditos_ponderados, 2)
            if suma_creditos_ponderados > 0
            else None
        )

        # 7. Determinar ciclo referencial según la malla de la carrera
        malla = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        approved_course_ids = set(approved_courses.keys())
        ciclos_aprobados = [
            m.ciclo_sugerido for m in malla if m.asignatura_id in approved_course_ids
        ]
        ciclo_referencial = max(ciclos_aprobados) if ciclos_aprobados else 1

        return AcademicMetricsResponse(
            usuario_id=user.id,
            estudiante=f"{user.nombres} {user.apellidos}",
            carrera=user.carrera.nombre if user.carrera else "No definida",
            total_creditos_carrera=total_creditos_carrera,
            creditos_aprobados=round(creditos_aprobados, 1),
            creditos_en_curso=round(creditos_en_curso, 1),
            creditos_pendientes=round(creditos_pendientes, 1),
            porcentaje_avance=porcentaje_avance,
            ciclo_referencial=ciclo_referencial,
            promedio_ponderado=promedio_ponderado,
            cursos_aprobados_count=len(approved_courses),
            cursos_en_curso_count=len(in_progress_courses),
            cursos_en_riesgo_count=risk_courses_count
        )


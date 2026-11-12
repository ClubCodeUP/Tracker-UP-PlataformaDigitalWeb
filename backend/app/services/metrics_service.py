"""
Servicio optimizado para el cálculo dinámico de métricas curriculares (RF-04, RF-08).
"""
from typing import Dict, Set, Tuple
import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.domain.entities import EstadoAsignatura
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.infrastructure.repositories.course_repository import CourseRepository
from app.schemas.metrics import AcademicMetricsResponse, CohortBenchmarkResponse


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
        malla = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        total_cursos = len(malla) if malla else 50

        if creditos_aprobados > 0:
            porcentaje_avance = round((creditos_aprobados / float(total_creditos_carrera)) * 100, 2)
        elif len(approved_courses) > 0:
            # Si aprobó materias pero son de nivelación (0 créditos), reflejar avance respecto al total de cursos
            porcentaje_avance = round((len(approved_courses) / float(total_cursos)) * 100, 2)
        else:
            porcentaje_avance = 0.0

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

    @classmethod
    def calculate_cohort_benchmark(cls, db: Session, user: UsuarioModel) -> CohortBenchmarkResponse:
        """Calcula la comparativa dual: 1) Vs. Cohorte/Promoción real y 2) Vs. Ritmo teórico de la Malla."""
        student_metrics = cls.calculate_metrics(db, user)

        # 1. Semestres transcurridos
        match = re.match(r"^(\d{4})-(0|1|2)$", (user.periodo_ingreso or "2023-1").strip())
        y_adm, t_adm = (int(match.group(1)), int(match.group(2))) if match else (2023, 1)
        t_adm_norm = 1 if t_adm == 0 else t_adm

        now = datetime.now()
        current_year = now.year
        current_term = 1 if now.month <= 7 else 2

        semesters = ((current_year - y_adm) * 2) + (current_term - t_adm_norm) + 1
        elapsed_semesters = max(1, min(12, semesters))

        # 2. Promedio y avance de la cohorte real
        cohort_users = db.query(UsuarioModel).filter(
            UsuarioModel.carrera_id == user.carrera_id,
            UsuarioModel.periodo_ingreso == user.periodo_ingreso,
            UsuarioModel.activo == True
        ).all()

        cohort_credits = []
        cohort_gpas = []
        for peer in cohort_users:
            peer_metric = cls.calculate_metrics(db, peer)
            cohort_credits.append(peer_metric.creditos_aprobados)
            if peer_metric.promedio_ponderado is not None:
                cohort_gpas.append(peer_metric.promedio_ponderado)

        cohorte_tamano = len(cohort_users)
        cohorte_media_creditos = (
            round(sum(cohort_credits) / len(cohort_credits), 1)
            if cohort_credits
            else student_metrics.creditos_aprobados
        )
        cohorte_media_promedio = (
            round(sum(cohort_gpas) / len(cohort_gpas), 2)
            if cohort_gpas
            else student_metrics.promedio_ponderado
        )
        total_creditos = float(student_metrics.total_creditos_carrera)
        cohorte_media_avance = round((cohorte_media_creditos / total_creditos) * 100, 1)
        diferencia_creditos_cohorte = round(student_metrics.creditos_aprobados - cohorte_media_creditos, 1)

        # 3. Trayectoria teórica según la Malla Oficial
        malla = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        malla_creditos_esperados = sum(
            float(m.asignatura.creditos)
            for m in malla
            if m.ciclo_sugerido <= elapsed_semesters and m.ciclo_sugerido > 0
        )
        if malla_creditos_esperados == 0:
            malla_creditos_esperados = round(elapsed_semesters * 20.5, 1)

        malla_avance_esperado = round((malla_creditos_esperados / total_creditos) * 100, 1)
        diferencia_creditos_malla = round(student_metrics.creditos_aprobados - malla_creditos_esperados, 1)

        # 4. Evaluación y redacción positiva/constructiva
        if student_metrics.creditos_aprobados >= malla_creditos_esperados:
            estado_ritmo = "ADELANTADO"
            mensaje_evaluacion = f"¡Excelente avance! Te encuentras {abs(diferencia_creditos_malla):.1f} créditos por delante del plan sugerido de estudios."
            recomendacion = "Vas a paso firme. Es un momento propicio para enfocar electivos de tu concentración o proyectar prácticas preprofesionales."
        elif abs(diferencia_creditos_malla) <= 12:
            estado_ritmo = "AL_DIA"
            mensaje_evaluacion = "Ritmo académico consistente y alineado al plan de estudios regular de la facultad."
            recomendacion = "Mantener una matrícula de 18 a 21 créditos te permitirá continuar en tu ciclo objetivo con total estabilidad."
        else:
            estado_ritmo = "EN_PROGRESO"
            mensaje_evaluacion = f"Tu trayectoria continúa avanzando. Estás a {abs(diferencia_creditos_malla):.1f} créditos de equilibrar la meta ideal de tu semestre."
            recomendacion = "Recomendamos priorizar los cursos que funcionan como prerrequisito de múltiples materias para optimizar tus opciones de matrícula futura."

        return CohortBenchmarkResponse(
            periodo_ingreso=user.periodo_ingreso,
            semestres_transcurridos=elapsed_semesters,
            estudiante_creditos_aprobados=student_metrics.creditos_aprobados,
            estudiante_promedio_ponderado=student_metrics.promedio_ponderado,
            estudiante_porcentaje_avance=student_metrics.porcentaje_avance,
            cohorte_tamano=cohorte_tamano,
            cohorte_media_creditos=cohorte_media_creditos,
            cohorte_media_promedio=cohorte_media_promedio,
            cohorte_media_avance=cohorte_media_avance,
            diferencia_creditos_cohorte=diferencia_creditos_cohorte,
            malla_creditos_esperados=round(malla_creditos_esperados, 1),
            malla_avance_esperado=malla_avance_esperado,
            diferencia_creditos_malla=diferencia_creditos_malla,
            estado_ritmo=estado_ritmo,
            mensaje_evaluacion=mensaje_evaluacion,
            recomendacion_constructiva=recomendacion,
        )


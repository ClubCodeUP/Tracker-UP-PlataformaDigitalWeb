"""
Motor determinístico de reglas curriculares y evaluación de riesgos académicos (RF-10 al RF-16).
"""
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
from sqlalchemy.orm import Session

from app.domain.entities import EstadoAsignatura, TipoAlerta, SeveridadAlerta
from app.infrastructure.models.user_model import UsuarioModel, ConcentracionModel
from app.infrastructure.models.course_model import MallaCurricularModel, AsignaturaModel
from app.infrastructure.repositories.course_repository import CourseRepository
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.schemas.rules_engine import (
    RiskAlertResponse,
    SuggestedCourseItem,
    CreditRange,
    RecommendationResponse,
    CurriculumEvaluationResponse,
    ConcentrationTrackingProgress,
    StudentConcentrationsStatusResponse,
)


class CurriculumEngineService:
    @staticmethod
    def _parse_period(period: str) -> Tuple[int, int]:
        """Convierte '2023-1' en tupla (2023, 1)."""
        match = re.match(r"^(\d{4})-(0|1|2)$", period.strip())
        if match:
            return int(match.group(1)), int(match.group(2))
        return 2024, 1

    @classmethod
    def _next_academic_period(cls, current_period: str) -> str:
        """Calcula el siguiente periodo académico regular."""
        year, term = cls._parse_period(current_period)
        if term == 1:
            return f"{year}-2"
        elif term == 2:
            return f"{year + 1}-1"
        else:
            return f"{year}-1"

    @classmethod
    def _calculate_elapsed_semesters(cls, admission_period: str, current_period: str) -> int:
        """Calcula el número de semestres transcurridos entre el ingreso y el periodo actual."""
        y_adm, t_adm = cls._parse_period(admission_period)
        y_cur, t_cur = cls._parse_period(current_period)

        # Tratar término 0 como ciclo previo o regular
        t_adm_norm = 1 if t_adm == 0 else t_adm
        t_cur_norm = 1 if t_cur == 0 else t_cur

        semesters = ((y_cur - y_adm) * 2) + (t_cur_norm - t_adm_norm) + 1
        return max(1, semesters)

    @classmethod
    def _build_dependency_dag(cls, db: Session) -> Dict[int, Set[int]]:
        """Construye un grafo dirigido (DAG) donde cada nodo apunta a todas las materias que desbloquea."""
        all_prerreqs = CourseRepository.get_all_prerrequisitos(db)
        direct_unlocks: Dict[int, Set[int]] = defaultdict(set)
        for p in all_prerreqs:
            # prerrequisito_asignatura_id desbloquea a asignatura_id
            direct_unlocks[p.prerrequisito_asignatura_id].add(p.asignatura_id)

        # Calcular clausura transitiva para contar todas las materias posteriores condicionadas
        transitive_unlocks: Dict[int, Set[int]] = {}
        for req_id in list(direct_unlocks.keys()):
            visited: Set[int] = set()
            stack = list(direct_unlocks[req_id])
            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    stack.extend(direct_unlocks.get(curr, []))
            transitive_unlocks[req_id] = visited

        return transitive_unlocks

    @classmethod
    def evaluate_risks(cls, db: Session, user: UsuarioModel) -> List[RiskAlertResponse]:
        """Evalúa el historial del estudiante y emite las 4 alertas de riesgo del MVP (RF-13 a RF-16)."""
        alerts: List[RiskAlertResponse] = []
        history_entries = HistoryRepository.get_all_by_user(db, user.id)

        # 1. Identificar cursos aprobados, fallidos y en curso
        approved_map: Dict[int, float] = {}  # asignatura_id -> calificacion
        in_progress_ids: Set[int] = set()
        retake_entries: List = []

        latest_period = user.periodo_ingreso
        for entry in history_entries:
            if entry.periodo_academico > latest_period:
                latest_period = entry.periodo_academico

            if entry.estado == EstadoAsignatura.APROBADA.value:
                approved_map[entry.asignatura_id] = float(entry.calificacion) if entry.calificacion else 11.0
            elif entry.estado == EstadoAsignatura.EN_CURSO.value:
                in_progress_ids.add(entry.asignatura_id)

            # Detectar si está en 2da o 3ra matrícula y no aprobó previamente
            if entry.numero_matricula >= 2:
                retake_entries.append(entry)

        # --- ALERTA 1: Asignaturas en 2ª o 3ª matrícula (RF-13 - Riesgo Crítico) ---
        for entry in retake_entries:
            # Solo alertar si el registro no está como aprobado en el pasado
            if entry.asignatura_id not in approved_map or entry.estado != EstadoAsignatura.APROBADA.value:
                asig = entry.asignatura
                alerts.append(RiskAlertResponse(
                    tipo_alerta=TipoAlerta.REITERACION_MATRICULA,
                    nivel_severidad=SeveridadAlerta.CRITICA,
                    codigo_asignatura=asig.codigo,
                    nombre_asignatura=asig.nombre,
                    mensaje=(
                        f"Asignatura en {entry.numero_matricula}ª matrícula en el periodo {entry.periodo_academico}. "
                        "Riesgo crítico de desaprobación reiterada bajo el reglamento académico."
                    ),
                    detalles={
                        "numero_matricula": entry.numero_matricula,
                        "periodo": entry.periodo_academico,
                        "estado": entry.estado
                    }
                ))

        # --- ALERTA 2: Prerrequisitos aprobados con nota en límite mínimo (11.00 - 11.50) (RF-14) ---
        # Evaluar cursos que el estudiante está cursando actualmente o pendientes dependientes
        all_prerreqs = CourseRepository.get_all_prerrequisitos(db)
        target_course_ids = in_progress_ids  # Cursos en curso
        for p in all_prerreqs:
            if p.asignatura_id in target_course_ids:
                req_grade = approved_map.get(p.prerrequisito_asignatura_id)
                if req_grade is not None and 11.00 <= req_grade <= 11.50:
                    asig_obj = p.asignatura_objetivo
                    asig_req = p.asignatura_requisito
                    alerts.append(RiskAlertResponse(
                        tipo_alerta=TipoAlerta.PRERREQUISITO_NOTA_LIMITE,
                        nivel_severidad=SeveridadAlerta.ADVERTENCIA,
                        codigo_asignatura=asig_obj.codigo,
                        nombre_asignatura=asig_obj.nombre,
                        mensaje=(
                            f"El curso {asig_obj.codigo} ({asig_obj.nombre}) depende del prerrequisito "
                            f"{asig_req.codigo} ({asig_req.nombre}), el cual fue aprobado en el límite "
                            f"con nota {req_grade:.2f}/20. Se aconseja tutoría o repaso de fundamentos."
                        ),
                        detalles={
                            "prerrequisito_codigo": asig_req.codigo,
                            "prerrequisito_nombre": asig_req.nombre,
                            "nota_obtenida": req_grade
                        }
                    ))

        # --- ALERTA 3: Rezago por permanencia según créditos y tiempo transcurrido (RF-15) ---
        # Referencia temporal: 2024-1 si no hay periodos posteriores
        current_ref_period = max(latest_period, "2024-1")
        elapsed_semesters = cls._calculate_elapsed_semesters(user.periodo_ingreso, current_ref_period)
        
        # Créditos aprobados actuales
        malla_usuario = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        creditos_por_asignatura = {m.asignatura_id: float(m.asignatura.creditos) for m in malla_usuario}
        creditos_aprobados = sum(creditos_por_asignatura.get(aid, 0.0) for aid in approved_map.keys())

        # Ritmo estándar: ~20 créditos por semestre regular
        creditos_esperados = min(
            float(user.carrera.total_creditos_graduacion),
            elapsed_semesters * 20.0
        )

        if elapsed_semesters >= 3:
            ratio_avance = creditos_aprobados / creditos_esperados if creditos_esperados > 0 else 1.0
            if ratio_avance < 0.50:
                alerts.append(RiskAlertResponse(
                    tipo_alerta=TipoAlerta.REZAGO_PERMANENCIA,
                    nivel_severidad=SeveridadAlerta.CRITICA,
                    mensaje=(
                        f"Alerta crítica de permanencia: Han transcurrido {elapsed_semesters} semestres desde "
                        f"su ingreso ({user.periodo_ingreso}) y cuenta con {creditos_aprobados:.1f} créditos aprobados "
                        f"de {creditos_esperados:.1f} esperados (ritmo de avance: {ratio_avance * 100:.1f}%)."
                    ),
                    detalles={
                        "periodo_ingreso": user.periodo_ingreso,
                        "semestres_transcurridos": elapsed_semesters,
                        "creditos_aprobados": creditos_aprobados,
                        "creditos_esperados": creditos_esperados,
                        "ratio_avance": round(ratio_avance, 2)
                    }
                ))
            elif ratio_avance < 0.70:
                alerts.append(RiskAlertResponse(
                    tipo_alerta=TipoAlerta.REZAGO_PERMANENCIA,
                    nivel_severidad=SeveridadAlerta.ADVERTENCIA,
                    mensaje=(
                        f"Alerta de rezago académico: Su progreso ({creditos_aprobados:.1f} créditos) se encuentra "
                        f"por debajo del avance proyectado ({creditos_esperados:.1f} créditos en {elapsed_semesters} semestres)."
                    ),
                    detalles={
                        "periodo_ingreso": user.periodo_ingreso,
                        "semestres_transcurridos": elapsed_semesters,
                        "creditos_aprobados": creditos_aprobados,
                        "creditos_esperados": creditos_esperados,
                        "ratio_avance": round(ratio_avance, 2)
                    }
                ))

        # --- ALERTA 4: Cursos cuello de botella pendientes en la malla (RF-16) ---
        dag_unlocks = cls._build_dependency_dag(db)
        for m in malla_usuario:
            asig = m.asignatura
            if asig.id not in approved_map:
                unlock_count = len(dag_unlocks.get(asig.id, set()))
                if asig.es_cuello_botella or unlock_count >= 2:
                    alerts.append(RiskAlertResponse(
                        tipo_alerta=TipoAlerta.CUELLO_DE_BOTELLA,
                        nivel_severidad=SeveridadAlerta.INFORMATIVA,
                        codigo_asignatura=asig.codigo,
                        nombre_asignatura=asig.nombre,
                        mensaje=(
                            f"La asignatura {asig.codigo} ({asig.nombre}) es un cuello de botella estratégico "
                            f"que condiciona el desbloqueo de {unlock_count} cursos posteriores en la malla."
                        ),
                        detalles={
                            "ciclo_sugerido": m.ciclo_sugerido,
                            "cursos_desbloqueados_count": unlock_count,
                            "es_cuello_botella_formal": asig.es_cuello_botella
                        }
                    ))

        return alerts

    @classmethod
    def generate_recommendations(cls, db: Session, user: UsuarioModel) -> RecommendationResponse:
        """Motor determinístico para recomendar el bloque de matrícula del siguiente ciclo (RF-10, RF-11, RF-12)."""
        malla_usuario = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        history_entries = HistoryRepository.get_all_by_user(db, user.id)
        dag_unlocks = cls._build_dependency_dag(db)

        # 1. Mapear estado académico por asignatura
        approved_ids: Set[int] = set()
        failed_attempts: Dict[int, int] = defaultdict(int)
        latest_period = user.periodo_ingreso

        for entry in history_entries:
            if entry.periodo_academico > latest_period:
                latest_period = entry.periodo_academico

            if entry.estado == EstadoAsignatura.APROBADA.value:
                approved_ids.add(entry.asignatura_id)
            elif entry.estado == EstadoAsignatura.DESAPROBADA.value:
                failed_attempts[entry.asignatura_id] = max(
                    failed_attempts[entry.asignatura_id], entry.numero_matricula
                )

        # Créditos aprobados acumulados
        creditos_map = {m.asignatura_id: float(m.asignatura.creditos) for m in malla_usuario}
        creditos_aprobados = sum(creditos_map.get(aid, 0.0) for aid in approved_ids)

        # 2. Obtener requisitos por materia
        prerreqs_by_course: Dict[int, List] = defaultdict(list)
        for p in CourseRepository.get_all_prerrequisitos(db):
            prerreqs_by_course[p.asignatura_id].append(p)

        # Identificar cursos que aportan a las concentraciones declaradas por el estudiante
        conc_course_codes: Set[str] = set()
        for conc_obj in [user.concentracion, user.concentracion_secundaria]:
            if conc_obj and conc_obj.cursos_info:
                try:
                    c_info = json.loads(conc_obj.cursos_info)
                    for c_item in c_info.get("cursos_obligatorios", []) + c_info.get("cursos_electivos", []):
                        code = c_item.get("codigo", "").strip().upper()
                        if code:
                            conc_course_codes.add(code)
                except Exception:
                    pass

        # 3. Filtrar asignaturas elegibles (que cumplen bolsa de créditos y prerrequisitos)
        eligible_candidates: List[SuggestedCourseItem] = []

        for m in malla_usuario:
            asig = m.asignatura
            # Regla A: No debe haber sido aprobada previamente
            if asig.id in approved_ids:
                continue

            # Regla B: Filtrado de electivas por concentración temática elegida (RF-06)
            if asig.tipo == "ELECTIVA" and m.concentracion_id is not None:
                if user.concentracion_id is not None and m.concentracion_id != user.concentracion_id:
                    continue  # Es de otra concentración

            # Regla C: Bolsa mínima de créditos aprobados requerida (RF-10)
            if creditos_aprobados < float(m.creditos_minimos_requeridos):
                continue

            # Regla D: Prerrequisitos directos aprobados (RF-10)
            direct_reqs = prerreqs_by_course.get(asig.id, [])
            all_reqs_met = True
            for req in direct_reqs:
                if req.prerrequisito_asignatura_id not in approved_ids:
                    all_reqs_met = False
                    break
            if not all_reqs_met:
                continue

            # 4. Cálculo de Prioridad Determinística (RF-12)
            score = 0.0
            motivos = []
            is_reiteracion = False
            proy_matricula = 1

            # Prioridad 1: Cursos desaprobados previamente (Repitencia / 2ª o 3ª matrícula obligatoria)
            if asig.id in failed_attempts and asig.id not in approved_ids:
                is_reiteracion = True
                proy_matricula = failed_attempts[asig.id] + 1
                score += 100000.0 * (proy_matricula - 1)
                motivos.append(f"Prioridad Máxima: Re-matriculación ({proy_matricula}ª matrícula obligatoria)")

            # Prioridad 2: Cuello de botella crítico en la malla
            unlock_count = len(dag_unlocks.get(asig.id, set()))
            if asig.es_cuello_botella or unlock_count >= 2:
                score += 5000.0 + (unlock_count * 500.0)
                motivos.append(f"Cuello de botella (desbloquea {unlock_count} materias)")

            # Prioridad 3: Ciclo sugerido en la malla
            score += (14 - m.ciclo_sugerido) * 200.0
            motivos.append(f"Malla Ciclo {m.ciclo_sugerido}")

            # Prioridad 4: Electivo perteneciente a la(s) concentración(es) declarada(s)
            if asig.codigo.upper() in conc_course_codes:
                score += 350.0
                motivos.append("Aporta a concentración declarada")

            # Prioridad 5: Obligatoria antes que Electiva general
            if asig.tipo == "OBLIGATORIA":
                score += 100.0

            eligible_candidates.append(SuggestedCourseItem(
                asignatura_id=asig.id,
                codigo=asig.codigo,
                nombre=asig.nombre,
                creditos=float(asig.creditos),
                ciclo_sugerido=m.ciclo_sugerido,
                tipo=asig.tipo,
                es_cuello_botella=asig.es_cuello_botella,
                es_reiteracion=is_reiteracion,
                numero_matricula_proyectada=proy_matricula,
                prioridad_score=score,
                motivo_prioridad=" | ".join(motivos)
            ))

        # 5. Algoritmo Greedy con Restricción de Rango Regular de Créditos (RF-11)
        # Ordenamiento determinístico: mayor score primero; en caso de empate, alfabético por código
        eligible_candidates.sort(key=lambda c: (-c.prioridad_score, c.codigo))

        max_creditos_permitidos = float(user.carrera.max_creditos_ciclo_regular) if user.carrera else 22.0
        min_creditos_permitidos = 12.0

        selected_courses: List[SuggestedCourseItem] = []
        accumulated_credits = 0.0

        for candidate in eligible_candidates:
            if accumulated_credits + candidate.creditos <= max_creditos_permitidos:
                selected_courses.append(candidate)
                accumulated_credits += candidate.creditos

        periodo_proyectado = cls._next_academic_period(latest_period)
        concentracion_nombre = user.concentracion.nombre if user.concentracion else "General / Sin concentración"
        concentracion_sec_nombre = user.concentracion_secundaria.nombre if user.concentracion_secundaria else None

        return RecommendationResponse(
            usuario_id=user.id,
            carrera=user.carrera.nombre if user.carrera else "No definida",
            concentracion=concentracion_nombre,
            concentracion_secundaria=concentracion_sec_nombre,
            periodo_proyectado=periodo_proyectado,
            creditos_totales_sugeridos=round(accumulated_credits, 1),
            rango_creditos_permitido=CreditRange(
                minimo_regular=min_creditos_permitidos,
                maximo_regular=max_creditos_permitidos
            ),
            cantidad_cursos_sugeridos=len(selected_courses),
            cursos_sugeridos=selected_courses,
            resumen_criterios_deterministicos=[
                "1. Obligatoriedad legal de matricular asignaturas desaprobadas en 2ª o 3ª matrícula en primer orden.",
                "2. Priorización de cursos 'cuello de botella' según índice de desbloqueo transitivo en el grafo curricular.",
                "3. Priorización por ciclo curricular referencial inferior para evitar desfasaje.",
                "4. Impulso a cursos electivos que computan hacia la(s) concentración(es) declarada(s) del estudiante.",
                f"5. Ajuste estricto dentro de la carga crediticia regular ({min_creditos_permitidos} a {max_creditos_permitidos} créditos)."
            ]
        )

    @classmethod
    def evaluate_concentration_progress(
        cls, db: Session, user: UsuarioModel, conc: ConcentracionModel, used_course_codes: Optional[Set[str]] = None
    ) -> ConcentrationTrackingProgress:
        """
        Evalúa el progreso del estudiante en una concentración específica, aplicando las reglas de:
        - Incompatibilidad con cursos obligatorios del plan de estudios (Norma IV CA 24.06.2026).
        - No duplicidad de cursos entre concentraciones.
        - Verificación de creditaje mínimo y materias obligatorias de la concentración.
        """
        if used_course_codes is None:
            used_course_codes = set()

        history_entries = HistoryRepository.get_all_by_user(db, user.id)
        approved_map = {
            e.asignatura.codigo.upper(): (e.asignatura, float(e.calificacion) if e.calificacion else 11.0)
            for e in history_entries
            if e.estado == EstadoAsignatura.APROBADA.value and e.asignatura
        }

        # Cursos obligatorios de la carrera del estudiante
        malla_usuario = CourseRepository.get_malla_by_carrera(db, user.carrera_id)
        carrera_obligatorias = {
            m.asignatura.codigo.upper() for m in malla_usuario if m.asignatura and m.asignatura.tipo == "OBLIGATORIA"
        }

        # Excepción única de la Norma IV: Finanzas para FCE
        is_fce = bool(user.carrera and user.carrera.codigo.upper() in {"ADM", "CON", "MKT", "NEG", "FIN"})
        is_finanzas_fce = is_fce and "FINANZAS" in conc.nombre.upper()

        cursos_info: Dict[str, Any] = {}
        if conc.cursos_info:
            try:
                cursos_info = json.loads(conc.cursos_info)
            except Exception:
                cursos_info = {}

        raw_oblig = cursos_info.get("cursos_obligatorios", [])
        raw_elect = cursos_info.get("cursos_electivos", [])

        # Evaluar cursos obligatorios de la concentración
        cursos_aprobados_computados: List[Dict[str, Any]] = []
        cursos_oblig_pendientes: List[Dict[str, Any]] = []
        creditos_completados = 0.0

        for co in raw_oblig:
            c_code = co["codigo"].upper()
            # Si el curso es obligatorio de la carrera y no es la excepción Finanzas FCE, no cuenta
            if not is_finanzas_fce and c_code in carrera_obligatorias:
                continue

            if c_code in approved_map and c_code not in used_course_codes:
                asig, nota = approved_map[c_code]
                c_cred = float(co.get("creditos", asig.creditos))
                creditos_completados += c_cred
                used_course_codes.add(c_code)
                cursos_aprobados_computados.append({
                    "codigo": c_code,
                    "nombre": co["nombre"],
                    "creditos": c_cred,
                    "tipo": "OBLIGATORIO_CONCENTRACION",
                    "calificacion": nota
                })
            else:
                cursos_oblig_pendientes.append({
                    "codigo": c_code,
                    "nombre": co["nombre"],
                    "creditos": float(co.get("creditos", 4.0)),
                    "departamento": co.get("departamento", "")
                })

        # Evaluar electivos de la concentración
        cursos_elect_disponibles: List[Dict[str, Any]] = []
        for ce in raw_elect:
            c_code = ce["codigo"].upper()
            if not is_finanzas_fce and c_code in carrera_obligatorias:
                continue

            if c_code in approved_map and c_code not in used_course_codes:
                asig, nota = approved_map[c_code]
                c_cred = float(ce.get("creditos", asig.creditos))
                creditos_completados += c_cred
                used_course_codes.add(c_code)
                cursos_aprobados_computados.append({
                    "codigo": c_code,
                    "nombre": ce["nombre"],
                    "creditos": c_cred,
                    "tipo": "ELECTIVO_CONCENTRACION",
                    "calificacion": nota
                })
            elif c_code not in approved_map:
                cursos_elect_disponibles.append({
                    "codigo": c_code,
                    "nombre": ce["nombre"],
                    "creditos": float(ce.get("creditos", 3.0)),
                    "departamento": ce.get("departamento", "")
                })

        cred_min = conc.creditos_minimos or 12
        # Ajuste de creditaje especial por carrera (ej: Derecho empresarial para ADM/CON = 12 cr)
        if conc.creditos_por_carrera and user.carrera:
            try:
                c_rules = json.loads(conc.creditos_por_carrera)
                if user.carrera.codigo.upper() in c_rules:
                    cred_min = c_rules[user.carrera.codigo.upper()]
            except Exception:
                pass

        esta_completada = (creditos_completados >= cred_min) and (len(cursos_oblig_pendientes) == 0)
        porcentaje_avance = min(100.0, round((creditos_completados / cred_min) * 100.0, 1))

        return ConcentrationTrackingProgress(
            concentracion_id=conc.id,
            codigo=conc.codigo,
            nombre=conc.nombre,
            creditos_minimos=cred_min,
            creditos_completados=round(creditos_completados, 1),
            porcentaje_avance=porcentaje_avance,
            esta_completada=esta_completada,
            cursos_aprobados_computados=cursos_aprobados_computados,
            cursos_obligatorios_pendientes=cursos_oblig_pendientes,
            cursos_electivos_disponibles=cursos_elect_disponibles
        )

    @classmethod
    def get_student_concentrations_status(cls, db: Session, user: UsuarioModel) -> StudentConcentrationsStatusResponse:
        """Determina el estado global de concentraciones del estudiante, umbral de 110 créditos y progreso de las declaradas."""
        history = HistoryRepository.get_all_by_user(db, user.id)
        creditos_aprobados = round(sum(
            float(e.asignatura.creditos) for e in history if e.estado == EstadoAsignatura.APROBADA.value and e.asignatura
        ), 1)

        puede_declarar = creditos_aprobados >= 110.0
        if puede_declarar:
            mensaje = "Cumples con el requisito de 110 créditos acumulados. Puedes declarar hasta dos concentraciones."
        else:
            faltantes = round(110.0 - creditos_aprobados, 1)
            mensaje = f"Aún no alcanzas el requisito de 110 créditos acumulados (te faltan {faltantes} créditos). Norma III CA 24.06.2026."

        used_codes: Set[str] = set()
        prog_primaria = None
        if user.concentracion:
            prog_primaria = cls.evaluate_concentration_progress(db, user, user.concentracion, used_codes)

        prog_secundaria = None
        if user.concentracion_secundaria:
            prog_secundaria = cls.evaluate_concentration_progress(db, user, user.concentracion_secundaria, used_codes)

        # Contar concentraciones elegibles para la carrera
        todas_concs = db.query(ConcentracionModel).all()
        carrera_code = user.carrera.codigo.upper() if user.carrera else ""
        elegibles_count = 0
        for c in todas_concs:
            excluidas = json.loads(c.carreras_excluidas) if c.carreras_excluidas else []
            exclusivas = json.loads(c.carreras_exclusivas) if c.carreras_exclusivas else []
            if carrera_code in excluidas:
                continue
            if exclusivas and carrera_code not in exclusivas:
                continue
            elegibles_count += 1

        total_declaradas = (1 if user.concentracion_id else 0) + (1 if user.concentracion_secundaria_id else 0)

        return StudentConcentrationsStatusResponse(
            usuario_id=user.id,
            carrera_id=user.carrera_id,
            carrera_codigo=carrera_code,
            carrera_nombre=user.carrera.nombre if user.carrera else "No definida",
            creditos_aprobados_totales=creditos_aprobados,
            creditos_minimos_requeridos_acceso=110.0,
            puede_declarar_concentracion=puede_declarar,
            mensaje_estado=mensaje,
            concentracion_primaria=prog_primaria,
            concentracion_secundaria=prog_secundaria,
            total_concentraciones_declaradas=total_declaradas,
            concentraciones_elegibles_count=elegibles_count
        )

    @classmethod
    def evaluate_full_curriculum(cls, db: Session, user: UsuarioModel) -> CurriculumEvaluationResponse:
        """Evaluación integral que combina recomendaciones de matrícula y diagnóstico de riesgos."""
        recomendacion = cls.generate_recommendations(db, user)
        alertas = cls.evaluate_risks(db, user)

        resumen_alertas: Dict[str, int] = defaultdict(int)
        for a in alertas:
            resumen_alertas[a.tipo_alerta.value] += 1

        return CurriculumEvaluationResponse(
            usuario_id=user.id,
            estudiante=f"{user.nombres} {user.apellidos}",
            recomendacion_matricula=recomendacion,
            alertas_riesgo=alertas,
            resumen_alertas=dict(resumen_alertas)
        )


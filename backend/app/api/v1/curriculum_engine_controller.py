import json
from typing import Dict, List, Optional
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user, get_current_user_optional
from app.core.curriculum_loader import CurriculumLoader
from app.domain.exceptions import ConcentrationEligibilityException, EntityNotFoundException
from app.infrastructure.models import CarreraModel, MallaCurricularModel, AsignaturaModel, ConcentracionModel
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.course_repository import CourseRepository
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.schemas.rules_engine import (
    CurriculumEvaluationResponse,
    RecommendationResponse,
    RiskAlertResponse,
    OfficialConcentrationResponse,
    OfficialConcentrationCourseItem,
    ConcentrationTrackingProgress,
    StudentConcentrationsStatusResponse,
    DeclareConcentrationsRequest,
)
from app.services.curriculum_engine_service import CurriculumEngineService

router = APIRouter(prefix="/curriculum", tags=["Motor Curricular y Alertas"])


@router.get(
    "/careers",
    summary="Listar programas académicos y concentraciones disponibles (RF-02)",
    description="Devuelve el catálogo de todas las carreras precargadas en el sistema junto con sus concentraciones oficiales elegibles."
)
def list_careers(db: Session = Depends(get_db)):
    carreras = db.query(CarreraModel).all()
    all_concs = db.query(ConcentracionModel).all()
    results = []
    for c in carreras:
        c_code = c.codigo.upper()
        career_concs = []
        for co in all_concs:
            excluidas = json.loads(co.carreras_excluidas) if co.carreras_excluidas else []
            exclusivas = json.loads(co.carreras_exclusivas) if co.carreras_exclusivas else []
            if c_code in excluidas:
                continue
            if exclusivas and c_code not in exclusivas:
                continue
            career_concs.append({
                "id": co.id,
                "codigo": co.codigo,
                "nombre": co.nombre,
                "creditos_minimos": co.creditos_minimos,
                "descripcion": co.descripcion or co.notas_reglamento
            })

        results.append({
            "id": c.id,
            "codigo": c.codigo,
            "nombre": c.nombre,
            "total_creditos_graduacion": c.total_creditos_graduacion,
            "total_ciclos": c.total_ciclos,
            "max_creditos_ciclo_regular": float(c.max_creditos_ciclo_regular),
            "concentraciones": career_concs
        })
    return results


@router.get(
    "/malla",
    summary="Consultar malla curricular y grafo de flujograma por carrera (RF-05, RF-06)",
    description=(
        "Retorna la estructura completa de asignaturas de la carrera seleccionada (o de la carrera del usuario autenticado), "
        "con sus ciclos sugeridos, prerrequisitos directos, cuellos de botella calculados y concentraciones."
    )
)
def get_malla(
    carrera_id: Optional[int] = Query(None, description="ID de la carrera a consultar (opcional si hay usuario autenticado)"),
    current_user: Optional[UsuarioModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    target_carrera_id = carrera_id
    if target_carrera_id is None:
        if current_user and current_user.carrera_id:
            target_carrera_id = current_user.carrera_id
        else:
            first_carrera = db.query(CarreraModel).first()
            if not first_carrera:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay carreras registradas.")
            target_carrera_id = first_carrera.id

    carrera = db.query(CarreraModel).filter(CarreraModel.id == target_carrera_id).first()
    if not carrera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Carrera con ID {target_carrera_id} no encontrada.")

    # 1. Obtener entradas de la malla
    malla_entries = CourseRepository.get_malla_by_carrera(db, target_carrera_id)

    # 2. Obtener grafo de prerrequisitos
    all_prereqs = CourseRepository.get_all_prerrequisitos(db)
    prereqs_by_target: Dict[int, List] = defaultdict(list)
    unlocks_count: Dict[int, int] = defaultdict(int)

    for p in all_prereqs:
        prereqs_by_target[p.asignatura_id].append(p)
        unlocks_count[p.prerrequisito_asignatura_id] += 1

    # Obtener historial del usuario actual si está autenticado
    user_approved_course_ids = set()
    user_grades = {}
    if current_user:
        user_history = HistoryRepository.get_all_by_user(db, current_user.id)
        for h in user_history:
            if h.estado == "APROBADA":
                user_approved_course_ids.add(h.asignatura_id)
                user_grades[h.asignatura_id] = float(h.calificacion) if h.calificacion is not None else None

    cursos_response = []
    for m in malla_entries:
        asig = m.asignatura
        reqs = [
            {
                "id": p.prerrequisito_asignatura_id,
                "codigo": p.asignatura_requisito.codigo,
                "nombre": p.asignatura_requisito.nombre,
                "aprobado": p.prerrequisito_asignatura_id in user_approved_course_ids,
                "calificacion": user_grades.get(p.prerrequisito_asignatura_id)
            }
            for p in prereqs_by_target.get(asig.id, [])
        ]
        u_count = unlocks_count.get(asig.id, 0)
        is_bottleneck = asig.es_cuello_botella or (u_count >= 2)

        cursos_response.append({
            "id": asig.id,
            "codigo": asig.codigo,
            "nombre": asig.nombre,
            "creditos": float(asig.creditos),
            "ciclo": m.ciclo_sugerido,
            "tipo": asig.tipo,
            "esCuelloBotella": is_bottleneck,
            "creditosMinimosRequeridos": float(m.creditos_minimos_requeridos),
            "concentracion": m.concentracion.nombre if m.concentracion else None,
            "concentracionCodigo": m.concentracion.codigo if m.concentracion else None,
            "desbloqueaCount": u_count,
            "prerrequisitos": reqs
        })

    return {
        "carrera": {
            "id": carrera.id,
            "codigo": carrera.codigo,
            "nombre": carrera.nombre,
            "total_creditos": carrera.total_creditos_graduacion,
            "total_ciclos": carrera.total_ciclos,
            "max_creditos_regular": float(carrera.max_creditos_ciclo_regular)
        },
        "cursos": cursos_response
    }


@router.post(
    "/reload",
    summary="Recargar mallas curriculares desde archivos JSON",
    description="Vuelve a leer el directorio backend/data/curricula/ y sincroniza la base de datos."
)
def reload_curricula(db: Session = Depends(get_db)):
    try:
        results = CurriculumLoader.load_all_curricula(db)
        return {"status": "ok", "carreras_sincronizadas": results}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/evaluate",
    response_model=CurriculumEvaluationResponse,
    summary="Evaluación integral curricular (Recomendación + Riesgos)",
    description=(
        "Ejecuta el motor determinístico completo: evalúa el avance del estudiante, "
        "recomienda el bloque de asignaturas para el siguiente ciclo y emite todas las alertas "
        "de riesgo académico (reiteración de matrícula, prerrequisitos límite, rezago y cuellos de botella)."
    )
)
def evaluate_curriculum(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.evaluate_full_curriculum(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/recommendation",
    response_model=RecommendationResponse,
    summary="Obtener recomendación de bloque de matrícula",
    description=(
        "Genera determinísticamente la propuesta de asignaturas a matricular para el siguiente periodo, "
        "respetando prerrequisitos cumplidos, bolsa de créditos y el rango regular de créditos de la carrera."
    )
)
def get_course_recommendations(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.generate_recommendations(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/risks",
    response_model=List[RiskAlertResponse],
    summary="Diagnóstico de alertas de riesgo académico",
    description=(
        "Emite la lista de alertas codificadas: asignaturas en 2ª/3ª matrícula, prerrequisitos aprobados "
        "con nota en límite (11.00), rezago por permanencia y asignaturas cuello de botella pendientes."
    )
)
def get_risk_alerts(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.evaluate_risks(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "/concentrations",
    response_model=List[OfficialConcentrationResponse],
    summary="Listar las 33 concentraciones oficiales de pregrado (CA 24.06.2026)",
    description="Devuelve el catálogo de 33 concentraciones oficiales con reglas de creditaje, exclusiones por carrera y desglose de asignaturas."
)
def list_official_concentrations(
    carrera_id: Optional[int] = Query(None, description="Filtrar o evaluar elegibilidad para una carrera específica"),
    current_user: Optional[UsuarioModel] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    target_carrera = None
    if carrera_id:
        target_carrera = db.query(CarreraModel).filter(CarreraModel.id == carrera_id).first()
    elif current_user and current_user.carrera:
        target_carrera = current_user.carrera

    carrera_code = target_carrera.codigo.upper() if target_carrera else None

    concs = db.query(ConcentracionModel).order_by(ConcentracionModel.id.asc()).all()
    results = []

    for c in concs:
        excluidas = json.loads(c.carreras_excluidas) if c.carreras_excluidas else []
        exclusivas = json.loads(c.carreras_exclusivas) if c.carreras_exclusivas else []

        aplica = True
        motivo = None

        if carrera_code:
            if carrera_code in excluidas:
                aplica = False
                motivo = f"No aplica para estudiantes de {target_carrera.nombre} (Normativa oficial CA 24.06.2026)."
            elif exclusivas and carrera_code not in exclusivas:
                aplica = False
                motivo = f"Concentración reservada exclusivamente para estudiantes de {', '.join(exclusivas)}."

        cursos_info = {}
        if c.cursos_info:
            try:
                cursos_info = json.loads(c.cursos_info)
            except Exception:
                cursos_info = {}

        raw_oblig = cursos_info.get("cursos_obligatorios", [])
        raw_elect = cursos_info.get("cursos_electivos", [])

        cred_min = c.creditos_minimos
        if c.creditos_por_carrera and carrera_code:
            try:
                c_rules = json.loads(c.creditos_por_carrera)
                if carrera_code in c_rules:
                    cred_min = c_rules[carrera_code]
            except Exception:
                pass

        results.append(OfficialConcentrationResponse(
            id=c.id,
            codigo=c.codigo,
            nombre=c.nombre,
            creditos_minimos=cred_min,
            carreras_excluidas=excluidas,
            carreras_exclusivas=exclusivas,
            notas_reglamento=c.notas_reglamento or "",
            aplica_a_carrera_estudiante=aplica,
            motivo_exclusion=motivo,
            total_cursos=len(raw_oblig) + len(raw_elect),
            cursos_obligatorios=[
                OfficialConcentrationCourseItem(
                    codigo=co.get("codigo", ""),
                    nombre=co.get("nombre", ""),
                    departamento=co.get("departamento", ""),
                    creditos=float(co.get("creditos", 4.0)),
                    es_obligatorio_concentracion=True,
                    horas_teoria=co.get("horas_teoria", 0),
                    horas_practica=co.get("horas_practica", 0)
                )
                for co in raw_oblig
            ],
            cursos_electivos=[
                OfficialConcentrationCourseItem(
                    codigo=ce.get("codigo", ""),
                    nombre=ce.get("nombre", ""),
                    departamento=ce.get("departamento", ""),
                    creditos=float(ce.get("creditos", 3.0)),
                    es_obligatorio_concentracion=False,
                    horas_teoria=ce.get("horas_teoria", 0),
                    horas_practica=ce.get("horas_practica", 0)
                )
                for ce in raw_elect
            ]
        ))

    return results


@router.get(
    "/concentrations/status",
    response_model=StudentConcentrationsStatusResponse,
    summary="Consultar estado de concentraciones del estudiante autenticado",
    description="Evalúa el requisito de 110 créditos acumulados (Norma III CA 24.06.2026) y el progreso de avance en concentraciones declaradas."
)
def get_concentrations_status(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return CurriculumEngineService.get_student_concentrations_status(db, current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/concentrations/declare",
    response_model=StudentConcentrationsStatusResponse,
    summary="Declarar o actualizar concentraciones de pregrado (hasta 2)",
    description="Permite al estudiante oficializar la declaración de hasta 2 concentraciones cuando cuente con 110+ créditos acumulados."
)
def declare_concentrations(
    request: DeclareConcentrationsRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.schemas.user import UserProfileUpdate
    from app.services.profile_service import ProfileService

    update_dto = UserProfileUpdate(
        concentracion_id=request.concentracion_id,
        concentracion_secundaria_id=request.concentracion_secundaria_id
    )
    try:
        ProfileService.update_profile(db, current_user, update_dto)
    except ConcentrationEligibilityException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return CurriculumEngineService.get_student_concentrations_status(db, current_user)

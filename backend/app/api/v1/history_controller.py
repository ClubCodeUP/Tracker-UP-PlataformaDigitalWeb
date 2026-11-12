"""
Controlador CRUD para el historial de asignaturas del estudiante (RF-03, RF-07).
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.domain.entities import EstadoAsignatura
from app.domain.exceptions import EntityNotFoundException, InvalidAcademicRecordException
from app.infrastructure.models.user_model import UsuarioModel
from app.infrastructure.repositories.course_repository import CourseRepository
from app.schemas.history import CourseHistoryCreate, CourseHistoryUpdate, CourseHistoryResponse, BulkDeleteRequest
from app.services.history_service import HistoryService
from app.services.transcript_parser import (
    BLOCK_OPTION_TO_GROUP,
    detect_block_group,
    extract_text_from_pdf_bytes,
    parse_up_transcript_text,
)

router = APIRouter(prefix="/history", tags=["Historial Académico"])


@router.get(
    "",
    response_model=List[CourseHistoryResponse],
    summary="Listar historial académico",
    description="Devuelve el conjunto de asignaturas registradas por el estudiante con sus calificaciones y matrículas."
)
def get_history(
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return HistoryService.get_history(db, current_user.id)


@router.post(
    "",
    response_model=CourseHistoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asignatura en el historial",
    description="Permite registrar una asignatura como aprobada, desaprobada, en curso o pendiente con su nota y veces cursada."
)
def add_course_history(
    data: CourseHistoryCreate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return HistoryService.add_entry(db, current_user.id, data)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidAcademicRecordException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put(
    "/{history_id}",
    response_model=CourseHistoryResponse,
    summary="Actualizar estado o calificación de asignatura",
    description="Actualiza el estado (aprobada/en curso/pendiente), calificación o número de matrícula de una asignatura."
)
def update_course_history(
    history_id: int,
    data: CourseHistoryUpdate,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return HistoryService.update_entry(db, current_user.id, history_id, data)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar registro del historial",
    description="Elimina una entrada de asignatura del historial académico del estudiante."
)
def delete_course_history(
    history_id: int,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        HistoryService.delete_entry(db, current_user.id, history_id)
        return None
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/bulk",
    response_model=List[CourseHistoryResponse],
    summary="Registrar asignaturas en lote",
    description="Permite registrar o actualizar múltiples asignaturas de una sola vez."
)
def add_bulk_history(
    items: List[CourseHistoryCreate],
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return HistoryService.add_bulk_entries(db, current_user.id, items)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except InvalidAcademicRecordException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/bulk-delete",
    summary="Eliminar asignaturas en lote",
    description="Permite desmarcar o eliminar múltiples asignaturas del historial en lote."
)
def delete_bulk_history(
    data: BulkDeleteRequest,
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        count = HistoryService.delete_bulk_entries(db, current_user.id, data.asignatura_ids)
        return {"deleted_count": count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/import-transcript",
    summary="Importar historial desde Unofficial Transcript PDF",
    description="Extrae en memoria las asignaturas, notas, periodos y cursos en curso desde el PDF de Autoservicio UP y actualiza el historial del estudiante."
)
async def import_transcript_pdf(
    file: UploadFile = File(...),
    current_user: UsuarioModel = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos en formato PDF (.pdf)."
        )

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo PDF está vacío."
        )
    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo PDF excede el tamaño máximo permitido (10 MB)."
        )

    try:
        raw_text = extract_text_from_pdf_bytes(pdf_bytes)
        parsed = parse_up_transcript_text(raw_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se pudo procesar el PDF del transcript: {str(e)}"
        )

    if not parsed.courses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se detectaron asignaturas válidas en el PDF. Verifica que sea un Unofficial Transcript de Autoservicio UP."
        )

    malla_entries = CourseRepository.get_malla_by_carrera(db, current_user.carrera_id)
    by_code = {entry.asignatura.codigo.upper(): entry.asignatura for entry in malla_entries}

    # Agrupar slots de Bloques Sello UP disponibles en orden de ciclo
    block_slots: Dict[str, List[Any]] = {}
    for entry in malla_entries:
        group_id = detect_block_group(entry.asignatura.codigo, entry.asignatura.nombre)
        if group_id:
            block_slots.setdefault(group_id, []).append(entry.asignatura)

    used_block_slot_ids = set()
    block_selections: Dict[int, str] = {}
    imported_courses: List[Dict[str, Any]] = []
    unmatched_courses: List[Dict[str, Any]] = []

    approved_count = 0
    in_progress_count = 0
    failed_count = 0

    for course in parsed.courses:
        target_asig = by_code.get(course.codigo)
        matched_via_block = False

        if target_asig is None and course.codigo in BLOCK_OPTION_TO_GROUP:
            group_id = BLOCK_OPTION_TO_GROUP[course.codigo]
            for candidate in block_slots.get(group_id, []):
                if candidate.id not in used_block_slot_ids:
                    target_asig = candidate
                    used_block_slot_ids.add(candidate.id)
                    block_selections[candidate.id] = course.codigo
                    matched_via_block = True
                    break

        if target_asig is None:
            unmatched_courses.append({
                "codigo": course.codigo,
                "titulo": course.titulo,
                "estado": course.estado,
                "calificacion": course.calificacion,
                "periodo": course.periodo,
            })
            continue

        HistoryService.add_entry(
            db,
            current_user.id,
            CourseHistoryCreate(
                asignatura_id=target_asig.id,
                periodo_academico=course.periodo,
                estado=EstadoAsignatura(course.estado),
                calificacion=course.calificacion,
                numero_matricula=course.numero_matricula,
            ),
        )

        if course.estado == "APROBADA":
            approved_count += 1
        elif course.estado == "EN_CURSO":
            in_progress_count += 1
        elif course.estado == "DESAPROBADA":
            failed_count += 1

        imported_courses.append({
            "codigo": course.codigo,
            "nombre": course.titulo if matched_via_block else target_asig.nombre,
            "estado": course.estado,
            "calificacion": course.calificacion,
            "periodo": course.periodo,
            "matched_to": target_asig.nombre if matched_via_block else None,
        })

    return {
        "detected_program": parsed.detected_program,
        "imported_count": len(imported_courses),
        "approved_count": approved_count,
        "in_progress_count": in_progress_count,
        "failed_count": failed_count,
        "retired_skipped_count": parsed.retired_count,
        "block_selections": block_selections,
        "imported_courses": imported_courses,
        "unmatched_courses": unmatched_courses,
    }

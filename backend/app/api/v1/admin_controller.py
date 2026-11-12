"""
Controlador RESTful para el Panel de Administración Académico (Punto 6 del Roadmap).
Permite a personal autorizado actualizar mallas y gestionar solicitudes de cambio de carrera.
"""
import json
import os
import tempfile
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import require_admin_user
from app.infrastructure.models.user_model import UsuarioModel, CarreraModel, SolicitudCambioCarreraModel
from app.core.curriculum_loader import CurriculumLoader
from app.schemas.admin import (
    CareerChangeRequestResponse,
    CareerChangeAction,
    CurriculumUploadResponse
)

router = APIRouter(prefix="/admin", tags=["Panel de Administración"])


@router.get(
    "/career-requests",
    response_model=List[CareerChangeRequestResponse],
    summary="Listar solicitudes de cambio de carrera",
    description="Obtiene todas las solicitudes registradas por alumnos para revisión de personal autorizado."
)
def list_career_requests(
    estado: Optional[str] = None,
    admin_user: UsuarioModel = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    query = db.query(SolicitudCambioCarreraModel)
    if estado:
        query = query.filter(SolicitudCambioCarreraModel.estado == estado.upper())
    requests = query.order_by(SolicitudCambioCarreraModel.creado_en.desc()).all()

    results = []
    for r in requests:
        results.append(CareerChangeRequestResponse(
            id=r.id,
            usuario_id=r.usuario_id,
            estudiante_nombres=r.usuario.nombres if r.usuario else "N/A",
            estudiante_apellidos=r.usuario.apellidos if r.usuario else "N/A",
            estudiante_email=r.usuario.email if r.usuario else "N/A",
            carrera_actual_id=r.carrera_actual_id,
            carrera_actual_nombre=r.carrera_actual.nombre if r.carrera_actual else "N/A",
            carrera_destino_id=r.carrera_destino_id,
            carrera_destino_nombre=r.carrera_destino.nombre if r.carrera_destino else "N/A",
            motivo=r.motivo,
            estado=r.estado,
            respuesta_admin=r.respuesta_admin,
            creado_en=r.creado_en
        ))
    return results


@router.post(
    "/career-requests/{request_id}/action",
    response_model=CareerChangeRequestResponse,
    summary="Aprobar o rechazar solicitud de cambio de carrera",
    description="Ejecuta la autorización administrativa. Si se aprueba, actualiza la carrera oficial del estudiante."
)
def handle_career_request_action(
    request_id: int,
    action: CareerChangeAction,
    admin_user: UsuarioModel = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    req = db.query(SolicitudCambioCarreraModel).filter(SolicitudCambioCarreraModel.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada.")

    if req.estado != "PENDIENTE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La solicitud ya ha sido procesada previamente con estado: {req.estado}."
        )

    if action.accion == "APROBAR":
        req.estado = "APROBADA"
        req.respuesta_admin = action.respuesta_admin or "Cambio de carrera aprobado formalmente."
        
        # Actualizar carrera del estudiante
        student = req.usuario
        if student:
            student.carrera_id = req.carrera_destino_id
            student.concentracion_id = None  # Reiniciar concentración por cambio de facultad/carrera
            db.add(student)
    else:
        req.estado = "RECHAZADA"
        req.respuesta_admin = action.respuesta_admin or "Solicitud no aprobada tras evaluación curricular."

    db.add(req)
    db.commit()
    db.refresh(req)

    return CareerChangeRequestResponse(
        id=req.id,
        usuario_id=req.usuario_id,
        estudiante_nombres=req.usuario.nombres if req.usuario else "N/A",
        estudiante_apellidos=req.usuario.apellidos if req.usuario else "N/A",
        estudiante_email=req.usuario.email if req.usuario else "N/A",
        carrera_actual_id=req.carrera_actual_id,
        carrera_actual_nombre=req.carrera_actual.nombre if req.carrera_actual else "N/A",
        carrera_destino_id=req.carrera_destino_id,
        carrera_destino_nombre=req.carrera_destino.nombre if req.carrera_destino else "N/A",
        motivo=req.motivo,
        estado=req.estado,
        respuesta_admin=req.respuesta_admin,
        creado_en=req.creado_en
    )


@router.post(
    "/curriculum/upload",
    response_model=CurriculumUploadResponse,
    summary="Cargar o actualizar malla curricular (JSON)",
    description="Permite subir un archivo JSON con la especificación de malla curricular y sincronizarla en la base de datos."
)
async def upload_curriculum_file(
    file: UploadFile = File(...),
    admin_user: UsuarioModel = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se admiten archivos en formato JSON (.json)."
        )

    content = await file.read()
    try:
        data = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato JSON inválido: {str(e)}"
        )

    # Guardar en archivo temporal para CurriculumLoader
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", encoding="utf-8") as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name

    try:
        load_result = CurriculumLoader.load_curriculum_from_file(db, tmp_path)
        CurriculumLoader.validate_dag_acyclic(db)
        
        # También guardar una copia en data/curricula
        curricula_dir = CurriculumLoader.DEFAULT_CURRICULA_DIR
        target_path = os.path.join(curricula_dir, os.path.basename(file.filename))
        with open(target_path, "w", encoding="utf-8") as out:
            json.dump(data, out, ensure_ascii=False, indent=2)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error validando la malla curricular: {str(e)}"
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return CurriculumUploadResponse(
        archivo=file.filename,
        carrera_codigo=load_result.get("carrera_codigo", "N/A"),
        carrera_nombre=load_result.get("carrera_nombre", "N/A"),
        cursos_cargados=load_result.get("cursos_cargados", 0),
        prerrequisitos_procesados=load_result.get("prerrequisitos_procesados", 0),
        estado="EXITOSO"
    )


@router.get(
    "/stats",
    summary="Resumen de estadísticas para administradores",
    description="Retorna métricas consolidadas sobre alumnos registrados, carreras y solicitudes."
)
def get_admin_stats(
    admin_user: UsuarioModel = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    total_students = db.query(UsuarioModel).filter(UsuarioModel.rol == "ESTUDIANTE").count()
    total_careers = db.query(CarreraModel).count()
    pending_requests = db.query(SolicitudCambioCarreraModel).filter(SolicitudCambioCarreraModel.estado == "PENDIENTE").count()
    approved_requests = db.query(SolicitudCambioCarreraModel).filter(SolicitudCambioCarreraModel.estado == "APROBADA").count()

    carreras = db.query(CarreraModel).all()
    carreras_stats = []
    for c in carreras:
        students_count = db.query(UsuarioModel).filter(UsuarioModel.carrera_id == c.id, UsuarioModel.rol == "ESTUDIANTE").count()
        carreras_stats.append({
            "id": c.id,
            "codigo": c.codigo,
            "nombre": c.nombre,
            "total_estudiantes": students_count
        })

    return {
        "total_estudiantes": total_students,
        "total_carreras": total_careers,
        "solicitudes_pendientes": pending_requests,
        "solicitudes_aprobadas": approved_requests,
        "carreras": carreras_stats
    }

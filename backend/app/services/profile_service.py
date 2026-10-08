"""
Servicio para la configuración y actualización del perfil del estudiante (RF-02 y Normativa de Concentraciones CA 24.06.2026).
"""
import json
from typing import Optional
from sqlalchemy.orm import Session
from app.domain.exceptions import EntityNotFoundException, ConcentrationEligibilityException
from app.infrastructure.models.user_model import UsuarioModel, ConcentracionModel
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.history_repository import HistoryRepository
from app.schemas.user import UserProfileUpdate, UserProfileResponse


class ProfileService:
    @staticmethod
    def get_profile(user: UsuarioModel, db: Optional[Session] = None) -> UserProfileResponse:
        """Obtiene la información base del perfil del estudiante autenticado y su elegibilidad para concentraciones."""
        active_db = db or Session.object_session(user)
        creditos_acumulados = 0.0

        if active_db:
            history = HistoryRepository.get_all_by_user(active_db, user.id)
            creditos_acumulados = round(sum(
                float(e.asignatura.creditos) for e in history if e.estado == "APROBADA" and e.asignatura
            ), 1)
        elif user.historial:
            creditos_acumulados = round(sum(
                float(e.asignatura.creditos) for e in user.historial if e.estado == "APROBADA" and e.asignatura
            ), 1)

        puede_declarar = creditos_acumulados >= 110.0

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            nombres=user.nombres,
            apellidos=user.apellidos,
            carrera_id=user.carrera_id,
            carrera_nombre=user.carrera.nombre if user.carrera else None,
            carrera_codigo=user.carrera.codigo if user.carrera else None,
            concentracion_id=user.concentracion_id,
            concentracion_nombre=user.concentracion.nombre if user.concentracion else None,
            concentracion_secundaria_id=user.concentracion_secundaria_id,
            concentracion_secundaria_nombre=user.concentracion_secundaria.nombre if user.concentracion_secundaria else None,
            creditos_acumulados=creditos_acumulados,
            puede_declarar_concentracion=puede_declarar,
            periodo_ingreso=user.periodo_ingreso,
            activo=user.activo
        )

    @staticmethod
    def validate_concentration_for_user(db: Session, user: UsuarioModel, conc_id: int, creditos_acumulados: float) -> ConcentracionModel:
        """Valida que el estudiante cumpla con los 110 créditos acumulados y que la concentración no esté excluida para su carrera."""
        if creditos_acumulados < 110.0:
            raise ConcentrationEligibilityException(
                f"El estudiante cuenta con {creditos_acumulados:.1f} créditos aprobados. "
                "Según la Norma III del Consejo Académico (24.06.2026), se requiere un mínimo de 110 créditos acumulados "
                "para participar en el proceso de obtención de concentraciones de pregrado."
            )

        conc = db.query(ConcentracionModel).filter(ConcentracionModel.id == conc_id).first()
        if not conc:
            raise EntityNotFoundException("Concentración oficial", conc_id)

        carrera_codigo = user.carrera.codigo.upper() if user.carrera else ""
        if conc.carreras_excluidas:
            try:
                excluidas = json.loads(conc.carreras_excluidas)
                if carrera_codigo in excluidas:
                    raise ConcentrationEligibilityException(
                        f"La concentración '{conc.nombre}' ({conc.codigo}) no aplica para los estudiantes de "
                        f"la carrera de {user.carrera.nombre} según la normativa oficial de la Universidad del Pacífico."
                    )
            except json.JSONDecodeError:
                pass

        if conc.carreras_exclusivas:
            try:
                exclusivas = json.loads(conc.carreras_exclusivas)
                if exclusivas and carrera_codigo not in exclusivas:
                    raise ConcentrationEligibilityException(
                        f"La concentración '{conc.nombre}' ({conc.codigo}) está reservada exclusivamente para estudiantes de "
                        f"{', '.join(exclusivas)}."
                    )
            except json.JSONDecodeError:
                pass

        return conc

    @staticmethod
    def update_profile(db: Session, user: UsuarioModel, update_data: UserProfileUpdate) -> UserProfileResponse:
        """Actualiza la carrera, concentraciones (hasta 2) y periodo de ingreso del estudiante."""
        if update_data.carrera_id is not None:
            carrera = UserRepository.get_carrera_by_id(db, update_data.carrera_id)
            if not carrera:
                raise EntityNotFoundException("Carrera", update_data.carrera_id)
            user.carrera_id = update_data.carrera_id

        history = HistoryRepository.get_all_by_user(db, user.id)
        creditos_acumulados = round(sum(
            float(e.asignatura.creditos) for e in history if e.estado == "APROBADA" and e.asignatura
        ), 1)

        # Concentración primaria
        if update_data.concentracion_id is not None:
            if update_data.concentracion_id <= 0:
                user.concentracion_id = None
            else:
                ProfileService.validate_concentration_for_user(db, user, update_data.concentracion_id, creditos_acumulados)
                user.concentracion_id = update_data.concentracion_id

        # Concentración secundaria
        if update_data.concentracion_secundaria_id is not None:
            if update_data.concentracion_secundaria_id <= 0:
                user.concentracion_secundaria_id = None
            else:
                target_sec_id = update_data.concentracion_secundaria_id
                target_prim_id = user.concentracion_id
                if target_prim_id and target_sec_id == target_prim_id:
                    raise ConcentrationEligibilityException("No se puede elegir la misma concentración como primaria y secundaria.")

                ProfileService.validate_concentration_for_user(db, user, target_sec_id, creditos_acumulados)
                user.concentracion_secundaria_id = target_sec_id

        if update_data.periodo_ingreso is not None:
            user.periodo_ingreso = update_data.periodo_ingreso.strip()

        updated_user = UserRepository.update(db, user)
        refreshed = UserRepository.get_by_id(db, updated_user.id)
        return ProfileService.get_profile(refreshed or updated_user, db)

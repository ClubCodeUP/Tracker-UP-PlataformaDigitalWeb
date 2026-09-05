"""
Servicio centralizado de carga y sincronización de mallas curriculares ("Curriculum as Code").
Carga especificaciones curriculares desde JSON a la base de datos relacional y valida el DAG de dependencias.
"""
import glob
import json
import logging
import os
from typing import Dict, List, Set
from collections import defaultdict

from sqlalchemy.orm import Session

from app.infrastructure.models import (
    CarreraModel,
    ConcentracionModel,
    AsignaturaModel,
    MallaCurricularModel,
    PrerrequisitoModel
)
from app.schemas.curriculum_load import CurriculumFileSchema

logger = logging.getLogger(__name__)


class CurriculumCycleException(Exception):
    """Excepción lanzada si se detecta un bucle o ciclo infinito en los prerrequisitos."""
    pass


class CurriculumLoader:
    DEFAULT_CURRICULA_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "curricula")
    )

    @classmethod
    def load_all_curricula(cls, db: Session, directory: str = None) -> List[Dict]:
        """
        Escanea el directorio de mallas y procesa cada archivo JSON.
        Ordena para dar prioridad a las carreras con ID explícito.
        """
        target_dir = directory or cls.DEFAULT_CURRICULA_DIR
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            logger.warning(f"Directorio de mallas creado: {target_dir}")
            return []

        json_files = glob.glob(os.path.join(target_dir, "*.json"))
        # Ordenar para que ingenieria_informacion se procese primero si existe
        json_files.sort(key=lambda x: 0 if "informacion" in x else 1)

        results = []
        for file_path in json_files:
            try:
                res = cls.load_curriculum_from_file(db, file_path)
                results.append(res)
            except Exception as e:
                logger.error(f"Error cargando malla desde {file_path}: {e}")
                raise e

        # Purgar asignaturas huérfanas (como datos de prueba antiguos) del catálogo global
        cls.purge_orphan_courses(db)

        # Validar consistencia global del DAG de prerrequisitos
        cls.validate_dag_acyclic(db)

        return results

    @classmethod
    def purge_orphan_courses(cls, db: Session) -> int:
        """
        Elimina del catálogo global cualquier asignatura que no pertenezca a ninguna malla curricular activa,
        así como sus dependencias en la tabla de prerrequisitos.
        """
        active_asig_subquery = db.query(MallaCurricularModel.asignatura_id).distinct()
        orphan_asigs = db.query(AsignaturaModel).filter(
            ~AsignaturaModel.id.in_(active_asig_subquery)
        ).all()

        if not orphan_asigs:
            return 0

        orphan_ids = [a.id for a in orphan_asigs]
        db.query(PrerrequisitoModel).filter(
            (PrerrequisitoModel.asignatura_id.in_(orphan_ids)) |
            (PrerrequisitoModel.prerrequisito_asignatura_id.in_(orphan_ids))
        ).delete(synchronize_session=False)

        deleted_count = db.query(AsignaturaModel).filter(
            AsignaturaModel.id.in_(orphan_ids)
        ).delete(synchronize_session=False)

        db.commit()
        logger.info(f"Se purgaron {deleted_count} asignaturas huérfanas del catálogo.")
        return deleted_count

    @classmethod
    def load_curriculum_from_file(cls, db: Session, file_path: str) -> Dict:
        """Parsea y persiste una carrera individual desde su archivo JSON."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        curriculum = CurriculumFileSchema.model_validate(data)
        carrera_def = curriculum.carrera

        # 1. Upsert Carrera
        carrera = None
        if carrera_def.id:
            carrera = db.query(CarreraModel).filter(CarreraModel.id == carrera_def.id).first()
        if not carrera:
            carrera = db.query(CarreraModel).filter(CarreraModel.codigo == carrera_def.codigo.upper()).first()

        if not carrera:
            kwargs = {
                "codigo": carrera_def.codigo.upper(),
                "nombre": carrera_def.nombre,
                "total_creditos_graduacion": carrera_def.total_creditos_graduacion,
                "total_ciclos": carrera_def.total_ciclos,
                "max_creditos_ciclo_regular": carrera_def.max_creditos_ciclo_regular
            }
            if carrera_def.id:
                kwargs["id"] = carrera_def.id
            carrera = CarreraModel(**kwargs)
            db.add(carrera)
            db.flush()
        else:
            carrera.nombre = carrera_def.nombre
            carrera.total_creditos_graduacion = carrera_def.total_creditos_graduacion
            carrera.total_ciclos = carrera_def.total_ciclos
            carrera.max_creditos_ciclo_regular = carrera_def.max_creditos_ciclo_regular
            db.flush()

        # 2. Upsert Concentraciones
        conc_map: Dict[str, int] = {}
        for conc_def in curriculum.concentraciones:
            conc = None
            if conc_def.id:
                conc = db.query(ConcentracionModel).filter(ConcentracionModel.id == conc_def.id).first()
            if not conc:
                conc = db.query(ConcentracionModel).filter(
                    ConcentracionModel.carrera_id == carrera.id,
                    ConcentracionModel.codigo == conc_def.codigo.upper()
                ).first()

            if not conc:
                conc_kwargs = {
                    "carrera_id": carrera.id,
                    "codigo": conc_def.codigo.upper(),
                    "nombre": conc_def.nombre,
                    "descripcion": conc_def.descripcion
                }
                if conc_def.id:
                    conc_kwargs["id"] = conc_def.id
                conc = ConcentracionModel(**conc_kwargs)
                db.add(conc)
                db.flush()
            else:
                conc.nombre = conc_def.nombre
                conc.descripcion = conc_def.descripcion
                db.flush()
            conc_map[conc_def.codigo.upper()] = conc.id

        # 3. Upsert Asignaturas del catálogo
        courses_count = 0
        active_asig_ids: Set[int] = set()
        prereqs_to_create: List[tuple] = []  # (target_code, req_code)

        for c_def in curriculum.cursos:
            c_code = c_def.codigo.strip().upper()
            asignatura = None
            if c_def.id:
                asignatura = db.query(AsignaturaModel).filter(AsignaturaModel.id == c_def.id).first()
            if not asignatura:
                asignatura = db.query(AsignaturaModel).filter(AsignaturaModel.codigo == c_code).first()

            if not asignatura:
                asig_kwargs = {
                    "codigo": c_code,
                    "nombre": c_def.nombre.strip(),
                    "creditos": c_def.creditos,
                    "tipo": c_def.tipo.upper(),
                    "es_cuello_botella": c_def.es_cuello_botella
                }
                if c_def.id:
                    asig_kwargs["id"] = c_def.id
                asignatura = AsignaturaModel(**asig_kwargs)
                db.add(asignatura)
                db.flush()
            else:
                asignatura.nombre = c_def.nombre.strip()
                asignatura.creditos = c_def.creditos
                asignatura.tipo = c_def.tipo.upper()
                if c_def.es_cuello_botella:
                    asignatura.es_cuello_botella = True
                db.flush()

            active_asig_ids.add(asignatura.id)

            # 4. Vincular a la Malla Curricular
            conc_id = conc_map.get(c_def.concentracion_codigo.upper()) if c_def.concentracion_codigo else None
            malla = db.query(MallaCurricularModel).filter(
                MallaCurricularModel.carrera_id == carrera.id,
                MallaCurricularModel.asignatura_id == asignatura.id
            ).first()

            if not malla:
                malla = MallaCurricularModel(
                    carrera_id=carrera.id,
                    asignatura_id=asignatura.id,
                    ciclo_sugerido=c_def.ciclo_sugerido,
                    concentracion_id=conc_id,
                    creditos_minimos_requeridos=c_def.creditos_minimos_requeridos
                )
                db.add(malla)
            else:
                malla.ciclo_sugerido = c_def.ciclo_sugerido
                malla.concentracion_id = conc_id
                malla.creditos_minimos_requeridos = c_def.creditos_minimos_requeridos

            courses_count += 1

            for req_code in c_def.prerrequisitos:
                if req_code and req_code.strip():
                    prereqs_to_create.append((c_code, req_code.strip().upper()))

        # Sincronización estricta: eliminar de la malla asignaturas que ya no pertenecen a esta carrera
        if active_asig_ids:
            db.query(MallaCurricularModel).filter(
                MallaCurricularModel.carrera_id == carrera.id,
                ~MallaCurricularModel.asignatura_id.in_(active_asig_ids)
            ).delete(synchronize_session=False)

        db.flush()

        # 5. Conectar Prerrequisitos
        prereqs_count = 0
        for target_code, req_code in prereqs_to_create:
            asig_target = db.query(AsignaturaModel).filter(AsignaturaModel.codigo == target_code).first()
            asig_req = db.query(AsignaturaModel).filter(AsignaturaModel.codigo == req_code).first()

            if asig_target and asig_req and asig_target.id != asig_req.id:
                existing_prereq = db.query(PrerrequisitoModel).filter(
                    PrerrequisitoModel.asignatura_id == asig_target.id,
                    PrerrequisitoModel.prerrequisito_asignatura_id == asig_req.id
                ).first()

                if not existing_prereq:
                    new_prereq = PrerrequisitoModel(
                        asignatura_id=asig_target.id,
                        prerrequisito_asignatura_id=asig_req.id,
                        grupo_logico=1,
                        operador_intra_grupo="AND",
                        nota_minima_aprobatoria=11.00
                    )
                    db.add(new_prereq)
                    prereqs_count += 1

        db.commit()

        return {
            "carrera_id": carrera.id,
            "carrera_codigo": carrera.codigo,
            "carrera_nombre": carrera.nombre,
            "cursos_procesados": courses_count,
            "prerrequisitos_nuevos": prereqs_count,
            "archivo": os.path.basename(file_path)
        }

    @classmethod
    def validate_dag_acyclic(cls, db: Session) -> None:
        """Verifica que el grafo dirigido de prerrequisitos no contenga ciclos."""
        prereqs = db.query(PrerrequisitoModel).all()
        adj: Dict[int, List[int]] = defaultdict(list)
        all_nodes: Set[int] = set()

        for p in prereqs:
            adj[p.prerrequisito_asignatura_id].append(p.asignatura_id)
            all_nodes.add(p.prerrequisito_asignatura_id)
            all_nodes.add(p.asignatura_id)

        state: Dict[int, int] = {node: 0 for node in all_nodes}

        def dfs(node: int, path: List[int]) -> None:
            state[node] = 1
            for neighbor in adj[node]:
                if state[neighbor] == 1:
                    cycle_path = " -> ".join(map(str, path + [neighbor]))
                    raise CurriculumCycleException(
                        f"Dependencia circular detectada en el grafo curricular: {cycle_path}"
                    )
                if state[neighbor] == 0:
                    dfs(neighbor, path + [neighbor])
            state[node] = 2

        for n in all_nodes:
            if state[n] == 0:
                dfs(n, [n])


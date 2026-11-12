"""
Generador automático de mallas curriculares oficiales de la UP (12 carreras).
Extrae la topología completa (nodos, ciclos, aristas de prerrequisito) desde los PDFs de flujograma
y cruza con los PDFs tabulares para asignar los códigos oficiales reales (PowerCampus/Banner),
créditos exactos y tipos de curso, preservando metadatos y concentraciones.
"""
import os
import json
import sys
from typing import Dict, Any, List

# Asegurar path de backend
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, BACKEND_DIR)

from scripts.extractor_flujograma_v2 import build_curriculum_graph_and_validate
from app.schemas.curriculum_load import CurriculumFileSchema

CURRICULA_DIR = os.path.join(BACKEND_DIR, "data", "curricula")
os.makedirs(CURRICULA_DIR, exist_ok=True)

CAREER_SPECS = [
    {
        "filename": "administracion.json",
        "flujo": "docs/mallas/ADMINISTRACION.pdf",
        "tabular": "docs/mallas_tabulares/administracion_tabular.pdf",
        "id": 2,
        "codigo": "ADM",
        "nombre": "Administración",
        "facultad": "Facultad de Ciencias Empresariales",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "contabilidad.json",
        "flujo": "docs/mallas/CONTABILIDAD.pdf",
        "tabular": "docs/mallas_tabulares/contabilidad_tabular.pdf",
        "id": 3,
        "codigo": "CON",
        "nombre": "Contabilidad",
        "facultad": "Facultad de Ciencias Empresariales",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "derecho.json",
        "flujo": "docs/mallas/DERECHO.pdf",
        "tabular": "docs/mallas_tabulares/derecho_tabular.pdf",
        "id": 4,
        "codigo": "DER",
        "nombre": "Derecho",
        "facultad": "Facultad de Derecho",
        "total_creditos": 240,
        "total_ciclos": 12,
    },
    {
        "filename": "economia.json",
        "flujo": "docs/mallas/ECONOMIA.pdf",
        "tabular": "docs/mallas_tabulares/economia_tabular.pdf",
        "id": 5,
        "codigo": "ECO",
        "nombre": "Economía",
        "facultad": "Facultad de Economía y Finanzas",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "finanzas.json",
        "flujo": "docs/mallas/FINANZAS.pdf",
        "tabular": "docs/mallas_tabulares/finanzas_tabular.pdf",
        "id": 6,
        "codigo": "FIN",
        "nombre": "Finanzas",
        "facultad": "Facultad de Economía y Finanzas",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "humanidades_digitales.json",
        "flujo": "docs/mallas/HUMANIDADES DIGITALES.pdf",
        "tabular": "docs/mallas_tabulares/humanidades_digitales_tabular.pdf",
        "id": 7,
        "codigo": "HUM",
        "nombre": "Humanidades Digitales",
        "facultad": "Facultad de Ciencias Empresariales",
        "total_creditos": 205,
        "total_ciclos": 10,
    },
    {
        "filename": "ingenieria_empresarial.json",
        "flujo": "docs/mallas/INGENIERÍA EMPRESARIAL.pdf",
        "tabular": "docs/mallas_tabulares/ingenieria_empresarial_tabular.pdf",
        "id": 8,
        "codigo": "EMP",
        "nombre": "Ingeniería Empresarial",
        "facultad": "Facultad de Ingeniería",
        "total_creditos": 218,
        "total_ciclos": 10,
    },
    {
        "filename": "ingenieria_informacion.json",
        "flujo": "docs/mallas/INGENIERÍA DE LA INFORMACIÓN.pdf",
        "tabular": "docs/mallas_tabulares/ingenieria_informacion_tabular.pdf",
        "id": 1,
        "codigo": "INF",
        "nombre": "Ingeniería de la Información",
        "facultad": "Facultad de Ingeniería",
        "total_creditos": 218,
        "total_ciclos": 10,
    },
    {
        "filename": "innovacion_diseno.json",
        "flujo": "docs/mallas/INGENIERÍA EN INNOVACIÓN Y DISEÑO.pdf",
        "tabular": "docs/mallas_tabulares/ingenieria_innovacion_diseño_tabular.pdf",
        "id": 9,
        "codigo": "IID",
        "nombre": "Ingeniería en Innovación y Diseño",
        "facultad": "Facultad de Ingeniería",
        "total_creditos": 218,
        "total_ciclos": 10,
    },
    {
        "filename": "marketing.json",
        "flujo": "docs/mallas/MARKETING.pdf",
        "tabular": "docs/mallas_tabulares/marketing_tabular.pdf",
        "id": 10,
        "codigo": "MKT",
        "nombre": "Marketing",
        "facultad": "Facultad de Ciencias Empresariales",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "negocios_internacionales.json",
        "flujo": "docs/mallas/NEGOCIOS INTERNACIONALES.pdf",
        "tabular": "docs/mallas_tabulares/negocios_internacionales_tabular.pdf",
        "id": 11,
        "codigo": "NEG",
        "nombre": "Negocios Internacionales",
        "facultad": "Facultad de Ciencias Empresariales",
        "total_creditos": 204,
        "total_ciclos": 10,
    },
    {
        "filename": "politica_filosofia_economia.json",
        "flujo": "docs/mallas/POLÍTICA, FILOSOFÍA Y ECONOMÍA.pdf",
        "tabular": "docs/mallas_tabulares/politica_filosofia_economia_tabular.pdf",
        "id": 12,
        "codigo": "PFE",
        "nombre": "Política, Filosofía y Economía",
        "facultad": "Facultad de Economía y Finanzas",
        "total_creditos": 200,
        "total_ciclos": 10,
        "use_existing_courses": True,  # Ya tenía códigos oficiales UP completos
    },
]


def load_existing_concentraciones(target_path: str) -> List[Dict[str, Any]]:
    if os.path.exists(target_path):
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                d = json.load(f)
                return d.get("concentraciones", [])
        except Exception:
            pass
    return []


def generate_all_official():
    print("=" * 75)
    print("GENERADOR DE MALLAS OFICIALES UP (EXTRACCIÓN AUTOMÁTICA VISIO + TABULAR)")
    print("=" * 75)

    stats = []

    for spec in CAREER_SPECS:
        target_path = os.path.join(CURRICULA_DIR, spec["filename"])
        concs = load_existing_concentraciones(target_path)

        if spec.get("use_existing_courses") and os.path.exists(target_path):
            with open(target_path, "r", encoding="utf-8") as f:
                curr_data = json.load(f)
            courses = curr_data.get("cursos", [])
            print(f"[PRESERVED] {spec['nombre']}: {len(courses)} cursos oficiales existentes.")
        else:
            tmp_json = f"/tmp/{spec['filename']}"
            # Ejecutar extractor con ambos PDFs
            build_curriculum_graph_and_validate(
                flujo_path=spec["flujo"],
                malla_path=spec["tabular"],
                career_override=spec["nombre"],
                json_out=tmp_json
            )

            with open(tmp_json, "r", encoding="utf-8") as f:
                extracted = json.load(f)
            courses = extracted.get("cursos", [])

            # Limpiar archivo temporal
            if os.path.exists(tmp_json):
                os.remove(tmp_json)

        # Configurar creditos_minimos_requeridos para electivos o cursos avanzados
        for c in courses:
            ciclo = c.get("ciclo_sugerido", 1)
            if c.get("tipo") == "ELECTIVA" and not c.get("creditos_minimos_requeridos"):
                c["creditos_minimos_requeridos"] = max(50.0, float((ciclo - 1) * 15))
            elif ciclo >= 4 and not c.get("prerrequisitos") and not c.get("creditos_minimos_requeridos"):
                c["creditos_minimos_requeridos"] = max(50.0, float((ciclo - 1) * 15))

        # Construir estructura canónica
        carr_info = {
            "id": spec.get("id"),
            "codigo": spec["codigo"],
            "nombre": spec["nombre"],
            "facultad": spec.get("facultad", "Universidad del Pacífico"),
            "plan": "2024" if spec["codigo"] == "PFE" else "2022",
            "total_creditos_graduacion": spec.get("total_creditos", 205),
            "total_ciclos": spec.get("total_ciclos", 10),
            "max_creditos_ciclo_regular": 22.0,
        }

        final_data = {
            "carrera": carr_info,
            "concentraciones": concs,
            "cursos": courses,
        }

        # Validar rigurosamente con CurriculumFileSchema
        CurriculumFileSchema.model_validate(final_data)

        # Guardar en backend/data/curricula/
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)

        edge_count = sum(len(c.get("prerrequisitos", [])) for c in courses)
        official_codes = sum(1 for c in courses if not c.get("codigo", "").startswith("GEN-"))
        print(f"[OK] Guardado: {spec['filename']:<32} | {len(courses)} cursos ({official_codes} oficiales) | {edge_count} prerreqs | {len(concs)} concentraciones")
        stats.append((spec["nombre"], len(courses), official_codes, edge_count))

    print("\n" + "=" * 75)
    print("RESUMEN DE GENERACIÓN:")
    for name, n_c, n_of, n_e in stats:
        print(f"  - {name:<35}: {n_c:2d} cursos ({n_of:2d} oficiales), {n_e:2d} aristas DAG")
    print("=" * 75)


if __name__ == "__main__":
    generate_all_official()

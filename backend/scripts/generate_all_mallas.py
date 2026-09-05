"""
Generador e Ingestor de Mallas Curriculares Oficiales UP (12 Carreras).
Genera los JSONs en backend/data/curricula/ basados fielmente en los PDFs de docs/mallas/.
"""
import json
import os
from typing import Dict, Any, List

CURRICULA_DIR = r"e:\Coding\Tracker-UP-PlataformaDigitalWeb\backend\data\curricula"
os.makedirs(CURRICULA_DIR, exist_ok=True)

def save_curriculum(filename: str, data: Dict[str, Any]):
    for course in data.get("cursos", []):
        if course.get("tipo") == "ELECTIVA" and "creditos_minimos_requeridos" not in course:
            course["creditos_minimos_requeridos"] = max(50.0, float((course.get("ciclo_sugerido", 1) - 1) * 15))
        elif course.get("ciclo_sugerido", 0) >= 4 and not course.get("prerrequisitos") and "creditos_minimos_requeridos" not in course:
            course["creditos_minimos_requeridos"] = max(50.0, float((course.get("ciclo_sugerido", 1) - 1) * 15))

    path = os.path.join(CURRICULA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Guardado: {filename} ({len(data['cursos'])} cursos)")

# =============================================================================
# 1. INGENIERÍA DE LA INFORMACIÓN (INF) - PLAN 2022
# =============================================================================
inf_data = {
  "carrera": {
    "id": 1,
    "codigo": "INF",
    "nombre": "Ingeniería de la Información",
    "facultad": "Facultad de Ingeniería",
    "plan": "2022",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "id": 1,
      "codigo": "CONC-SWE",
      "nombre": "Ingeniería de Software y Sistemas Cloud",
      "descripcion": "Arquitecturas distribuidas, desarrollo web/móvil y DevOps."
    },
    {
      "id": 2,
      "codigo": "CONC-DS",
      "nombre": "Ciencia de Datos e Inteligencia Artificial",
      "descripcion": "Modelado estadístico, machine learning y procesamiento big data."
    }
  ],
  "cursos": [
    # Ciclo 0
    {"codigo": "134654", "nombre": "Nivelación en Matemática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    # Ciclo 1 (4 cursos / 18 cr)
    {"codigo": "170001", "nombre": "Introducción a la Ingeniería", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    # Ciclo 2 (5 cursos / 22 cr)
    {"codigo": "170002", "nombre": "Herramientas de Programación", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170131"]},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    # Ciclo 3 (6 cursos / 24 cr)
    {"codigo": "170003", "nombre": "Algoritmos y Estructura de Datos", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170002"]},
    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092"]},
    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138650"]},
    {"codigo": "120020", "nombre": "Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},

    # Ciclo 4 (5 cursos / 20 cr)
    {"codigo": "130225", "nombre": "Estadística II", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130224"]},
    {"codigo": "170004", "nombre": "Ingeniería de Procesos", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170001"]},
    {"codigo": "170005", "nombre": "Matemáticas Discretas para la Computación", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170003"]},
    {"codigo": "141040", "nombre": "Marketing Estratégico", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    # Ciclo 5 (5 cursos / 20 cr)
    {"codigo": "170007", "nombre": "Fundamentos de Analítica", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "170008", "nombre": "Programación Avanzada para la Ciencia de Datos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170003"]},
    {"codigo": "170009", "nombre": "Álgebra Lineal Aplicada", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "170010", "nombre": "Ingeniería de Datos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170003"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093", "132642"]},

    # Ciclo 6 (5 cursos / 20 cr)
    {"codigo": "170011", "nombre": "Física", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170012", "nombre": "Data Mining", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "170013", "nombre": "Machine Learning", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170005"]},
    {"codigo": "141045", "nombre": "Gestión del Capital Humano", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120030"]},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    # Ciclo 7 (5 cursos / 20 cr)
    {"codigo": "170014", "nombre": "Analítica de la Web", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170007"]},
    {"codigo": "170015", "nombre": "Inteligencia Computacional", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170009"]},
    {"codigo": "170016", "nombre": "Desarrollo de Soluciones Empresariales", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170004"]},
    {"codigo": "141050", "nombre": "Estrategia", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020", "141040"]},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    # Ciclo 8 (6 cursos / 22 cr)
    {"codigo": "170017", "nombre": "Tecnología para el Desarrollo Sostenible", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170011"]},
    {"codigo": "170018", "nombre": "Computación de Alto Desempeño y Cloud Computing", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "concentracion_codigo": "CONC-SWE", "prerrequisitos": ["170008"]},
    {"codigo": "170019", "nombre": "Deep Learning", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "concentracion_codigo": "CONC-DS", "prerrequisitos": ["170013"]},
    {"codigo": "170020", "nombre": "Infraestructura Tecnológica", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170006"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},
    {"codigo": "ELE-INF01", "nombre": "Electivo I (Especialidad)", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "ELECTIVA", "prerrequisitos": []},

    # Ciclo 9 (6 cursos / 22 cr)
    {"codigo": "170021", "nombre": "Big Data Analytics", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170010"]},
    {"codigo": "170022", "nombre": "Business Intelligence", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170012"]},
    {"codigo": "170023", "nombre": "Trabajo Final de Ingeniería de la Información I", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170015", "170016", "141050", "170019"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},
    {"codigo": "ELE-INF02", "nombre": "Electivo II", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},
    {"codigo": "ELE-INF03", "nombre": "Electivo III", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},

    # Ciclo 10 (5 cursos / 18 cr)
    {"codigo": "170024", "nombre": "Trabajo Final de Ingeniería de la Información II", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["170023"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120047"]},
    {"codigo": "ELE-INF04", "nombre": "Electivo IV", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "ELECTIVA", "prerrequisitos": []}
  ]
}
save_curriculum("ingenieria_informacion.json", inf_data)

# =============================================================================
# 2. INGENIERÍA EMPRESARIAL (EMP) - PLAN 2022
# =============================================================================
emp_data = {
  "carrera": {
    "codigo": "EMP",
    "nombre": "Ingeniería Empresarial",
    "facultad": "Facultad de Ingeniería",
    "plan": "2022",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-PROC",
      "nombre": "Gestión de Procesos y Operaciones",
      "descripcion": "Optimización de procesos, supply chain y analítica operacional."
    },
    {
      "codigo": "CONC-PROJ",
      "nombre": "Dirección de Proyectos y Transformación Digital",
      "descripcion": "Metodologías ágiles, gestión del cambio e innovación empresarial."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170001", "nombre": "Introducción a la Ingeniería", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "170002", "nombre": "Herramientas de Programación", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["170131"]},
    {"codigo": "170030", "nombre": "Tecnología y Negocios Digitales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092"]},
    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138650"]},
    {"codigo": "120020", "nombre": "Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},

    {"codigo": "130225", "nombre": "Estadística II", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130224"]},
    {"codigo": "170004", "nombre": "Ingeniería de Procesos", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170001"]},
    {"codigo": "170031", "nombre": "Design Thinking and Technological Innovation", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170030"]},
    {"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170004"]},
    {"codigo": "141040", "nombre": "Marketing Estratégico", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170007", "nombre": "Fundamentos de Analítica", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "170032", "nombre": "Investigación de Operaciones", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "170033", "nombre": "Métodos de Investigación Cuantitativa", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "170010", "nombre": "Ingeniería de Datos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170006"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093", "132642"]},

    {"codigo": "170011", "nombre": "Física", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170034", "nombre": "Procesos de Suministro", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170004", "170032"]},
    {"codigo": "170035", "nombre": "Gestión de Proyectos", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170031", "170033"]},
    {"codigo": "141045", "nombre": "Gestión del Capital Humano", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120030"]},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170036", "nombre": "Procesos de Producción", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170034"]},
    {"codigo": "170037", "nombre": "Metodologías Ágiles", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170035"]},
    {"codigo": "170016", "nombre": "Desarrollo de Soluciones Empresariales", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170010"]},
    {"codigo": "141050", "nombre": "Estrategia", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020", "141040"]},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170017", "nombre": "Tecnología para el Desarrollo Sostenible", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170011"]},
    {"codigo": "170038", "nombre": "Procesos de Distribución", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170036"]},
    {"codigo": "170039", "nombre": "Transformación Digital y Gestión del Cambio", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170037"]},
    {"codigo": "170020", "nombre": "Infraestructura Tecnológica", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170016"]},
    {"codigo": "170040", "nombre": "Formulación y Evaluación de Proyectos", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020", "141050"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},
    {"codigo": "ELE-EMP01", "nombre": "Electivo I", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "ELECTIVA", "prerrequisitos": []},

    {"codigo": "170041", "nombre": "Gerencia de Ingeniería de Valor", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170038", "170040"]},
    {"codigo": "170042", "nombre": "Emprendimiento Tecnológico", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170039"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},
    {"codigo": "ELE-EMP02", "nombre": "Electivo II", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},
    {"codigo": "ELE-EMP03", "nombre": "Electivo III", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},

    {"codigo": "170043", "nombre": "Trabajo Final de Ingeniería Empresarial", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["170017", "170020", "170041", "170042"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120047"]},
    {"codigo": "ELE-EMP04", "nombre": "Electivo IV", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "ELECTIVA", "prerrequisitos": []}
  ]
}
save_curriculum("ingenieria_empresarial.json", emp_data)

# =============================================================================
# 3. DERECHO (DER) - PLAN 2022 (12 Ciclos)
# =============================================================================
der_data = {
  "carrera": {
    "codigo": "DER",
    "nombre": "Derecho",
    "facultad": "Facultad de Derecho",
    "plan": "2022",
    "total_creditos_graduacion": 230,
    "total_ciclos": 12,
    "max_creditos_ciclo_regular": 23.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-CORP",
      "nombre": "Derecho Corporativo y Financiero",
      "descripcion": "Especialización en sociedades, finanzas corporativas, banca y mercado de valores."
    },
    {
      "codigo": "CONC-PUB",
      "nombre": "Regulación, Arbitraje y Políticas Públicas",
      "descripcion": "Especialización en derecho administrativo, regulación económica y arbitraje internacional."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141038", "nombre": "Fundamentos de las Ciencias Empresariales", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "180001", "nombre": "Introducción al Derecho", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": []},
    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "180002", "nombre": "Personas del Derecho Civil", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["180001"]},
    {"codigo": "180003", "nombre": "Derecho Constitucional General", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180001"]},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    {"codigo": "180004", "nombre": "Acto Jurídico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["180002"]},
    {"codigo": "180005", "nombre": "Derechos Reales", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["180001"]},
    {"codigo": "120020", "nombre": "Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},

    {"codigo": "180006", "nombre": "Teoría General del Proceso", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180001"]},
    {"codigo": "180007", "nombre": "Derecho Procesal Constitucional", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["180003"]},
    {"codigo": "180008", "nombre": "Obligaciones", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180004", "180005"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "180009", "nombre": "Derecho Procesal Civil", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["180006"]},
    {"codigo": "180010", "nombre": "Contratos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180008"]},
    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},

    {"codigo": "180011", "nombre": "Responsabilidad Extracontractual", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["180008"]},
    {"codigo": "180012", "nombre": "Derecho Penal", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180001"]},
    {"codigo": "180013", "nombre": "Derecho Administrativo I", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["180007"]},
    {"codigo": "180014", "nombre": "Contratos Especiales", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["180010"]},
    {"codigo": "180015", "nombre": "Sistemas Financieros", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093"]},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "180016", "nombre": "Derecho Laboral I", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180010"]},
    {"codigo": "180017", "nombre": "Derecho Internacional Público", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180003"]},
    {"codigo": "180018", "nombre": "Derecho Administrativo II", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180013"]},
    {"codigo": "180019", "nombre": "Instituciones de Derecho Mercantil", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180014"]},
    {"codigo": "180020", "nombre": "Derecho Penal Económico", "creditos": 2.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180012"]},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "180021", "nombre": "Análisis Económico del Derecho", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["132642"]},
    {"codigo": "180022", "nombre": "Derecho Internacional Privado", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["180010"]},
    {"codigo": "180023", "nombre": "Sociedades", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["180019"]},
    {"codigo": "180024", "nombre": "Derecho Tributario I", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["180013"]},
    {"codigo": "180025", "nombre": "Derecho Procesal Penal", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["180006", "180012"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},

    {"codigo": "180026", "nombre": "Arbitraje", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["180009", "180010"]},
    {"codigo": "180027", "nombre": "Derecho Laboral II", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["180016"]},
    {"codigo": "180028", "nombre": "Destrezas Legales I", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 120.0, "prerrequisitos": []},
    {"codigo": "180029", "nombre": "Derecho Tributario II", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["180024"]},
    {"codigo": "180030", "nombre": "Derecho de Familia y Sucesiones", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["180004"]},
    {"codigo": "180031", "nombre": "Economía y Estadística Aplicada al Derecho", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["132642"]},

    {"codigo": "180032", "nombre": "Libre Competencia", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["180023"]},
    {"codigo": "180033", "nombre": "Derecho Ambiental", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["180018"]},
    {"codigo": "180034", "nombre": "Destrezas Legales II", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["180028"]},
    {"codigo": "180035", "nombre": "Políticas Públicas", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["180018"]},

    {"codigo": "180036", "nombre": "Innovación Legal y Tecnología", "creditos": 3.0, "ciclo_sugerido": 11, "tipo": "OBLIGATORIA", "prerrequisitos": ["180023"]},
    {"codigo": "180037", "nombre": "Banca y Mercado de Valores", "creditos": 4.0, "ciclo_sugerido": 11, "tipo": "OBLIGATORIA", "prerrequisitos": ["180015", "180023"]},
    {"codigo": "180038", "nombre": "Responsabilidad del Abogado", "creditos": 3.0, "ciclo_sugerido": 11, "tipo": "OBLIGATORIA", "prerrequisitos": ["180034"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 11, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 160.0, "prerrequisitos": []},

    {"codigo": "180039", "nombre": "Seminario de Tesis", "creditos": 3.0, "ciclo_sugerido": 12, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 180.0, "prerrequisitos": []},
    {"codigo": "180040", "nombre": "Derecho del Comercio Internacional", "creditos": 3.0, "ciclo_sugerido": 12, "tipo": "OBLIGATORIA", "prerrequisitos": ["180026"]},
    {"codigo": "180041", "nombre": "Instrumentos de Financiación y Garantías", "creditos": 4.0, "ciclo_sugerido": 12, "tipo": "OBLIGATORIA", "prerrequisitos": ["180023"]},
    {"codigo": "ELE-DER01", "nombre": "Electivo Especializado", "creditos": 4.0, "ciclo_sugerido": 12, "tipo": "ELECTIVA", "prerrequisitos": []}
  ]
}
save_curriculum("derecho.json", der_data)

# =============================================================================
# 4. ECONOMÍA (ECO) - PLAN 2022-I
# =============================================================================
eco_data = {
  "carrera": {
    "codigo": "ECO",
    "nombre": "Economía",
    "facultad": "Facultad de Economía y Finanzas",
    "plan": "2022-I",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-MACRO",
      "nombre": "Macroeconomía y Finanzas Cuantitativas",
      "descripcion": "Modelos DSGE, política monetaria y análisis macrofinanciero."
    },
    {
      "codigo": "CONC-APPLIED",
      "nombre": "Economía Aplicada y Políticas Públicas",
      "descripcion": "Microeconometría, evaluación de impacto y organización industrial."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["134654"]},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132641"]},
    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138649"]},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},
    {"codigo": "120020", "nombre": "Introducción al Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "132001", "nombre": "Microeconomía I", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132641", "138650"]},
    {"codigo": "138001", "nombre": "Matemáticas III", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138650"]},
    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138650"]},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},

    {"codigo": "132002", "nombre": "Microeconomía II", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132001"]},
    {"codigo": "132003", "nombre": "Macroeconomía I", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132642", "138001"]},
    {"codigo": "138002", "nombre": "Matemáticas IV", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["138001"]},
    {"codigo": "130225", "nombre": "Estadística II", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130224"]},

    {"codigo": "132004", "nombre": "Teoría del Comercio Internacional", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["132002"]},
    {"codigo": "132005", "nombre": "Macroeconomía II", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132003"]},
    {"codigo": "132006", "nombre": "Evaluación Privada de Proyectos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092", "132002"]},
    {"codigo": "130001", "nombre": "Estadística Aplicada", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130225"]},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "132007", "nombre": "Gestión de los Recursos Naturales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["132002"]},
    {"codigo": "132008", "nombre": "Macroeconomía III", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["132005"]},
    {"codigo": "150001", "nombre": "Economía Financiera I", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["132006"]},
    {"codigo": "130002", "nombre": "Econometría I", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130001", "138002"]},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},

    {"codigo": "132009", "nombre": "Historia del Pensamiento Económico", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["132005"]},
    {"codigo": "132010", "nombre": "Macroeconomía Internacional", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["132008"]},
    {"codigo": "180050", "nombre": "Economía y Derecho", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["132001", "132003"]},
    {"codigo": "130003", "nombre": "Econometría II", "creditos": 5.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["130002"]},

    {"codigo": "132011", "nombre": "Organización Industrial", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["132002"]},
    {"codigo": "132012", "nombre": "Política Económica", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["132005"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},

    {"codigo": "132013", "nombre": "Investigación Económica I", "creditos": 2.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 160.0, "prerrequisitos": []},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 160.0, "prerrequisitos": []},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "132014", "nombre": "Investigación Económica II", "creditos": 2.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["132013"]},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []}
  ]
}
save_curriculum("economia.json", eco_data)

# =============================================================================
# 5. FINANZAS (FIN) - PLAN 2022-I
# =============================================================================
fin_data = {
  "carrera": {
    "codigo": "FIN",
    "nombre": "Finanzas",
    "facultad": "Facultad de Economía y Finanzas",
    "plan": "2022-I",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-RISK",
      "nombre": "Gestión de Riesgos y Mercado de Capitales",
      "descripcion": "Riesgo de crédito, mercado y liquidez, derivados e inversión cuantitativa."
    },
    {
      "codigo": "CONC-CORPFIN",
      "nombre": "Banca de Inversión y Finanzas Corporativas",
      "descripcion": "M&A, estructuración de deuda, valorización de empresas y venture capital."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132641"]},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},
    {"codigo": "120020", "nombre": "Introducción al Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138001", "nombre": "Matemáticas III", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["138650"]},
    {"codigo": "132001", "nombre": "Microeconomía I", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "180015", "nombre": "Sistemas Financieros", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092", "132642"]},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},

    {"codigo": "130225", "nombre": "Estadística II", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130224"]},
    {"codigo": "150002", "nombre": "Microeconomía Financiera", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["132001"]},
    {"codigo": "150003", "nombre": "Macroeconomía Financiera", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["132642"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["160092"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},

    {"codigo": "130001", "nombre": "Estadística Aplicada", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "150004", "nombre": "Finanzas Corporativas I", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["150020", "180015"]},
    {"codigo": "150005", "nombre": "Finanzas Sostenibles", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020"]},
    {"codigo": "150006", "nombre": "Análisis Financiero", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020"]},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},

    {"codigo": "130002", "nombre": "Econometría I", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["130001"]},
    {"codigo": "150007", "nombre": "Renta Fija", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},
    {"codigo": "150008", "nombre": "Renta Variable", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},
    {"codigo": "150009", "nombre": "Instrumentos Derivados", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},

    {"codigo": "150010", "nombre": "Finanzas Cuantitativas", "creditos": 5.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["130002", "150008"]},
    {"codigo": "150011", "nombre": "Finanzas Corporativas II", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},
    {"codigo": "180060", "nombre": "Derecho de la Empresa", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 120.0, "prerrequisitos": []},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "150012", "nombre": "Análisis y Gestión de Riesgo", "creditos": 5.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["150007", "150008", "150010"]},
    {"codigo": "150013", "nombre": "Riesgo Crediticio", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["150011"]},
    {"codigo": "150014", "nombre": "Negociación Financiera", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 140.0, "prerrequisitos": []},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},

    {"codigo": "150015", "nombre": "Certificaciones Internacionales", "creditos": 2.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 140.0, "prerrequisitos": []},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 160.0, "prerrequisitos": []},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "150016", "nombre": "Investigación Financiera", "creditos": 2.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["150012", "150013"]},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []}
  ]
}
save_curriculum("finanzas.json", fin_data)

# =============================================================================
# 6. CONTABILIDAD (CON) - PLAN 2022
# =============================================================================
con_data = {
  "carrera": {
    "codigo": "CON",
    "nombre": "Contabilidad",
    "facultad": "Facultad de Ciencias Empresariales",
    "plan": "2022",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 24.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-AUDIT",
      "nombre": "Auditoría Financiera y Control de Riesgos",
      "descripcion": "Auditoría interna, forense, compliance y evaluación de control interno."
    },
    {
      "codigo": "CONC-TRIB",
      "nombre": "Tributación Internacional y Planeamiento Fiscal",
      "descripcion": "Tributación corporativa, fiscalidad internacional y precios de transferencia."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "141038", "nombre": "Fundamentos de las Ciencias Empresariales", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "138651", "nombre": "Matemáticas para los Negocios", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["141038"]},
    {"codigo": "180070", "nombre": "Derecho Civil y Comercial", "creditos": 3.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138651"]},
    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["160092"]},
    {"codigo": "180071", "nombre": "Derecho Laboral y Tributario", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["180070"]},
    {"codigo": "120046", "nombre": "Bloque Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120040", "nombre": "Bloque Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141060", "nombre": "Analítica de Datos para los Negocios", "creditos": 3.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "141061", "nombre": "Diseño Organizacional y Estrategia", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["141038"]},
    {"codigo": "1MN018", "nombre": "Fundamentos de Marketing", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160094", "nombre": "Contabilidad Financiera Aplicada", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["160093"]},
    {"codigo": "120048", "nombre": "Bloque Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},
    {"codigo": "120020", "nombre": "Bloque Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141062", "nombre": "Análisis Multivariado para los Negocios", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["141060"]},
    {"codigo": "141063", "nombre": "Métodos Cuantitativos para la Gestión", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "141064", "nombre": "Gestión del Cambio y Transformación Cultural", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["141061"]},
    {"codigo": "160095", "nombre": "Contabilidad de Costos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["160094"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093"]},

    {"codigo": "141065", "nombre": "Gestión de Operaciones en las Organizaciones", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["141063"]},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},
    {"codigo": "160096", "nombre": "Normas Contables Internacionales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["160094"]},
    {"codigo": "160097", "nombre": "Contabilidad de Gestión", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["160095"]},
    {"codigo": "150004", "nombre": "Finanzas Corporativas I", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020"]},
    {"codigo": "120045", "nombre": "Bloque Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141066", "nombre": "Sistemas de Información y Análisis de Datos", "creditos": 3.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["141062"]},
    {"codigo": "160098", "nombre": "SAP Hana para la Gestión de la Información", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["160095"]},
    {"codigo": "160099", "nombre": "Auditoría", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["160096"]},
    {"codigo": "150030", "nombre": "Evaluación Financiera de las Organizaciones", "creditos": 5.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},
    {"codigo": "160100", "nombre": "Contabilidad y Finanzas Avanzadas", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},

    {"codigo": "141051", "nombre": "Dirección Estratégica", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["141065"]},
    {"codigo": "160101", "nombre": "Control Interno y Gestión del Riesgo", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["160099"]},
    {"codigo": "160102", "nombre": "Gestión y Costos Estratégicos", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["160097"]},
    {"codigo": "160103", "nombre": "Tributación Aplicada I", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["180071"]},

    {"codigo": "160104", "nombre": "Gestión de la Información y Métricas de Sostenibilidad", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["160101"]},
    {"codigo": "160105", "nombre": "Tributación Aplicada II", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["160103"]},
    {"codigo": "120030", "nombre": "Bloque Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120047", "nombre": "Bloque Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},

    {"codigo": "160106", "nombre": "Investigación para Contadores", "creditos": 5.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["160104", "160105"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []}
  ]
}
save_curriculum("contabilidad.json", con_data)

# =============================================================================
# 7. NEGOCIOS INTERNACIONALES (NEG) - PLAN 2022
# =============================================================================
neg_data = {
  "carrera": {
    "codigo": "NEG",
    "nombre": "Negocios Internacionales",
    "facultad": "Facultad de Ciencias Empresariales",
    "plan": "2022",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 24.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-GLOBALLOG",
      "nombre": "Cadena de Suministro Global y Operaciones Internacionales",
      "descripcion": "Logística portuaria, aduanas, distribución internacional y comercio marítimo."
    },
    {
      "codigo": "CONC-INTMKT",
      "nombre": "Estrategias de Internacionalización y Expansión Global",
      "descripcion": "Penetración de mercados, negociaciones internacionales y global branding."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "141038", "nombre": "Fundamentos de las Ciencias Empresariales", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "138651", "nombre": "Matemáticas para los Negocios", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "120040", "nombre": "Bloque Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138651"]},
    {"codigo": "141061", "nombre": "Diseño Organizacional y Estrategia", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["141038"]},
    {"codigo": "160107", "nombre": "Contabilidad para la Toma de Decisiones", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093"]},
    {"codigo": "120045", "nombre": "Bloque Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120030", "nombre": "Bloque Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141060", "nombre": "Analítica de Datos para los Negocios", "creditos": 3.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "141040", "nombre": "Marketing Estratégico", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["141061"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093"]},
    {"codigo": "141070", "nombre": "Teoría del Comercio Internacional y Proceso de Integración", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["132642"]},
    {"codigo": "120046", "nombre": "Bloque Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141062", "nombre": "Análisis Multivariado para los Negocios", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["141060"]},
    {"codigo": "141071", "nombre": "Investigación de Mercados", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["141040", "130224"]},
    {"codigo": "141072", "nombre": "Fundamentos Económicos y Organizacionales para los Negocios", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["141061"]},
    {"codigo": "150004", "nombre": "Finanzas Corporativas I", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020"]},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},
    {"codigo": "120048", "nombre": "Bloque Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},

    {"codigo": "141073", "nombre": "Innovación y Gestión en Negocios Digitales", "creditos": 3.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["141061"]},
    {"codigo": "141074", "nombre": "Gestión Sostenible de la Oferta Exportable", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["141070"]},
    {"codigo": "141075", "nombre": "Administración del Comercio Internacional", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["141070"]},
    {"codigo": "150031", "nombre": "International Finance", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["150004"]},
    {"codigo": "180072", "nombre": "Derecho para los Negocios Internacionales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["141070"]},

    {"codigo": "141066", "nombre": "Sistemas de Información y Análisis de Datos", "creditos": 3.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["141062"]},
    {"codigo": "141076", "nombre": "Logística Internacional", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["141075"]},
    {"codigo": "141077", "nombre": "Dirección Internacional de Empresas", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["141072"]},
    {"codigo": "141078", "nombre": "International Affairs", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["180072"]},
    {"codigo": "120047", "nombre": "Bloque Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},

    {"codigo": "141051", "nombre": "Dirección Estratégica", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["141077"]},
    {"codigo": "141079", "nombre": "Gestión de Mercados Globales", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["141071"]},
    {"codigo": "141080", "nombre": "Cross Cultural & International Management", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["141077"]},
    {"codigo": "141081", "nombre": "Negociaciones Comerciales Internacionales", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["180072"]},
    {"codigo": "120020", "nombre": "Bloque Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141082", "nombre": "Investigación Aplicada en Negocios Internacionales", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["141076", "141079"]},
    {"codigo": "141083", "nombre": "Estrategias de Internacionalización", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["141051", "141080"]},
    {"codigo": "141084", "nombre": "International Human Resources Management", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["141080"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "141085", "nombre": "International Business Plan", "creditos": 5.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["141082", "141083"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []}
  ]
}
save_curriculum("negocios_internacionales.json", neg_data)

# =============================================================================
# 8. HUMANIDADES DIGITALES (HUM) - PLAN DE ESTUDIOS
# =============================================================================
hum_data = {
  "carrera": {
    "codigo": "HUM",
    "nombre": "Humanidades Digitales",
    "facultad": "Facultad de Humanidades",
    "plan": "2022",
    "total_creditos_graduacion": 200,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-CULTDATA",
      "nombre": "Patrimonio Cultural Digital y Archivos",
      "descripcion": "Digitalización de archivos, curaduría digital, visualización del patrimonio cultural."
    },
    {
      "codigo": "CONC-COMUX",
      "nombre": "Comunicación Digital, Medios y UX",
      "descripcion": "Diseño de experiencia de usuario, análisis de redes sociales y medios digitales interactivos."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},
    {"codigo": "120101", "nombre": "Introducción a las Humanidades Digitales", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120102", "nombre": "Lectura Crítica de la Prensa Digital y Redes Sociales", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170002", "nombre": "Herramientas de Programación", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["170131"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},
    {"codigo": "120103", "nombre": "Cultura, Visualidad y Política", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "141040", "nombre": "Marketing Estratégico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120020", "nombre": "Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120104", "nombre": "Comunicación Digital", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},

    {"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170002"]},
    {"codigo": "170005", "nombre": "Matemáticas Discretas para la Computación", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "120105", "nombre": "Taller de Humanidades Digitales 1", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["120101"]},
    {"codigo": "120106", "nombre": "Curaduría Digital de Contenidos Culturales", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["120103"]},
    {"codigo": "120107", "nombre": "Análisis Cuantitativo en las Ciencias Humanas", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},

    {"codigo": "120108", "nombre": "Análisis de Datos Geográficos", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170006"]},
    {"codigo": "170007", "nombre": "Fundamentos de Analítica", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "170031", "nombre": "Design Thinking and Technological Innovation", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "120109", "nombre": "Procesamiento de Datos Multimedia", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120108"]},
    {"codigo": "120110", "nombre": "Introducción al Análisis de Texto", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170007"]},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120111", "nombre": "Ciencia, Tecnología y Sociedad", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120112", "nombre": "Literatura y Videojuegos", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "120113", "nombre": "Análisis de Datos Multimedia", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120109"]},
    {"codigo": "120114", "nombre": "Diseño", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170031"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},
    {"codigo": "120115", "nombre": "Dinámicas Espaciales y Territoriales del Perú", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170010", "nombre": "Ingeniería de Datos", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120113"]},
    {"codigo": "120116", "nombre": "Machine Learning para Negocios y Humanidades", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120110", "170005"]},
    {"codigo": "120117", "nombre": "Experiencia del Usuario", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120114"]},
    {"codigo": "120118", "nombre": "Taller de Humanidades Digitales 2", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120105"]},

    {"codigo": "120119", "nombre": "Taller de Humanidades Digitales 3", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120118"]},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "120120", "nombre": "Gobierno Electrónico", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["170010"]},
    {"codigo": "120121", "nombre": "Trabajo Final de Humanidades Digitales", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120116", "120119"]},
    {"codigo": "120122", "nombre": "Ética en la Era Digital", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120050"]}
  ]
}
save_curriculum("humanidades_digitales.json", hum_data)

# =============================================================================
# 9. INGENIERÍA EN INNOVACIÓN Y DISEÑO (IID) - PLAN DE ESTUDIOS
# =============================================================================
iid_data = {
  "carrera": {
    "codigo": "IID",
    "nombre": "Ingeniería en Innovación y Diseño",
    "facultad": "Facultad de Ingeniería",
    "plan": "2022",
    "total_creditos_graduacion": 205,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-UXUI",
      "nombre": "Diseño de Experiencia de Usuario y Productos Digitales",
      "descripcion": "UX Research, diseño interactivo y prototipado avanzado de productos digitales."
    },
    {
      "codigo": "CONC-INDDES",
      "nombre": "Innovación de Materiales y Diseño Industrial",
      "descripcion": "Diseño de productos físicos sostenibles, fabricación digital e ingeniería de materiales."
    }
  ],
  "cursos": [
    {"codigo": "134654", "nombre": "Nivelación en Matemática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170001", "nombre": "Introducción a la Ingeniería", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},

    {"codigo": "170002", "nombre": "Herramientas de Programación", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["170131"]},
    {"codigo": "170030", "nombre": "Tecnología y Negocios Digitales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},

    {"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["160092"]},
    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "120020", "nombre": "Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},

    {"codigo": "130225", "nombre": "Estadística II", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170002"]},
    {"codigo": "170031", "nombre": "Design Thinking and Technological Innovation", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170030"]},
    {"codigo": "170004", "nombre": "Ingeniería de Procesos", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["170001"]},
    {"codigo": "141040", "nombre": "Marketing Estratégico", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170007", "nombre": "Fundamentos de Analítica", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130225"]},
    {"codigo": "170201", "nombre": "Comportamiento del Consumidor", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170031"]},
    {"codigo": "170202", "nombre": "Historia Crítica del Diseño", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170031"]},
    {"codigo": "170203", "nombre": "Tecnología de los Materiales", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["170004"]},
    {"codigo": "150020", "nombre": "Fundamentos de Finanzas", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["160093", "132642"]},

    {"codigo": "170011", "nombre": "Física", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120117", "nombre": "Experiencia del Usuario", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170201"]},
    {"codigo": "170204", "nombre": "Teoría de los Sentidos", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["170202"]},
    {"codigo": "141045", "nombre": "Gestión del Capital Humano", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["120030"]},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170205", "nombre": "Tecnología y Medios de Comunicación", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120117"]},
    {"codigo": "170206", "nombre": "Semiótica y Teoría del Diseño", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["170204"]},
    {"codigo": "170207", "nombre": "Técnicas de Innovación y Experimentación 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "es_cuello_botella": True, "prerrequisitos": ["170203"]},
    {"codigo": "141050", "nombre": "Estrategia", "creditos": 3.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["150020", "141040"]},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "170017", "nombre": "Tecnología para el Desarrollo Sostenible", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170011"]},
    {"codigo": "170208", "nombre": "Urbanismo y Espacios Sociales", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170205"]},
    {"codigo": "170209", "nombre": "Diseño Gráfico Digital", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170206"]},
    {"codigo": "170210", "nombre": "Técnicas de Innovación y Experimentación 2", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["170207"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},
    {"codigo": "ELE-IID01", "nombre": "Electivo I", "creditos": 3.0, "ciclo_sugerido": 8, "tipo": "ELECTIVA", "prerrequisitos": []},

    {"codigo": "170211", "nombre": "Curso Integrador de Experiencia del Usuario", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170208"]},
    {"codigo": "170212", "nombre": "Diseño de Herramientas Digitales", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170209"]},
    {"codigo": "170213", "nombre": "Técnicas de Innovación y Experimentación 3", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["170210"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},
    {"codigo": "ELE-IID02", "nombre": "Electivo II", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},
    {"codigo": "ELE-IID03", "nombre": "Electivo III", "creditos": 3.0, "ciclo_sugerido": 9, "tipo": "ELECTIVA", "prerrequisitos": []},

    {"codigo": "170214", "nombre": "Trabajo Final de Innovación y Diseño", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["170211", "170212", "170213"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["120047"]},
    {"codigo": "ELE-IID04", "nombre": "Electivo IV", "creditos": 3.0, "ciclo_sugerido": 10, "tipo": "ELECTIVA", "prerrequisitos": []}
  ]
}
save_curriculum("innovacion_diseno.json", iid_data)

# =============================================================================
# 10. POLÍTICA, FILOSOFÍA Y ECONOMÍA (PFE) - PLAN 2024-I
# =============================================================================
pfe_data = {
  "carrera": {
    "codigo": "PFE",
    "nombre": "Política, Filosofía y Economía",
    "facultad": "Facultad de Economía y Finanzas",
    "plan": "2024-I",
    "total_creditos_graduacion": 200,
    "total_ciclos": 10,
    "max_creditos_ciclo_regular": 22.0
  },
  "concentraciones": [
    {
      "codigo": "CONC-POLPHIL",
      "nombre": "Filosofía Política y Gobernanza",
      "descripcion": "Teoría política avanzada, ética pública y diseño institucional."
    },
    {
      "codigo": "CONC-POLDEV",
      "nombre": "Economía Política y Desarrollo",
      "descripcion": "Políticas de desarrollo, economía institucional y análisis global."
    }
  ],
  "cursos": [
    {"codigo": "170131", "nombre": "Nivelación en Informática", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "134654", "nombre": "Nivelación en Matemáticas", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120000", "nombre": "Nivelación en Lenguaje", "creditos": 0.0, "ciclo_sugerido": 0, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138649", "nombre": "Matemáticas I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["134654"]},
    {"codigo": "132641", "nombre": "Economía General I", "creditos": 5.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120001", "nombre": "Lenguaje I", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": ["120000"]},
    {"codigo": "190001", "nombre": "Introducción a la Política, Filosofía y Economía", "creditos": 4.0, "ciclo_sugerido": 1, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "190002", "nombre": "Poder e Instituciones", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120006", "nombre": "Lenguaje II", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": ["120001"]},
    {"codigo": "190003", "nombre": "Antropología Filosófica", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120040", "nombre": "Ciencias Sociales", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "120045", "nombre": "Pensamiento Crítico 1", "creditos": 4.0, "ciclo_sugerido": 2, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "138650", "nombre": "Matemáticas II", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["138649"]},
    {"codigo": "132642", "nombre": "Economía General II", "creditos": 5.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "190004", "nombre": "Política Comparada", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["190002"]},
    {"codigo": "120015", "nombre": "Investigación Académica", "creditos": 3.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120006"]},
    {"codigo": "120046", "nombre": "Procesos Sociales 1", "creditos": 4.0, "ciclo_sugerido": 3, "tipo": "OBLIGATORIA", "prerrequisitos": ["120040"]},

    {"codigo": "130224", "nombre": "Estadística I", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["138650"]},
    {"codigo": "132001", "nombre": "Microeconomía I", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["132641"]},
    {"codigo": "190005", "nombre": "Ciudadanía y Democratización", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["190004"]},
    {"codigo": "180001", "nombre": "Introducción al Derecho", "creditos": 5.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": []},
    {"codigo": "190006", "nombre": "Filosofía Política", "creditos": 4.0, "ciclo_sugerido": 4, "tipo": "OBLIGATORIA", "prerrequisitos": ["190003"]},

    {"codigo": "130004", "nombre": "Econometría Aplicada", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["130224"]},
    {"codigo": "132020", "nombre": "Macroeconomía de Corto Plazo", "creditos": 5.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["132642"]},
    {"codigo": "190007", "nombre": "Economía Política Internacional", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": ["190005"]},
    {"codigo": "120020", "nombre": "Introducción al Quehacer Científico", "creditos": 4.0, "ciclo_sugerido": 5, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "132021", "nombre": "Microeconomía Aplicada", "creditos": 5.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["132001"]},
    {"codigo": "132007", "nombre": "Gestión de los Recursos Naturales", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["132001"]},
    {"codigo": "190008", "nombre": "Fundamentos Filosóficos de los Derechos Humanos", "creditos": 4.0, "ciclo_sugerido": 6, "tipo": "OBLIGATORIA", "prerrequisitos": ["190006"]},

    {"codigo": "132004", "nombre": "Teoría del Comercio Internacional", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["132021"]},
    {"codigo": "190009", "nombre": "Diseño, Evaluación y Gestión de Proyectos", "creditos": 5.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["132020"]},
    {"codigo": "190010", "nombre": "Métodos Mixtos de Investigación para las CCSS", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["130004"]},
    {"codigo": "120047", "nombre": "Pensamiento Crítico 2", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120045"]},
    {"codigo": "120048", "nombre": "Procesos Sociales 2", "creditos": 4.0, "ciclo_sugerido": 7, "tipo": "OBLIGATORIA", "prerrequisitos": ["120046"]},

    {"codigo": "190011", "nombre": "Crecimiento e Instituciones", "creditos": 5.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["132020"]},
    {"codigo": "190012", "nombre": "Debates sobre Política y Desarrollo", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 120.0, "prerrequisitos": []},
    {"codigo": "190013", "nombre": "Debates en Filosofía", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 120.0, "prerrequisitos": []},
    {"codigo": "190014", "nombre": "Fundamentos Filosóficos de la Economía", "creditos": 4.0, "ciclo_sugerido": 8, "tipo": "OBLIGATORIA", "prerrequisitos": ["190008"]},

    {"codigo": "132009", "nombre": "Historia del Pensamiento Económico", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": ["190011"]},
    {"codigo": "120060", "nombre": "Proyección Social", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "creditos_minimos_requeridos": 160.0, "prerrequisitos": []},
    {"codigo": "120050", "nombre": "Ética", "creditos": 4.0, "ciclo_sugerido": 9, "tipo": "OBLIGATORIA", "prerrequisitos": []},

    {"codigo": "190015", "nombre": "Seminario de Investigación Aplicada PFE", "creditos": 2.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": ["190010"]},
    {"codigo": "120030", "nombre": "Desarrollo Personal", "creditos": 4.0, "ciclo_sugerido": 10, "tipo": "OBLIGATORIA", "prerrequisitos": []}
  ]
}
save_curriculum("politica_filosofia_economia.json", pfe_data)

print("\n[OK] Todas las 10 mallas nuevas/actualizadas han sido generadas!")

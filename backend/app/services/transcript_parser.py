"""
Servicio de extracción de historial académico desde el Unofficial Transcript PDF
de Autoservicio de la Universidad del Pacífico (Banner / PowerCampus Self-Service).

Procesa el archivo exclusivamente en memoria sin almacenarlo en disco.
"""
import io
import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Mapeo de códigos oficiales de asignaturas por bloque (Mallas Tabulares UP)
BLOCK_OPTION_TO_GROUP: Dict[str, str] = {
    # Bloque Introducción al Quehacer Científico
    "124019": "QUEHACER_CIENTIFICO",
    "170354": "QUEHACER_CIENTIFICO",
    "170334": "QUEHACER_CIENTIFICO",
    # Bloque Desarrollo Personal
    "142082": "DESARROLLO_PERSONAL",
    "124020": "DESARROLLO_PERSONAL",
    "142095": "DESARROLLO_PERSONAL",
    # Bloque Ciencias Sociales
    "158109": "CIENCIAS_SOCIALES",
    "158143": "CIENCIAS_SOCIALES",
    "158000": "CIENCIAS_SOCIALES",
    # Bloque Pensamiento Crítico
    "129007": "PENSAMIENTO_CRITICO",
    "120125": "PENSAMIENTO_CRITICO",
    "157006": "PENSAMIENTO_CRITICO",
    # Bloque Procesos Sociales
    "150004": "PROCESOS_SOCIALES",
    "120070": "PROCESOS_SOCIALES",
    "122005": "PROCESOS_SOCIALES",
}


def detect_block_group(codigo: str, nombre: str) -> Optional[str]:
    """Detecta a qué bloque Sello UP pertenece una asignatura de la malla curricular."""
    code = (codigo or "").upper()
    norm = (
        (nombre or "")
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )
    if code == "120020" or code.startswith("SELLO-QC") or "quehacer cientifico" in norm:
        return "QUEHACER_CIENTIFICO"
    if code == "120030" or code.startswith("SELLO-DP") or "desarrollo personal" in norm:
        return "DESARROLLO_PERSONAL"
    if code == "120040" or code.startswith("SELLO-CS") or "ciencias sociales" in norm:
        return "CIENCIAS_SOCIALES"
    if code in ("120045", "120047") or code.startswith("SELLO-PC") or "pensamiento critico" in norm:
        return "PENSAMIENTO_CRITICO"
    if code in ("120046", "120048") or code.startswith("SELLO-PS") or "procesos sociales" in norm:
        return "PROCESOS_SOCIALES"
    return None


@dataclass
class ParsedTranscriptCourse:
    codigo: str
    titulo: str
    periodo: str
    estado: str  # APROBADA | DESAPROBADA | EN_CURSO | RETIRADA
    calificacion: Optional[float]
    creditos: float
    numero_matricula: int = 1


@dataclass
class ParsedTranscriptResult:
    detected_program: Optional[str] = None
    courses: List[ParsedTranscriptCourse] = field(default_factory=list)
    retired_count: int = 0


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extrae texto del PDF en memoria usando pdfplumber o pdftotext como respaldo."""
    try:
        import pdfplumber  # type: ignore

        pages_text: List[str] = []
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text(layout=True) or page.extract_text() or ""
                if txt:
                    pages_text.append(txt)
        if pages_text:
            return "\n".join(pages_text)
    except ImportError:
        pass

    # Respaldo sin dependencias Python externas usando poppler pdftotext en memoria (stdin -> stdout)
    proc = subprocess.run(
        ["pdftotext", "-layout", "-", "-"],
        input=pdf_bytes,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError("No se pudo leer el contenido del archivo PDF.")
    return proc.stdout.decode("utf-8", errors="replace")


# Patrones de cabecera de periodo académico en Self-Service UP
TERM_REGULAR_RE = re.compile(r"^\s*(\d{4})\s+(I{1,2})\s+PERIODO\b", re.IGNORECASE)
TERM_EXTRA_RE = re.compile(r"^\s*(\d{4})\s+CUR\s+EXTRAORDINARIOS\b", re.IGNORECASE)
EXTRACURRICULAR_SECTION_RE = re.compile(r"Dir\.\s*Form\.\s*Exta-Acad", re.IGNORECASE)

# Fila de curso en el transcript:
# <codigo>  <titulo>  <sub_type>  [grade]  <credits 0.000>  <quality_points 0.0000>
COURSE_ROW_RE = re.compile(
    r"^\s*(?P<codigo>[A-Z0-9]{5,8})\s+"
    r"(?P<titulo>.+?)\s+"
    r"(?P<subtype>PRESENCIAL|VIRTUAL|SEMIPRESENCIAL|H[IÍ]BRIDO|A\s+DISTANCIA|No\s+Acad[eé]mi\w*)\s+"
    r"(?:(?P<grade>\[?\d{1,2}\.\d{2}\]?|RET|REC|ASIS|CONV?|EX)\s+)?"
    r"(?P<credits>\d+\.\d{3})\s+"
    r"(?P<qpoints>\d+\.\d{4})\s*$",
    re.IGNORECASE,
)


def parse_up_transcript_text(raw_text: str) -> ParsedTranscriptResult:
    """Parsea el texto extraído de un Unofficial Transcript de la UP."""
    result = ParsedTranscriptResult()

    # Detectar programa académico en la cabecera
    prog_match = re.search(
        r"Pregrado/[^/\n]+/([^/\n]+)",
        raw_text,
        re.IGNORECASE,
    )
    if prog_match:
        result.detected_program = prog_match.group(1).strip()

    current_term = "2024-1"
    raw_attempts: List[Tuple[str, str, str, str, Optional[float], float]] = []

    for line in raw_text.splitlines():
        # Detener el parseo académico al llegar a la sección extracurricular (TIVU, talleres)
        if EXTRACURRICULAR_SECTION_RE.search(line):
            break

        m_reg = TERM_REGULAR_RE.match(line)
        if m_reg:
            year = m_reg.group(1)
            rom = m_reg.group(2).upper()
            current_term = f"{year}-{'1' if rom == 'I' else '2'}"
            continue

        m_ext = TERM_EXTRA_RE.match(line)
        if m_ext:
            year = m_ext.group(1)
            current_term = f"{year}-0"
            continue

        m_row = COURSE_ROW_RE.match(line)
        if not m_row:
            continue

        subtype = m_row.group("subtype").strip()
        if subtype.lower().startswith("no acad"):
            continue

        codigo = m_row.group("codigo").strip().upper()
        titulo = re.sub(r"\s+", " ", m_row.group("titulo")).strip()
        grade_raw = (m_row.group("grade") or "").strip().upper()
        credits = float(m_row.group("credits"))

        if grade_raw in ("REC", "ASIS"):
            continue

        if grade_raw == "RET":
            result.retired_count += 1
            raw_attempts.append((codigo, titulo, current_term, "RETIRADA", None, credits))
            continue

        if grade_raw in ("CON", "CONV", "EX"):
            raw_attempts.append((codigo, titulo, current_term, "APROBADA", None, credits))
            continue

        if not grade_raw:
            raw_attempts.append((codigo, titulo, current_term, "EN_CURSO", None, credits))
            continue

        # Nota numérica, posiblemente entre corchetes ej. [11.00]
        clean_grade = grade_raw.strip("[]")
        try:
            grade_val = float(clean_grade)
        except ValueError:
            continue

        estado = "APROBADA" if grade_val >= 11.0 else "DESAPROBADA"
        raw_attempts.append((codigo, titulo, current_term, estado, grade_val, credits))

    # Consolidar múltiples intentos por asignatura en orden cronológico
    by_code: Dict[str, List[Tuple[str, str, str, str, Optional[float], float]]] = {}
    for item in raw_attempts:
        by_code.setdefault(item[0], []).append(item)

    for codigo, attempts in by_code.items():
        # Contar matrículas reales (excluyendo retiros)
        non_ret = [a for a in attempts if a[3] != "RETIRADA"]
        if not non_ret:
            # Solo tuvo retiros -> no se registra como cursada/desaprobada
            continue

        matricula_count = len(non_ret)
        # Prioridad: si alguna vez aprobó, tomar la última aprobación; sino el último intento no-retiro
        approved_attempts = [a for a in non_ret if a[3] == "APROBADA"]
        chosen = approved_attempts[-1] if approved_attempts else non_ret[-1]

        result.courses.append(
            ParsedTranscriptCourse(
                codigo=codigo,
                titulo=chosen[1],
                periodo=chosen[2],
                estado=chosen[3],
                calificacion=chosen[4],
                creditos=chosen[5],
                numero_matricula=matricula_count,
            )
        )

    return result

"""
Script utilitario para asistir en la extracción de cursos, créditos y flujogramas
a partir de los PDFs vectoriales oficiales de la Universidad del Pacífico en docs/mallas/.
"""
import sys
import os
import re
import json
from typing import List, Dict
import pymupdf


def parse_flujograma_pdf(pdf_path: str) -> Dict:
    """Extrae bloques de texto y cursos del PDF del flujograma."""
    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe.")
        sys.exit(1)

    doc = pymupdf.open(pdf_path)
    page = doc[0]
    blocks = page.get_text("blocks")

    # Extraer cajas de cursos detectando patrones de créditos "(X créd.)", "(ECO 5)", "(4)"
    credit_pattern = re.compile(r"\(\s*(?:[A-Z]{2,4}\s*)?(\d+)\s*(?:cr[eé]d\.?)?\s*\)", re.IGNORECASE)

    extracted_courses = []
    headers = []

    for b in blocks:
        text = b[4].strip()
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        full_str = " ".join(lines)

        # Detectar cabeceras de ciclo
        if re.search(r"Ciclo\s+([0-9IXV]+)", full_str, re.IGNORECASE):
            headers.append({"box": b[:4], "text": full_str})
            continue

        match = credit_pattern.search(full_str)
        if match:
            creditos = float(match.group(1))
            # Quitar la mención de créditos para obtener el nombre
            nombre = credit_pattern.sub("", full_str).strip()
            # Limpiar saltos y caracteres extra
            nombre = re.sub(r"\s+", " ", nombre)

            extracted_courses.append({
                "nombre": nombre,
                "creditos": creditos,
                "bbox": [round(coord, 1) for coord in b[:4]],
                "x": round((b[0] + b[2]) / 2, 1),
                "y": round((b[1] + b[3]) / 2, 1)
            })

    # Ordenar por posición X (ciclos de izquierda a derecha) y luego Y (arriba a abajo)
    extracted_courses.sort(key=lambda c: (c["x"], c["y"]))

    filename = os.path.basename(pdf_path)
    print(f"\n=======================================================")
    print(f"ANÁLISIS DE: {filename}")
    print(f"Total cursos/asignaturas detectadas: {len(extracted_courses)}")
    print(f"Cabeceras de ciclo identificadas: {len(headers)}")
    print(f"=======================================================\n")

    for i, c in enumerate(extracted_courses[:20], 1):
        print(f"{i:2d}. {c['nombre']} ({c['creditos']} cr.) [pos: x={c['x']}, y={c['y']}]")

    if len(extracted_courses) > 20:
        print(f"   ... y {len(extracted_courses) - 20} asignaturas más.")

    return {
        "archivo": filename,
        "total_cursos": len(extracted_courses),
        "cursos": extracted_courses
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_pdf = sys.argv[1]
    else:
        target_pdf = os.path.join("docs", "mallas", "FLUJOGRAMA DE ASIGNATURAS DE FORMACIÓN GENERAL Y PROFESIONAL DE LA CARRERA DE MARKETING-PLAN DE ESTUDIOS 2022.pdf")
    parse_flujograma_pdf(target_pdf)

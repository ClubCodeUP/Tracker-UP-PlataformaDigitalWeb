#!/usr/bin/env python3
"""
Extractor geométrico de flujogramas curriculares (Visio / draw.io) y cruce con mallas (pdfplumber).
Compatible con los planes de estudio UP (Ingeniería, Derecho, Economía, Administración, etc.).

Uso:
    python extractor_flujograma_v2.py <flujograma.pdf> [malla.pdf] [-o salida.csv] [--carrera "Nombre"] [--json-out salida.json]
"""

import argparse
import csv
import json
import math
import os
import re
import sys
import unicodedata
from collections import defaultdict
from difflib import SequenceMatcher
import pdfplumber


# =============================================================================
# 1. NORMALIZACIÓN DE TEXTO Y UTILIDADES
# =============================================================================

ROMAN_TO_INT = {
    "0": 0, "CERO": 0,
    "I": 1, "1": 1, "PRIMER": 1, "PRIMERO": 1,
    "II": 2, "2": 2, "SEGUNDO": 2, "11": 2,
    "III": 3, "3": 3, "TERCER": 3, "TERCERO": 3,
    "IV": 4, "4": 4, "CUARTO": 4,
    "V": 5, "5": 5, "QUINTO": 5,
    "VI": 6, "6": 6, "SEXTO": 6,
    "VII": 7, "7": 7, "SEPTIMO": 7,
    "VIII": 8, "8": 8, "OCTAVO": 8,
    "IX": 9, "9": 9, "NOVENO": 9,
    "X": 10, "10": 10, "DECIMO": 10,
    "XI": 11, "11": 11, "UNDECIMO": 11, "DECIMO PRIMER": 11,
    "XII": 12, "12": 12, "DUODECIMO": 12, "DECIMO SEGUNDO": 12,
}

STOPWORDS = {"de", "del", "la", "las", "el", "los", "en", "para", "y", "a", "al", "o", "u", "curso", "bloque"}


def fix_spaced_letters(text: str) -> str:
    """Colapsa secuencias de letras sueltas separadas por espacio ('M a t e' -> 'Mate')."""
    return re.sub(
        r'(?<![A-Za-z0-9])(?:[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]\s+){2,}[A-Za-zÁÉÍÓÚÜÑáéíóúüñ](?![A-Za-z0-9])',
        lambda m: m.group(0).replace(" ", ""),
        text,
    )


def dedup_doubled_chars(text: str) -> str:
    """Repara capas duplicadas de Visio ('PPeennssaammiieennttoo' -> 'Pensamiento')."""
    words = text.split()
    new_words = []
    for w in words:
        if len(w) >= 2 and len(w) % 2 == 0 and all(w[2*i] == w[2*i+1] for i in range(len(w)//2)):
            new_words.append("".join(w[2*i] for i in range(len(w)//2)))
        else:
            new_words.append(w)
    return " ".join(new_words)


def clean_display_text(text: str) -> str:
    """Limpia ligaduras rotas (\\x00 -> ti), letras duplicadas y espacios múltiples manteniendo capitalización legible."""
    if not text:
        return ""
    text = text.replace("\x00", "ti").replace("\ufffd", "ti")
    text = dedup_doubled_chars(text)
    text = fix_spaced_letters(text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    """Normaliza el texto: repara ligadura \\x00='ti', quita espacios entre letras, tildes y pasa a minúsculas."""
    if not text:
        return ""
    text = text.replace("\x00", "ti").replace("\ufffd", "ti")
    text = dedup_doubled_chars(text)
    text = fix_spaced_letters(text)
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_roman_suffix(norm_str: str) -> str:
    """Convierte sufijos arábigos de nivel de curso a romanos para emparejar ('estadistica 1' -> 'estadistica i')."""
    tokens = norm_str.split()
    if not tokens:
        return norm_str
    map_num = {"1": "i", "2": "ii", "3": "iii", "4": "iv"}
    if tokens[-1] in map_num:
        tokens[-1] = map_num[tokens[-1]]
    return " ".join(tokens)


def extract_course_info_from_box_text(raw_text: str):
    """
    Separa el nombre limpio del curso, los créditos declarados en la caja y notas de créditos
    (ej. '160 créditos') a partir del texto crudo de la caja del flujograma.
    """
    disp = clean_display_text(raw_text)
    notas_cred = []

    for m in re.finditer(r"\(?\b(\d{2,3})\s*(?:creditos|credito|cred\.?|cr\.?)\b\)?", disp, flags=re.IGNORECASE):
        val = int(m.group(1))
        if val >= 30:
            notas_cred.append(f"Requiere {val} créditos")

    creditos = None
    for m in re.finditer(r"[\(\[\{]([^\)\]\}]*)[\)\]\}]", disp):
        inner = m.group(1)
        m_c = re.search(r"\b(\d{1,2})\b", inner)
        if m_c:
            val = int(m_c.group(1))
            if val <= 15:
                creditos = val

    if creditos is None:
        m_broken = re.search(r"\b(\d{1,2})\s*(?:creditos|cred\.?|cr\.?)\s*[\)\]\}]", disp, flags=re.IGNORECASE)
        if m_broken:
            val = int(m_broken.group(1))
            if val > 10 and val % 10 in (3, 4, 5):
                val = val % 10
            if val <= 10:
                creditos = val

    clean_name = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", " ", disp)
    clean_name = re.sub(r"\b\d{1,3}\s*(?:creditos|credito|cred\.?|cr\.?)\s*[\)\]\}]?", " ", clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s+", " ", clean_name).strip(" -.,;:")
    return clean_name, creditos, notas_cred


def classify_block_type(norm_name: str):
    """Identifica si un texto corresponde a un bloque Sello UP o Electivo."""
    if "electivo" in norm_name or "electiva" in norm_name:
        return "BLOCK_ELECTIVO"
    if any(k in norm_name for k in ("quehacer cientifico", "cosmologia", "pensamiento sistemico", "filosofia de la ciencia")):
        return "SELLO_CIENTIFICO"
    if any(k in norm_name for k in ("desarrollo personal", "emprendimiento e innovacion", "liderazgo")):
        return "SELLO_PERSONAL"
    if any(k in norm_name for k in ("ciencias sociales", "sociologia", "antropologia", "sicologia", "psicologia")):
        return "SELLO_SOCIALES"
    if any(k in norm_name for k in ("pensamiento critico", "teologia de las religiones", "pensamiento social contemporaneo")):
        return "SELLO_CRITICO"
    if any(k in norm_name for k in ("procesos sociales", "ciencia politica", "historia economica", "historia critica")):
        return "SELLO_PROCESOS"
    return None


# =============================================================================
# 2. GEOMETRÍA DEL PDF (CAJAS, MÓDULOS, CONECTORES Y PUNTAS DE FLECHA)
# =============================================================================

def dist_pt(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def dist_pt_to_segment(pt, a, b):
    px, py = pt
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return dist_pt(pt, a), a
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    proj = (ax + t * dx, ay + t * dy)
    return dist_pt(pt, proj), proj


def dist_pt_to_box_border(pt, box):
    x, y = pt
    x0, y0, x1, y1 = box["x0"], box["top"], box["x1"], box["bottom"]
    segs = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
    return min(dist_pt_to_segment(pt, s[0], s[1])[0] for s in segs)


def point_in_or_touching_box(pt, box, tol=4.5):
    x, y = pt
    return (box["x0"] - tol <= x <= box["x1"] + tol) and (box["top"] - tol <= y <= box["bottom"] + tol)


def is_white_or_gray_shadow(color):
    if color is None:
        return False
    if isinstance(color, (int, float)):
        return color == 0
    if isinstance(color, (tuple, list)) and len(color) == 3:
        r, g, b = color
        if r == 0 and g == 0 and b == 0:
            return True
    return False


def extract_words_in_bbox(words, bbox, page=None):
    if page is not None:
        try:
            px0 = max(0.0, bbox[0] - 0.5)
            ptop = max(0.0, bbox[1] - 0.5)
            px1 = min(float(page.width), bbox[2] + 0.5)
            pbot = min(float(page.height), bbox[3] + 0.5)
            if px1 > px0 and pbot > ptop:
                cropped = page.crop((px0, ptop, px1, pbot))
                txt = cropped.extract_text(x_tolerance=3, y_tolerance=3)
                if txt and txt.strip():
                    return " ".join(txt.split())
        except Exception:
            pass

    x0, top, x1, bottom = bbox
    inside = []
    for w in words:
        cx = 0.5 * (w["x0"] + w["x1"])
        cy = 0.5 * (w["top"] + w["bottom"])
        if x0 <= cx <= x1 and top <= cy <= bottom:
            inside.append(w)
    inside.sort(key=lambda w: (round(w["top"] / 4.0), w["x0"]))
    return " ".join(w["text"] for w in inside)


def get_object_pts(obj):
    if "pts" in obj and obj["pts"]:
        return [(float(p[0]), float(p[1])) for p in obj["pts"]]
    return [
        (float(obj["x0"]), float(obj["top"])),
        (float(obj["x1"]), float(obj["top"])),
        (float(obj["x1"]), float(obj["bottom"])),
        (float(obj["x0"]), float(obj["bottom"])),
    ]


def is_dashed_or_colored(obj):
    dash = obj.get("dash")
    is_dashed = False
    if dash:
        if isinstance(dash, (tuple, list)):
            arr = dash[0] if isinstance(dash[0], (tuple, list)) else dash
            if any(isinstance(v, (int, float)) and v > 0 for v in arr):
                is_dashed = True
        elif isinstance(dash, (int, float)) and dash > 0:
            is_dashed = True

    sc = obj.get("stroking_color")
    is_colored = False
    color_desc = "negro"
    if isinstance(sc, (tuple, list)) and len(sc) == 3:
        r, g, b = sc
        if max(abs(r - g), abs(g - b), abs(r - b)) > 0.15:
            is_colored = True
            if r > 0.6 and g < 0.4 and b < 0.4:
                color_desc = "rojo"
            elif b > 0.6 and r < 0.4:
                color_desc = "azul"
            elif g > 0.5 and r < 0.4:
                color_desc = "verde"
            else:
                color_desc = f"RGB({r:.1f},{g:.1f},{b:.1f})"

    if is_dashed and is_colored:
        return True, f"línea punteada color {color_desc}"
    if is_dashed:
        return True, "línea punteada"
    if is_colored:
        return True, f"línea color {color_desc}"
    return False, ""


def extract_flowchart_geometry(pdf_path: str):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        page_w, page_h = float(page.width), float(page.height)
        words = page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=False)

        all_shapes = []
        for kind in ("rect", "curve", "line"):
            for obj in page.objects.get(kind, []):
                o = dict(obj)
                o["kind"] = kind
                o["w"] = float(o["x1"]) - float(o["x0"])
                o["h"] = float(o["bottom"]) - float(o["top"])
                all_shapes.append(o)

    scale = page_w / 842.0
    tol_t = 3.5 * scale
    touch_tol = 6.0 * scale
    arrow_max = 14.0 * scale

    cycle_headers = detect_cycle_columns(words, page_w, page_h)

    min_box_w, max_box_w = 30.0 * scale, 150.0 * scale
    min_box_h, max_box_h = 16.0 * scale, 90.0 * scale

    filled_candidates = [
        s for s in all_shapes
        if s["kind"] in ("rect", "curve")
        and s.get("fill")
        and min_box_w <= s["w"] <= max_box_w
        and min_box_h <= s["h"] <= max_box_h
    ]
    stroke_candidates = [
        s for s in all_shapes
        if s["kind"] in ("rect", "curve")
        and s.get("stroke")
        and min_box_w <= s["w"] <= max_box_w
        and min_box_h <= s["h"] <= max_box_h
    ]

    used_stroke_ids = set()
    raw_boxes = []

    for f_obj in filled_candidates:
        if is_white_or_gray_shadow(f_obj.get("non_stroking_color")):
            continue
        twin = None
        if f_obj.get("stroke"):
            twin = f_obj
        else:
            for s_obj in stroke_candidates:
                if (
                    abs(f_obj["x0"] - s_obj["x0"]) <= 3.0 * scale
                    and abs(f_obj["top"] - s_obj["top"]) <= 3.0 * scale
                    and abs(f_obj["x1"] - s_obj["x1"]) <= 3.0 * scale
                    and abs(f_obj["bottom"] - s_obj["bottom"]) <= 3.0 * scale
                ):
                    twin = s_obj
                    used_stroke_ids.add(id(s_obj))
                    break
        if twin is not None:
            raw_boxes.append((f_obj, twin))

    dedup_boxes = []
    for f_obj, twin in raw_boxes:
        cx = 0.5 * (f_obj["x0"] + f_obj["x1"])
        cy = 0.5 * (f_obj["top"] + f_obj["bottom"])
        is_dup = False
        for b in dedup_boxes:
            if (
                abs(cx - b["cx"]) < 10.0 * scale
                and abs(cy - b["cy"]) < 10.0 * scale
                and abs(f_obj["w"] - b["w"]) < 8.0 * scale
                and abs(f_obj["h"] - b["h"]) < 8.0 * scale
            ):
                is_dup = True
                break
        if not is_dup:
            bbox = (float(f_obj["x0"]), float(f_obj["top"]), float(f_obj["x1"]), float(f_obj["bottom"]))
            txt = extract_words_in_bbox(words, bbox, page=page)
            dedup_boxes.append({
                "x0": bbox[0], "top": bbox[1], "x1": bbox[2], "bottom": bbox[3],
                "w": f_obj["w"], "h": f_obj["h"],
                "cx": cx, "cy": cy,
                "raw_text": txt,
                "norm_text": normalize_text(txt),
                "fill_id": id(f_obj),
                "stroke_id": id(twin),
            })

    course_boxes = []
    for b in dedup_boxes:
        nt = b["norm_text"]
        if not nt:
            continue
        if re.match(r"^(?:ciclo|cicio|cicle|cido|cred|cur|total|\d+\s*cursos|\d+\s*/\s*\d+)\b", nt):
            continue
        if nt.startswith("cursos de ") or nt.startswith("cursos sello") or nt == "cursos fundamentales":
            continue
        if b["top"] > page_h * 0.92 and "cred" not in nt and not re.search(r"\(\d+\)", b["raw_text"]):
            continue

        clean_name, cred, credit_notes = extract_course_info_from_box_text(b["raw_text"])
        b["curso_limpio"] = clean_name
        b["norm_curso"] = normalize_text(clean_name)
        b["creditos_caja"] = cred
        b["notas_caja"] = credit_notes
        b["ciclo"] = assign_cycle_to_x(b["cx"], cycle_headers)
        b["id"] = f"BOX_{len(course_boxes)}"
        b["is_module"] = False
        course_boxes.append(b)

    modules = detect_modules(all_shapes, words, course_boxes, scale)

    box_contour_ids = set()
    for b in dedup_boxes:
        box_contour_ids.add(b["fill_id"])
        box_contour_ids.add(b["stroke_id"])
    for m in modules:
        box_contour_ids.update(m["shape_ids"])

    for s in stroke_candidates:
        for b in dedup_boxes:
            if (
                abs(s["x0"] - b["x0"]) <= 3.0 * scale
                and abs(s["top"] - b["top"]) <= 3.0 * scale
                and abs(s["x1"] - b["x1"]) <= 3.0 * scale
                and abs(s["bottom"] - b["bottom"]) <= 3.0 * scale
            ):
                box_contour_ids.add(id(s))

    arrowheads, arrow_shape_ids = detect_arrowheads(all_shapes, course_boxes, box_contour_ids, page_h, scale, arrow_max)

    connectors = extract_connectors(
        all_shapes, box_contour_ids, arrow_shape_ids, course_boxes, modules, page_w, page_h
    )

    edges, orphan_arrows = trace_all_arrows(arrowheads, connectors, course_boxes, modules, tol_t, touch_tol)

    return {
        "boxes": course_boxes,
        "modules": modules,
        "arrowheads": arrowheads,
        "connectors": connectors,
        "edges": edges,
        "orphan_arrows": orphan_arrows,
        "cycle_headers": cycle_headers,
    }


def detect_cycle_columns(words, page_w, page_h):
    top_words = [w for w in words if w["top"] < page_h * 0.16]
    top_words.sort(key=lambda w: (round(w["top"] / 5.0), w["x0"]))

    clusters = []
    for w in top_words:
        if clusters and abs(w["top"] - clusters[-1]["top"]) < 6.0 and 0 <= (w["x0"] - clusters[-1]["x1"]) < 25.0:
            clusters[-1]["text"] += " " + w["text"]
            clusters[-1]["x1"] = max(clusters[-1]["x1"], w["x1"])
        else:
            clusters.append({"x0": w["x0"], "x1": w["x1"], "top": w["top"], "text": w["text"]})

    cycle_x = {}
    for cl in clusters:
        nt = normalize_text(cl["text"]).upper()
        m1 = re.search(r"\b(?:CICLO|CICIO|CICLE|CIDO)\s+([0-9IVX]+|CERO)\b", nt)
        m2 = re.search(r"\b(CERO|PRIMER|PRIMERO|SEGUNDO|TERCER|TERCERO|CUARTO|QUINTO|SEXTO|SEPTIMO|OCTAVO|NOVENO|DECIMO)\s+(?:CICLO|CICIO)\b", nt)
        cyc = None
        if m1 and m1.group(1) in ROMAN_TO_INT:
            cyc = ROMAN_TO_INT[m1.group(1)]
        elif m2 and m2.group(1) in ROMAN_TO_INT:
            cyc = ROMAN_TO_INT[m2.group(1)]
        if cyc is not None:
            cx = 0.5 * (cl["x0"] + cl["x1"])
            if cyc not in cycle_x:
                cycle_x[cyc] = cx

    if len(cycle_x) >= 4:
        sorted_cycs = sorted(cycle_x.keys())
        diffs = [
            (cycle_x[sorted_cycs[i + 1]] - cycle_x[sorted_cycs[i]]) / (sorted_cycs[i + 1] - sorted_cycs[i])
            for i in range(len(sorted_cycs) - 1)
            if sorted_cycs[i + 1] > sorted_cycs[i]
        ]
        if diffs:
            step = sorted(diffs)[len(diffs) // 2]
            min_c, max_c = min(sorted_cycs), max(sorted_cycs)
            for c in range(min_c, max_c + 1):
                if c not in cycle_x:
                    ref_c = min(sorted_cycs, key=lambda k: abs(k - c))
                    cycle_x[c] = cycle_x[ref_c] + (c - ref_c) * step

    return cycle_x


def assign_cycle_to_x(cx, cycle_headers):
    if not cycle_headers:
        return None
    return min(cycle_headers.keys(), key=lambda c: abs(cx - cycle_headers[c]))


def detect_modules(all_shapes, words, course_boxes, scale):
    lines_by_y = defaultdict(list)
    for w in words:
        lines_by_y[round(w["top"] / 4.0)].append(w)

    module_labels = []
    for _, line_words in lines_by_y.items():
        line_words.sort(key=lambda w: w["x0"])
        line_txt = clean_display_text(" ".join(w["text"] for w in line_words))
        norm_txt = normalize_text(line_txt)
        if "modulo de " in norm_txt or "cursos fundamentales" in norm_txt:
            x0 = min(w["x0"] for w in line_words)
            x1 = max(w["x1"] for w in line_words)
            top = min(w["top"] for w in line_words)
            bottom = max(w["bottom"] for w in line_words)
            module_labels.append({
                "label": line_txt,
                "norm_label": norm_txt,
                "cx": 0.5 * (x0 + x1),
                "cy": 0.5 * (top + bottom),
                "x0": x0, "top": top, "x1": x1, "bottom": bottom,
            })

    large_shapes = []
    for s in all_shapes:
        if s["kind"] not in ("rect", "curve"):
            continue
        if not (s["w"] > 110.0 * scale or s["h"] > 70.0 * scale):
            continue
        if s["w"] >= 800.0 * scale or s["h"] >= 550.0 * scale:
            continue
        pts = get_object_pts(s)
        is_closed = (s["kind"] == "rect") or (len(pts) >= 4 and dist_pt(pts[0], pts[-1]) < 3.5)
        if is_closed:
            large_shapes.append(s)

    modules = []
    for s in large_shapes:
        contained = [
            b for b in course_boxes
            if s["x0"] - 2.0 <= b["cx"] <= s["x1"] + 2.0
            and s["top"] - 2.0 <= b["cy"] <= s["bottom"] + 2.0
        ]
        if len(contained) < 2:
            continue

        dup = None
        for m in modules:
            if (
                abs(s["x0"] - m["x0"]) <= 5.0 * scale
                and abs(s["top"] - m["top"]) <= 5.0 * scale
                and abs(s["x1"] - m["x1"]) <= 5.0 * scale
                and abs(s["bottom"] - m["bottom"]) <= 5.0 * scale
            ):
                dup = m
                break
        if dup is not None:
            dup["shape_ids"].add(id(s))
            continue

        pts = get_object_pts(s)
        modules.append({
            "id": f"MOD_{len(modules)}",
            "x0": float(s["x0"]), "top": float(s["top"]),
            "x1": float(s["x1"]), "bottom": float(s["bottom"]),
            "w": s["w"], "h": s["h"],
            "pts": pts,
            "courses": contained,
            "shape_ids": {id(s)},
            "label": f"Módulo ({len(modules) + 1})",
            "is_module": True,
        })

    for lbl in module_labels:
        best_m = None
        best_d = 999.0
        for m in modules:
            d = dist_pt_to_box_border((lbl["cx"], lbl["cy"]), m)
            if (m["x0"] - 15 <= lbl["cx"] <= m["x1"] + 15) and d < best_d:
                best_d = d
                best_m = m
        if best_m is not None and best_d <= 30.0 * scale:
            best_m["label"] = lbl["label"]

    return modules


def detect_arrowheads(all_shapes, course_boxes, box_contour_ids, page_h, scale, arrow_max):
    arrowheads = []
    arrow_shape_ids = set()

    for s in all_shapes:
        if id(s) in box_contour_ids:
            continue
        w, h = s["w"], s["h"]
        if not (1.0 * scale <= max(w, h) <= arrow_max and min(w, h) >= 0.6):
            continue
        if s["top"] < page_h * 0.08 or s["top"] > page_h * 0.93:
            continue

        color = s.get("non_stroking_color")
        if isinstance(color, (tuple, list)) and len(color) == 3:
            if abs(color[0] - color[1]) < 0.02 and abs(color[1] - color[2]) < 0.02 and 0.15 < color[0] < 0.85:
                continue

        pts = get_object_pts(s)
        if len(pts) < 3:
            continue
        uniq = []
        for p in pts:
            if not any(dist_pt(p, u) < 0.5 for u in uniq):
                uniq.append(p)
        if not (3 <= len(uniq) <= 4):
            continue

        is_candidate = bool(s.get("fill") or s.get("stroke"))
        if not is_candidate:
            continue

        cx = 0.5 * (s["x0"] + s["x1"])
        cy = 0.5 * (s["top"] + s["bottom"])

        inside_box = False
        for b in course_boxes:
            if (b["x0"] + 1.5 < cx < b["x1"] - 1.5) and (b["top"] + 1.5 < cy < b["bottom"] - 1.5):
                inside_box = True
                break
        if inside_box:
            continue

        arrow_shape_ids.add(id(s))

        if any(abs(cx - a["cx"]) < 2.0 * scale and abs(cy - a["cy"]) < 2.0 * scale for a in arrowheads):
            continue

        uniq_pts = []
        for p in pts:
            if not any(dist_pt(p, u) < 0.6 for u in uniq_pts):
                uniq_pts.append(p)

        tip, base = compute_triangle_tip_and_base(uniq_pts, course_boxes, scale)
        is_special, style_note = is_dashed_or_colored(s)

        arrowheads.append({
            "id": f"ARR_{len(arrowheads)}",
            "x0": float(s["x0"]), "top": float(s["top"]),
            "x1": float(s["x1"]), "bottom": float(s["bottom"]),
            "cx": cx, "cy": cy,
            "pts": uniq_pts,
            "tip": tip,
            "base": base,
            "is_special": is_special,
            "style_note": style_note,
        })

    return arrowheads, arrow_shape_ids


def compute_triangle_tip_and_base(uniq_pts, course_boxes, scale):
    if not uniq_pts:
        return (0.0, 0.0), (0.0, 0.0)
    if len(uniq_pts) < 3:
        return uniq_pts[0], uniq_pts[-1]

    best_pt = None
    best_box_dist = 999.0
    for p in uniq_pts:
        for b in course_boxes:
            d = dist_pt_to_box_border(p, b)
            if d < best_box_dist:
                best_box_dist = d
                best_pt = p

    if best_pt is not None and best_box_dist <= 7.0 * scale:
        others = [p for p in uniq_pts if p != best_pt]
        bx = sum(p[0] for p in others) / len(others)
        by = sum(p[1] for p in others) / len(others)
        return best_pt, (bx, by)

    if len(uniq_pts) == 3:
        p0, p1, p2 = uniq_pts
        d01, d12, d20 = dist_pt(p0, p1), dist_pt(p1, p2), dist_pt(p2, p0)
        if d01 <= d12 and d01 <= d20:
            return p2, (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]))
        if d12 <= d01 and d12 <= d20:
            return p0, (0.5 * (p1[0] + p2[0]), 0.5 * (p1[1] + p2[1]))
        return p1, (0.5 * (p0[0] + p2[0]), 0.5 * (p0[1] + p2[1]))

    cx = sum(p[0] for p in uniq_pts) / len(uniq_pts)
    cy = sum(p[1] for p in uniq_pts) / len(uniq_pts)
    tip = max(uniq_pts, key=lambda p: dist_pt(p, (cx, cy)))
    others = [p for p in uniq_pts if p != tip]
    bx = sum(p[0] for p in others) / len(others)
    by = sum(p[1] for p in others) / len(others)
    return tip, (bx, by)


def extract_connectors(all_shapes, box_contour_ids, arrow_shape_ids, course_boxes, modules, page_w, page_h):
    raw_polylines = []

    for s in all_shapes:
        if id(s) in box_contour_ids or id(s) in arrow_shape_ids:
            continue
        if s.get("fill") and not s.get("stroke"):
            continue
        if not s.get("stroke"):
            continue
        if s["w"] > page_w * 0.88 or s["h"] > page_h * 0.85:
            continue
        if s["top"] < page_h * 0.08 or s["top"] > page_h * 0.93:
            continue

        pts = get_object_pts(s)
        if len(pts) < 2:
            continue

        clean_pts = [pts[0]]
        for p in pts[1:]:
            if dist_pt(p, clean_pts[-1]) > 0.2:
                clean_pts.append(p)
        if len(clean_pts) < 2:
            continue

        if dist_pt(clean_pts[0], clean_pts[-1]) < 1.5 and s["w"] > 20 and s["h"] > 12:
            continue

        is_spec, style_note = is_dashed_or_colored(s)
        raw_polylines.append({
            "pts": clean_pts,
            "is_special": is_spec,
            "style_note": style_note,
        })

    if len(raw_polylines) > 600:
        raw_polylines = merge_fragmented_segments(raw_polylines, page_w, page_h)

    connectors = []
    for idx, pl in enumerate(raw_polylines):
        connectors.append({
            "id": f"CON_{idx}",
            "pts": pl["pts"],
            "start": pl["pts"][0],
            "end": pl["pts"][-1],
            "is_special": pl["is_special"],
            "style_note": pl["style_note"],
        })
    return connectors


def merge_fragmented_segments(polylines, page_w, page_h):
    horiz = []
    vert = []
    other = []
    for pl in polylines:
        pts = pl["pts"]
        if len(pts) == 2:
            (x0, y0), (x1, y1) = pts
            if abs(y0 - y1) < 0.6 and abs(x0 - x1) > 0.2:
                horiz.append([min(x0, x1), max(x0, x1), 0.5 * (y0 + y1), pl["is_special"], pl["style_note"]])
            elif abs(x0 - x1) < 0.6 and abs(y0 - y1) > 0.2:
                vert.append([min(y0, y1), max(y0, y1), 0.5 * (x0 + x1), pl["is_special"], pl["style_note"]])
            else:
                other.append(pl)
        else:
            other.append(pl)

    horiz.sort(key=lambda r: (round(r[2], 1), r[0]))
    merged_h = []
    for seg in horiz:
        if merged_h and abs(seg[2] - merged_h[-1][2]) < 0.8 and seg[0] <= merged_h[-1][1] + 2.0:
            merged_h[-1][1] = max(merged_h[-1][1], seg[1])
        else:
            merged_h.append(seg)

    vert.sort(key=lambda r: (round(r[2], 1), r[0]))
    merged_v = []
    for seg in vert:
        if merged_v and abs(seg[2] - merged_v[-1][2]) < 0.8 and seg[0] <= merged_v[-1][1] + 2.0:
            merged_v[-1][1] = max(merged_v[-1][1], seg[1])
        else:
            merged_v.append(seg)

    segments = list(other)
    for x0, x1, y, is_spec, note in merged_h:
        if (x1 - x0) > page_w * 0.78:
            continue
        segments.append({"pts": [(x0, y), (x1, y)], "is_special": is_spec, "style_note": note})

    for y0, y1, x, is_spec, note in merged_v:
        if (y1 - y0) > page_h * 0.75:
            continue
        segments.append({"pts": [(x, y0), (x, y1)], "is_special": is_spec, "style_note": note})

    changed = True
    while changed:
        changed = False
        n = len(segments)
        used = [False] * n
        new_segs = []
        for i in range(n):
            if used[i]:
                continue
            pts_i = list(segments[i]["pts"])
            spec_i = segments[i]["is_special"]
            note_i = segments[i]["style_note"]
            for end_idx in (0, -1):
                ep = pts_i[end_idx]
                matches = []
                for j in range(i + 1, n):
                    if used[j]:
                        continue
                    pts_j = segments[j]["pts"]
                    if dist_pt(ep, pts_j[0]) <= 1.5:
                        matches.append((j, 0))
                    elif dist_pt(ep, pts_j[-1]) <= 1.5:
                        matches.append((j, -1))
                if len(matches) == 1:
                    j, j_end = matches[0]
                    pts_j = list(segments[j]["pts"])
                    if end_idx == -1:
                        if j_end == 0:
                            pts_i.extend(pts_j[1:])
                        else:
                            pts_i.extend(reversed(pts_j[:-1]))
                    else:
                        if j_end == -1:
                            pts_i = pts_j[:-1] + pts_i
                        else:
                            pts_i = list(reversed(pts_j[1:])) + pts_i
                    used[j] = True
                    changed = True
            used[i] = True
            new_segs.append({"pts": pts_i, "is_special": spec_i, "style_note": note_i})
        segments = new_segs

    return segments


def find_target_node(arrow, course_boxes, modules, touch_tol):
    candidates = []
    for b in course_boxes:
        d = min(dist_pt_to_box_border(p, b) for p in arrow["pts"])
        if d <= touch_tol:
            candidates.append((d, b))
    for m in modules:
        d = min(dist_pt_to_box_border(p, m) for p in arrow["pts"])
        if d <= touch_tol:
            candidates.append((d + 0.5, m))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def find_node_at_origin_point(pt, course_boxes, modules, exclude_node=None, tol=5.0):
    best_box = None
    best_d = 999.0
    for b in course_boxes:
        if exclude_node is not None and b["id"] == exclude_node["id"]:
            continue
        if point_in_or_touching_box(pt, b, tol=tol):
            d = dist_pt_to_box_border(pt, b)
            if d < best_d:
                best_d = d
                best_box = b
    if best_box is not None:
        return best_box

    for m in modules:
        if exclude_node is not None and m["id"] == exclude_node["id"]:
            continue
        d = dist_pt_to_box_border(pt, m)
        if d <= tol:
            return m
    return None


def get_segment_vector(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = math.hypot(dx, dy)
    return (dx / norm, dy / norm) if norm > 0.001 else (0.0, 0.0)


def is_perpendicular_or_t_junction(v_incoming, v_host):
    dot = abs(v_incoming[0] * v_host[0] + v_incoming[1] * v_host[1])
    return dot <= 0.60


def trace_all_arrows(arrowheads, connectors, course_boxes, modules, tol_t, touch_tol):
    arrow_dest = {}
    orphan_arrows = []
    for arr in arrowheads:
        tgt = find_target_node(arr, course_boxes, modules, touch_tol)
        if tgt is not None:
            arrow_dest[arr["id"]] = (arr, tgt)

    head_of_con = defaultdict(list)
    for arr_id, (arr, tgt) in arrow_dest.items():
        best_con = None
        best_k = None
        best_d = 999.0
        for con in connectors:
            d_end = min(dist_pt(con["end"], arr["base"]), dist_pt(con["end"], arr["tip"]))
            d_start = min(dist_pt(con["start"], arr["base"]), dist_pt(con["start"], arr["tip"]))
            if d_end < best_d:
                best_d = d_end
                best_con = con
                best_k = 1
            if d_start < best_d:
                best_d = d_start
                best_con = con
                best_k = 0

        if best_con is not None and best_d <= touch_tol + 2.5:
            head_of_con[best_con["id"]].append((best_k, arr, tgt))
        else:
            orphan_arrows.append((arr, f"Destino={tgt.get('curso_limpio', tgt.get('label'))}, conector desconectado"))

    con_segs = []
    for con in connectors:
        pts = con["pts"]
        for idx in range(len(pts) - 1):
            con_segs.append((con["id"], pts[idx], pts[idx + 1], con))

    con_map = {c["id"]: c for c in connectors}
    edges = []

    def get_sources_for_connector(con_id, tip_k, target_node, visited):
        con = con_map[con_id]
        pts = con["pts"] if tip_k == 1 else list(reversed(con["pts"]))
        origin_pt = pts[0]
        v_incoming = get_segment_vector(pts[1], pts[0]) if len(pts) >= 2 else (0.0, 0.0)

        for p in pts:
            node = find_node_at_origin_point(p, course_boxes, modules, exclude_node=target_node, tol=tol_t)
            if node is not None:
                return [(node, con["is_special"], con["style_note"])]

        found = []
        for host_id, s_a, s_b, host_con in con_segs:
            if host_id == con_id or host_id in visited:
                continue
            d, proj = dist_pt_to_segment(origin_pt, s_a, s_b)
            if d <= tol_t:
                v_host = get_segment_vector(s_a, s_b)
                if not is_perpendicular_or_t_junction(v_incoming, v_host) and d > 1.2:
                    continue

                new_vis = visited | {host_id}
                h_pts = host_con["pts"]
                for ep in (h_pts[0], h_pts[-1]):
                    h_node = find_node_at_origin_point(ep, course_boxes, modules, exclude_node=target_node, tol=tol_t)
                    if h_node is not None:
                        spec = con["is_special"] or host_con["is_special"]
                        note = con["style_note"] or host_con["style_note"]
                        found.append((h_node, spec, note))

                if not found and len(visited) < 6:
                    sub_res = get_sources_for_connector(host_id, 1, target_node, new_vis)
                    found.extend(sub_res)

        return found

    for con_id, head_entries in head_of_con.items():
        for tip_k, arr, tgt in head_entries:
            sources = get_sources_for_connector(con_id, tip_k, tgt, {con_id})
            valid_sources = [s for s in sources if s[0]["id"] != tgt["id"]]
            if not valid_sources:
                orphan_arrows.append((arr, f"Destino={tgt.get('curso_limpio', tgt.get('label'))}, sin origen en trazado"))
            else:
                for src_node, is_spec, s_note in valid_sources:
                    spec = is_spec or arr["is_special"]
                    note = s_note or arr["style_note"]
                    edges.append({
                        "source": src_node,
                        "target": tgt,
                        "is_special": spec,
                        "style_note": note,
                        "arrow": arr,
                    })

    return edges, orphan_arrows


# =============================================================================
# 3. EXTRACCIÓN Y CRUCE CON LA MALLA CURRICULAR
# =============================================================================

def parse_malla_pdf(malla_path: str):
    if not malla_path or not os.path.exists(malla_path):
        return None, [], False

    carrera_detected = None
    has_requisito_col = False
    malla_courses = []

    with pdfplumber.open(malla_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            full_text = page.extract_text() or ""
            if page_idx == 0 and not carrera_detected:
                carrera_detected = detect_career_name(full_text, malla_path)

            if re.search(r"\bREQUISITO(?:S)?\b", full_text, flags=re.IGNORECASE):
                has_requisito_col = True

            tables = page.extract_tables()
            if tables:
                page_courses = parse_tables_from_page(tables, has_requisito_col)
                malla_courses.extend(page_courses)

            line_courses = parse_text_lines_fallback(full_text, has_requisito_col)
            malla_courses = merge_malla_course_lists(malla_courses, line_courses)

    return carrera_detected, malla_courses, has_requisito_col


def detect_career_name(text: str, filepath: str) -> str:
    clean = clean_display_text(text)
    patterns = [
        r"CARRERA DE\s+([A-ZÁÉÍÓÚÜÑ\s]+?)(?=\s+ASIGNATURAS|\s+PLAN|\n|$)",
        r"Plan de estudios\s*\d{4}\s*[-–]\s*([A-Za-záéíóúüñÁÉÍÓÚÜÑ\s]+?)(?=\s+Facultad|\n|$)",
        r"SECCI[ÓO]N\s+([A-ZÁÉÍÓÚÜÑ]+)",
        r"FACULTAD DE\s+(DERECHO)",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return clean_display_text(m.group(1)).title()
    return clean_display_text(filepath.split("/")[-1].replace(".pdf", ""))


def parse_cycle_token(token: str):
    if not token:
        return None
    t = normalize_text(token).upper().strip()
    if t in ROMAN_TO_INT:
        return ROMAN_TO_INT[t]
    return None


def split_multiline_row(row):
    cells = [(c or "").strip() for c in row]
    if not any("\n" in c for c in cells):
        return [cells]

    code_col = None
    for idx, c in enumerate(cells[:3]):
        lines = [ln.strip() for ln in c.splitlines() if ln.strip()]
        if len(lines) >= 2 and all(
            re.match(r"^\(?([0-9][0-9A-Z]{4,5}|Sello\s*UP|Bloque|Bioque)$", ln, flags=re.I)
            for ln in lines
        ):
            code_col = idx
            break

    if code_col is None:
        return [cells]

    code_lines = [ln.strip() for ln in cells[code_col].splitlines() if ln.strip()]
    n_sub = len(code_lines)
    sub_rows = []
    for s_idx in range(n_sub):
        new_r = []
        for col_idx, cell_val in enumerate(cells):
            lines = [ln.strip() for ln in cell_val.splitlines() if ln.strip()]
            if not lines:
                new_r.append("")
            elif len(lines) == n_sub:
                new_r.append(lines[s_idx])
            elif col_idx == 0:
                new_r.append(lines[min(s_idx, len(lines) - 1)])
            else:
                chunk = max(1, len(lines) // n_sub)
                start = s_idx * chunk
                end = len(lines) if s_idx == n_sub - 1 else (s_idx + 1) * chunk
                new_r.append(" ".join(lines[start:end]))
        sub_rows.append(new_r)
    return sub_rows


def parse_tables_from_page(tables, has_requisito_col=False):
    courses = []
    curr_cycle = None
    in_electives_section = False

    for table in tables:
        for raw_row in table:
            if not raw_row or all(not (c or "").strip() for c in raw_row):
                continue

            row_joined = " ".join((c or "") for c in raw_row)
            norm_joined = normalize_text(row_joined)

            if "asignaturas por bloques" in norm_joined or re.search(r"\belectivos\b.*\bdat\b", norm_joined):
                in_electives_section = True
                continue
            if in_electives_section:
                continue
            if "creditos obligatorios totales" in norm_joined or "total de creditos" in norm_joined:
                continue

            for row in split_multiline_row(raw_row):
                c0 = row[0].strip() if len(row) > 0 else ""
                cyc_cand = parse_cycle_token(c0)
                if cyc_cand is not None:
                    if cyc_cand == 11 and (curr_cycle in (1, 2)):
                        cyc_cand = 2
                    curr_cycle = cyc_cand

                parsed = parse_single_malla_row(row, curr_cycle, has_requisito_col)
                if parsed:
                    courses.append(parsed)

    return courses


def parse_single_malla_row(row, curr_cycle, has_requisito_col):
    cells = [clean_display_text(c or "") for c in row]
    non_empty = [c for c in cells if c]
    if not non_empty:
        return None

    joined = " ".join(non_empty)
    norm_j = normalize_text(joined)
    if any(h in norm_j for h in ("asignaturas obligatorias", "plan de estudios", "facultad de")):
        return None

    codigo = ""
    nombre = ""
    req_raw = ""
    creditos = None

    code_idx = None
    for idx, c in enumerate(cells[:3]):
        c_clean = c.lstrip("(").strip()
        if re.match(r"^[0-9][0-9A-Z]{4,5}$", c_clean):
            codigo = c_clean
            code_idx = idx
            break
        if re.match(r"^(?:Sello\s*UP|Bloque|Bioque)$", c_clean, flags=re.I):
            codigo = "SELLO_UP" if "sello" in c_clean.lower() else "BLOQUE"
            code_idx = idx
            break

    if code_idx is not None and code_idx + 1 < len(cells):
        nombre = cells[code_idx + 1]
        if has_requisito_col and code_idx + 2 < len(cells):
            req_raw = cells[code_idx + 2]
    else:
        for idx, c in enumerate(cells):
            nc = normalize_text(c)
            if "electivo" in nc or "electvo" in nc or "curso del bloque" in nc or "curso 1 del bloque" in nc or "curso 2 del bloque" in nc or "escoger " in nc:
                nombre = c
                codigo = "ELECTIVO" if "elect" in nc else "BLOQUE"
                if has_requisito_col and idx + 1 < len(cells):
                    req_raw = cells[idx + 1]
                break

    if not nombre:
        return None

    nombre = re.sub(r"\s+[A-Z]{1,3}$", "", nombre).strip()
    if normalize_text(nombre) in ("electvo", "electivo"):
        nombre = "Electivo"

    nums = []
    start_search = (code_idx + 2) if code_idx is not None else 1
    for c in cells[start_search:]:
        for token in re.findall(r"\d+", c):
            val = int(token)
            if val >= 100 and len(token) == 3:
                nums.append(val % 10)
            elif val < 12:
                nums.append(val)
    if nums:
        creditos = nums[-1]
    if curr_cycle == 0:
        creditos = 0

    norm_name = normalize_text(nombre)
    return {
        "ciclo": curr_cycle,
        "codigo": codigo if codigo not in ("SELLO_UP", "BLOQUE", "ELECTIVO") else "",
        "tipo_codigo": codigo,
        "curso": nombre,
        "norm_curso": norm_name,
        "block_type": classify_block_type(norm_name),
        "creditos": creditos,
        "requisito_raw": req_raw,
    }


def parse_text_lines_fallback(full_text: str, has_requisito_col: bool):
    courses = []
    curr_cycle = None
    for raw_line in full_text.splitlines():
        line = clean_display_text(raw_line)
        if not line:
            continue
        if re.search(r"ASIGNATURAS POR BLOQUES|ELECTIVOS\s+DAT", line, flags=re.I):
            break

        m = re.match(
            r"^(?:(0|I{1,3}|IV|V|VI{0,3}|IX|X|XI{0,2}|\d{1,2})\s+)?\(?([0-9][0-9A-Z]{4,5})\s+(.+)$",
            line,
        )
        if m:
            if m.group(1):
                c_val = parse_cycle_token(m.group(1))
                if c_val is not None:
                    curr_cycle = 2 if (c_val == 11 and curr_cycle == 1) else c_val
            code = m.group(2)
            rest = m.group(3)
            m_tail = re.search(r"\s+(?:ING|ECO|HUM|HIM|CON|CONSP|CSP|MKT|FIN|ADM|MNI|A|E|H|C|D|F|S)\s+(?:\d.*)$", rest)
            name = rest[: m_tail.start()].strip() if m_tail else rest
            tail = rest[m_tail.start() :] if m_tail else ""
            digits = [int(d) for d in re.findall(r"\d", tail)]
            cred = 0 if curr_cycle == 0 else (digits[-1] if digits else None)
            norm_name = normalize_text(name)
            courses.append({
                "ciclo": curr_cycle,
                "codigo": code,
                "tipo_codigo": code,
                "curso": name,
                "norm_curso": norm_name,
                "block_type": classify_block_type(norm_name),
                "creditos": cred,
                "requisito_raw": "",
            })
    return courses


def merge_malla_course_lists(primary, fallback):
    seen_codes = {c["codigo"] for c in primary if c["codigo"]}
    result = list(primary)
    for fb in fallback:
        if fb["codigo"] and fb["codigo"] not in seen_codes:
            result.append(fb)
            seen_codes.add(fb["codigo"])
    return result


def similarity_score(norm_a: str, norm_b: str) -> float:
    a = normalize_roman_suffix(norm_a)
    b = normalize_roman_suffix(norm_b)
    if a == b:
        return 1.0

    romans = {"i", "ii", "iii", "iv"}
    ta = set(a.split())
    tb = set(b.split())
    ra = ta & romans
    rb = tb & romans
    if ra and rb and ra != rb:
        return 0.2

    seq_ratio = SequenceMatcher(None, a, b).ratio()
    wa = {w for w in ta if w not in STOPWORDS}
    wb = {w for w in tb if w not in STOPWORDS}
    if wa and wb:
        jaccard = len(wa & wb) / len(wa | wb)
        overlap = len(wa & wb) / min(len(wa), len(wb))
        return max(seq_ratio, 0.55 * jaccard + 0.45 * overlap)
    return seq_ratio


def link_boxes_to_malla(boxes, malla_courses):
    if not malla_courses:
        return {}, list(boxes), []

    used_malla_indices = set()
    box_to_malla = {}

    for b in boxes:
        b_block = classify_block_type(b["norm_curso"])
        best_idx = None
        best_score = 0.0

        for idx, mc in enumerate(malla_courses):
            if idx in used_malla_indices:
                continue
            score = similarity_score(b["norm_curso"], mc["norm_curso"])
            if b["ciclo"] is not None and mc["ciclo"] is not None and b["ciclo"] == mc["ciclo"]:
                score += 0.06
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None and best_score >= 0.68:
            used_malla_indices.add(best_idx)
            box_to_malla[b["id"]] = malla_courses[best_idx]
            continue

        if b_block is not None:
            candidates = [
                (idx, mc) for idx, mc in enumerate(malla_courses)
                if idx not in used_malla_indices and mc["block_type"] == b_block
            ]
            if candidates:
                candidates.sort(
                    key=lambda item: abs((item[1]["ciclo"] or 0) - (b["ciclo"] or 0))
                )
                chosen_idx, chosen_mc = candidates[0]
                used_malla_indices.add(chosen_idx)
                box_to_malla[b["id"]] = chosen_mc

    unmatched_boxes = [b for b in boxes if b["id"] not in box_to_malla]
    unmatched_malla = [mc for idx, mc in enumerate(malla_courses) if idx not in used_malla_indices]
    return box_to_malla, unmatched_boxes, unmatched_malla


def parse_malla_requisitos_column(requisito_raw: str, all_courses):
    if not requisito_raw:
        return [], []

    notas = []
    text = clean_display_text(requisito_raw)

    for m in re.finditer(r"\b(\d{2,3})\s*cr[eé]ditos(?:\s+acad[eé]micos)?\b", text, flags=re.IGNORECASE):
        notas.append(f"Requiere {m.group(1)} créditos")
    text_wo_cred = re.sub(r"\b\d{2,3}\s*cr[eé]ditos(?:\s+acad[eé]micos)?\b", " ", text, flags=re.IGNORECASE)

    if " O " in text_wo_cred:
        notas.append(f"Condición malla: {text_wo_cred.strip()}")

    norm_req = normalize_text(text_wo_cred)
    if not norm_req:
        return [], notas

    matched_prereqs = []
    sorted_courses = sorted(all_courses, key=lambda c: len(c["norm_curso"]), reverse=True)
    remaining = " " + normalize_roman_suffix(norm_req) + " "

    for c in sorted_courses:
        cname = normalize_roman_suffix(c["norm_curso"])
        if not cname or len(cname) < 4:
            continue
        if f" {cname} " in remaining:
            matched_prereqs.append(c["display_id"])
            remaining = remaining.replace(f" {cname} ", " ")

    return sorted(set(matched_prereqs)), notas


# =============================================================================
# 4. CONSTRUCCIÓN DE LA TABLA CSV / JSON Y VALIDACIONES
# =============================================================================

def build_curriculum_graph_and_validate(flujo_path: str, malla_path: str = None, output_csv: str = None, career_override: str = None, json_out: str = None):
    geom = extract_flowchart_geometry(flujo_path)
    carrera_malla, malla_courses, has_req_col = parse_malla_pdf(malla_path) if malla_path else (None, [], False)
    
    # Extraer nombre de carrera del archivo si no se especificó
    if not career_override and not carrera_malla:
        fname = os.path.basename(flujo_path).replace(".pdf", "")
        m_carr = re.search(r"CARRERA DE\s+([A-ZÁÉÍÓÚÜÑ\s]+?)(?=\s*[-–]|\s+PLAN|$)", fname, re.IGNORECASE)
        carrera = clean_display_text(m_carr.group(1)).title() if m_carr else fname.title()
    else:
        carrera = career_override or carrera_malla or "Carrera"

    boxes = geom["boxes"]
    modules = geom["modules"]
    edges = geom["edges"]

    box_to_malla, unmatched_boxes, unmatched_malla = link_boxes_to_malla(boxes, malla_courses)

    # Asignar códigos automáticos si no vinieron de la tabla
    for idx, b in enumerate(boxes, 1):
        mc = box_to_malla.get(b["id"])
        b["codigo"] = mc["codigo"] if (mc and mc["codigo"]) else f"GEN-{idx:03d}"
        b["curso_oficial"] = b["curso_limpio"]
        b["ciclo_oficial"] = mc["ciclo"] if (mc and mc["ciclo"] is not None) else (b["ciclo"] or 1)
        b["creditos_oficial"] = mc["creditos"] if (mc and mc["creditos"] is not None) else (b["creditos_caja"] or 4.0)
        b["display_id"] = f"{b['codigo']} {b['curso_oficial']}".strip()

    flow_prereqs = defaultdict(set)
    flow_mod_prereqs = defaultdict(set)
    flow_opens = defaultdict(set)
    flow_notes = defaultdict(list)
    bad_cycle_arrows = []

    for e in edges:
        src = e["source"]
        tgt = e["target"]
        is_spec = e["is_special"]
        style_note = e["style_note"]

        if tgt.get("is_module"):
            min_c = min((c.get("ciclo") or 99) for c in tgt["courses"])
            tgt_courses = [c for c in tgt["courses"] if (c.get("ciclo") or 99) == min_c]
        else:
            tgt_courses = [tgt]

        src_courses = src["courses"] if src.get("is_module") else [src]
        src_label = src["label"] if src.get("is_module") else src["display_id"]
        tgt_label = tgt["label"] if tgt.get("is_module") else tgt["display_id"]

        if not src.get("is_module") and not tgt.get("is_module"):
            c_src = src.get("ciclo")
            c_tgt = tgt.get("ciclo")
            if c_src is not None and c_tgt is not None and c_src >= c_tgt:
                bad_cycle_arrows.append((src["display_id"], c_src, tgt["display_id"], c_tgt, style_note or "normal"))

        if is_spec:
            for tc in tgt_courses:
                flow_notes[tc["id"]].append(f"Relación ({style_note}) desde {src_label}")
            for sc in src_courses:
                flow_notes[sc["id"]].append(f"Relación ({style_note}) hacia {tgt_label}")

        if tgt.get("is_module"):
            for tc in tgt_courses:
                flow_mod_prereqs[tc["id"]].add(f"{src_label} -> {tgt['label']}")
            for sc in src_courses:
                for tc in tgt_courses:
                    flow_opens[sc["id"]].add(tc["display_id"])
        elif src.get("is_module"):
            for tc in tgt_courses:
                flow_mod_prereqs[tc["id"]].add(f"{src['label']}")
            for sc in src_courses:
                flow_opens[sc["id"]].add(tgt["display_id"])
        else:
            flow_prereqs[tgt["id"]].add(src["display_id"])
            flow_opens[src["id"]].add(tgt["display_id"])

    for m in modules:
        for c in m["courses"]:
            flow_notes[c["id"]].append(f"Pertenece a {m['label']}")

    malla_prereqs_by_box = {}
    if has_req_col:
        for b in boxes:
            mc = box_to_malla.get(b["id"])
            if mc and mc.get("requisito_raw"):
                reqs, req_notes = parse_malla_requisitos_column(mc["requisito_raw"], boxes)
                malla_prereqs_by_box[b["id"]] = set(reqs)
                flow_notes[b["id"]].extend(req_notes)
            else:
                malla_prereqs_by_box[b["id"]] = set()

    final_prereqs = {}
    final_opens = defaultdict(set)
    for b in boxes:
        if has_req_col and b["id"] in box_to_malla and malla_prereqs_by_box.get(b["id"]):
            final_prereqs[b["id"]] = malla_prereqs_by_box[b["id"]]
        else:
            final_prereqs[b["id"]] = flow_prereqs[b["id"]]

    display_to_box = {b["display_id"]: b for b in boxes}
    for b in boxes:
        for pr_disp in final_prereqs[b["id"]]:
            if pr_disp in display_to_box:
                final_opens[display_to_box[pr_disp]["id"]].add(b["display_id"])
        for o_disp in flow_opens[b["id"]]:
            if not has_req_col:
                final_opens[b["id"]].add(o_disp)

    rows = []
    diff_ciclo_cred = []

    for b in sorted(boxes, key=lambda x: (x["ciclo_oficial"] if x["ciclo_oficial"] is not None else 99, x["top"], x["x0"])):
        mc = box_to_malla.get(b["id"])
        if mc:
            if b["ciclo"] is not None and mc["ciclo"] is not None and b["ciclo"] != mc["ciclo"]:
                diff_ciclo_cred.append(
                    f"Ciclo distinto en '{b['curso_oficial']}': flujograma={b['ciclo']} vs malla={mc['ciclo']}"
                )
            if b["creditos_caja"] is not None and mc["creditos"] is not None and b["creditos_caja"] != mc["creditos"]:
                diff_ciclo_cred.append(
                    f"Créditos distintos en '{b['curso_oficial']}': flujograma={b['creditos_caja']} vs malla={mc['creditos']}"
                )

        all_notes = list(dict.fromkeys(b["notas_caja"] + flow_notes[b["id"]]))
        rows.append({
            "carrera": carrera,
            "ciclo": b["ciclo_oficial"] if b["ciclo_oficial"] is not None else "",
            "codigo": b["codigo"],
            "curso": b["curso_oficial"],
            "creditos": b["creditos_oficial"] if b["creditos_oficial"] is not None else "",
            "prerrequisitos": "; ".join(sorted(final_prereqs[b["id"]])),
            "prerreq_via_modulo": "; ".join(sorted(flow_mod_prereqs[b["id"]])),
            "cursos_que_abre": "; ".join(sorted(final_opens[b["id"]])),
            "notas": "; ".join(all_notes),
            "es_cuello_botella": len(final_opens[b["id"]]) >= 2,
            "tipo": "ELECTIVA" if "electiv" in b["norm_curso"] else "OBLIGATORIA"
        })

    if output_csv:
        fieldnames = [
            "carrera", "ciclo", "codigo", "curso", "creditos",
            "prerrequisitos", "prerreq_via_modulo", "cursos_que_abre", "notas",
        ]
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r[k] for k in fieldnames})

    # Exportación opcional a JSON estructurado para Tracker UP
    if json_out:
        # Construir estructura compatible con CurriculumFileSchema
        cursos_json = []
        name_to_code = {b["curso_oficial"]: b["codigo"] for b in boxes}
        disp_to_code = {b["display_id"]: b["codigo"] for b in boxes}

        for r in rows:
            # Extraer códigos de prerrequisitos
            prereq_codes = []
            if r["prerrequisitos"]:
                for pr in r["prerrequisitos"].split("; "):
                    pr = pr.strip()
                    if pr in disp_to_code:
                        prereq_codes.append(disp_to_code[pr])
                    else:
                        m_code = re.match(r"^([0-9][0-9A-Z]{4,5}|GEN-\d{3})\b", pr)
                        if m_code:
                            prereq_codes.append(m_code.group(1))

            cursos_json.append({
                "codigo": r["codigo"],
                "nombre": r["curso"],
                "creditos": float(r["creditos"]) if r["creditos"] != "" else 4.0,
                "ciclo_sugerido": int(r["ciclo"]) if str(r["ciclo"]).isdigit() else 1,
                "tipo": r["tipo"],
                "es_cuello_botella": r["es_cuello_botella"],
                "prerrequisitos": prereq_codes
            })

        total_creds = sum(c["creditos"] for c in cursos_json)
        json_data = {
            "carrera": {
                "codigo": carrera[:3].upper(),
                "nombre": carrera,
                "facultad": "Universidad del Pacífico",
                "plan": "2022",
                "total_creditos_graduacion": int(total_creds) if total_creds > 0 else 205,
                "total_ciclos": 10,
                "max_creditos_ciclo_regular": 22.0
            },
            "concentraciones": [],
            "cursos": cursos_json
        }

        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON Tracker UP generado en: {json_out}")

    # Validaciones impresas
    print("=" * 72)
    print(f"REPORTE DE VALIDACIÓN: {carrera}")
    print(f"Flujograma : {flujo_path}")
    if malla_path:
        print(f"Malla      : {malla_path}")
    print(f"Cursos detectados : {len(rows)}")
    print("=" * 72)

    print("\n1) Cursos del flujograma sin equivalente en la malla:")
    if unmatched_boxes and malla_path:
        for b in unmatched_boxes:
            print(f"   - [Ciclo {b['ciclo']}] {b['curso_limpio']}")
    else:
        print("   Ninguno o sin archivo de malla tabular para contrastar.")

    print("\n2) Flechas cuyo origen está en un ciclo igual o posterior al destino:")
    if bad_cycle_arrows:
        for src_d, c_s, tgt_d, c_t, kind in bad_cycle_arrows:
            print(f"   - {src_d} (Ciclo {c_s}) -> {tgt_d} (Ciclo {c_t}) [{kind}]")
    else:
        print("   Ninguna (relaciones temporales consistentes).")

    print("\n3) Puntas de flecha sin origen detectado:")
    if geom["orphan_arrows"]:
        for arr, reason in geom["orphan_arrows"][:10]:
            print(f"   - Punta en ({arr['tip'][0]:.1f}, {arr['tip'][1]:.1f}): {reason}")
        if len(geom["orphan_arrows"]) > 10:
            print(f"   ... y {len(geom['orphan_arrows']) - 10} más.")
    else:
        print("   Ninguna (todas las puntas trazadas con éxito).")

    print("=" * 72 + "\n")
    return rows


def main():
    parser = argparse.ArgumentParser(description="Extractor geométrico de flujogramas y mallas curriculares UP v2.")
    parser.add_argument("flujograma", help="Ruta al PDF del flujograma curricular.")
    parser.add_argument("malla", nargs="?", default=None, help="Ruta al PDF de la malla curricular tabular (opcional).")
    parser.add_argument("-o", "--output", default=None, help="Ruta del archivo CSV de salida.")
    parser.add_argument("--json-out", default=None, help="Ruta para exportar el JSON oficial compatible con Tracker UP.")
    parser.add_argument("--carrera", default=None, help="Nombre de la carrera (opcional, se autodetecta).")
    args = parser.parse_args()

    build_curriculum_graph_and_validate(args.flujograma, args.malla, args.output, args.carrera, args.json_out)


if __name__ == "__main__":
    main()

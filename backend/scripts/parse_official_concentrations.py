"""
Parser robusto y completo para las 33 concentraciones de pregrado de la Universidad del Pacífico.
Extrae asignaturas fijas (obligatorias de la concentración), bolsa de electivos válidos,
créditos mínimos y exclusiones por carrera según las Normas Especiales aprobadas el 24.06.2026.
"""
import re
import json

def parse_concentrations():
    with open('scratch_clean_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()

    # Known career exclusions and rules according to Consejo Académico 24.06.2026
    known_rules = {
        5: {  # Cultura y sociedad digital
            "carreras_excluidas": ["HUM"],
            "notas": "No aplica para estudiantes de Humanidades Digitales."
        },
        6: {  # Derecho empresarial
            "carreras_excluidas": ["DER"],
            "creditos_por_carrera": {"ADM": 12, "CON": 12},
            "creditos_minimos": 15,
            "notas": "No aplica para estudiantes de Derecho. Para Administración y Contabilidad el creditaje mínimo es 12 créditos."
        },
        9: {  # Diseño
            "carreras_excluidas": ["IID"],
            "notas": "No aplica para Ingeniería en Innovación y Diseño. Humanidades Digitales deberá completar 12 créditos adicionales al curso obligatorio de UX."
        },
        11: { # Experiencia del usuario
            "carreras_excluidas": ["IID"],
            "notas": "No aplica para Ingeniería en Innovación y Diseño. Humanidades Digitales deberá completar 12 créditos adicionales al bloque de UX."
        },
        13: { # Finanzas
            "notas": "13.1 Solo para estudiantes de Economía (12 cr: 1F0229 + 8 cr electivos DA Finanzas). 13.2 Para FCE e Ingeniería (12 cr: 1F0120 + 7 cr electivos DA Finanzas).",
            "carreras_excluidas": ["DER", "HUM", "PFE"]
        },
        14: { # Finanzas Corporativas
            "carreras_exclusivas": ["DER"],
            "creditos_minimos": 17,
            "notas": "Solo para estudiantes de Derecho (17 créditos obligatorios de la concentración)."
        },
        18: { # Gestión empresarial sostenible
            "creditos_por_carrera": {"CON": 12},
            "notas": "Requiere 7 créditos obligatorios (142315 y 160173) + 5 electivos (para Contabilidad son 9 créditos electivos de la lista)."
        },
        25: { # Machine Learning
            "carreras_excluidas": ["INF"],
            "creditos_minimos": 15,
            "notas": "No aplica para estudiantes de Ingeniería de la Información (sus asignaturas ya forman parte de su malla obligatoria)."
        },
        31: { # Procesos y tecnología
            "notas": "Incluye asignaturas UP y 3 asignaturas del convenio con UTEC (IN5009, IN4007, IN4304)."
        },
        33: { # Teoría Económica
            "creditos_minimos": 15,
            "notas": "15 créditos académicos obligatorios de la concentración (Macroeconomía Avanzada I, Matemáticas Avanzada, Microeconomía Avanzada I)."
        }
    }

    c_pattern = re.compile(
        r'^(1[A-Z0-9]{5,6}|IN[0-9]{4}|N)\s+(.+?)\s+([A-Z]{3})\s*(?:(\d+|-)\s+(\d+|-)\s+)?(\d+)\s*$'
    )

    sections = re.split(r'\n(?=[0-9]+\.\s+[A-ZÁÉÍÓÚÑ])', text)
    concentraciones = []

    for idx, s in enumerate(sections[1:], 1):
        lines = [l.strip() for l in s.split('\n') if l.strip()]
        header = lines[0]
        name_match = re.match(r'^\d+\.\s+(.+?)(?:\s*\(\d+\s*cr[ée]ditos\))?$', header)
        name = name_match.group(1).strip() if name_match else header

        cred_match = re.search(r'Creditaje m[íi]nimo:?\s*(\d+)', s, re.IGNORECASE)
        creditos_min = int(cred_match.group(1)) if cred_match else (15 if "15 cr" in header or idx == 33 else 12)

        rule = known_rules.get(idx, {})
        if "creditos_minimos" in rule:
            creditos_min = rule["creditos_minimos"]

        cursos_obligatorios = []
        cursos_electivos = []
        is_elective_section = False

        i = 1
        while i < len(lines):
            line = lines[i]

            # Detect elective pool header
            if re.search(r'(cr[ée]ditos correspondientes|siguiente lista|oferta utec)', line, re.IGNORECASE):
                is_elective_section = True
                i += 1
                continue

            # Check alternative pair e.g. "170135 o 142084"
            alt_match = re.search(r'(1[A-Z0-9]{5})\s+(?:o|\/)\s+(1[A-Z0-9]{5})\s+(.+?)\s+([A-Z]{3})\s*(?:(\d+|-)\s+(\d+|-)\s+)?(\d+)', line)
            if alt_match:
                c1, c2, c_name, da, t_h, p_h, c_cr = alt_match.groups()
                course_item = {
                    "codigo": f"{c1} / {c2}",
                    "nombre": c_name.strip(),
                    "departamento": da.strip(),
                    "horas_teoria": int(t_h) if t_h and t_h.isdigit() else 0,
                    "horas_practica": int(p_h) if p_h and p_h.isdigit() else 0,
                    "creditos": float(c_cr),
                    "es_opcional_alternativo": True,
                    "es_obligatorio_concentracion": False
                }
                cursos_electivos.append(course_item)
                i += 1
                continue

            # Check regular course line (possibly wrapped on 2 lines)
            if re.match(r'^(1[A-Z0-9]{5,6}|IN[0-9]{4}|N\s)', line):
                full_line = line
                m = c_pattern.match(full_line)
                if not m and i + 1 < len(lines):
                    test_line = full_line + ' ' + lines[i+1]
                    if c_pattern.match(test_line):
                        full_line = test_line
                        i += 1
                        m = c_pattern.match(full_line)

                if m:
                    code, c_name, da, t_h, p_h, c_cr = m.groups()
                    course_item = {
                        "codigo": code.strip(),
                        "nombre": c_name.strip(),
                        "departamento": da.strip(),
                        "horas_teoria": int(t_h) if t_h and t_h.isdigit() else 0,
                        "horas_practica": int(p_h) if p_h and p_h.isdigit() else 0,
                        "creditos": float(c_cr),
                        "es_obligatorio_concentracion": False
                    }
                    if idx in [14, 33]:
                        course_item["es_obligatorio_concentracion"] = True
                        cursos_obligatorios.append(course_item)
                    elif idx in [7, 8, 12, 16, 18, 21, 22, 23] and not is_elective_section:
                        course_item["es_obligatorio_concentracion"] = True
                        cursos_obligatorios.append(course_item)
                    elif idx == 13:
                        course_item["es_obligatorio_concentracion"] = True
                        cursos_obligatorios.append(course_item)
                    else:
                        cursos_electivos.append(course_item)

            i += 1

        concentraciones.append({
            "id": idx,
            "codigo": f"CONC-{idx:02d}",
            "nombre": name,
            "creditos_minimos": creditos_min,
            "carreras_excluidas": rule.get("carreras_excluidas", []),
            "carreras_exclusivas": rule.get("carreras_exclusivas", []),
            "creditos_por_carrera": rule.get("creditos_por_carrera", {}),
            "notas_reglamento": rule.get("notas", "Abierta a estudiantes de todas las carreras (a partir de 110 créditos acumulados)."),
            "total_cursos_en_lista": len(cursos_obligatorios) + len(cursos_electivos),
            "cursos_obligatorios": cursos_obligatorios,
            "cursos_electivos": cursos_electivos
        })

    return concentraciones

if __name__ == "__main__":
    concs = parse_concentrations()
    with open('backend/data/concentraciones_oficiales.json', 'w', encoding='utf-8') as f:
        json.dump(concs, f, ensure_ascii=False, indent=2)
    print(f"Total concentraciones parsed: {len(concs)}")
    for c in concs:
        total = c['total_cursos_en_lista']
        print(f"[{c['codigo']}] {c['nombre'][:35]:35} | Min {c['creditos_minimos']} cr | Oblig: {len(c['cursos_obligatorios'])} | Elect: {len(c['cursos_electivos'])} | Total: {total}")


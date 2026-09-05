"""
Pruebas exhaustivas para el motor determinístico de reglas curriculares y evaluación de riesgos (RF-10 al RF-16).
"""
import pytest
from fastapi.testclient import TestClient


def register_user(client: TestClient, email: str, ingreso: str = "2023-1", concentracion_id: int = 1) -> str:
    """Helper para registrar usuario y obtener JWT."""
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "nombres": "Estudiante",
        "apellidos": "Prueba",
        "carrera_id": 1,
        "concentracion_id": concentracion_id,
        "periodo_ingreso": ingreso
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    return login_res.json()["access_token"]


# -----------------------------------------------------------------------------
# 1. PRUEBAS DEL MOTOR DETERMINÍSTICO DE RECOMENDACIÓN DE MATRÍCULA (RF-10, 11, 12)
# -----------------------------------------------------------------------------
def test_new_student_recommendation_cycle_1(client: TestClient):
    """Un estudiante nuevo sin historial debe recibir los cursos elegibles iniciales dentro del rango de créditos."""
    token = register_user(client, "20240001@up.edu.pe", ingreso="2024-1")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/curriculum/recommendation", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Cursos iniciales elegibles sin prerrequisito previo (nivelaciones y materias sin prerrequisito)
    assert data["cantidad_cursos_sugeridos"] == 6
    assert data["creditos_totales_sugeridos"] == 12.0
    assert data["rango_creditos_permitido"]["minimo_regular"] == 12.0
    assert data["rango_creditos_permitido"]["maximo_regular"] == 22.0

    codigos = [c["codigo"] for c in data["cursos_sugeridos"]]
    assert "134654" in codigos  # Nivelación en Matemática
    assert "170131" in codigos  # Nivelación en Informática
    assert "120000" in codigos  # Nivelación en Lenguaje
    assert "170001" in codigos  # Introducción a la Ingeniería
    assert "120020" in codigos  # Quehacer Científico
    assert "120030" in codigos  # Desarrollo Personal

    # Tras aprobar las nivelaciones (ej. convalidación o examen de ingreso), se desbloquea Ciclo 1 completo
    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}
    for code in ["134654", "170131", "120000"]:
        client.post("/api/v1/history", headers=headers, json={
            "asignatura_id": by_code[code]["id"],
            "periodo_academico": "2024-0",
            "estado": "APROBADA",
            "calificacion": 16.0,
            "numero_matricula": 1
        })
    res2 = client.get("/api/v1/curriculum/recommendation", headers=headers)
    codigos2 = [c["codigo"] for c in res2.json()["cursos_sugeridos"]]
    assert "138649" in codigos2  # Matemáticas I
    assert "132641" in codigos2  # Economía General I
    assert "120001" in codigos2  # Lenguaje I


def test_recommendation_prioritizes_failed_course_for_retake(client: TestClient):
    """Si un estudiante desaprobó un curso, el motor DEBE priorizarlo como 1ª opción obligatoria (RF-12, RF-13)."""
    token = register_user(client, "20230555@up.edu.pe", ingreso="2023-1")
    headers = {"Authorization": f"Bearer {token}"}

    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}
    asig_fail = by_code["170001"]  # Introducción a la Ingeniería
    asig_pass = by_code["132641"]  # Economía General I

    # Desaprobó Introducción a la Ingeniería (170001) con nota 08.0
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_fail["id"],
        "periodo_academico": "2023-1",
        "estado": "DESAPROBADA",
        "calificacion": 8.0,
        "numero_matricula": 1
    })
    # Aprobó Economía General I (132641) con 14.0
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_pass["id"],
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 14.0,
        "numero_matricula": 1
    })

    res = client.get("/api/v1/curriculum/recommendation", headers=headers)
    assert res.status_code == 200
    cursos = res.json()["cursos_sugeridos"]

    # El primer curso sugerido DEBE ser el desaprobado (170001) proyectado en 2ª matrícula
    top_course = cursos[0]
    assert top_course["codigo"] == "170001"
    assert top_course["es_reiteracion"] is True
    assert top_course["numero_matricula_proyectada"] == 2
    assert "Re-matriculación" in top_course["motivo_prioridad"]


def test_credit_bag_and_concentration_filtering_for_electives(client: TestClient):
    """Las materias avanzadas de especialidad con concentración o prerrequisitos no deben sugerirse sin cumplirlos (RF-06, RF-10)."""
    token = register_user(client, "20230777@up.edu.pe", ingreso="2023-1", concentracion_id=1)  # Software
    headers = {"Authorization": f"Bearer {token}"}

    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}

    # Estudiante aprueba nivelaciones y materias iniciales
    for code in ["134654", "170131", "120000", "170001", "138649"]:
        client.post("/api/v1/history", headers=headers, json={
            "asignatura_id": by_code[code]["id"],
            "periodo_academico": "2023-1",
            "estado": "APROBADA",
            "calificacion": 15.0,
            "numero_matricula": 1
        })

    res = client.get("/api/v1/curriculum/recommendation", headers=headers)
    assert res.status_code == 200
    codigos_sugeridos = [c["codigo"] for c in res.json()["cursos_sugeridos"]]

    # No debe incluir cursos avanzados de ciclo 8/9 de otra concentración (ej. 170019 Deep Learning de CONC-DS)
    assert "170019" not in codigos_sugeridos
    # Debe sugerir cursos de Ciclo 2 que ya tienen prerrequisitos cumplidos
    assert "138650" in codigos_sugeridos  # Matemáticas II (requiere Matemáticas I: 138649)
    assert "170002" in codigos_sugeridos  # Herramientas de Programación (requiere Nivelación Informática: 170131)


# -----------------------------------------------------------------------------
# 2. PRUEBAS DEL SISTEMA DE EVALUACIÓN DE RIESGOS ACADÉMICOS (RF-13, 14, 15, 16)
# -----------------------------------------------------------------------------
def test_risk_alert_reiteracion_matricula_rf13(client: TestClient):
    """Detecta alerta CRÍTICA ante asignaturas en 2ª o 3ª matrícula (RF-13)."""
    token = register_user(client, "20220111@up.edu.pe", ingreso="2022-1")
    headers = {"Authorization": f"Bearer {token}"}

    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}
    asig_target = by_code["138649"]  # Matemáticas I

    # Registra un curso cursándose en 2ª matrícula
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_target["id"],
        "periodo_academico": "2023-1",
        "estado": "EN_CURSO",
        "numero_matricula": 2
    })

    res = client.get("/api/v1/curriculum/risks", headers=headers)
    assert res.status_code == 200
    alertas = res.json()

    alerta_reit = next((a for a in alertas if a["tipo_alerta"] == "REITERACION_MATRICULA"), None)
    assert alerta_reit is not None
    assert alerta_reit["nivel_severidad"] == "CRITICA"
    assert alerta_reit["codigo_asignatura"] == "138649"
    assert alerta_reit["detalles"]["numero_matricula"] == 2


def test_risk_alert_prerrequisito_nota_limite_rf14(client: TestClient):
    """Detecta alerta de advertencia cuando el curso en curso depende de un prerrequisito aprobado con 11.00 (RF-14)."""
    token = register_user(client, "20230222@up.edu.pe", ingreso="2023-1")
    headers = {"Authorization": f"Bearer {token}"}

    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}
    asig_req = by_code["138649"]   # Matemáticas I
    asig_obj = by_code["138650"]   # Matemáticas II (depende de 138649)

    # Aprobó Matemáticas I con nota límite 11.00
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_req["id"],
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 11.0,
        "numero_matricula": 1
    })

    # Actualmente cursa Matemáticas II, cuyo prerrequisito es 138649
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_obj["id"],
        "periodo_academico": "2023-2",
        "estado": "EN_CURSO",
        "numero_matricula": 1
    })

    res = client.get("/api/v1/curriculum/risks", headers=headers)
    assert res.status_code == 200
    alertas = res.json()

    alerta_limite = next((a for a in alertas if a["tipo_alerta"] == "PRERREQUISITO_NOTA_LIMITE"), None)
    assert alerta_limite is not None
    assert alerta_limite["nivel_severidad"] == "ADVERTENCIA"
    assert alerta_limite["codigo_asignatura"] == "138650"
    assert alerta_limite["detalles"]["prerrequisito_codigo"] == "138649"
    assert alerta_limite["detalles"]["nota_obtenida"] == 11.0


def test_risk_alert_rezago_permanencia_rf15(client: TestClient):
    """Detecta alerta de permanencia si han transcurrido muchos semestres con pocos créditos (RF-15)."""
    # Ingresó en 2021-1 (han pasado más de 6 semestres a 2024-1)
    token = register_user(client, "20210001@up.edu.pe", ingreso="2021-1")
    headers = {"Authorization": f"Bearer {token}"}

    malla = client.get("/api/v1/curriculum/malla?carrera_id=1").json()
    by_code = {c["codigo"]: c for c in malla["cursos"]}
    asig_intro = by_code["170001"]

    # Solo tiene 1 curso de 4 créditos aprobado
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": asig_intro["id"],
        "periodo_academico": "2021-1",
        "estado": "APROBADA",
        "calificacion": 14.0,
        "numero_matricula": 1
    })

    res = client.get("/api/v1/curriculum/risks", headers=headers)
    assert res.status_code == 200
    alertas = res.json()

    alerta_rezago = next((a for a in alertas if a["tipo_alerta"] == "REZAGO_PERMANENCIA"), None)
    assert alerta_rezago is not None
    assert alerta_rezago["nivel_severidad"] == "CRITICA"
    assert alerta_rezago["detalles"]["semestres_transcurridos"] >= 6


def test_risk_alert_cuello_de_botella_rf16(client: TestClient):
    """Detecta y lista asignaturas pendientes catalogadas como cuello de botella (RF-16)."""
    token = register_user(client, "20230333@up.edu.pe", ingreso="2023-1")
    headers = {"Authorization": f"Bearer {token}"}

    # El estudiante nuevo no ha aprobado 138649 (Matemáticas I) ni 170002 (Herramientas de Programación)
    res = client.get("/api/v1/curriculum/risks", headers=headers)
    assert res.status_code == 200
    alertas = res.json()

    cuellos = [a for a in alertas if a["tipo_alerta"] == "CUELLO_DE_BOTELLA"]
    assert len(cuellos) >= 2
    codigos_cuello = [a["codigo_asignatura"] for a in cuellos]
    assert "138649" in codigos_cuello
    assert "170002" in codigos_cuello


def test_full_curriculum_evaluation_endpoint(client: TestClient):
    """Prueba el endpoint consolidado /curriculum/evaluate."""
    token = register_user(client, "20230444@up.edu.pe", ingreso="2023-1")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/curriculum/evaluate", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "recomendacion_matricula" in data
    assert "alertas_riesgo" in data
    assert "resumen_alertas" in data
    assert data["recomendacion_matricula"]["creditos_totales_sugeridos"] > 0


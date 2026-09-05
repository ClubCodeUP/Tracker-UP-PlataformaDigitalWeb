"""
Suite de pruebas automatizadas para la API RESTful de Tracker UP (Auth, Perfil, Historial, Métricas).
"""
import pytest
from fastapi.testclient import TestClient


# -----------------------------------------------------------------------------
# 1. PRUEBAS DE AUTENTICACIÓN Y RESTRICCIÓN DE DOMINIO INSTITUCIONAL (RF-01)
# -----------------------------------------------------------------------------
def test_reject_non_institutional_email_on_register(client: TestClient):
    """Verifica el rechazo estricto de correos no institucionales."""
    payload = {
        "email": "estudiante@gmail.com",
        "password": "Password123!",
        "nombres": "Juan",
        "apellidos": "Perez",
        "carrera_id": 1,
        "periodo_ingreso": "2023-1"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "@up.edu.pe" in response.json()["detail"]


def test_reject_non_institutional_email_on_login(client: TestClient):
    """Verifica que el login tampoco admita dominios externos."""
    response = client.post("/api/v1/auth/login", json={
        "email": "hacker@yahoo.com",
        "password": "Password123!"
    })
    assert response.status_code == 400
    assert "@up.edu.pe" in response.json()["detail"]


def test_successful_registration_and_login_up(client: TestClient):
    """Registra y autentica a un estudiante con correo institucional UP."""
    register_payload = {
        "email": "20230145@up.edu.pe",
        "password": "MiClaveSegura2026",
        "nombres": "Carlos",
        "apellidos": "Gutiérrez Mendoza",
        "carrera_id": 1,
        "concentracion_id": 1,
        "periodo_ingreso": "2023-1"
    }
    reg_response = client.post("/api/v1/auth/register", json=register_payload)
    assert reg_response.status_code == 201
    data = reg_response.json()
    assert "access_token" in data
    assert data["email"] == "20230145@up.edu.pe"

    # Login con las mismas credenciales
    login_response = client.post("/api/v1/auth/login", json={
        "email": "20230145@up.edu.pe",
        "password": "MiClaveSegura2026"
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


# -----------------------------------------------------------------------------
# 2. PRUEBAS DE PERFIL DE ESTUDIANTE (RF-02)
# -----------------------------------------------------------------------------
def get_auth_token(client: TestClient) -> str:
    """Helper para registrar un usuario y obtener su token de autorización."""
    client.post("/api/v1/auth/register", json={
        "email": "20230999@up.edu.pe",
        "password": "Password123!",
        "nombres": "Ana",
        "apellidos": "Torres",
        "carrera_id": 1,
        "concentracion_id": 1,
        "periodo_ingreso": "2023-1"
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "20230999@up.edu.pe",
        "password": "Password123!"
    })
    return login_res.json()["access_token"]


def test_profile_endpoints(client: TestClient):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Consultar perfil
    get_res = client.get("/api/v1/profile/me", headers=headers)
    assert get_res.status_code == 200
    profile = get_res.json()
    assert profile["email"] == "20230999@up.edu.pe"
    assert profile["carrera_codigo"] == "INF"

    # 2. Actualizar perfil (cambio de concentración)
    put_res = client.put("/api/v1/profile/me", headers=headers, json={
        "concentracion_id": 2
    })
    assert put_res.status_code == 200
    assert put_res.json()["concentracion_id"] == 2


# -----------------------------------------------------------------------------
# 3. PRUEBAS DE HISTORIAL ACADÉMICO Y VALIDACIÓN DE NOTAS (RF-03, RF-07)
# -----------------------------------------------------------------------------
def test_history_crud_and_grade_validations(client: TestClient):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Registro inválido: Aprobada con nota menor a 11
    bad_res1 = client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 1,
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 10.5,
        "numero_matricula": 1
    })
    assert bad_res1.status_code == 422

    # 2. Registro inválido: EN_CURSO con calificación
    bad_res2 = client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 1,
        "periodo_academico": "2023-1",
        "estado": "EN_CURSO",
        "calificacion": 14.0,
        "numero_matricula": 1
    })
    assert bad_res2.status_code == 422

    # 3. Registro válido: Aprobada con 16.0
    ok_res = client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 1,  # MAT-1101 (4 créditos)
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 16.0,
        "numero_matricula": 1
    })
    assert ok_res.status_code == 201
    entry_id = ok_res.json()["id"]

    # 4. Listar historial
    list_res = client.get("/api/v1/history", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 5. Modificar registro
    put_res = client.put(f"/api/v1/history/{entry_id}", headers=headers, json={
        "calificacion": 17.0
    })
    assert put_res.status_code == 200
    assert put_res.json()["calificacion"] == 17.0

    # 6. Eliminar registro
    del_res = client.delete(f"/api/v1/history/{entry_id}", headers=headers)
    assert del_res.status_code == 204


# -----------------------------------------------------------------------------
# 4. PRUEBAS DEL SERVICIO DE CÁLCULO DINÁMICO DE MÉTRICAS (RF-04, RF-08)
# -----------------------------------------------------------------------------
def test_dynamic_metrics_calculation(client: TestClient):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Inicialmente: 0 créditos aprobados, 0% avance
    init_metrics = client.get("/api/v1/metrics/me", headers=headers).json()
    assert init_metrics["creditos_aprobados"] == 0.0
    assert init_metrics["porcentaje_avance"] == 0.0
    assert init_metrics["total_creditos_carrera"] == 205

    # Registrar 2 cursos aprobados del Ciclo 1:
    # Asignatura 1 (MAT-1101): 4 créditos con nota 15.0
    # Asignatura 2 (PRO-1101): 4 créditos con nota 17.0
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 1,
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 15.0,
        "numero_matricula": 1
    })
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 2,
        "periodo_academico": "2023-1",
        "estado": "APROBADA",
        "calificacion": 17.0,
        "numero_matricula": 1
    })

    # Registrar 1 curso en curso:
    # Asignatura 3 (COM-1101): 3 créditos
    client.post("/api/v1/history", headers=headers, json={
        "asignatura_id": 3,
        "periodo_academico": "2023-2",
        "estado": "EN_CURSO",
        "numero_matricula": 1
    })

    # Consultar métricas actualizadas
    metrics_res = client.get("/api/v1/metrics/me", headers=headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()

    assert metrics["creditos_aprobados"] == 8.0
    assert metrics["creditos_en_curso"] == 3.0
    assert metrics["creditos_pendientes"] == 197.0
    # Avance: 8 / 205 * 100 = 3.90%
    assert metrics["porcentaje_avance"] == 3.90
    assert metrics["promedio_ponderado"] == 16.0  # (15*4 + 17*4) / 8 = 16.0
    assert metrics["cursos_aprobados_count"] == 2
    assert metrics["cursos_en_curso_count"] == 1

"""
Pruebas para las nuevas funcionalidades v2:
- Benchmark de cohorte (comparativa dual: promoción y malla).
- Solicitudes de cambio de carrera y aprobación administrativa.
- Detalle de concentraciones y sus cursos.
"""
from fastapi.testclient import TestClient
from app.infrastructure.models.user_model import UsuarioModel, CarreraModel
from app.core.security import hash_password, create_access_token


def test_cohort_benchmark_endpoint(client: TestClient, db_session):
    # Crear usuario de prueba
    carrera = db_session.query(CarreraModel).first()
    user = UsuarioModel(
        email="benchmark_test@up.edu.pe",
        password_hash=hash_password("clave123"),
        nombres="Juan",
        apellidos="Pérez",
        carrera_id=carrera.id,
        periodo_ingreso="2023-1",
        rol="ESTUDIANTE",
        activo=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/metrics/cohort-benchmark", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "periodo_ingreso" in data
    assert "estudiante_creditos_aprobados" in data
    assert "cohorte_media_creditos" in data
    assert "malla_creditos_esperados" in data
    assert data["estado_ritmo"] in ["ADELANTADO", "AL_DIA", "EN_PROGRESO"]
    assert len(data["recomendacion_constructiva"]) > 0


def test_career_concentrations_detail(client: TestClient, db_session):
    carrera = db_session.query(CarreraModel).first()
    response = client.get(f"/api/v1/curriculum/careers/{carrera.id}/concentrations")
    assert response.status_code == 200
    data = response.json()
    assert "concentraciones" in data
    assert "carrera_id" in data


def test_career_change_request_flow(client: TestClient, db_session):
    carreras = db_session.query(CarreraModel).limit(2).all()
    if len(carreras) < 2:
        return

    c1, c2 = carreras[0], carreras[1]

    # Crear estudiante
    student = UsuarioModel(
        email="estudiante_cambio@up.edu.pe",
        password_hash=hash_password("clave123"),
        nombres="Ana",
        apellidos="Torres",
        carrera_id=c1.id,
        periodo_ingreso="2023-1",
        rol="ESTUDIANTE",
        activo=True
    )
    # Crear admin
    admin = UsuarioModel(
        email="admin_test_flow@up.edu.pe",
        password_hash=hash_password("admin123"),
        nombres="Admin",
        apellidos="Central",
        carrera_id=c1.id,
        periodo_ingreso="2020-1",
        rol="ADMIN",
        activo=True
    )
    db_session.add_all([student, admin])
    db_session.commit()
    db_session.refresh(student)
    db_session.refresh(admin)

    student_token = create_access_token(student.id)
    admin_token = create_access_token(admin.id)

    # 1. Estudiante solicita cambio a c2
    req_resp = client.post(
        "/api/v1/profile/career-change-request",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"carrera_destino_id": c2.id, "motivo": "Interés en la especialidad técnica."}
    )
    assert req_resp.status_code == 200
    req_data = req_resp.json()
    assert req_data["estado"] == "PENDIENTE"
    req_id = req_data["id"]

    # 2. Admin lista solicitudes
    admin_list = client.get(
        "/api/v1/admin/career-requests",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_list.status_code == 200
    assert any(r["id"] == req_id for r in admin_list.json())

    # 3. Admin aprueba la solicitud
    approve_resp = client.post(
        f"/api/v1/admin/career-requests/{req_id}/action",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"accion": "APROBAR", "respuesta_admin": "Aprobado según vacantes disponibles."}
    )
    assert approve_resp.status_code == 200
    assert approve_resp.json()["estado"] == "APROBADA"

    # 4. Verificar que el estudiante ahora tiene c2.id
    db_session.refresh(student)
    assert student.carrera_id == c2.id

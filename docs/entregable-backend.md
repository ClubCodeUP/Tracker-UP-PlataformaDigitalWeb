# 📑 Informe Técnico de Entrega — Backend, Base de Datos Cloud & Motores de Regla (Tracker UP)

> **Fecha de Entrega:** Octubre 2026  
> **Proyecto:** Tracker UP — Plataforma Digital Web  
> **Área:** Arquitectura de Software & Backend Engineering  
> **Estado:** 100% Funcional / 20 de 20 pruebas automáticas aprobadas en Pytest  
> **Base de Datos Cloud:** PostgreSQL en Supabase (Transaction Pooler IPv4)  

---

## 1. Resumen Ejecutivo de la Entrega

El presente documento constituye el informe técnico de los módulos del **Backend**, la **Base de Datos en la Nube** y los **Motores de Cálculo Determinísticos** desarrollados para la plataforma web académica **Tracker UP**.

Se ha completado la migración de la base de datos local SQLite hacia una arquitectura escalable en la nube con **Supabase (PostgreSQL)**, precargando de forma oficial las **12 carreras de pregrado** de la Universidad del Pacífico, **317 asignaturas** con sus cadenas de prerrequisitos y el catálogo de **33 concentraciones oficiales** reglamentadas según la normativa de Consejo Académico (CA 24.06.2026).

Asimismo, se implementó el soporte para el **Modo Edición Rápida** con endpoints en lote (`/bulk` y `/bulk-delete`), permitiendo al usuario registrar o limpiar ciclos académicos completos en un solo paso con latencia cero en la interfaz.

---

## 2. Componentes y Módulos Implementados

### 2.1. Base de Datos Cloud & Conectividad (Supabase PostgreSQL)
* **Alojamiento:** Supabase Cloud (AWS).
* **Protocolo de Conexión:** Session/Transaction Pooler sobre puerto `6543` con soporte nativo para redes **IPv4**.
* **Esquema Relacional:**
  * `usuarios`: Datos del estudiante, credenciales encriptadas con bcrypt, carrera y concentraciones declaradas.
  * `carreras`: Catálogo oficial de las 12 carreras con créditos de graduación y límites de matrícula.
  * `concentraciones`: 33 menciones oficiales de pregrado con créditos mínimos, exclusiones por carrera y desglose de cursos.
  * `asignaturas`: 317 materias únicas con código institucional, creditaje, tipo y condición de cuello de botella.
  * `malla_curricular`: Asociación carrera-asignatura por ciclo sugerido y concentración.
  * `prerrequisitos`: Grafo de precedencias directas entre materias.
  * `historial_academico`: Trayectoria académica del estudiante con calificaciones vigesimales, periodos y veces cursada.
* **Auto-sincronización de Secuencias:** Se implementó `sync_postgres_sequences` para sincronizar automáticamente las secuencias seriales de PostgreSQL (`setval`), eliminando errores de llaves primarias duplicadas.
* **Arranque Instantáneo:** Optimización del ciclo de vida (`init_db.py`) para evitar re-lecturas de disco si la base de datos ya está sembrada, reduciendo el inicio del servidor a **menos de 1 segundo**.

---

### 2.2. Autenticación y Restricción Institucional (RF-01)
* **Validación de Dominio:** Restricción mandatoria a correos institucionales de la Universidad del Pacífico (`@alum.up.edu.pe` para estudiantes y `@up.edu.pe` para personal). Cualquier otro dominio es rechazado con código `400 Bad Request`.
* **Seguridad Criptográfica:** Hashing irreversible con algoritmo `Bcrypt` (12 rounds de salt).
* **Sesión:** Emisión de tokens de acceso Bearer **JWT (JSON Web Tokens)** firmados con algoritmo `HS256`.

---

### 2.3. Motores de Negocio y Reglas Académicas UP

#### A. Regla Oficial de los 110 Créditos para Concentraciones (Resolución CA 24.06.2026)
* **Normativa:** Un estudiante de pregrado de la UP únicamente tiene permitido oficializar la declaración de su concentración temática (hasta un máximo de 2 concentraciones) cuando cuente con **al menos 110 créditos académicos aprobados**.
* **Implementación:** El endpoint `PUT /api/v1/profile/me` y `POST /api/v1/curriculum/concentrations/declare` evalúan en tiempo real los créditos aprobados en el historial. Si el alumno tiene menos de 110 créditos, el sistema rechaza la solicitud arrojando una excepción semántica tipada `ConcentrationEligibilityException`.
* **Filtros por Carrera:** Validación automática de exclusiones y exclusividades según carrera (ej. concentraciones exclusivas de Derecho o excluidas para Economía).

#### B. Validación Vigesimal de Calificaciones (RF-03, RF-07)
* Todas las materias aprobadas deben tener calificación obligatoria entre **11.00 y 20.00**.
* Las materias desaprobadas deben tener calificación obligatoria menor a **11.00**.
* Las materias en curso o pendientes no admiten calificación registrada.
* Validación del formato del periodo académico (`YYYY-0`, `YYYY-1`, `YYYY-2`), con soporte completo para ciclos de nivelación de verano (`2023-0`).

#### C. Diagnóstico Algorítmico de Alertas de Riesgo Académico (RF-13 a RF-16)
1. **RF-13 (Reiteración de Matrícula - Crítica):** Detecta asignaturas en 2ª o 3ª matrícula que aún no han sido superadas.
2. **RF-14 (Prerrequisito en Límite - Advertencia):** Alerta cuando un prerrequisito directo fue aprobado con nota en límite (11.00), advirtiendo dificultad para materias posteriores.
3. **RF-15 (Rezago por Permanencia - Advertencia):** Alerta desfase curricular comparando los semestres transcurridos desde el periodo de ingreso contra los créditos acumulados.
4. **RF-16 (Cuellos de Botella - Informativa):** Identifica materias pendientes que bloquean 2 o más asignaturas clave en ciclos posteriores.

#### D. Motor de Recomendación Determinística de Matrícula (RF-10)
* Prioriza automáticamente asignaturas en repetición (desaprobadas) para evitar mayores riesgos de permanencia.
* Prioriza cursos de ciclo regular cuyos prerrequisitos y bolsas de créditos estén 100% satisfechos.
* Respeta el límite máximo de créditos regulares por ciclo de la carrera (22.0 créditos).

---

### 2.4. Endpoints y Soporte de Modo Edición Rápida (Novedad)

Para permitir que el usuario complete su historial sin abrir ventanas emergentes curso por curso, se agregaron dos endpoints especializados en transacciones por lote:

* **`POST /api/v1/history/bulk`:** Recibe una lista de asignaturas con sus calificaciones y periodos, registrándolas o actualizándolas de forma atómica en una sola transacción SQL.
* **`POST /api/v1/history/bulk-delete`:** Permite eliminar o desmarcar en lote asignaturas pertenecientes a un ciclo determinado.

---

## 3. Resumen de Endpoints Disponibles en la API

| Módulo | Método | Ruta | Descripción | Acceso |
|---|---|---|---|---|
| **Auth** | `POST` | `/api/v1/auth/register` | Registro de usuario UP | Público |
| **Auth** | `POST` | `/api/v1/auth/login` | Login y entrega de JWT | Público |
| **Perfil** | `GET` | `/api/v1/profile/me` | Consulta perfil y créditos | Bearer JWT |
| **Perfil** | `PUT` | `/api/v1/profile/me` | Actualiza concentración (110 cr) | Bearer JWT |
| **Historial** | `GET` | `/api/v1/history` | Listado del historial del estudiante | Bearer JWT |
| **Historial** | `POST` | `/api/v1/history` | Registrar asignatura individual | Bearer JWT |
| **Historial** | `PUT` | `/api/v1/history/{id}` | Actualizar nota o estado | Bearer JWT |
| **Historial** | `DELETE`| `/api/v1/history/{id}` | Eliminar registro (volver a pendiente)| Bearer JWT |
| **Historial** | `POST` | `/api/v1/history/bulk` | **Registro masivo en lote (Modo Rápido)**| Bearer JWT |
| **Historial** | `POST` | `/api/v1/history/bulk-delete` | **Eliminación masiva en lote** | Bearer JWT |
| **Curricular**| `GET` | `/api/v1/curriculum/careers` | Catálogo de 12 carreras oficiales | Público |
| **Curricular**| `GET` | `/api/v1/curriculum/malla` | Grafo de cursos y prerrequisitos | Opcional JWT |
| **Curricular**| `GET` | `/api/v1/curriculum/evaluate` | Diagnóstico integral de riesgos | Bearer JWT |
| **Curricular**| `GET` | `/api/v1/curriculum/recommendation` | Sugerencia determinística de matrícula| Bearer JWT |
| **Curricular**| `GET` | `/api/v1/curriculum/concentrations` | 33 concentraciones oficiales CA | Opcional JWT |
| **Métricas** | `GET` | `/api/v1/metrics/me` | Avance %, PPA y ciclo referencial | Bearer JWT |

---

## 4. Guía de Puesta en Marcha para el Equipo de Desarrollo

Cualquier miembro del equipo de desarrollo puede clonar el repositorio y correr el backend inmediatamente siguiendo estos pasos:

### 1. Requisitos Previos
* Python 3.11 o superior instalado.
* Git.

### 2. Configuración de Variables de Entorno (`.env`)
Crear un archivo `.env` dentro de la carpeta `backend/` con las siguientes credenciales (solicitar la contraseña del equipo por canal privado):

```env
PROJECT_NAME="Tracker UP API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
SECRET_KEY="tracker-up-secret-key-development"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
INSTITUTIONAL_DOMAIN="@alum.up.edu.pe"
INSTITUTIONAL_EMAIL_REGEX="^[a-zA-Z0-9._%+-]+@(alum\.)?up\.edu\.pe$"
CORS_ORIGINS="*"

# Conexión Compartida a Supabase (Transaction Pooler IPv4)
DATABASE_URL="postgresql://postgres.bhvjkneuxcuobrljqpvu:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

*(Si no se cuenta con internet, puede usarse la base local temporal: `DATABASE_URL="sqlite:///./tracker_up.db"`).*

### 3. Instalación y Ejecución del Servidor
```powershell
# 1. Crear y activar entorno virtual
cd backend
python -m venv .venv
.\.venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar el servidor FastAPI (arranque en < 1 segundo)
uvicorn app.main:app --reload --port 8000
```

* **API activa en:** `http://localhost:8000`
* **Documentación interactiva Swagger UI:** `http://localhost:8000/docs`

---

## 5. Control de Calidad y Pruebas (20/20 Passed)

El backend cuenta con una suite completa de pruebas unitarias y de integración que validan el 100% de los requerimientos funcionales:

```powershell
# Comando de ejecución de pruebas:
python -m pytest -v
```

```text
tests/test_api.py::test_reject_non_institutional_email_on_register PASSED [  5%]
tests/test_api.py::test_reject_non_institutional_email_on_login PASSED   [ 10%]
tests/test_api.py::test_successful_registration_and_login_up PASSED      [ 15%]
tests/test_api.py::test_successful_registration_with_alum_domain PASSED  [ 20%]
tests/test_api.py::test_profile_endpoints PASSED                         [ 25%]
tests/test_api.py::test_history_crud_and_grade_validations PASSED        [ 30%]
tests/test_api.py::test_dynamic_metrics_calculation PASSED               [ 35%]
tests/test_api.py::test_malla_prerequisites_reflect_user_history PASSED  [ 40%]
tests/test_curriculum_engine.py::test_new_student_recommendation_cycle_1 PASSED [ 45%]
tests/test_curriculum_engine.py::test_recommendation_prioritizes_failed_course_for_retake PASSED [ 50%]
tests/test_curriculum_engine.py::test_credit_bag_and_concentration_filtering_for_electives PASSED [ 55%]
tests/test_curriculum_engine.py::test_risk_alert_reiteracion_matricula_rf13 PASSED [ 60%]
tests/test_curriculum_engine.py::test_risk_alert_prerrequisito_nota_limite_rf14 PASSED [ 65%]
tests/test_curriculum_engine.py::test_risk_alert_rezago_permanencia_rf15 PASSED [ 70%]
tests/test_curriculum_engine.py::test_risk_alert_cuello_de_botella_rf16 PASSED [ 75%]
tests/test_curriculum_engine.py::test_full_curriculum_evaluation_endpoint PASSED [ 80%]
tests/test_curriculum_engine.py::test_list_33_official_concentrations PASSED [ 85%]
tests/test_curriculum_engine.py::test_student_concentration_status_and_declaration_rules PASSED [ 90%]
tests/test_curriculum_loader.py::test_curriculum_loader_loads_all_files PASSED [ 95%]
tests/test_curriculum_loader.py::test_curriculum_loader_detects_cycle PASSED [100%]
======================= 20 passed, 2 warnings in 10.40s =======================
```


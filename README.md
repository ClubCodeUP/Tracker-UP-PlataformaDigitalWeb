# Tracker UP — Plataforma Digital Web Académica

> **Plataforma web académica inteligente para el seguimiento del progreso universitario, visualización de flujogramas curriculares en grafos interactivos y prevención de riesgos de permanencia en la Universidad del Pacífico.**

---

## 📌 Resumen del Proyecto

Tracker UP es una solución de autoservicio para el estudiante universitario concebida originalmente durante la hackathon *Commit at 3 AM*. Centraliza la estructura oficial de las 12 carreras de la Universidad del Pacífico en un grafo interactivo de dependencias y prerrequisitos en tiempo real, permitiendo:

1. **Flujograma Curricular Reactivo:** Mallas oficiales organizadas por ciclos (desde Ciclo 0 de nivelaciones hasta graduación), con flechas de prerrequisito que se vuelven verdes conforme el estudiante aprueba materias.
2. **Ficha Técnica Lateral (Drawer):** Registro de calificaciones ($0.00$ a $20.00$), número de matrícula, validación de bolsas de crédito y verificación automática del cumplimiento de prerrequisitos directos.
3. **Métricas de Avance Progresivo:** Cálculo exacto del porcentaje de carrera completado, créditos acumulados y promedio ponderado acumulado (GPA).
4. **Motor Determinístico de Recomendación:** Propuesta automática de asignaturas para el próximo ciclo según prioridad de materias repetidas, cursos cuello de botella y límites de carga de créditos regular.
5. **Detección Temprana de Riesgos (RF-13 a RF-16):** Banners e insignias visuales para asignaturas en reiteración (2ª/3ª matrícula), materias cuello de botella y prerrequisitos aprobados en nota límite ($11.00$ a $11.50$).
6. **Autenticación Institucional Segura:** Restringida exclusivamente a estudiantes y miembros UP con dominio `@alum.up.edu.pe` o `@up.edu.pe`.

---

## 📚 Índice de Documentación Oficial

El repositorio cuenta con documentación exhaustiva para desarrolladores, diseñadores y administradores académicos:

| Documento | Enlace | Propósito y Contenido |
| :--- | :--- | :--- |
| **Informe de Entrega Backend** | [docs/entregable-backend.md](docs/entregable-backend.md) | **Entregable oficial:** Arquitectura técnica, conectividad a Supabase Cloud, reglas de 110 créditos, endpoints por lote y 20 tests. |
| **Alcance del MVP** | [docs/alcance-mvp.md](docs/alcance-mvp.md) | Definición formal del producto, requerimientos funcionales (RF-01 al RF-16), requerimientos no funcionales y exclusiones. |
| **Sistema de Diseño UI/UX** | [docs/ui-ux-design-system.md](docs/ui-ux-design-system.md) | **Guía para diseñadores y frontends:** Design tokens, paleta de colores, tipografía, anatomía de nodos, aristas del flujograma, ficha lateral y UX user flows. |
| **Mallas Curriculares Oficiales** | [backend/data/curricula/](backend/data/curricula/) | Archivos JSON fuente con el catálogo curricular oficial de las 12 carreras UP sincronizados con los PDFs institucionales en `docs/mallas/`. |

---

## 🛠️ Stack Tecnológico

### Frontend
* **Core:** React 19 + TypeScript 5.5 + Vite 6
* **Canvas Interactivo:** `@xyflow/react` (React Flow) con aristas *smoothstep* determinísticas
* **Estilos & Diseño:** Tailwind CSS 3.4
* **Iconografía:** Lucide React
* **Gestión de Estado:** React Hooks nativos (`useMemo`, `useCallback`, `useState`) de alto rendimiento ($< 50\text{ ms}$)

### Backend
* **Framework:** Python 3.11+ / FastAPI
* **ORM & Base de Datos:** SQLAlchemy 2.0 sobre **PostgreSQL en Supabase Cloud** (Transaction Pooler IPv4) con fallback a SQLite local
* **Seguridad:** JWT (OAuth2 Bearer) con encriptación de contraseñas mediante `passlib` / `bcrypt`
* **Validación de Esquemas:** Pydantic 2.10 y Pydantic Settings
* **Testing:** Pytest (20 pruebas unitarias y de integración pasando al 100%)

---

## 🚀 Puesta en Marcha en Entorno Local

### 1. Requisitos Previos
* Node.js 18+ y npm
* Python 3.11 o superior
* Git

### 2. Configurar y Ejecutar el Backend (FastAPI)
```powershell
# Ingresar a la carpeta backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Iniciar servidor FastAPI (arranque en < 1s, puerto 8000)
uvicorn app.main:app --reload --port 8000
```
* API disponible en: `http://localhost:8000`
* Documentación interactiva Swagger: `http://localhost:8000/docs`

### 3. Configurar y Ejecutar el Frontend (React + Vite)
```powershell
# En una nueva terminal, ingresar a la carpeta frontend
cd frontend
npm install
npm run dev
```
* Aplicación web disponible en: `http://localhost:3000`

---

## 🧪 Ejecución de Pruebas Automatizadas

```powershell
# 1. Pruebas Backend (20 pruebas: API, autenticación, concentraciones, métricas, bulk)
python -m pytest backend/tests

# 2. Verificación de Compilación y Tipos Frontend
cd frontend
npm run build
```

---

## 📂 Estructura General del Proyecto

```text
Tracker-UP-PlataformaDigitalWeb/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Endpoints REST (auth, profile, history, metrics, curriculum)
│   │   ├── core/            # Configuración, JWT, base de datos y cargador de mallas
│   │   ├── domain/          # Entidades y excepciones de negocio
│   │   ├── infrastructure/  # Modelos SQLAlchemy y repositorios de datos
│   │   ├── schemas/         # Esquemas Pydantic
│   │   └── services/        # Servicios de historial, métricas y motor de reglas
│   ├── data/curricula/      # Catálogo JSON oficial de las 12 mallas UP
│   └── tests/               # Suite completa de pruebas unitarias y de integración
├── docs/
│   ├── alcance-mvp.md       # Documento de alcance y requerimientos funcionales
│   ├── ui-ux-design-system.md # Sistema de diseño UI/UX y arquitectura frontend
│   └── mallas/              # PDFs oficiales de los planes de estudio UP
├── frontend/
│   ├── src/
│   │   ├── components/      # Componentes UI (Map, Drawer, Metrics, Auth, Alerts)
│   │   ├── hooks/           # useCurriculumMap (nodos y aristas dinámicos)
│   │   ├── services/        # trackerApi y cliente HTTP con JWT
│   │   └── types/           # Interfaces TypeScript de asignaturas e historial
│   └── index.html
├── tracker_up.db            # Base de datos SQLite persistente
└── README.md                # Entrada general del repositorio
```
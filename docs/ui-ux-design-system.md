# Sistema de Diseño UI/UX y Arquitectura Frontend — Tracker UP

Este documento constituye la especificación completa del **Sistema de Diseño (Design System)**, la **Arquitectura de Componentes** y los **Flujos de Interacción (UX)** de la plataforma **Tracker UP**. Está redactado para que cualquier diseñador UI/UX o desarrollador frontend pueda incorporarse al proyecto y continuar evolucionando la interfaz con total consistencia visual y técnica.

---

## 1. Filosofía de Diseño y Principios Rectores

* **Fricción Cognitiva Cero:** El estudiante universitario planifica momentos críticos de su vida académica (matrículas, créditos, riesgo de permanencia). La interfaz debe ser transparente, determinística y altamente legible, eliminando la ambigüedad en los prerrequisitos.
* **Jerarquía Académica Inmediata:** La información vital (código de asignatura, créditos, estado de aprobación y condición de cuello de botella) debe identificarse en menos de 200 ms con una rápida lectura visual.
* **Reactividad Visual en Cadena:** Toda acción en el récord académico (marcar un curso como aprobado) debe repercutir en tiempo real en las conexiones del flujograma (flechas verdes continuas), en la barra superior de avance y en las fichas técnicas de asignaturas dependientes.
* **Estética Institucional Moderna:** Combina tonos oscuros sobrios (`slate-950`, `slate-900`) con acentos profesionales institucionales (`blue-600`, `indigo-500`) y estados cromáticos de alto contraste accesibles bajo estándares WCAG AA.

---

## 2. Tokens de Diseño (Design Tokens)

### 2.1. Paleta de Colores y Estados Semánticos

| Rol de Color | Código Hex | Clases Tailwind | Significado / Uso |
| :--- | :--- | :--- | :--- |
| **Canvas / Fondo Principal** | `#020617` | `bg-slate-950` | Fondo general de la plataforma y lienzo del grafo. |
| **Superficie / Header** | `#0f172a` | `bg-slate-900` | Barra de navegación superior, cabeceras de cursos obligatorios y modales. |
| **Acento Institucional** | `#2563eb` | `bg-blue-600` / `text-blue-500` | Acciones principales, botones de confirmación, insignia de créditos. |
| **Estado: Aprobada** | `#10b981` | `bg-emerald-50`, `text-emerald-700`, `border-emerald-300` | Curso aprobado, flechas de dependencia cumplidas en el grafo, badges de éxito. |
| **Estado: En Curso** | `#f59e0b` | `bg-amber-50`, `text-amber-700`, `border-amber-300` | Asignatura en semestre activo actual, anillo ámbar en nodo. |
| **Estado: Desaprobada** | `#ef4444` | `bg-red-50`, `text-red-700`, `border-red-300` | Asignatura perdida en récord, anillo rojo y alerta de repetición. |
| **Estado: Pendiente** | `#94a3b8` | `bg-slate-100`, `text-slate-600`, `border-slate-200` | Materia por cursar a futuro; aristas grises animadas en grafo. |
| **Cuello de Botella** | `#ea580c` | `bg-orange-100`, `text-orange-700`, `border-orange-300` | Alerta de curso crítico con $\ge 2$ materias posteriores condicionadas. |
| **Curso Electivo** | `#7e22ce` | `bg-purple-900`, `border-purple-400`, `text-purple-100` | Cabecera y borde punteado distintivo para electivas de concentración. |

### 2.2. Tipografía

La aplicación utiliza la fuente nativa del sistema optimizada (`font-sans` / Inter style) y tipografía monoespaciada para identificadores:
* **Textos Generales:** `font-sans` (`text-xs`, `text-sm`, `text-base`, `text-xl`).
* **Códigos de Asignatura:** `font-mono font-bold` (ej. `120001`, `170131`) para evitar confusión entre caracteres alfanuméricos y acelerar la identificación de materias.
* **Métricas y Créditos:** `font-semibold` / `font-bold` con pesos `600` a `800`.

### 2.3. Iconografía (Lucide React)

Todos los íconos provienen de la biblioteca `lucide-react`:
* `CheckCircle2`: Aprobación de curso, prerrequisitos cumplidos, éxito al guardar.
* `Clock`: Curso en matrícula activa o prerrequisito en espera.
* `AlertTriangle`: Alerta de riesgo (reiteración de matrícula, prerrequisitos con nota límite).
* `Flame`: Materia identificada como cuello de botella curricular.
* `ShieldCheck`: Requisito de bolsa mínima de créditos aprobados.
* `BookOpen`: Estado pendiente por cursar.
* `Layers`: Ciclo académico sugerido.
* `Award`: Valor crediticio de la materia.
* `Sparkles`: Motor de recomendación determinística de matrícula.
* `ArrowRight`: Dirección del flujo de precedencia entre asignaturas.

---

## 3. Arquitectura de Componentes Frontend

El árbol de componentes se organiza bajo el principio de responsabilidad única en `frontend/src/`:

```text
frontend/src/
├── components/
│   ├── Alerts/
│   │   └── RiskAlertsBanner.tsx       # Banners de riesgo académico (RF-13, RF-14, RF-15)
│   ├── Auth/
│   │   └── AuthModal.tsx              # Modal de login/registro (@alum.up.edu.pe)
│   ├── Drawer/
│   │   └── CourseDetailDrawer.tsx     # Ficha técnica lateral interactiva (RF-07, RF-09)
│   ├── Header.tsx                     # Barra institucional con selector de carrera (RF-02)
│   ├── Map/
│   │   ├── CourseNode.tsx             # Nodo personalizado de asignatura en React Flow (RF-05)
│   │   ├── CurriculumMap.tsx          # Canvas principal de React Flow con controles
│   │   └── CycleHeader.tsx            # Cabeceras visuales fijas de ciclo (Ciclo 0 al 10)
│   ├── Metrics/
│   │   └── MetricsBar.tsx             # Barra superior de métricas, créditos y GPA (RF-04, RF-08)
│   └── Recommendation/
│       └── RecommendationModal.tsx    # Modal de propuesta determinística de matrícula (RF-10)
├── hooks/
│   └── useCurriculumMap.ts            # Layout determinístico de nodos, aristas y reactividad
├── services/
│   ├── apiClient.ts                   # Cliente HTTP base con inyección de JWT
│   └── trackerApi.ts                  # Métodos RESTful y fallback offline de mallas
├── types/
│   └── curriculum.ts                  # Interfaces TypeScript del modelo de dominio
├── App.tsx                            # Orquestador del estado global y montaje de vistas
└── index.css                          # Directivas Tailwind, estilos de React Flow y scrollbars
```

---

## 4. Especificación Detallada de Componentes Clave

### 4.1. Nodo de Asignatura (`CourseNode.tsx`)
Renderizado dentro del lienzo de React Flow para cada curso de la carrera:

* **Dimensiones fijas:** Ancho de `230px` con bordes redondeados `rounded-xl`.
* **Handle Conector:** Ubicado a la izquierda (`Position.Left`) para recibir flechas de prerrequisito, con efecto hover interactivo.
* **Cabecera de Tarjeta:**
  * **Obligatoria:** Fondo `bg-slate-900 text-white`, código monoespaciado en negrita y valor crediticio (`4 cr`).
  * **Electiva:** Fondo `bg-purple-900 text-white`, etiqueta `Electivo` y borde punteado violeta (`border-dashed border-purple-400`).
* **Cuerpo:**
  * Nombre del curso a 2 líneas (`line-clamp-2 min-h-[32px]`).
  * Badges de estado: `Aprobada (15.0)` en verde, `En curso` en ámbar, `Desaprobada` en rojo o `Pendiente` en gris.
  * Insignias de riesgo si aplican:
    * `Cuello (N)`: Fuego animado indicando cuántas materias desbloquea.
    * `2ª/3ª Matrícula`: Anillo rojo y badge de advertencia.
    * `Nota Límite`: Badge amarillo si se aprobó con $\le 11.50$.
* **Pie:** Ciclo sugerido y resumen rápido (`Sin prereq.` o `N prereq.`).

### 4.2. Aristas y Grafo de Dependencias (`useCurriculumMap.ts`)
* **Matriz de Coordenadas Determinística:**
  $$X = (\text{ciclo} - 1) \times 290\text{px} + 30\text{px}$$
  $$Y = (\text{índice en ciclo}) \times 170\text{px} + 80\text{px}$$
* **Estado de Conexiones (Aristas):**
  * **Prerrequisito Aprobado:** Trazo sólido verde esmeralda (`#10b981`), grosor `2.5px`, opacidad `0.95`, marcador de flecha cerrado verde y sin animación (`animated: false`).
  * **Prerrequisito Pendiente:** Trazo sutil gris pizarra (`#94a3b8`), grosor `1.5px`, opacidad `0.60`, con animación activa de flujo punteado (`animated: true`).

### 4.3. Ficha Técnica Lateral (`CourseDetailDrawer.tsx`)
Panel deslizante (*Slide-over Drawer*) desde el lateral derecho:
* **Fondo / Backdrop:** `bg-slate-900/40` con desenfoque de fondo moderno (`backdrop-blur-sm`).
* **Sección de Récord Académico:**
  * Selector de estado interactivo: `Aprobada`, `En Curso`, `Desaprobada`, `Pendiente`.
  * Input numérico validado para calificación ($0.00$ a $20.00$).
  * Contador de matrícula (1ª, 2ª o 3ª vez cursada).
  * Botón de guardado persistente con microinteracción de confirmación (`¡Guardado!`).
* **Sección de Prerrequisitos Directos:**
  * **Banner Dinámico de Validación:**
    * Si todos los prerrequisitos están aprobados: Banner verde con check indicando que el estudiante está habilitado para matricularse.
    * Si existen prerrequisitos pendientes: Banner ámbar de advertencia especificando las materias pendientes.
  * **Lista de Prerrequisitos:** Cada materia previa incluye código, nombre, y un badge independiente (`✓ Aprobado (16.0)` o `⏳ Pendiente`).
* **Requisito de Bolsa de Créditos:** Caja informativa azul cuando la materia exige un mínimo acumulado de créditos (ej. 100 créditos para prácticas preprofesionales).

### 4.4. Barra de Progreso y Métricas (`MetricsBar.tsx`)
Barra superior de control y analítica:
* **Porcentaje de Avance Progresivo:**
  * Computa avance porcentual incluso con materias de Ciclo 0 (nivelaciones de 0 créditos oficiales) dividiendo materias aprobadas entre el total de cursos.
  * Al aprobar materias con créditos, se pondera por el total de créditos de graduación (ej. 205 cr).
* **Tarjeta de Aprobados:** Muestra el conteo de materias completadas junto a los créditos (ej. `3 materias aprobadas (0 cr)`).
* **Promedio Ponderado Acumulado:** Calculado matemáticamente sobre los cursos calificados.
* **Botón CTA:** Acceso directo a la **Propuesta de Matrícula Inteligente**.

---

## 5. Flujos de Usuario (UX User Flows)

### Flujo 1: Exploración Pública (Visitante / Sin Cuenta)
1. El usuario ingresa a la plataforma.
2. Un banner informativo le da la bienvenida como visitante.
3. Puede navegar libremente por el selector de carreras (12 programas oficiales UP) y explorar cualquier flujograma con zoom y paneo interactivo.
4. Al hacer clic en una materia, se abre la ficha técnica en modo solo lectura. Si desea modificar notas, se le ofrece el botón de registro/login.

### Flujo 2: Registro e Inicio de Sesión
1. Modal institucional restringido a correos terminados en `@alum.up.edu.pe` o `@up.edu.pe`.
2. El estudiante selecciona su carrera al registrarse.
3. Al autenticarse, recibe un JWT seguro de 24 horas almacenado en `localStorage` (`tracker_up_token`).
4. La interfaz carga automáticamente su perfil, historial guardado y alertas de riesgo.

### Flujo 3: Actualización del Récord y Desbloqueo en Cadena
1. El estudiante hace clic en una asignatura (ej. `120000 Nivelación en Lenguaje`).
2. En la ficha técnica, marca el curso como `Aprobada` con nota `16.0` y presiona **"Actualizar en Mi Historial"**.
3. El frontend envía la solicitud al backend y sincroniza `tracker_up.db`.
4. De inmediato y sin recargar la página:
   * La barra superior incrementa el contador de materias aprobadas y el porcentaje.
   * En el flujograma, la flecha hacia `120001 Lenguaje I` pasa de gris punteada a **verde esmeralda sólida**.
   * Al abrir la ficha de `Lenguaje I`, el prerrequisito cambia de `Pendiente` a **`✓ Aprobado (16.0)`** y el banner se torna verde informando que está habilitado para cursarla.

---

## 6. Guía de Handoff para Desarrolladores y Diseñadores

### 6.1. Requisitos y Ejecución Local

**Requisitos:** Node.js 18+, Python 3.11+, Git.

1. **Clonar e instalar dependencias:**
   ```bash
   # Terminal Frontend
   cd frontend
   npm install
   npm run dev      # Corre en http://localhost:5173

   # Terminal Backend
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000   # Corre en http://localhost:8000
   ```

2. **Ejecutar Pruebas Automatizadas:**
   ```bash
   # Backend (18 pruebas unitarias de API y motor curricular)
   $env:PYTHONPATH="backend"; .\.venv\Scripts\python.exe -m pytest backend/tests

   # Frontend (Verificación de tipos TypeScript y empaquetado Vite)
   cd frontend
   npm run build
   ```

### 6.2. Dónde Realizar Modificaciones

* **Nuevos estilos visuales o animaciones:** Modificar `frontend/src/index.css` o agregar clases de utilidad de Tailwind en los componentes.
* **Diseño de los Nodos del Grafo:** Modificar `frontend/src/components/Map/CourseNode.tsx`.
* **Ficha Lateral:** Modificar `frontend/src/components/Drawer/CourseDetailDrawer.tsx`.
* **Reglas del Flujograma (espaciados, colores de aristas):** Ajustar la función generadora en `frontend/src/hooks/useCurriculumMap.ts`.
* **Mallas Curriculares Oficiales:** Se encuentran en `backend/data/curricula/*.json` y se sincronizan automáticamente con la base de datos `tracker_up.db`.

---

## 7. Oportunidades de Mejora UI/UX (Roadmap Recomendado)

Para el diseñador o frontend que tome la siguiente fase, se sugieren las siguientes optimizaciones de alta prioridad:

1. **Filtro Dinámico de Concentración en Pantalla:** Agregar una barra de píldoras (*chips*) para resaltar u ocultar asignaturas electivas según la concentración temática elegida.
2. **Exportación de Flujograma:** Permitir descargar el mapa curricular personalizado del alumno en formato PNG o PDF de alta resolución con su estado de avance.
3. **Modo Compacto / Modo Expandido:** Ofrecer un botón en el canvas para alternar entre tarjetas detalladas y tarjetas simplificadas (solo código y estado) para mallas muy densas.
4. **Modo Oscuro / Claro Toggle:** El sistema actual está optimizado para modo oscuro profundo (`slate-950`); añadir soporte formal para tema claro institucional.
5. **Drawer Adaptativo en Móviles:** En pantallas menores a `768px`, transformar el drawer lateral en un modal inferior deslizable (*bottom sheet*).

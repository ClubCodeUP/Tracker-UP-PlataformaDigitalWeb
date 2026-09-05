-- =============================================================================
-- PROYECTO: Tracker UP — Plataforma Digital Web
-- COMPONENTE: Arquitectura de Base de Datos Relacional (PostgreSQL 14+)
-- DOCUMENTO BASE: docs/alcance-mvp.md
-- AUTOR: Database Architect
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 0. LIMPIEZA TOTAL PREVIA (Idempotencia en entornos de desarrollo / CI)
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS v_alertas_academicas CASCADE;
DROP VIEW IF EXISTS v_resumen_curricular_estudiante CASCADE;
DROP TABLE IF EXISTS historial_academico CASCADE;
DROP TABLE IF EXISTS prerrequisitos CASCADE;
DROP TABLE IF EXISTS malla_curricular CASCADE;
DROP TABLE IF EXISTS asignaturas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS concentraciones CASCADE;
DROP TABLE IF EXISTS carreras CASCADE;

DROP TYPE IF EXISTS operador_logico_enum CASCADE;
DROP TYPE IF EXISTS estado_asignatura_enum CASCADE;
DROP TYPE IF EXISTS tipo_asignatura_enum CASCADE;
DROP TYPE IF EXISTS tipo_alerta_enum CASCADE;
DROP DOMAIN IF EXISTS email_institucional_up CASCADE;
DROP DOMAIN IF EXISTS nota_vigesimal CASCADE;

-- -----------------------------------------------------------------------------
-- 1. DOMINIOS Y TIPOS ENUMERADOS (Data Integrity & Type Safety)
-- -----------------------------------------------------------------------------

-- Dominio para correos institucionales de la Universidad del Pacífico (RF-01)
CREATE DOMAIN email_institucional_up AS VARCHAR(255)
    CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@up\.edu\.pe$');

-- Dominio para escala vigesimal peruana estándar (0.00 a 20.00)
CREATE DOMAIN nota_vigesimal AS NUMERIC(4, 2)
    CHECK (VALUE >= 0.00 AND VALUE <= 20.00);

-- Estados formales del curso en el ciclo de vida del estudiante (RF-07)
CREATE TYPE estado_asignatura_enum AS ENUM (
    'PENDIENTE',
    'EN_CURSO',
    'APROBADA',
    'DESAPROBADA'
);

-- Naturaleza de la asignatura dentro de la malla (RF-05)
CREATE TYPE tipo_asignatura_enum AS ENUM (
    'OBLIGATORIA',
    'ELECTIVA'
);

-- Operador de agrupación lógica para prerrequisitos concurrentes (AND / OR)
CREATE TYPE operador_logico_enum AS ENUM (
    'AND',
    'OR'
);

-- Tipología formal de alertas para el motor determinístico (RF-13, RF-14, RF-15, RF-16)
CREATE TYPE tipo_alerta_enum AS ENUM (
    'REITERACION_MATRICULA',     -- 2da o 3ra matrícula
    'PRERREQUISITO_NOTA_LIMITE', -- Prerrequisito aprobado con nota en límite (11.00)
    'REZAGO_PERMANENCIA',        -- Desfase entre semestres cursados y avance en créditos
    'CUELLO_DE_BOTELLA'          -- Curso crítico pendiente que bloquea múltiples materias
);

-- -----------------------------------------------------------------------------
-- 2. TABLAS MAESTRAS DEL PROGRAMA ACADÉMICO
-- -----------------------------------------------------------------------------

-- 2.1. Carreras Universitarias
CREATE TABLE carreras (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    total_creditos_graduacion INT NOT NULL CHECK (total_creditos_graduacion > 0),
    total_ciclos INT NOT NULL DEFAULT 10 CHECK (total_ciclos BETWEEN 8 AND 14),
    max_creditos_ciclo_regular NUMERIC(3, 1) NOT NULL DEFAULT 22.0 CHECK (max_creditos_ciclo_regular > 0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2.2. Concentraciones Temáticas (RF-02, RF-06)
CREATE TABLE concentraciones (
    id SERIAL PRIMARY KEY,
    carrera_id INT NOT NULL REFERENCES carreras(id) ON DELETE CASCADE,
    codigo VARCHAR(30) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_carrera_concentracion UNIQUE (carrera_id, codigo)
);

-- 2.3. Catálogo Normalizado de Asignaturas
CREATE TABLE asignaturas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    creditos NUMERIC(3, 1) NOT NULL CHECK (creditos > 0.0),
    tipo tipo_asignatura_enum NOT NULL DEFAULT 'OBLIGATORIA',
    es_cuello_botella BOOLEAN NOT NULL DEFAULT FALSE,
    descripcion TEXT,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 3. MALLA CURRICULAR Y CADENA DE PRERREQUISITOS LÓGICOS (RF-05, RF-09, RF-10)
-- -----------------------------------------------------------------------------

-- 3.1. Estructura de Malla Curricular por Carrera y Ciclos
CREATE TABLE malla_curricular (
    id SERIAL PRIMARY KEY,
    carrera_id INT NOT NULL REFERENCES carreras(id) ON DELETE CASCADE,
    asignatura_id INT NOT NULL REFERENCES asignaturas(id) ON DELETE RESTRICT,
    ciclo_sugerido INT NOT NULL CHECK (ciclo_sugerido BETWEEN 1 AND 14),
    concentracion_id INT REFERENCES concentraciones(id) ON DELETE SET NULL,
    creditos_minimos_requeridos NUMERIC(4, 1) NOT NULL DEFAULT 0.0 CHECK (creditos_minimos_requeridos >= 0.0),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_malla_carrera_asignatura UNIQUE (carrera_id, asignatura_id)
);

-- 3.2. Tabla de Asociación para la Cadena de Prerrequisitos Lógicos (RF-09, RF-10, RF-14)
-- Soporta grupos lógicos (ej: Grupo 1 AND Grupo 2; y dentro del grupo: Curso A OR Curso B)
CREATE TABLE prerrequisitos (
    id SERIAL PRIMARY KEY,
    asignatura_id INT NOT NULL REFERENCES asignaturas(id) ON DELETE CASCADE,
    prerrequisito_asignatura_id INT NOT NULL REFERENCES asignaturas(id) ON DELETE RESTRICT,
    grupo_logico INT NOT NULL DEFAULT 1 CHECK (grupo_logico > 0),
    operador_intra_grupo operador_logico_enum NOT NULL DEFAULT 'AND',
    nota_minima_aprobatoria nota_vigesimal NOT NULL DEFAULT 11.00,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_asignatura_prerrequisito UNIQUE (asignatura_id, prerrequisito_asignatura_id),
    CONSTRAINT chk_no_autoreferencia CHECK (asignatura_id <> prerrequisito_asignatura_id)
);

-- -----------------------------------------------------------------------------
-- 4. USUARIOS / ESTUDIANTES (RF-01, RF-02, CA-01)
-- -----------------------------------------------------------------------------
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    email email_institucional_up NOT NULL UNIQUE, -- Restricción vía DOMAIN a @up.edu.pe
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    carrera_id INT NOT NULL REFERENCES carreras(id) ON DELETE RESTRICT,
    concentracion_id INT REFERENCES concentraciones(id) ON DELETE SET NULL,
    periodo_ingreso VARCHAR(10) NOT NULL CHECK (periodo_ingreso ~* '^[0-9]{4}-(0|1|2)$'),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. HISTORIAL ACADÉMICO (RF-03, RF-07, RF-13, RF-14, CA-02)
-- -----------------------------------------------------------------------------
CREATE TABLE historial_academico (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    asignatura_id INT NOT NULL REFERENCES asignaturas(id) ON DELETE RESTRICT,
    periodo_academico VARCHAR(10) NOT NULL CHECK (periodo_academico ~* '^[0-9]{4}-(0|1|2)$'),
    estado estado_asignatura_enum NOT NULL DEFAULT 'PENDIENTE',
    calificacion nota_vigesimal,
    numero_matricula INT NOT NULL DEFAULT 1 CHECK (numero_matricula BETWEEN 1 AND 3),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- Una sola ocurrencia de matrícula por asignatura en un mismo periodo
    CONSTRAINT uq_usuario_asignatura_periodo UNIQUE (usuario_id, asignatura_id, periodo_academico),
    -- Integridad semántica estricta de calificaciones según estado del curso
    CONSTRAINT chk_consistencia_estado_nota CHECK (
        (estado IN ('PENDIENTE', 'EN_CURSO') AND calificacion IS NULL) OR
        (estado = 'APROBADA' AND calificacion >= 11.00) OR
        (estado = 'DESAPROBADA' AND calificacion < 11.00)
    )
);

-- -----------------------------------------------------------------------------
-- 6. ESTRATEGIA DE INDEXACIÓN (Optimización RNF-03: Renderizado < 3 segundos)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_malla_carrera_ciclo ON malla_curricular(carrera_id, ciclo_sugerido);
CREATE INDEX idx_malla_concentracion ON malla_curricular(concentracion_id) WHERE concentracion_id IS NOT NULL;
CREATE INDEX idx_prerrequisitos_asignatura ON prerrequisitos(asignatura_id);
CREATE INDEX idx_prerrequisitos_dependiente ON prerrequisitos(prerrequisito_asignatura_id);
CREATE INDEX idx_historial_estudiante_estado ON historial_academico(usuario_id, estado);
CREATE INDEX idx_historial_usuario_asignatura ON historial_academico(usuario_id, asignatura_id);

-- -----------------------------------------------------------------------------
-- 7. VISTAS ANALÍTICAS Y MOTOR DE REGLAS (RF-04, RF-08, RF-13, RF-14, RF-16)
-- -----------------------------------------------------------------------------

-- 7.1. Resumen Curricular Consolidado del Estudiante
CREATE OR REPLACE VIEW v_resumen_curricular_estudiante AS
SELECT 
    u.id AS usuario_id,
    u.email,
    u.nombres || ' ' || u.apellidos AS estudiante,
    c.codigo AS codigo_carrera,
    c.nombre AS carrera,
    c.total_creditos_graduacion,
    COALESCE(SUM(a.creditos) FILTER (WHERE h.estado = 'APROBADA'), 0.0) AS creditos_aprobados,
    ROUND(
        (COALESCE(SUM(a.creditos) FILTER (WHERE h.estado = 'APROBADA'), 0.0) / c.total_creditos_graduacion::NUMERIC) * 100, 
        2
    ) AS porcentaje_avance,
    COALESCE(MAX(m.ciclo_sugerido) FILTER (WHERE h.estado = 'APROBADA'), 1) AS ciclo_referencial
FROM usuarios u
JOIN carreras c ON u.carrera_id = c.id
LEFT JOIN historial_academico h ON u.id = h.usuario_id
LEFT JOIN asignaturas a ON h.asignatura_id = a.id
LEFT JOIN malla_curricular m ON m.carrera_id = u.carrera_id AND m.asignatura_id = a.id
GROUP BY u.id, u.email, u.nombres, u.apellidos, c.codigo, c.nombre, c.total_creditos_graduacion;

-- 7.2. Motor Determinístico de Alertas de Riesgo Curricular
CREATE OR REPLACE VIEW v_alertas_academicas AS
-- Alerta 1: Segunda o tercera matrícula (RF-13 - Severidad Crítica)
SELECT 
    h.usuario_id,
    'REITERACION_MATRICULA'::tipo_alerta_enum AS tipo_alerta,
    'CRITICA' AS nivel_severidad,
    a.codigo AS codigo_asignatura,
    a.nombre AS asignatura,
    'Asignatura en ' || h.numero_matricula || 'ª matrícula en el periodo ' || h.periodo_academico || '.' AS detalle_alerta
FROM historial_academico h
JOIN asignaturas a ON h.asignatura_id = a.id
WHERE h.numero_matricula >= 2 AND h.estado IN ('EN_CURSO', 'PENDIENTE', 'DESAPROBADA')

UNION ALL

-- Alerta 2: Prerrequisito aprobado con calificación en límite mínimo (11.00 - 11.50) (RF-14 - Severidad Advertencia)
SELECT 
    h_act.usuario_id,
    'PRERREQUISITO_NOTA_LIMITE'::tipo_alerta_enum AS tipo_alerta,
    'ADVERTENCIA' AS nivel_severidad,
    a_act.codigo AS codigo_asignatura,
    a_act.nombre AS asignatura,
    'Prerrequisito ' || a_pre.codigo || ' (' || a_pre.nombre || ') aprobado en límite con nota ' || h_pre.calificacion || '.' AS detalle_alerta
FROM historial_academico h_act
JOIN asignaturas a_act ON h_act.asignatura_id = a_act.id
JOIN prerrequisitos p ON p.asignatura_id = a_act.id
JOIN asignaturas a_pre ON p.prerrequisito_asignatura_id = a_pre.id
JOIN historial_academico h_pre ON h_pre.usuario_id = h_act.usuario_id 
     AND h_pre.asignatura_id = p.prerrequisito_asignatura_id 
     AND h_pre.estado = 'APROBADA'
WHERE h_act.estado IN ('EN_CURSO', 'PENDIENTE')
  AND h_pre.calificacion BETWEEN 11.00 AND 11.50

UNION ALL

-- Alerta 3: Asignaturas cuello de botella pendientes (RF-16 - Severidad Informativa/Prioritaria)
SELECT 
    u.id AS usuario_id,
    'CUELLO_DE_BOTELLA'::tipo_alerta_enum AS tipo_alerta,
    'ALERTA_ESTRUCTURAL' AS nivel_severidad,
    a.codigo AS codigo_asignatura,
    a.nombre AS asignatura,
    'Asignatura crítica cuello de botella aún no ha sido aprobada.' AS detalle_alerta
FROM usuarios u
JOIN malla_curricular m ON u.carrera_id = m.carrera_id
JOIN asignaturas a ON m.asignatura_id = a.id
WHERE a.es_cuello_botella = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM historial_academico h 
      WHERE h.usuario_id = u.id 
        AND h.asignatura_id = a.id 
        AND h.estado = 'APROBADA'
  );

-- -----------------------------------------------------------------------------
-- 8. DATOS SEMILLA REALES (Plan de Ingeniería de la Información - UP)
-- -----------------------------------------------------------------------------

-- 8.1. Carreras de Ingeniería
INSERT INTO carreras (id, codigo, nombre, total_creditos_graduacion, total_ciclos, max_creditos_ciclo_regular) VALUES
(1, 'INF', 'Ingeniería de la Información', 205, 10, 22.0),
(2, 'EMP', 'Ingeniería Empresarial', 205, 10, 22.0);

-- 8.2. Concentraciones Especializadas
INSERT INTO concentraciones (id, carrera_id, codigo, nombre, descripcion) VALUES
(1, 1, 'CONC-SWE', 'Ingeniería de Software y Sistemas Cloud', 'Arquitecturas distribuidas, desarrollo web/móvil y DevOps.'),
(2, 1, 'CONC-DS',  'Ciencia de Datos e Inteligencia Artificial', 'Modelado estadístico, machine learning y procesamiento big data.'),
(3, 2, 'CONC-BIZ', 'Gestión de Procesos y Transformación Digital', 'Optimización de procesos operativos, gobernanza y estrategia digital.');

-- 8.3. Asignaturas Reales (Malla Formativa de Ciclos 1 al 5 + Electivos)
INSERT INTO asignaturas (id, codigo, nombre, creditos, tipo, es_cuello_botella, descripcion) VALUES
-- Ciclo 1
(1,  'MAT-1101', 'Álgebra y Geometría Analítica', 4.0, 'OBLIGATORIA', FALSE, 'Matrices, sistemas de ecuaciones lineales y geometría analítica.'),
(2,  'PRO-1101', 'Fundamentos de Programación',   4.0, 'OBLIGATORIA', FALSE, 'Algoritmia estructurada, estructuras de control y funciones en Python.'),
(3,  'COM-1101', 'Comunicación Académica',        3.0, 'OBLIGATORIA', FALSE, 'Redacción académica, argumentación y lectura crítica.'),
(4,  'ADM-1101', 'Administración y Organizaciones',3.0, 'OBLIGATORIA', FALSE, 'Principios de teoría organizacional y dinámica de empresas.'),
(5,  'ECO-1101', 'Economía General',              4.0, 'OBLIGATORIA', FALSE, 'Fundamentos micro y macroeconómicos.'),
-- Ciclo 2
(6,  'MAT-1102', 'Cálculo Diferencial e Integral',4.0, 'OBLIGATORIA', FALSE, 'Límites, derivadas, integrales y aplicaciones prácticas.'),
(7,  'PRO-1102', 'Algoritmos y Estructuras Datos',4.0, 'OBLIGATORIA', TRUE,  'Estructuras de datos lineales/no lineales y OOP. Cuello de botella principal.'),
(8,  'EST-1101', 'Estadística y Probabilidades',  4.0, 'OBLIGATORIA', FALSE, 'Variables aleatorias, distribuciones y estadística descriptiva.'),
(9,  'CON-1101', 'Contabilidad Financiera',       3.0, 'OBLIGATORIA', FALSE, 'Estados financieros, balance general y costos.'),
-- Ciclo 3
(10, 'MAT-1103', 'Álgebra Lineal Computacional',  4.0, 'OBLIGATORIA', FALSE, 'Transformaciones lineales, autovalores y aplicaciones numéricas.'),
(11, 'BD-1101',  'Fundamentos de Bases de Datos', 4.0, 'OBLIGATORIA', TRUE,  'Modelo relacional, álgebra relacional y PostgreSQL. Cuello de botella.'),
(12, 'ARQ-1101', 'Arquitectura de Computadoras',  4.0, 'OBLIGATORIA', FALSE, 'Organización del procesador, ensamblador y memoria.'),
(13, 'EST-1102', 'Estadística Inferencial',       4.0, 'OBLIGATORIA', FALSE, 'Pruebas de hipótesis, intervalos de confianza y modelos lineales.'),
-- Ciclo 4
(14, 'SOF-1101', 'Ingeniería de Software I',      4.0, 'OBLIGATORIA', TRUE,  'Ciclos de vida ágiles, análisis de requerimientos y testing. Cuello de botella.'),
(15, 'BD-1102',  'Bases de Datos NoSQL y Big Data', 4.0, 'OBLIGATORIA', FALSE, 'Bases de datos documentales, clave-valor y pipelines distributed.'),
(16, 'RED-1101', 'Redes y Comunicaciones',        4.0, 'OBLIGATORIA', FALSE, 'Modelo OSI, TCP/IP, routing, switching y seguridad de red.'),
-- Ciclo 5 (Electivos de Concentración)
(17, 'ELE-SW01', 'Arquitecturas Cloud y DevOps',  4.0, 'ELECTIVA',    FALSE, 'Contenedores, CI/CD, kubernetes e infraestructura como código.'),
(18, 'ELE-DS01', 'Machine Learning Supervisado',  4.0, 'ELECTIVA',    FALSE, 'Modelos de clasificación, regresión y validación cruzada.');

-- 8.4. Malla Curricular
INSERT INTO malla_curricular (carrera_id, asignatura_id, ciclo_sugerido, concentracion_id, creditos_minimos_requeridos) VALUES
-- Ciclo 1 (18 créditos)
(1, 1,  1, NULL, 0.0),
(1, 2,  1, NULL, 0.0),
(1, 3,  1, NULL, 0.0),
(1, 4,  1, NULL, 0.0),
(1, 5,  1, NULL, 0.0),
-- Ciclo 2 (15 créditos)
(1, 6,  2, NULL, 0.0),
(1, 7,  2, NULL, 0.0),
(1, 8,  2, NULL, 0.0),
(1, 9,  2, NULL, 0.0),
-- Ciclo 3 (16 créditos)
(1, 10, 3, NULL, 0.0),
(1, 11, 3, NULL, 0.0),
(1, 12, 3, NULL, 0.0),
(1, 13, 3, NULL, 0.0),
-- Ciclo 4 (12 créditos obligatorios)
(1, 14, 4, NULL, 0.0),
(1, 15, 4, NULL, 0.0),
(1, 16, 4, NULL, 0.0),
-- Ciclo 5 (Electivos de especialidad con bolsa de 50 créditos mínimos requeridos)
(1, 17, 5, 1,    50.0), -- Concentración Software
(1, 18, 5, 2,    50.0); -- Concentración Data Science

-- 8.5. Cadena de Prerrequisitos Lógicos de Asignaturas
INSERT INTO prerrequisitos (asignatura_id, prerrequisito_asignatura_id, grupo_logico, operador_intra_grupo, nota_minima_aprobatoria) VALUES
-- Ciclo 2
(6,  1,  1, 'AND', 11.00), -- MAT-1102 requiere Álgebra y Geometría (1)
(7,  2,  1, 'AND', 11.00), -- PRO-1102 requiere Fundamentos de Programación (2)
(8,  1,  1, 'AND', 11.00), -- EST-1101 requiere Álgebra y Geometría (1)
(9,  4,  1, 'AND', 11.00), -- CON-1101 requiere Administración (4)
-- Ciclo 3
(10, 6,  1, 'AND', 11.00), -- MAT-1103 requiere Cálculo (6)
(11, 7,  1, 'AND', 11.00), -- BD-1101 requiere Estructuras de Datos (7)
(12, 7,  1, 'AND', 11.00), -- ARQ-1101 requiere Estructuras de Datos (7)
(13, 8,  1, 'AND', 11.00), -- EST-1102 requiere Estadística Descriptiva (8)
-- Ciclo 4
(14, 11, 1, 'AND', 11.00), -- SOF-1101 requiere Bases de Datos (11)
(15, 11, 1, 'AND', 11.00), -- BD-1102 requiere Bases de Datos (11)
(16, 12, 1, 'AND', 11.00), -- RED-1101 requiere Arquitectura de Computadoras (12)
-- Ciclo 5 (Electivos con prerrequisito técnico específico)
(17, 14, 1, 'AND', 11.00), -- Cloud/DevOps requiere Ingeniería de Software I (14)
(18, 13, 1, 'AND', 11.00); -- Machine Learning requiere Estadística Inferencial (13)

-- 8.6. Usuarios Semilla (Estudiantes UP con correos institucionales verificados)
INSERT INTO usuarios (id, email, nombres, apellidos, carrera_id, concentracion_id, periodo_ingreso) VALUES
(1, '20230145@up.edu.pe', 'Carlos', 'Gutiérrez Mendoza', 1, 1, '2023-1'),
(2, '20220892@up.edu.pe', 'Andrea', 'Morales Benavides', 1, 2, '2022-1');

-- 8.7. Historial Académico Semilla (Escenarios de prueba rigurosos)
-- Caso Estudiante 1: Carlos Gutiérrez (Avance regular sin contingencias)
INSERT INTO historial_academico (usuario_id, asignatura_id, periodo_academico, estado, calificacion, numero_matricula) VALUES
-- Periodo 2023-1 (Ciclo 1 completo aprobado)
(1, 1, '2023-1', 'APROBADA', 15.00, 1),
(1, 2, '2023-1', 'APROBADA', 17.50, 1),
(1, 3, '2023-1', 'APROBADA', 16.00, 1),
(1, 4, '2023-1', 'APROBADA', 14.00, 1),
(1, 5, '2023-1', 'APROBADA', 15.50, 1),
-- Periodo 2023-2 (Ciclo 2 completo aprobado)
(1, 6, '2023-2', 'APROBADA', 14.50, 1),
(1, 7, '2023-2', 'APROBADA', 16.00, 1),
(1, 8, '2023-2', 'APROBADA', 15.00, 1),
(1, 9, '2023-2', 'APROBADA', 14.00, 1),
-- Periodo actual 2024-1 (Ciclo 3 en curso)
(1, 10, '2024-1', 'EN_CURSO', NULL, 1),
(1, 11, '2024-1', 'EN_CURSO', NULL, 1),
(1, 12, '2024-1', 'EN_CURSO', NULL, 1),
(1, 13, '2024-1', 'EN_CURSO', NULL, 1);

-- Caso Estudiante 2: Andrea Morales (Escenario con disparadores de alerta RF-13, RF-14 y RF-16)
INSERT INTO historial_academico (usuario_id, asignatura_id, periodo_academico, estado, calificacion, numero_matricula) VALUES
-- Periodo 2022-1:
(2, 1, '2022-1', 'APROBADA', 11.00, 1), -- Nota límite aprobatoria (Detonante de alerta RF-14)
(2, 2, '2022-1', 'DESAPROBADA', 08.00, 1),
(2, 3, '2022-1', 'APROBADA', 13.00, 1),
(2, 4, '2022-1', 'APROBADA', 12.50, 1),
(2, 5, '2022-1', 'APROBADA', 11.50, 1),
-- Periodo 2022-2:
(2, 2, '2022-2', 'APROBADA', 12.00, 2), -- 2da matrícula superada
(2, 6, '2022-2', 'DESAPROBADA', 09.00, 1), -- Desaprobó Cálculo
-- Periodo actual 2023-1:
-- 1. Cálculo (6) cursándose en 2da matrícula -> Alerta RF-13 (Crítica)
-- 2. Estadística (8) cursándose teniendo prerrequisito MAT-1101 con nota 11.00 -> Alerta RF-14 (Advertencia)
-- 3. Cuellos de botella PRO-1102 (7), BD-1101 (11) y SOF-1101 (14) pendientes -> Alerta RF-16
(2, 6, '2023-1', 'EN_CURSO', NULL, 2),
(2, 8, '2023-1', 'EN_CURSO', NULL, 1);

-- -----------------------------------------------------------------------------
-- 9. AJUSTE Y SINCRONIZACIÓN DE SECUENCIAS
-- -----------------------------------------------------------------------------
SELECT setval('carreras_id_seq', (SELECT MAX(id) FROM carreras));
SELECT setval('concentraciones_id_seq', (SELECT MAX(id) FROM concentraciones));
SELECT setval('asignaturas_id_seq', (SELECT MAX(id) FROM asignaturas));
SELECT setval('malla_curricular_id_seq', (SELECT MAX(id) FROM malla_curricular));
SELECT setval('prerrequisitos_id_seq', (SELECT MAX(id) FROM prerrequisitos));
SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios));
SELECT setval('historial_academico_id_seq', (SELECT MAX(id) FROM historial_academico));

COMMIT;


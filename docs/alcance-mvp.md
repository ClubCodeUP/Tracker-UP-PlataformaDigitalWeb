# Alcance del MVP — Tracker UP

---

## 1. Contexto

Tracker UP es una plataforma web orientada a centralizar la información curricular universitaria en un mapa interactivo, facilitando el seguimiento del avance académico, la identificación de asignaturas pendientes y la prevención de riesgos curriculares.

La propuesta toma como base el concepto concebido por el equipo **Commit at 3 AM** durante una hackathon. Esta etapa formaliza su evolución dentro de la organización estudiantil bajo un alcance viable para el equipo actual y preservando la autoría original.

---

## 2. Objetivo del MVP

Entregar una versión funcional y autocontenida de Tracker UP centrada en el autoservicio del estudiante que permita:

1. Autenticación restringida a correo institucional.
2. Registro y gestión manual del historial académico: asignaturas, calificaciones, número de matrículas y periodo de ingreso.
3. Visualización del avance curricular mediante una malla interactiva estructurada por ciclos y concentraciones de electivos.
4. Generación de recomendaciones de matrícula basadas en reglas y restricciones de carga de créditos regular.
5. Detección visual de alertas de riesgo: asignaturas en segunda o tercera matrícula, prerrequisitos aprobados con baja calificación, asignaturas cuello de botella y rezago por permanencia.

El sistema operará de manera independiente, sin integraciones automáticas con sistemas institucionales en esta fase. El MVP está dirigido exclusivamente al alumno; el seguimiento institucional queda fuera de esta versión.

---

## 3. Rol de Usuario

* **Estudiante:** Registra su trayectoria académica, consulta su progreso en el mapa interactivo, selecciona su concentración y recibe alertas y sugerencias de matrícula.

---

## 4. Requerimientos Funcionales (RF)

Priorizados mediante metodología MoSCoW.

### 4.1. Autenticación y Perfil

| ID | Requerimiento | Prioridad |
| --- | --- | --- |
| **RF-01** | El sistema debe permitir el inicio de sesión restringiendo el acceso exclusivamente a cuentas de correo institucional. *El mecanismo exacto de validación queda pendiente de definir.* | **Must** |
| **RF-02** | El estudiante puede registrar y editar su información base: carrera, periodo de ingreso y concentración. | **Must** |
| **RF-03** | El estudiante puede registrar manualmente su historial de asignaturas: estado, calificación final y número de veces cursada. | **Must** |
| **RF-04** | El sistema presenta un resumen con métricas consolidadas: porcentaje de avance curricular, créditos acumulados y ciclo académico referencial. | **Must** |

### 4.2. Mapa Curricular Interactivo

| ID | Requerimiento | Prioridad |
| --- | --- | --- |
| **RF-05** | El sistema renderiza un mapa gráfico del plan de estudios organizado por ciclos, diferenciando visualmente cursos obligatorios y electivos. | **Must** |
| **RF-06** | El sistema permite filtrar las asignaturas electivas según la concentración temática elegida. | **Must** |
| **RF-07** | El estudiante puede actualizar el estado de cada asignatura entre aprobada, en curso o pendiente. | **Must** |
| **RF-08** | El sistema recalcula el porcentaje de avance general ante cualquier modificación en los estados de las asignaturas. | **Must** |
| **RF-09** | El sistema despliega una ficha técnica por asignatura que detalla código, créditos, concentración y requisitos de precedencia por materia o créditos acumulados. | **Should** |

### 4.3. Recomendaciones de Matrícula

| ID | Requerimiento | Prioridad |
| --- | --- | --- |
| **RF-10** | El sistema sugiere un bloque de asignaturas para el siguiente ciclo académico, validando prerrequisitos directos y bolsa mínima de créditos aprobados. | **Must** |
| **RF-11** | La propuesta de asignaturas se ajusta estrictamente al rango de créditos estándar permitido para un ciclo regular. | **Must** |
| **RF-12** | La selección de asignaturas sugeridas opera mediante un motor determinístico de reglas curriculares. | **Must** |

### 4.4. Alertas de Riesgo Académico

| ID | Requerimiento | Prioridad |
| --- | --- | --- |
| **RF-13** | El sistema emite una alerta crítica ante asignaturas registradas en segunda o tercera matrícula. | **Must** |
| **RF-14** | El sistema notifica cuando una asignatura cursada o proyectada dependa de un prerrequisito aprobado con calificación en el límite mínimo aprobatorio. | **Must** |
| **RF-15** | El sistema emite una alerta de permanencia ante una discrepancia crítica entre los periodos transcurridos desde el ingreso y los créditos acumulados. | **Must** |
| **RF-16** | El sistema resalta asignaturas pendientes catalogadas como cuello de botella por condicionar el avance de múltiples cursos posteriores. | **Should** |

---

## 5. Delimitación del Alcance (Out-of-Scope)

### 5.1. Roadmap a Futuro

* **Integración Directa con Sistemas Universitarios:** Conexión vía API o procesamiento de expedientes externos; la carga permanece manual en el MVP.
* **Modelos Predictivos y Procesamiento Avanzado:** Sugerencias basadas en analítica predictiva o interfaces conversacionales.

### 5.2. Exclusiones del Ciclo Actual

* Notificaciones externas por correo electrónico, mensajería instantánea o alertas push.
* Aplicación móvil nativa.
* Soporte multi-idioma.

---

## 6. Requerimientos No Funcionales (RNF)

| ID | Atributo | Especificación |
| --- | --- | --- |
| **RNF-01** | **Usabilidad** | Navegación intuitiva orientada a la carga de datos sin requerir documentación o inducción previa. |
| **RNF-02** | **Diseño Responsivo** | Adaptabilidad completa en navegadores de escritorio y dispositivos móviles. |
| **RNF-03** | **Rendimiento** | Tiempo de carga inicial del mapa curricular inferior a 3 segundos en pruebas locales. |
| **RNF-04** | **Seguridad** | Validación y persistencia de sesiones protegidas mediante tokens de autenticación. |
| **RNF-05** | **Mantenibilidad** | Código fuente estructurado modularmente y documentado en el repositorio central. |
| **RNF-06** | **Disponibilidad** | Despliegue en capas estándar de infraestructura para proyectos estudiantiles sin requerimiento de alta disponibilidad continua. |

---

## 7. Supuestos y Restricciones

* **Consistencia de Datos:** La exactitud de las proyecciones y alertas depende de la integridad de los datos ingresados manualmente por el estudiante.
* **Estructura Curricular Precargada:** La base de datos contará previamente con la malla curricular configurada: códigos, créditos, cadenas de prerrequisitos y concentraciones.
* **Plazo de Ejecución:** El ciclo de diseño, desarrollo y entrega del **proyecto completo** se estima en 2 a 3 meses.
* **Validación de Correo Institucional:** El mecanismo exacto para restringir el acceso a cuentas institucionales está pendiente de definir.

---

## 8. Criterios de Aceptación (CA)

* **CA-01:** El estudiante inicia sesión con una cuenta de correo institucional y configura su carrera, periodo de ingreso y concentración.
* **CA-02:** El estudiante registra su historial de asignaturas con sus respectivas calificaciones y número de matrículas.
* **CA-03:** El mapa curricular muestra los cursos diferenciando su estado y calcula el porcentaje de avance académico.
* **CA-04:** El sistema detalla los prerrequisitos directos y la bolsa mínima de créditos requerida al consultar una asignatura.
* **CA-05:** El sistema genera una recomendación de matrícula respetando los prerrequisitos cumplidos y los límites regulares de carga crediticia.
* **CA-06:** Se visualizan de forma diferenciada las alertas por matrícula reiterada, notas límite en prerrequisitos, cuellos de botella y rezago curricular.

---

## 9. Reconocimiento

Tracker UP se fundamenta en el proyecto desarrollado originalmente por el equipo **Commit at 3 AM** en el marco de una hackathon. Esta versión continúa su desarrollo adaptándola a las necesidades de la comunidad estudiantil y acreditando a sus creadores originales.
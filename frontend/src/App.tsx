import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MetricsBar } from './components/Metrics/MetricsBar';
import { RiskAlertsBanner } from './components/Alerts/RiskAlertsBanner';
import { CurriculumMap } from './components/Map/CurriculumMap';
import { CourseDetailDrawer } from './components/Drawer/CourseDetailDrawer';
import { RecommendationModal } from './components/Recommendation/RecommendationModal';
import { useCurriculumMap } from './hooks/useCurriculumMap';
import { DEFAULT_MALLA_UP, trackerApi } from './services/trackerApi';
import { AcademicMetrics, HistorialEntry, RiskAlert } from './types/curriculum';

export function App() {
  // Estados de datos
  const [metrics, setMetrics] = useState<AcademicMetrics>({
    usuario_id: 1,
    estudiante: 'Carlos Gutiérrez Mendoza',
    carrera: 'Ingeniería de la Información',
    total_creditos_carrera: 205,
    creditos_aprobados: 29.0,
    creditos_en_curso: 8.0,
    creditos_pendientes: 176.0,
    porcentaje_avance: 14.15,
    ciclo_referencial: 2,
    promedio_ponderado: 15.65,
    cursos_aprobados_count: 7,
    cursos_en_curso_count: 2,
    cursos_en_riesgo_count: 1,
  });

  // Historial semilla por defecto (Ciclo 1 completo + parte de Ciclo 2)
  const [historial] = useState<HistorialEntry[]>([
    { id: 1, asignaturaId: 1, periodo: '2023-1', estado: 'APROBADA', calificacion: 15.0, numeroMatricula: 1 },
    { id: 2, asignaturaId: 2, periodo: '2023-1', estado: 'APROBADA', calificacion: 16.0, numeroMatricula: 1 },
    { id: 3, asignaturaId: 3, periodo: '2023-1', estado: 'APROBADA', calificacion: 14.0, numeroMatricula: 1 },
    { id: 4, asignaturaId: 4, periodo: '2023-1', estado: 'APROBADA', calificacion: 14.0, numeroMatricula: 1 },
    { id: 5, asignaturaId: 5, periodo: '2023-1', estado: 'APROBADA', calificacion: 15.0, numeroMatricula: 1 },
    { id: 6, asignaturaId: 6, periodo: '2023-2', estado: 'EN_CURSO', calificacion: null, numeroMatricula: 2 }, // 2da matrícula
    { id: 7, asignaturaId: 7, periodo: '2023-2', estado: 'EN_CURSO', calificacion: null, numeroMatricula: 1 },
    { id: 8, asignaturaId: 8, periodo: '2023-2', estado: 'APROBADA', calificacion: 16.0, numeroMatricula: 1 },
    { id: 9, asignaturaId: 9, periodo: '2023-2', estado: 'APROBADA', calificacion: 14.0, numeroMatricula: 1 },
  ]);

  // Alertas semilla por defecto
  const [alertas, setAlertas] = useState<RiskAlert[]>([
    {
      tipo_alerta: 'REITERACION_MATRICULA',
      nivel_severidad: 'CRITICA',
      codigo_asignatura: 'MAT-1102',
      nombre_asignatura: 'Cálculo Diferencial e Integral',
      mensaje: 'Asignatura en 2ª matrícula en el periodo 2023-2. Riesgo reglamentario prioritario.',
      detalles: { numero_matricula: 2 },
    },
    {
      tipo_alerta: 'PRERREQUISITO_NOTA_LIMITE',
      nivel_severidad: 'ADVERTENCIA',
      codigo_asignatura: 'MAT-1102',
      nombre_asignatura: 'Cálculo Diferencial e Integral',
      mensaje: 'Depende de Álgebra y Geometría (MAT-1101), aprobada en el límite con 11.00/20.',
      detalles: { nota_obtenida: 11.0 },
    },
    {
      tipo_alerta: 'CUELLO_DE_BOTELLA',
      nivel_severidad: 'INFORMATIVA',
      codigo_asignatura: 'PRO-1102',
      nombre_asignatura: 'Algoritmos y Estructuras de Datos',
      mensaje: 'Materia crítica cuello de botella que condiciona 5 asignaturas posteriores.',
      detalles: { cursos_desbloqueados_count: 5 },
    },
    {
      tipo_alerta: 'CUELLO_DE_BOTELLA',
      nivel_severidad: 'INFORMATIVA',
      codigo_asignatura: 'BD-1101',
      nombre_asignatura: 'Fundamentos de Bases de Datos',
      mensaje: 'Cuello de botella pendiente que condiciona 3 asignaturas posteriores.',
      detalles: { cursos_desbloqueados_count: 3 },
    },
  ]);

  // Modal y Drawer states
  const [isRecommendationOpen, setIsRecommendationOpen] = useState(false);
  const [recommendationData, setRecommendationData] = useState<any>(null);

  // Intentar conectar con la API backend si está activa
  useEffect(() => {
    async function loadData() {
      try {
        const evalData = await trackerApi.getCurriculumEvaluation();
        if (evalData) {
          setAlertas(evalData.alertas_riesgo || []);
          setRecommendationData(evalData.recomendacion_matricula);
        }
        const metricsData = await trackerApi.getMetrics();
        if (metricsData) {
          setMetrics(metricsData);
        }
      } catch {
        // Modo autónomo/demostración con datos semilla precargados
      }
    }
    loadData();
  }, []);

  // Hook del Grafo React Flow
  const {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory,
  } = useCurriculumMap({
    malla: DEFAULT_MALLA_UP,
    historial,
    alertas,
  });

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* 1. Header institucional */}
      <Header
        studentName={metrics.estudiante}
        careerName={metrics.carrera}
        onOpenRecommendation={() => setIsRecommendationOpen(true)}
      />

      {/* 2. Barra de Métricas y Avance Curricular */}
      <MetricsBar metrics={metrics} />

      {/* 3. Banner Desplegable de Diagnóstico de Riesgos */}
      <RiskAlertsBanner alertas={alertas} />

      {/* 4. Mapa Curricular Interactivo (React Flow) */}
      <main className="flex-1 relative w-full h-full">
        <CurriculumMap nodes={nodes} edges={edges} maxCiclos={5} />
      </main>

      {/* 5. Panel Lateral con la Ficha Técnica de la Asignatura */}
      <CourseDetailDrawer
        asignatura={selectedCourse}
        historialEntry={selectedCourseHistory}
        onClose={() => setSelectedCourse(null)}
      />

      {/* 6. Modal de Sugerencia Determinística de Matrícula */}
      <RecommendationModal
        isOpen={isRecommendationOpen}
        onClose={() => setIsRecommendationOpen(false)}
        recommendationData={recommendationData}
      />
    </div>
  );
}

export default App;


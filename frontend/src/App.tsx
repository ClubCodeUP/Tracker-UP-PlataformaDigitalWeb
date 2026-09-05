import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { MetricsBar } from './components/Metrics/MetricsBar';
import { RiskAlertsBanner } from './components/Alerts/RiskAlertsBanner';
import { CurriculumMap } from './components/Map/CurriculumMap';
import { CourseDetailDrawer } from './components/Drawer/CourseDetailDrawer';
import { RecommendationModal } from './components/Recommendation/RecommendationModal';
import { AuthModal } from './components/Auth/AuthModal';
import { useCurriculumMap } from './hooks/useCurriculumMap';
import { trackerApi, CareerSummary, UserProfile } from './services/trackerApi';
import { Asignatura, AcademicMetrics, HistorialEntry, RiskAlert, EstadoAsignatura } from './types/curriculum';

const GUEST_METRICS: AcademicMetrics = {
  usuario_id: 0,
  estudiante: 'Visitante (Sin Iniciar Sesión)',
  carrera: 'Ingeniería de la Información',
  total_creditos_carrera: 205,
  creditos_aprobados: 0,
  creditos_en_curso: 0,
  creditos_pendientes: 205,
  porcentaje_avance: 0,
  ciclo_referencial: 1,
  promedio_ponderado: null,
  cursos_aprobados_count: 0,
  cursos_en_curso_count: 0,
  cursos_en_riesgo_count: 0,
};

export function App() {
  // Usuario autenticado
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);

  // Modal de autenticación
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'register'>('login');

  // Catálogo de carreras y carrera seleccionada
  const [careers, setCareers] = useState<CareerSummary[]>([]);
  const [selectedCareerId, setSelectedCareerId] = useState<number>(1);
  const [activeMalla, setActiveMalla] = useState<Asignatura[]>([]);

  // Datos académicos reales del usuario
  const [metrics, setMetrics] = useState<AcademicMetrics>(GUEST_METRICS);
  const [historial, setHistorial] = useState<HistorialEntry[]>([]);
  const [alertas, setAlertas] = useState<RiskAlert[]>([]);

  // Modales y Drawer
  const [isRecommendationOpen, setIsRecommendationOpen] = useState(false);
  const [recommendationData, setRecommendationData] = useState<any>(null);

  // Cargar datos académicos del estudiante autenticado
  const loadStudentData = useCallback(async () => {
    const token = localStorage.getItem('tracker_up_token');
    if (!token) {
      setHistorial([]);
      setAlertas([]);
      setRecommendationData(null);
      return;
    }

    try {
      const [metricsRes, evalRes, histRes] = await Promise.all([
        trackerApi.getMetrics().catch(() => null),
        trackerApi.getCurriculumEvaluation().catch(() => null),
        trackerApi.getHistory().catch(() => []),
      ]);

      if (metricsRes) {
        setMetrics(metricsRes);
      }
      if (evalRes) {
        setAlertas(evalRes.alertas_riesgo || []);
        setRecommendationData(evalRes.recomendacion_matricula);
      }
      if (histRes) {
        setHistorial(histRes);
      }
    } catch (err) {
      console.error('Error sincronizando datos del estudiante:', err);
    }
  }, []);

  // 1. Inicialización en el montaje: catálogo de carreras y verificación de sesión JWT
  useEffect(() => {
    async function init() {
      // Cargar lista oficial de carreras
      try {
        const list = await trackerApi.getCareers();
        if (list && list.length > 0) {
          setCareers(list);
        }
      } catch (e) {
        console.warn('No se pudo cargar catálogo de carreras:', e);
      }

      // Verificar si existe token guardado
      const token = localStorage.getItem('tracker_up_token');
      if (token) {
        try {
          const profile = await trackerApi.getProfile();
          if (profile) {
            setCurrentUser(profile);
            setSelectedCareerId(profile.carrera_id);
            await loadStudentData();
            return;
          }
        } catch {
          // Token inválido o expirado
          trackerApi.logout();
          setCurrentUser(null);
        }
      }

      // Modo visitante inicial
      setCurrentUser(null);
      setHistorial([]);
      setAlertas([]);
    }

    init();
  }, [loadStudentData]);

  // 2. Cargar la malla curricular cuando cambia la carrera seleccionada
  useEffect(() => {
    async function loadMalla() {
      try {
        const mallaRes = await trackerApi.getMalla(selectedCareerId);
        if (mallaRes && mallaRes.cursos && mallaRes.cursos.length > 0) {
          setActiveMalla(mallaRes.cursos);
          if (mallaRes.carrera) {
            setMetrics((prev) => ({
              ...prev,
              carrera: mallaRes.carrera.nombre,
              total_creditos_carrera: mallaRes.carrera.total_creditos,
              creditos_pendientes: currentUser ? prev.creditos_pendientes : mallaRes.carrera.total_creditos,
            }));
          }
        }
      } catch (err) {
        console.error('Error al cargar la malla:', err);
      }
    }
    loadMalla();
  }, [selectedCareerId, currentUser]);

  // Manejo de Inicio de Sesión / Registro exitoso
  const handleAuthSuccess = async (profile: UserProfile) => {
    setCurrentUser(profile);
    setSelectedCareerId(profile.carrera_id);
    await loadStudentData();
  };

  // Manejo de Cierre de Sesión
  const handleLogout = () => {
    trackerApi.logout();
    setCurrentUser(null);
    setHistorial([]);
    setAlertas([]);
    setRecommendationData(null);
    const activeCareer = careers.find((c) => c.id === selectedCareerId);
    setMetrics({
      ...GUEST_METRICS,
      carrera: activeCareer?.nombre || 'Ingeniería de la Información',
      total_creditos_carrera: activeCareer?.total_creditos_graduacion || 205,
      creditos_pendientes: activeCareer?.total_creditos_graduacion || 205,
    });
  };

  // Manejo de actualización de estado de curso desde la Ficha Técnica
  const handleUpdateCourseState = async (
    asignaturaId: number,
    newState: EstadoAsignatura,
    calificacion?: number | null,
    numeroMatricula: number = 1
  ) => {
    if (!currentUser) {
      setAuthModalMode('login');
      setIsAuthModalOpen(true);
      return;
    }

    const existing = historial.find((h) => h.asignaturaId === asignaturaId);

    if (newState === 'PENDIENTE') {
      if (existing) {
        await trackerApi.deleteCourseHistory(existing.id);
      }
    } else {
      await trackerApi.saveCourseHistory({
        asignaturaId,
        periodo: existing?.periodo || `${new Date().getFullYear()}-1`,
        estado: newState,
        calificacion: calificacion ?? null,
        numeroMatricula: numeroMatricula || 1,
        existingHistoryId: existing?.id || null,
      });
    }

    // Refrescar analítica del estudiante tras el cambio
    await loadStudentData();
  };

  // Hook del Grafo React Flow
  const {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory,
  } = useCurriculumMap({
    malla: activeMalla,
    historial,
    alertas,
  });

  // Determinar máximo de ciclos para las cabeceras de columnas
  const maxCiclos = Math.max(5, ...activeMalla.map((c) => c.ciclo || 1));

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* 1. Header institucional con Selector de Carrera y Control de Usuarios */}
      <Header
        currentUser={currentUser}
        studentName={metrics.estudiante}
        careerName={metrics.carrera}
        careers={careers}
        selectedCareerId={selectedCareerId}
        onSelectCareer={setSelectedCareerId}
        onOpenRecommendation={() => {
          if (!currentUser) {
            setAuthModalMode('login');
            setIsAuthModalOpen(true);
          } else {
            setIsRecommendationOpen(true);
          }
        }}
        onOpenLogin={() => {
          setAuthModalMode('login');
          setIsAuthModalOpen(true);
        }}
        onOpenRegister={() => {
          setAuthModalMode('register');
          setIsAuthModalOpen(true);
        }}
        onLogout={handleLogout}
      />

      {/* Banner de Bienvenida si es visitante no autenticado */}
      {!currentUser && (
        <div className="bg-gradient-to-r from-blue-950/90 via-slate-900 to-indigo-950/90 border-b border-blue-800/30 px-6 py-2 flex items-center justify-between text-xs text-slate-300 select-none">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
            <span>
              <strong className="text-white">Modo Explorador:</strong> Estás visualizando la malla curricular pública. Para registrar tus notas, avance y alertas, inicia sesión o regístrate con tu correo UP.
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-4">
            <button
              onClick={() => {
                setAuthModalMode('login');
                setIsAuthModalOpen(true);
              }}
              className="px-2.5 py-1 text-slate-300 hover:text-white font-medium hover:underline text-xs"
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => {
                setAuthModalMode('register');
                setIsAuthModalOpen(true);
              }}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg shadow-sm transition-all text-xs"
            >
              Registrar Mi Cuenta
            </button>
          </div>
        </div>
      )}

      {/* 2. Barra de Métricas y Avance Curricular */}
      <MetricsBar metrics={metrics} />

      {/* 3. Banner Desplegable de Diagnóstico de Riesgos */}
      <RiskAlertsBanner alertas={alertas} />

      {/* 4. Mapa Curricular Interactivo (React Flow) */}
      <main className="flex-1 relative w-full h-full">
        <CurriculumMap nodes={nodes} edges={edges} maxCiclos={maxCiclos} />
      </main>

      {/* 5. Panel Lateral con la Ficha Técnica de la Asignatura */}
      <CourseDetailDrawer
        asignatura={selectedCourse}
        historialEntry={selectedCourseHistory}
        historial={historial}
        allCourses={activeMalla}
        isAuth={!!currentUser}
        onOpenAuth={() => {
          setAuthModalMode('login');
          setIsAuthModalOpen(true);
        }}
        onClose={() => setSelectedCourse(null)}
        onUpdateState={handleUpdateCourseState}
      />

      {/* 6. Modal de Sugerencia Determinística de Matrícula */}
      <RecommendationModal
        isOpen={isRecommendationOpen}
        onClose={() => setIsRecommendationOpen(false)}
        recommendationData={recommendationData}
      />

      {/* 7. Modal de Autenticación y Registro UP */}
      <AuthModal
        isOpen={isAuthModalOpen}
        initialMode={authModalMode}
        careers={careers}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}

export default App;

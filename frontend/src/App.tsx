import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { ActiveTab, NavbarTabs } from './components/Navigation/NavbarTabs';
import { DashboardView } from './components/Dashboard/DashboardView';
import { MetricsBar } from './components/Metrics/MetricsBar';
import { RiskAlertsBanner } from './components/Alerts/RiskAlertsBanner';
import { CurriculumMap } from './components/Map/CurriculumMap';
import { ConcentrationsView } from './components/Concentrations/ConcentrationsView';
import { ProjectionView } from './components/Projection/ProjectionView';
import { AdminPanelView } from './components/Admin/AdminPanelView';
import { CourseDetailDrawer } from './components/Drawer/CourseDetailDrawer';
import { RecommendationModal } from './components/Recommendation/RecommendationModal';
import { AuthModal } from './components/Auth/AuthModal';
import { ImportTranscriptModal } from './components/History/ImportTranscriptModal';
import { useCurriculumMap } from './hooks/useCurriculumMap';
import { trackerApi, CareerSummary, UserProfile, calculatePeriodForCycle } from './services/trackerApi';
import { Asignatura, AcademicMetrics, CohortBenchmark, HistorialEntry, RiskAlert, EstadoAsignatura } from './types/curriculum';

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
  // Pestaña activa
  const [activeTab, setActiveTab] = useState<ActiveTab>('dashboard');

  // Usuario autenticado
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);

  // Modal de autenticación
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalMode, setAuthModalMode] = useState<'login' | 'register'>('login');

  // Modo Edición Rápida (Opción 1)
  const [isQuickEditMode, setIsQuickEditMode] = useState(false);
  const [quickEditDefaultGrade, setQuickEditDefaultGrade] = useState(14);

  // Catálogo de carreras y carrera seleccionada
  const [careers, setCareers] = useState<CareerSummary[]>([]);
  const [selectedCareerId, setSelectedCareerId] = useState<number>(1);
  const [activeMalla, setActiveMalla] = useState<Asignatura[]>([]);

  // Datos académicos reales del usuario
  const [metrics, setMetrics] = useState<AcademicMetrics>(GUEST_METRICS);
  const [benchmark, setBenchmark] = useState<CohortBenchmark | null>(null);
  const [historial, setHistorial] = useState<HistorialEntry[]>([]);
  const [alertas, setAlertas] = useState<RiskAlert[]>([]);

  // Modal y Drawer
  const [isRecommendationModalOpen, setIsRecommendationModalOpen] = useState(false);
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);
  const [recommendationData, setRecommendationData] = useState<any>(null);

  // Cargar datos académicos del estudiante autenticado
  const loadStudentData = useCallback(async () => {
    const token = localStorage.getItem('tracker_up_token');
    if (!token) {
      setHistorial([]);
      setAlertas([]);
      setBenchmark(null);
      setRecommendationData(null);
      return;
    }

    try {
      const [metricsRes, evalRes, histRes, benchRes] = await Promise.all([
        trackerApi.getMetrics().catch(() => null),
        trackerApi.getCurriculumEvaluation().catch(() => null),
        trackerApi.getHistory().catch(() => []),
        trackerApi.getCohortBenchmark().catch(() => null),
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
      if (benchRes) {
        setBenchmark(benchRes);
      }
    } catch (err) {
      console.error('Error sincronizando datos del estudiante:', err);
    }
  }, []);

  // 1. Inicialización en el montaje: catálogo de carreras y verificación de sesión JWT
  useEffect(() => {
    async function init() {
      try {
        const list = await trackerApi.getCareers();
        if (list && list.length > 0) {
          setCareers(list);
        }
      } catch (e) {
        console.warn('No se pudo cargar catálogo de carreras:', e);
      }

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
          trackerApi.logout();
          setCurrentUser(null);
        }
      }

      setCurrentUser(null);
      setHistorial([]);
      setAlertas([]);
      setBenchmark(null);
      setActiveTab('map'); // Para visitante, iniciar directamente en el mapa
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
    setActiveTab('dashboard');
    await loadStudentData();
  };

  // Manejo de Cierre de Sesión
  const handleLogout = () => {
    trackerApi.logout();
    setCurrentUser(null);
    setHistorial([]);
    setAlertas([]);
    setBenchmark(null);
    setRecommendationData(null);
    setActiveTab('map');
    const activeCareer = careers.find((c) => c.id === selectedCareerId);
    setMetrics({
      ...GUEST_METRICS,
      carrera: activeCareer?.nombre || 'Ingeniería de la Información',
      total_creditos_carrera: activeCareer?.total_creditos_graduacion || 205,
      creditos_pendientes: activeCareer?.total_creditos_graduacion || 205,
    });
  };

  // Manejo de selección/cambio de concentración
  const handleSelectConcentration = async (concId: number | null) => {
    try {
      const updated = await trackerApi.updateProfile({ concentracion_id: concId });
      setCurrentUser(updated);
      await loadStudentData();
    } catch (err) {
      console.error('Error actualizando concentración:', err);
    }
  };

  // Manejo de actualización de estado de curso desde la Ficha Técnica
  const handleUpdateCourseState = async (
    asignaturaId: number,
    newState: EstadoAsignatura,
    calificacion?: number | null,
    numeroMatricula: number = 1,
    periodo?: string
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
      const course = activeMalla.find((c) => c.id === asignaturaId);
      const currentYear = new Date().getFullYear();
      const defaultPeriod = course?.ciclo === 0 ? `${currentYear}-0` : `${currentYear}-1`;

      await trackerApi.saveCourseHistory({
        asignaturaId,
        periodo: periodo || existing?.periodo || defaultPeriod,
        estado: newState,
        calificacion: calificacion ?? null,
        numeroMatricula: numeroMatricula || 1,
        existingHistoryId: existing?.id || null,
      });
    }

    await loadStudentData();
  };

  // Manejo de Aprobación/Desaprobación con 1 Clic (Modo Rápido)
  const handleQuickToggleCourse = async (asignatura: Asignatura) => {
    if (!currentUser) {
      setAuthModalMode('login');
      setIsAuthModalOpen(true);
      return;
    }

    const existing = historial.find((h) => h.asignaturaId === asignatura.id);
    const isCurrentlyApproved = existing?.estado === 'APROBADA';

    if (isCurrentlyApproved) {
      // Optimistic update: revertir a PENDIENTE (eliminar del historial)
      setHistorial((prev) => prev.filter((h) => h.asignaturaId !== asignatura.id));
      try {
        await trackerApi.deleteCourseHistory(existing.id);
        await loadStudentData();
      } catch (err) {
        console.error('Error desmarcando curso:', err);
        await loadStudentData();
      }
    } else {
      // Optimistic update: marcar como APROBADA
      const period =
        existing?.periodo ||
        calculatePeriodForCycle(currentUser.periodo_ingreso, asignatura.ciclo);

      const optimisticEntry: HistorialEntry = {
        id: existing?.id || -Date.now(),
        asignaturaId: asignatura.id,
        periodo: period,
        estado: 'APROBADA',
        calificacion: quickEditDefaultGrade,
        numeroMatricula: existing?.numeroMatricula || 1,
      };

      setHistorial((prev) => {
        const filtered = prev.filter((h) => h.asignaturaId !== asignatura.id);
        return [...filtered, optimisticEntry];
      });

      try {
        await trackerApi.saveCourseHistory({
          asignaturaId: asignatura.id,
          periodo: period,
          estado: 'APROBADA',
          calificacion: quickEditDefaultGrade,
          numeroMatricula: existing?.numeroMatricula || 1,
          existingHistoryId: existing?.id || null,
        });
        await loadStudentData();
      } catch (err) {
        console.error('Error aprobando curso en modo rápido:', err);
        await loadStudentData();
      }
    }
  };

  // Manejo de Aprobación de Todo un Ciclo en Lote
  const handleApproveCycle = async (ciclo: number) => {
    if (!currentUser) {
      setAuthModalMode('login');
      setIsAuthModalOpen(true);
      return;
    }

    const coursesInCycle = activeMalla.filter((c) => c.ciclo === ciclo);
    if (coursesInCycle.length === 0) return;

    const period = calculatePeriodForCycle(currentUser.periodo_ingreso, ciclo);

    // Optimistic update
    const newEntries: HistorialEntry[] = coursesInCycle.map((c) => {
      const existing = historial.find((h) => h.asignaturaId === c.id);
      return {
        id: existing?.id || -Date.now() - c.id,
        asignaturaId: c.id,
        periodo: period,
        estado: 'APROBADA',
        calificacion: quickEditDefaultGrade,
        numeroMatricula: existing?.numeroMatricula || 1,
      };
    });

    const courseIdsInCycle = new Set(coursesInCycle.map((c) => c.id));
    setHistorial((prev) => [
      ...prev.filter((h) => !courseIdsInCycle.has(h.asignaturaId)),
      ...newEntries,
    ]);

    try {
      await trackerApi.saveBulkCourseHistory(
        coursesInCycle.map((c) => ({
          asignatura_id: c.id,
          periodo_academico: period,
          estado: 'APROBADA',
          calificacion: quickEditDefaultGrade,
          numero_matricula: 1,
        }))
      );
      await loadStudentData();
    } catch (err) {
      console.error('Error aprobando ciclo en lote:', err);
      await loadStudentData();
    }
  };

  // Manejo de Limpiar Todo un Ciclo en Lote
  const handleClearCycle = async (ciclo: number) => {
    if (!currentUser) {
      setAuthModalMode('login');
      setIsAuthModalOpen(true);
      return;
    }

    const coursesInCycle = activeMalla.filter((c) => c.ciclo === ciclo);
    const courseIds = coursesInCycle.map((c) => c.id);

    // Optimistic update
    setHistorial((prev) => prev.filter((h) => !courseIds.includes(h.asignaturaId)));

    try {
      await trackerApi.deleteBulkCourseHistory(courseIds);
      await loadStudentData();
    } catch (err) {
      console.error('Error limpiando ciclo:', err);
      await loadStudentData();
    }
  };

  // Hook del Grafo React Flow
  const {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory,
    reloadBlockSelections,
  } = useCurriculumMap({
    malla: activeMalla,
    historial,
    alertas,
    isQuickEditMode,
    onQuickToggleCourse: handleQuickToggleCourse,
    selectedConcentrationId: currentUser?.concentracion_id || null,
  });

  const maxCiclos = Math.max(5, ...activeMalla.map((c) => c.ciclo || 1));
  const activeCareerObj = careers.find((c) => c.id === selectedCareerId);
  const activeCareerName = activeCareerObj?.nombre || metrics.carrera;

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-[#FBFBFE] font-sans text-slate-800">
      {/* 1. Header principal con Logo, Selector y Tabs */}
      <Header
        currentUser={currentUser}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        studentName={metrics.estudiante}
        careerName={metrics.carrera}
        careers={careers}
        selectedCareerId={selectedCareerId}
        onSelectCareer={setSelectedCareerId}
        isQuickEditMode={isQuickEditMode}
        onToggleQuickEdit={() => {
          const next = !isQuickEditMode;
          setIsQuickEditMode(next);
          if (next) setActiveTab('map');
        }}
        onOpenRecommendation={() => {
          if (!currentUser) {
            setAuthModalMode('login');
            setIsAuthModalOpen(true);
          } else {
            setIsRecommendationModalOpen(true);
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
        onOpenImportTranscript={() => {
          if (!currentUser) {
            setAuthModalMode('login');
            setIsAuthModalOpen(true);
            return;
          }
          setIsImportModalOpen(true);
        }}
      />

      {/* Tabs móviles/secundarios visibles en pantallas medianas o pequeñas */}
      <div className="md:hidden bg-white border-b border-violet-100 px-4 py-2 flex items-center justify-center">
        <NavbarTabs
          activeTab={activeTab}
          onTabChange={setActiveTab}
          isAdmin={currentUser?.rol === 'ADMIN'}
        />
      </div>

      {/* Banner de Bienvenida si es visitante no autenticado */}
      {!currentUser && (
        <div className="bg-gradient-to-r from-violet-50 via-white to-purple-50 border-b border-violet-100 px-6 py-2 flex items-center justify-between text-xs text-slate-600 select-none">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-violet-500 animate-ping" />
            <span>
              <strong className="text-violet-900">Modo Explorador:</strong> Visualizando la malla oficial pública. Inicia sesión para registrar tu historial de notas y acceder a la comparativa de cohorte.
            </span>
          </div>
          <div className="flex items-center gap-2 shrink-0 ml-4">
            <button
              onClick={() => {
                setAuthModalMode('login');
                setIsAuthModalOpen(true);
              }}
              className="px-2.5 py-1 text-slate-600 hover:text-violet-700 font-medium hover:underline text-xs"
            >
              Iniciar Sesión
            </button>
            <button
              onClick={() => {
                setAuthModalMode('register');
                setIsAuthModalOpen(true);
              }}
              className="px-3 py-1 bg-violet-600 hover:bg-violet-700 text-white font-bold rounded-xl shadow-sm text-xs"
            >
              Registrarse
            </button>
          </div>
        </div>
      )}

      {/* 2. Contenido Principal según la Pestaña Activa */}
      <div className="flex-1 relative w-full h-full overflow-hidden flex flex-col">
        {/* Pestaña: Dashboard / Inicio */}
        {activeTab === 'dashboard' && (
          <DashboardView
            currentUser={currentUser}
            metrics={metrics}
            benchmark={benchmark}
            malla={activeMalla}
            historial={historial}
            alertas={alertas}
            careers={careers}
            onNavigateToTab={setActiveTab}
            onRequestChangeCareerSuccess={loadStudentData}
          />
        )}

        {/* Pestaña: Mapa Académico */}
        {activeTab === 'map' && (
          <div className="flex-1 flex flex-col h-full w-full overflow-hidden">
            <MetricsBar metrics={metrics} />
            <RiskAlertsBanner alertas={alertas} />
            <main className="flex-1 relative w-full h-full">
              <CurriculumMap
                nodes={nodes}
                edges={edges}
                maxCiclos={maxCiclos}
                selectedConcentrationName={currentUser?.concentracion_nombre}
                isQuickEditMode={isQuickEditMode}
                onCloseQuickEdit={() => setIsQuickEditMode(false)}
                defaultGrade={quickEditDefaultGrade}
                onChangeDefaultGrade={setQuickEditDefaultGrade}
                allCourses={activeMalla}
                onApproveCycle={handleApproveCycle}
                onClearCycle={handleClearCycle}
                periodoIngreso={currentUser?.periodo_ingreso}
              />
            </main>
          </div>
        )}

        {/* Pestaña: Concentraciones */}
        {activeTab === 'concentrations' && (
          <ConcentrationsView
            currentUser={currentUser}
            careerId={selectedCareerId}
            careerName={activeCareerName}
            selectedConcentrationId={currentUser?.concentracion_id || null}
            onSelectConcentration={handleSelectConcentration}
            onNavigateToMap={() => setActiveTab('map')}
            onOpenLogin={() => {
              setAuthModalMode('login');
              setIsAuthModalOpen(true);
            }}
          />
        )}

        {/* Pestaña: Proyección */}
        {activeTab === 'projection' && (
          <ProjectionView
            recommendationData={recommendationData}
            malla={activeMalla}
            onNavigateToMap={() => setActiveTab('map')}
            onSelectCourse={(course) => setSelectedCourse(course)}
          />
        )}

        {/* Pestaña: Administración */}
        {activeTab === 'admin' && currentUser?.rol === 'ADMIN' && (
          <AdminPanelView />
        )}
      </div>

      {/* 3. Panel Lateral con la Ficha Técnica de la Asignatura */}
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

      {/* 4. Modal de Sugerencia Determinística (accesible si se requiere) */}
      <RecommendationModal
        isOpen={isRecommendationModalOpen}
        onClose={() => setIsRecommendationModalOpen(false)}
        recommendationData={recommendationData}
      />

      {/* 5. Modal de Autenticación y Registro UP */}
      <AuthModal
        isOpen={isAuthModalOpen}
        initialMode={authModalMode}
        careers={careers}
        onClose={() => setIsAuthModalOpen(false)}
        onSuccess={handleAuthSuccess}
      />

      {/* 6. Modal de Importación de Unofficial Transcript (PDF) */}
      <ImportTranscriptModal
        isOpen={isImportModalOpen}
        onClose={() => setIsImportModalOpen(false)}
        onImportSuccess={async () => {
          reloadBlockSelections();
          await loadStudentData();
        }}
      />
    </div>
  );
}

export default App;

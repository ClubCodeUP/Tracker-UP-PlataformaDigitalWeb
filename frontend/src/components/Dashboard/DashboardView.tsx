import React, { useState } from 'react';
import {
  TrendingUp,
  Award,
  BookOpen,
  Calendar,
  Sparkles,
  Users,
  Compass,
  ArrowRight,
  CheckCircle2,
  Clock,
  Layers,
  ArrowUpRight,
  GitBranch
} from 'lucide-react';
import { AcademicMetrics, CohortBenchmark, HistorialEntry, Asignatura, RiskAlert } from '../../types/curriculum';
import { CareerSummary, UserProfile, trackerApi } from '../../services/trackerApi';

interface DashboardViewProps {
  currentUser: UserProfile | null;
  metrics: AcademicMetrics;
  benchmark: CohortBenchmark | null;
  malla: Asignatura[];
  historial: HistorialEntry[];
  alertas: RiskAlert[];
  careers: CareerSummary[];
  onNavigateToTab: (tab: 'dashboard' | 'map' | 'concentrations' | 'projection' | 'admin') => void;
  onRequestChangeCareerSuccess?: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  currentUser,
  metrics,
  benchmark,
  malla,
  historial,
  alertas,
  careers,
  onNavigateToTab,
  onRequestChangeCareerSuccess,
}) => {
  const [isChangeCareerModalOpen, setIsChangeCareerModalOpen] = useState(false);
  const [selectedTargetCareer, setSelectedTargetCareer] = useState<number>(
    careers.find((c) => c.id !== currentUser?.carrera_id)?.id || 1
  );
  const [careerReason, setCareerReason] = useState('');
  const [submittingRequest, setSubmittingRequest] = useState(false);
  const [requestFeedback, setRequestFeedback] = useState<string | null>(null);

  // Cursos actualmente en curso
  const inProgressHistory = historial.filter((h) => h.estado === 'EN_CURSO');
  const inProgressCourses = inProgressHistory
    .map((h) => malla.find((c) => c.id === h.asignaturaId))
    .filter(Boolean) as Asignatura[];

  const handleCareerRequestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) return;
    setSubmittingRequest(true);
    setRequestFeedback(null);
    try {
      await trackerApi.requestCareerChange(selectedTargetCareer, careerReason);
      setRequestFeedback('¡Solicitud enviada con éxito! El personal de la universidad la evaluará.');
      setTimeout(() => {
        setIsChangeCareerModalOpen(false);
        setRequestFeedback(null);
        onRequestChangeCareerSuccess?.();
      }, 2000);
    } catch (err: any) {
      setRequestFeedback(err.message || 'No se pudo enviar la solicitud.');
    } finally {
      setSubmittingRequest(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#FBFBFE] px-6 py-8 text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* 1. Banner de Bienvenida y Perfil */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-violet-900 via-indigo-900 to-purple-900 text-white p-8 shadow-2xl shadow-purple-900/10">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-violet-200 text-xs font-semibold mb-3 border border-white/10">
                <Sparkles className="w-3.5 h-3.5 text-yellow-300" />
                <span>Periodo de Ingreso: {currentUser?.periodo_ingreso || '2023-1'}</span>
                {currentUser?.concentracion_nombre && (
                  <span className="bg-violet-500/50 px-2 py-0.5 rounded-full text-white">
                    🎯 {currentUser.concentracion_nombre}
                  </span>
                )}
              </div>
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
                Hola, {currentUser ? currentUser.nombres : 'Estudiante UP'} 👋
              </h2>
              <p className="text-sm text-violet-200 mt-1 max-w-2xl leading-relaxed">
                Bienvenido a tu panel de seguimiento curricular. Aquí podrás visualizar tu progreso integral, compararte con tu promoción y proyectar tu próxima matrícula.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => onNavigateToTab('map')}
                className="px-4 py-2.5 bg-white text-violet-900 font-bold rounded-2xl text-xs hover:bg-violet-50 shadow-lg shadow-black/10 transition-all flex items-center gap-2"
              >
                <Compass className="w-4 h-4 text-violet-700" />
                Explorar Mapa
              </button>
              {currentUser && (
                <button
                  onClick={() => setIsChangeCareerModalOpen(true)}
                  className="px-4 py-2.5 bg-white/15 hover:bg-white/20 text-white border border-white/20 font-semibold rounded-2xl text-xs transition-all flex items-center gap-2"
                >
                  <GitBranch className="w-4 h-4 text-violet-200" />
                  Cambio de Carrera
                </button>
              )}
            </div>
          </div>

          <div className="absolute -right-12 -bottom-12 w-64 h-64 rounded-full bg-violet-500/20 blur-3xl" />
        </div>

        {/* 2. Tarjetas de Métricas Clave */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-semibold">Avance Curricular</span>
              <div className="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center text-violet-600">
                <TrendingUp className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-black text-slate-900">
                {metrics.porcentaje_avance}%
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full mt-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-violet-600 to-purple-600 h-full rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, metrics.porcentaje_avance)}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-2">
                {metrics.creditos_aprobados} de {metrics.total_creditos_carrera} créditos
              </p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-semibold">Promedio Ponderado</span>
              <div className="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Award className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-black text-slate-900">
                {metrics.promedio_ponderado !== null && metrics.promedio_ponderado !== undefined
                  ? metrics.promedio_ponderado.toFixed(2)
                  : '—'}
              </div>
              <p className="text-[11px] text-emerald-600 font-semibold mt-2">
                Escala Vigesimal (0-20)
              </p>
              <p className="text-[11px] text-slate-500">
                {metrics.cursos_aprobados_count} asignaturas aprobadas
              </p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-semibold">Ciclo Referencial</span>
              <div className="w-8 h-8 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600">
                <Calendar className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-black text-slate-900">
                Ciclo {metrics.ciclo_referencial}
              </div>
              <p className="text-[11px] text-amber-600 font-semibold mt-2">
                Nivel Académico Actual
              </p>
              <p className="text-[11px] text-slate-500">
                {metrics.creditos_en_curso} cr. matriculados hoy
              </p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-500 mb-2">
              <span className="text-xs font-semibold">Créditos Restantes</span>
              <div className="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <BookOpen className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="text-2xl md:text-3xl font-black text-slate-900">
                {metrics.creditos_pendientes}
              </div>
              <p className="text-[11px] text-indigo-600 font-semibold mt-2">
                Para Graduación
              </p>
              <p className="text-[11px] text-slate-500">
                Meta: {metrics.total_creditos_carrera} créditos totales
              </p>
            </div>
          </div>
        </div>

        {/* 3. Indicador Comparativo Dual (Promoción Real + Malla Oficial) */}
        {benchmark && (
          <div className="bg-white rounded-3xl border border-violet-100 p-6 md:p-8 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Users className="w-5 h-5 text-violet-600" />
                  Comparativa de Rendimiento y Avance
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  Evaluación de tu trayectoria académica frente a tus compañeros de ingreso y frente a la malla oficial.
                </p>
              </div>

              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-violet-50 text-violet-700 font-bold text-xs rounded-xl border border-violet-200">
                <span className="w-2 h-2 rounded-full bg-violet-600" />
                <span>Estado: {benchmark.estado_ritmo}</span>
              </div>
            </div>

            {/* Dos Columnas Comparativas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Comparación 1: Tu Avance vs. Tu Promoción Real */}
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-3">
                    <span>👥 Frente a tu Promoción ({benchmark.periodo_ingreso})</span>
                    <span className="text-violet-600">{benchmark.cohorte_tamano} alumnos reg.</span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs text-slate-600 mb-1">
                        <span>Tus créditos aprobados:</span>
                        <strong className="text-slate-900">{benchmark.estudiante_creditos_aprobados} cr.</strong>
                      </div>
                      <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-violet-600 h-full rounded-full"
                          style={{ width: `${Math.min(100, benchmark.estudiante_porcentaje_avance)}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs text-slate-600 mb-1">
                        <span>Media de tu promoción:</span>
                        <strong className="text-slate-700">{benchmark.cohorte_media_creditos} cr.</strong>
                      </div>
                      <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-slate-400 h-full rounded-full"
                          style={{ width: `${Math.min(100, benchmark.cohorte_media_avance)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 text-xs">
                  {benchmark.diferencia_creditos_cohorte >= 0 ? (
                    <span className="text-emerald-700 font-semibold flex items-center gap-1">
                      <ArrowUpRight className="w-4 h-4" />
                      +{benchmark.diferencia_creditos_cohorte} créditos respecto a la media de tu cohorte.
                    </span>
                  ) : (
                    <span className="text-amber-700 font-semibold flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {Math.abs(benchmark.diferencia_creditos_cohorte)} créditos por debajo de la media de cohorte.
                    </span>
                  )}
                </div>
              </div>

              {/* Comparación 2: Tu Avance vs. Malla Oficial */}
              <div className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-xs font-bold text-slate-700 mb-3">
                    <span>📐 Frente al Plan de Estudios Oficial</span>
                    <span className="text-indigo-600">{benchmark.semestres_transcurridos} semestres cursados</span>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs text-slate-600 mb-1">
                        <span>Tus créditos aprobados:</span>
                        <strong className="text-slate-900">{benchmark.estudiante_creditos_aprobados} cr.</strong>
                      </div>
                      <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-indigo-600 h-full rounded-full"
                          style={{ width: `${Math.min(100, benchmark.estudiante_porcentaje_avance)}%` }}
                        />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-xs text-slate-600 mb-1">
                        <span>Trayectoria estándar sugerida:</span>
                        <strong className="text-slate-700">{benchmark.malla_creditos_esperados} cr.</strong>
                      </div>
                      <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-slate-400 h-full rounded-full"
                          style={{ width: `${Math.min(100, benchmark.malla_avance_esperado)}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 text-xs">
                  {benchmark.diferencia_creditos_malla >= 0 ? (
                    <span className="text-emerald-700 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4" />
                      Al día con el plan ({benchmark.diferencia_creditos_malla} cr. de holgura).
                    </span>
                  ) : (
                    <span className="text-amber-700 font-semibold flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      A {Math.abs(benchmark.diferencia_creditos_malla)} créditos del ritmo ideal sugerido.
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Diagnóstico en Lenguaje Positivo / Constructivo */}
            <div className="mt-6 p-4 rounded-2xl bg-gradient-to-r from-violet-50 to-indigo-50 border border-violet-100 flex items-start gap-3">
              <div className="w-8 h-8 rounded-xl bg-violet-600 text-white flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles className="w-4 h-4" />
              </div>
              <div className="text-xs">
                <h4 className="font-bold text-violet-950 mb-1">
                  {benchmark.mensaje_evaluacion}
                </h4>
                <p className="text-violet-800 leading-relaxed">
                  💡 <strong>Recomendación estratégica:</strong> {benchmark.recomendacion_constructiva}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 4. Cursos Matriculados Actualmente */}
        <div className="bg-white rounded-3xl border border-violet-100 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Clock className="w-4 h-4 text-indigo-600" />
                Asignaturas del Periodo Actual ({inProgressCourses.length})
              </h3>
              <p className="text-xs text-slate-500">
                Materias que estás cursando en este semestre académico.
              </p>
            </div>
            <button
              onClick={() => onNavigateToTab('map')}
              className="text-xs font-semibold text-violet-600 hover:text-violet-800 hover:underline flex items-center gap-1"
            >
              Ver en el mapa
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {inProgressCourses.length === 0 ? (
            <div className="text-center py-8 text-slate-400 text-xs">
              No tienes asignaturas registradas en estado "En curso".
              <br />
              <button
                onClick={() => onNavigateToTab('map')}
                className="mt-2 text-violet-600 font-semibold hover:underline"
              >
                Ir al mapa curricular para seleccionarlas
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {inProgressCourses.map((c) => (
                <div
                  key={c.id}
                  className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-[11px] text-slate-500 mb-1">
                      <span className="font-mono font-bold text-slate-700">{c.codigo}</span>
                      <span className="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-medium">
                        {c.creditos} cr
                      </span>
                    </div>
                    <h5 className="text-xs font-bold text-slate-800 line-clamp-2">
                      {c.nombre}
                    </h5>
                  </div>
                  <div className="mt-2 pt-2 border-t border-slate-200 flex items-center justify-between text-[10px] text-slate-500">
                    <span className="flex items-center gap-1">
                      <Layers className="w-3 h-3 text-slate-400" />
                      Ciclo {c.ciclo}
                    </span>
                    <span className="font-semibold text-indigo-600">En curso</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 5. Alertas Prioritarias en Positivo */}
        {alertas.length > 0 && (
          <div className="bg-white rounded-3xl border border-violet-100 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-600" />
              Puntos de Atención Académica ({alertas.length})
            </h3>
            <div className="space-y-2">
              {alertas.slice(0, 3).map((a, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-2xl bg-violet-50/50 border border-violet-100 text-xs flex items-start gap-2.5"
                >
                  <span className="w-2 h-2 rounded-full bg-violet-600 mt-1.5 shrink-0" />
                  <div className="text-slate-700 leading-relaxed">
                    {a.mensaje}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modal de Solicitud de Cambio de Carrera */}
      {isChangeCareerModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4">
          <div
            onClick={() => setIsChangeCareerModalOpen(false)}
            className="fixed inset-0 bg-violet-950/25 backdrop-blur-md"
          />
          <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl p-6 text-left border border-white/80 z-10">
            <h3 className="text-base font-bold text-slate-900 mb-1 flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-violet-600" />
              Solicitud de Cambio de Carrera
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Tu solicitud será enviada al panel administrativo para revisión y autorización oficial.
            </p>

            <form onSubmit={handleCareerRequestSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Carrera actual:
                </label>
                <div className="p-2.5 bg-slate-100 rounded-xl text-xs text-slate-700 font-medium">
                  {currentUser?.carrera_nombre || 'No definida'}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Nueva Carrera de Destino:
                </label>
                <select
                  value={selectedTargetCareer}
                  onChange={(e) => setSelectedTargetCareer(Number(e.target.value))}
                  className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 cursor-pointer"
                >
                  {careers
                    .filter((c) => c.id !== currentUser?.carrera_id)
                    .map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.nombre} ({c.codigo})
                      </option>
                    ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Motivo o justificación académica:
                </label>
                <textarea
                  rows={3}
                  value={careerReason}
                  onChange={(e) => setCareerReason(e.target.value)}
                  placeholder="Explica brevemente tu vocación o intereses formativos..."
                  className="w-full p-2.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-violet-500 resize-none"
                />
              </div>

              {requestFeedback && (
                <div className="text-xs p-2.5 rounded-xl bg-violet-50 border border-violet-200 text-violet-800 font-medium">
                  {requestFeedback}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsChangeCareerModalOpen(false)}
                  className="px-3.5 py-2 text-xs font-bold text-slate-500 hover:text-slate-800"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={submittingRequest}
                  className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold rounded-xl shadow-md shadow-violet-500/20 transition-all disabled:opacity-50"
                >
                  {submittingRequest ? 'Enviando...' : 'Enviar Solicitud'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

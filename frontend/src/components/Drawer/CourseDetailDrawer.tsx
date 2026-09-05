import React from 'react';
import { Asignatura, EstadoAsignatura, HistorialEntry } from '../../types/curriculum';
import { 
  X, BookOpen, Layers, Award, CheckCircle2, Clock, 
  AlertTriangle, ShieldCheck, Flame, ArrowRight
} from 'lucide-react';

interface CourseDetailDrawerProps {
  asignatura: Asignatura | null;
  historialEntry?: HistorialEntry;
  historial?: HistorialEntry[];
  allCourses?: Asignatura[];
  isAuth?: boolean;
  onOpenAuth?: () => void;
  onClose: () => void;
  onUpdateState?: (
    asignaturaId: number,
    newState: EstadoAsignatura,
    calificacion?: number | null,
    numeroMatricula?: number
  ) => Promise<void>;
}

export const CourseDetailDrawer: React.FC<CourseDetailDrawerProps> = ({
  asignatura,
  historialEntry,
  historial,
  allCourses,
  isAuth = false,
  onOpenAuth,
  onClose,
  onUpdateState,
}) => {
  if (!asignatura) return null;

  const [formState, setFormState] = React.useState<EstadoAsignatura>(historialEntry?.estado || 'PENDIENTE');
  const [formGrade, setFormGrade] = React.useState<string>(historialEntry?.calificacion !== undefined && historialEntry?.calificacion !== null ? String(historialEntry.calificacion) : '15.0');
  const [formMatricula, setFormMatricula] = React.useState<number>(historialEntry?.numeroMatricula || 1);
  const [isSaving, setIsSaving] = React.useState(false);
  const [saveSuccess, setSaveSuccess] = React.useState(false);

  React.useEffect(() => {
    setFormState(historialEntry?.estado || 'PENDIENTE');
    setFormGrade(historialEntry?.calificacion !== undefined && historialEntry?.calificacion !== null ? String(historialEntry.calificacion) : '15.0');
    setFormMatricula(historialEntry?.numeroMatricula || 1);
    setSaveSuccess(false);
  }, [asignatura, historialEntry]);

  const handleSave = async () => {
    if (!onUpdateState) return;
    setIsSaving(true);
    setSaveSuccess(false);
    try {
      let grade: number | null = null;
      if (formState === 'APROBADA') {
        grade = Math.max(11.0, Math.min(20.0, parseFloat(formGrade) || 11.0));
      } else if (formState === 'DESAPROBADA') {
        grade = Math.max(0.0, Math.min(10.9, parseFloat(formGrade) || 8.0));
      }

      await onUpdateState(asignatura.id, formState, grade, formMatricula);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch {
      // Error handled by parent
    } finally {
      setIsSaving(false);
    }
  };

  const isAprobada = historialEntry?.estado === 'APROBADA';
  const isEnCurso = historialEntry?.estado === 'EN_CURSO';
  const isDesaprobada = historialEntry?.estado === 'DESAPROBADA';

  // Resolución dinámica determinística del estado de los prerrequisitos
  const prereqsWithStatus = React.useMemo(() => {
    if (!asignatura) return [];

    const codeToId = new Map<string, number>();
    if (allCourses) {
      for (const c of allCourses) {
        codeToId.set(c.codigo, c.id);
      }
    }

    const historyByCourseId = new Map<number, HistorialEntry>();
    if (historial) {
      for (const h of historial) {
        historyByCourseId.set(h.asignaturaId, h);
      }
    }

    return (asignatura.prerrequisitos || []).map((prereq) => {
      const pId = (prereq as any).id || codeToId.get(prereq.codigo);
      const pHistory = pId ? historyByCourseId.get(pId) : undefined;
      const isAprobado = Boolean(prereq.aprobado || pHistory?.estado === 'APROBADA');
      const grade = prereq.calificacion ?? pHistory?.calificacion ?? undefined;

      return {
        ...prereq,
        id: pId,
        aprobado: isAprobado,
        calificacion: grade,
      };
    });
  }, [asignatura, historial, allCourses]);

  const hasPrereqs = prereqsWithStatus.length > 0;
  const allPrereqsFulfilled = !hasPrereqs || prereqsWithStatus.every((p) => p.aprobado);
  const pendingPrereqsCount = prereqsWithStatus.filter((p) => !p.aprobado).length;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop con desenfoque moderno */}
      <div 
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity duration-300"
      />

      {/* Panel deslizante lateral (Drawer) */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out border-l border-slate-200">
          
          {/* Header del Drawer */}
          <div className="px-6 py-5 bg-slate-900 text-white flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-sm font-bold bg-white/10 px-2 py-0.5 rounded text-slate-200">
                {asignatura.codigo}
              </span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                asignatura.tipo === 'ELECTIVA' ? 'bg-purple-600 text-purple-100' : 'bg-blue-600 text-blue-100'
              }`}>
                {asignatura.tipo}
              </span>
            </div>
            <button
              onClick={onClose}
              className="rounded-lg p-1.5 text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Contenido Principal */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            
            {/* Título y Ciclo */}
            <div>
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 mb-1">
                <Layers className="w-3.5 h-3.5 text-slate-400" />
                <span>Ciclo Académico Sugerido: {asignatura.ciclo}</span>
              </div>
              <h3 className="text-xl font-bold text-slate-900 leading-tight">
                {asignatura.nombre}
              </h3>
            </div>

            {/* Tarjetas de Métricas Rápidas */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
                <span className="text-xs text-slate-500 font-medium block">Valor Crediticio</span>
                <span className="text-lg font-bold text-slate-800 flex items-center gap-1 mt-0.5">
                  <Award className="w-4 h-4 text-blue-600" />
                  {asignatura.creditos} Créditos
                </span>
              </div>

              <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5">
                <span className="text-xs text-slate-500 font-medium block">Estado Actual</span>
                <span className="text-sm font-bold mt-1 inline-flex items-center gap-1.5">
                  {isAprobada && (
                    <span className="text-emerald-700 flex items-center gap-1">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      Aprobada ({historialEntry?.calificacion?.toFixed(1) || '11.0'})
                    </span>
                  )}
                  {isEnCurso && (
                    <span className="text-amber-700 flex items-center gap-1">
                      <Clock className="w-4 h-4 text-amber-600" />
                      En Curso ({historialEntry?.numeroMatricula}ª mat.)
                    </span>
                  )}
                  {isDesaprobada && (
                    <span className="text-red-700 flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4 text-red-600" />
                      Desaprobada
                    </span>
                  )}
                  {!isAprobada && !isEnCurso && !isDesaprobada && (
                    <span className="text-slate-600 flex items-center gap-1">
                      <BookOpen className="w-4 h-4 text-slate-400" />
                      Pendiente
                    </span>
                  )}
                </span>
              </div>
            </div>

            {/* Gestión del Historial del Estudiante */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide mb-2 flex items-center justify-between">
                <span>Mi Récord Académico</span>
                {saveSuccess && (
                  <span className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 animate-in fade-in">
                    <CheckCircle2 className="w-3.5 h-3.5" /> ¡Guardado!
                  </span>
                )}
              </h4>

              {isAuth ? (
                <div className="space-y-3">
                  <div>
                    <label className="block text-[11px] font-medium text-slate-600 mb-1">
                      Estado de la Asignatura
                    </label>
                    <div className="grid grid-cols-2 gap-1.5">
                      <button
                        type="button"
                        onClick={() => setFormState('APROBADA')}
                        className={`py-1.5 px-2 text-xs font-semibold rounded-lg border transition-all ${
                          formState === 'APROBADA'
                            ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        ✓ Aprobada
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormState('EN_CURSO')}
                        className={`py-1.5 px-2 text-xs font-semibold rounded-lg border transition-all ${
                          formState === 'EN_CURSO'
                            ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        ⏳ En Curso
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormState('DESAPROBADA')}
                        className={`py-1.5 px-2 text-xs font-semibold rounded-lg border transition-all ${
                          formState === 'DESAPROBADA'
                            ? 'bg-red-600 text-white border-red-600 shadow-sm'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        ✕ Desaprobada
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormState('PENDIENTE')}
                        className={`py-1.5 px-2 text-xs font-semibold rounded-lg border transition-all ${
                          formState === 'PENDIENTE'
                            ? 'bg-slate-700 text-white border-slate-700 shadow-sm'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                        }`}
                      >
                        ⚪ Pendiente
                      </button>
                    </div>
                  </div>

                  {formState === 'APROBADA' && (
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Calificación Aprobatoria (11.00 a 20.00)
                      </label>
                      <input
                        type="number"
                        min="11.0"
                        max="20.0"
                        step="0.1"
                        value={formGrade}
                        onChange={(e) => setFormGrade(e.target.value)}
                        className="w-full bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-semibold focus:outline-none focus:border-blue-500"
                        placeholder="ej. 15.5"
                      />
                    </div>
                  )}

                  {formState === 'DESAPROBADA' && (
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-[11px] font-medium text-slate-600 mb-1">
                          Nota (0.0 a 10.9)
                        </label>
                        <input
                          type="number"
                          min="0.0"
                          max="10.9"
                          step="0.1"
                          value={formGrade}
                          onChange={(e) => setFormGrade(e.target.value)}
                          className="w-full bg-white border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-semibold focus:outline-none focus:border-red-500"
                          placeholder="ej. 08.0"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-medium text-slate-600 mb-1">
                          Matrícula Cursada
                        </label>
                        <select
                          value={formMatricula}
                          onChange={(e) => setFormMatricula(Number(e.target.value))}
                          className="w-full bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-blue-500"
                        >
                          <option value="1">1ª Matrícula</option>
                          <option value="2">2ª Matrícula</option>
                          <option value="3">3ª Matrícula</option>
                        </select>
                      </div>
                    </div>
                  )}

                  {formState === 'EN_CURSO' && (
                    <div>
                      <label className="block text-[11px] font-medium text-slate-600 mb-1">
                        Número de Matrícula Actual
                      </label>
                      <select
                        value={formMatricula}
                        onChange={(e) => setFormMatricula(Number(e.target.value))}
                        className="w-full bg-white border border-slate-300 rounded-lg px-2 py-1.5 text-xs text-slate-800 focus:outline-none focus:border-blue-500"
                      >
                        <option value="1">1ª Matrícula Regular</option>
                        <option value="2">2ª Matrícula (Reiteración)</option>
                        <option value="3">3ª Matrícula (Riesgo Crítico)</option>
                      </select>
                    </div>
                  )}

                  <button
                    type="button"
                    onClick={handleSave}
                    disabled={isSaving}
                    className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-lg transition-all shadow-sm active:scale-[0.98] disabled:opacity-50 flex items-center justify-center gap-1.5 mt-2"
                  >
                    {isSaving ? (
                      <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                      <span>Actualizar en Mi Historial</span>
                    )}
                  </button>
                </div>
              ) : (
                <div className="text-center py-2 space-y-2">
                  <p className="text-xs text-slate-500">
                    Inicia sesión o regístrate con tu correo UP para registrar notas, materias aprobadas y calcular tus riesgos académicos.
                  </p>
                  {onOpenAuth && (
                    <button
                      type="button"
                      onClick={onOpenAuth}
                      className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-lg shadow-sm transition-all"
                    >
                      Iniciar Sesión / Registrarme
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Alerta de Cuello de Botella si aplica */}
            {asignatura.esCuelloBotella && (
              <div className="bg-orange-50 border border-orange-200 rounded-xl p-4 flex items-start gap-3">
                <Flame className="w-5 h-5 text-orange-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold text-orange-900 uppercase tracking-wide">
                    Asignatura Cuello de Botella
                  </h4>
                  <p className="text-xs text-orange-800 mt-1 leading-relaxed">
                    Esta materia es un prerrequisito crítico que condiciona el avance de{' '}
                    <strong>{asignatura.desbloqueaCount} cursos posteriores</strong> en la malla curricular.
                  </p>
                </div>
              </div>
            )}

            {/* Concentración (en caso de electivas) */}
            {asignatura.concentracionNombre && (
              <div className="border-t border-slate-100 pt-4">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Concentración Temática
                </h4>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3 text-xs text-purple-900 font-medium">
                  {asignatura.concentracionNombre}
                </div>
              </div>
            )}

            {/* Requisito de Bolsa de Créditos */}
            {asignatura.creditosMinimosRequeridos > 0 && (
              <div className="border-t border-slate-100 pt-4">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Bolsa Mínima de Créditos
                </h4>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-xs text-blue-900 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
                  <span>Requiere al menos <strong>{asignatura.creditosMinimosRequeridos} créditos aprobados</strong> para su matrícula.</span>
                </div>
              </div>
            )}

            {/* Cadena de Prerrequisitos Directos (RF-09, CA-04) */}
            <div className="border-t border-slate-100 pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                  Prerrequisitos Directos ({prereqsWithStatus.length})
                </h4>
                {hasPrereqs && (
                  allPrereqsFulfilled ? (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                      Requisitos cumplidos
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-[11px] font-medium text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                      <AlertTriangle className="w-3 h-3 text-amber-600" />
                      {pendingPrereqsCount} pendiente{pendingPrereqsCount > 1 ? 's' : ''}
                    </span>
                  )
                )}
              </div>

              {!hasPrereqs ? (
                <p className="text-xs text-slate-500 italic bg-slate-50 p-3 rounded-lg border border-slate-200">
                  Esta asignatura no exige prerrequisitos de materias previos.
                </p>
              ) : (
                <div className="space-y-2">
                  {allPrereqsFulfilled ? (
                    <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-2.5 text-xs text-emerald-900 flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      <span>¡Prerrequisitos cumplidos! Tienes todas las materias previas aprobadas para cursar esta asignatura.</span>
                    </div>
                  ) : (
                    <div className="bg-amber-50/80 border border-amber-200 rounded-lg p-2.5 text-xs text-amber-900 flex items-center gap-2 mb-2">
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                      <span>Atención: Debes aprobar los cursos pendientes indicados abajo para habilitar tu matrícula en esta materia.</span>
                    </div>
                  )}

                  {prereqsWithStatus.map((prereq) => (
                    <div 
                      key={prereq.codigo}
                      className={`p-3 rounded-lg border flex items-center justify-between text-xs transition-colors ${
                        prereq.aprobado 
                          ? 'border-emerald-200 bg-emerald-50/30' 
                          : 'border-slate-200 bg-white'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <ArrowRight className={`w-3.5 h-3.5 ${prereq.aprobado ? 'text-emerald-500' : 'text-slate-400'}`} />
                        <div>
                          <span className="font-mono font-bold text-slate-800">{prereq.codigo}</span>
                          <p className="text-slate-600 text-[11px]">{prereq.nombre}</p>
                        </div>
                      </div>
                      <div>
                        {prereq.aprobado ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-100/70 px-2.5 py-1 rounded border border-emerald-300">
                            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                            Aprobado {prereq.calificacion !== undefined && prereq.calificacion !== null ? `(${Number(prereq.calificacion).toFixed(1)})` : ''}
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600 bg-slate-100 px-2.5 py-1 rounded border border-slate-200">
                            <Clock className="w-3.5 h-3.5 text-slate-400" />
                            Pendiente
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

          </div>

          {/* Footer */}
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg shadow transition-colors"
            >
              Cerrar Ficha Técnica
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};


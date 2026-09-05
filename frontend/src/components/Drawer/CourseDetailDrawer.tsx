import React from 'react';
import { Asignatura, EstadoAsignatura, HistorialEntry } from '../../types/curriculum';
import { 
  X, BookOpen, Layers, Award, CheckCircle2, Clock, 
  AlertTriangle, ShieldCheck, Flame, ArrowRight
} from 'lucide-react';

interface CourseDetailDrawerProps {
  asignatura: Asignatura | null;
  historialEntry?: HistorialEntry;
  onClose: () => void;
  onUpdateState?: (asignaturaId: number, newState: EstadoAsignatura, calificacion?: number) => void;
}

export const CourseDetailDrawer: React.FC<CourseDetailDrawerProps> = ({
  asignatura,
  historialEntry,
  onClose,
}) => {
  if (!asignatura) return null;

  const isAprobada = historialEntry?.estado === 'APROBADA';
  const isEnCurso = historialEntry?.estado === 'EN_CURSO';
  const isDesaprobada = historialEntry?.estado === 'DESAPROBADA';

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
              <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                Prerrequisitos Directos de Materia ({asignatura.prerrequisitos.length})
              </h4>
              {asignatura.prerrequisitos.length === 0 ? (
                <p className="text-xs text-slate-500 italic bg-slate-50 p-3 rounded-lg border border-slate-200">
                  Esta asignatura no exige prerrequisitos de materias previos.
                </p>
              ) : (
                <div className="space-y-2">
                  {asignatura.prerrequisitos.map((prereq) => (
                    <div 
                      key={prereq.codigo}
                      className="p-3 rounded-lg border border-slate-200 bg-white flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2.5">
                        <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                        <div>
                          <span className="font-mono font-bold text-slate-800">{prereq.codigo}</span>
                          <p className="text-slate-600 text-[11px]">{prereq.nombre}</p>
                        </div>
                      </div>
                      <div>
                        {prereq.aprobado ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            Aprobado
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
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


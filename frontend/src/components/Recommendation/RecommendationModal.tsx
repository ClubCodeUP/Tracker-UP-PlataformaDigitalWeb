import React from 'react';
import { X, Sparkles, CheckCircle2, AlertTriangle, Flame, Award } from 'lucide-react';

interface RecommendationModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendationData?: any;
}

export const RecommendationModal: React.FC<RecommendationModalProps> = ({
  isOpen,
  onClose,
  recommendationData,
}) => {
  if (!isOpen) return null;

  const data = recommendationData || {
    periodo_proyectado: '2024-1',
    creditos_totales_sugeridos: 18.0,
    rango_creditos_permitido: { minimo_regular: 12.0, maximo_regular: 22.0 },
    cantidad_cursos_sugeridos: 5,
    cursos_sugeridos: [
      {
        codigo: 'MAT-1102',
        nombre: 'Cálculo Diferencial e Integral',
        creditos: 4.0,
        ciclo_sugerido: 2,
        tipo: 'OBLIGATORIA',
        es_cuello_botella: false,
        es_reiteracion: false,
        motivo_prioridad: 'Malla Ciclo 2 | Obligatoria'
      },
      {
        codigo: 'PRO-1102',
        nombre: 'Algoritmos y Estructuras de Datos',
        creditos: 4.0,
        ciclo_sugerido: 2,
        tipo: 'OBLIGATORIA',
        es_cuello_botella: true,
        es_reiteracion: false,
        motivo_prioridad: 'Cuello de botella (desbloquea 5 materias) | Malla Ciclo 2'
      },
      {
        codigo: 'EST-1101',
        nombre: 'Estadística y Probabilidades',
        creditos: 4.0,
        ciclo_sugerido: 2,
        tipo: 'OBLIGATORIA',
        es_cuello_botella: false,
        es_reiteracion: false,
        motivo_prioridad: 'Malla Ciclo 2 | Obligatoria'
      },
      {
        codigo: 'CON-1101',
        nombre: 'Contabilidad Financiera',
        creditos: 3.0,
        ciclo_sugerido: 2,
        tipo: 'OBLIGATORIA',
        es_cuello_botella: false,
        es_reiteracion: false,
        motivo_prioridad: 'Malla Ciclo 2 | Obligatoria'
      },
    ],
    resumen_criterios_deterministicos: [
      '1. Prioridad legal de matricular asignaturas desaprobadas en 2ª o 3ª matrícula.',
      '2. Priorización de cursos cuello de botella según materias condicionadas en el grafo.',
      '3. Ajuste al rango de carga regular permitida (12 a 22 créditos).'
    ]
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4">
      {/* Backdrop con blur */}
      <div onClick={onClose} className="fixed inset-0 bg-violet-950/25 backdrop-blur-md transition-opacity" />

      {/* Modal */}
      <div className="relative w-full max-w-2xl bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl shadow-purple-500/10 border border-white/70 overflow-hidden z-10 text-left">
        {/* Cabecera del Modal */}
        <div className="px-6 py-5 bg-gradient-to-r from-violet-700 to-purple-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-white/15 border border-white/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-violet-100" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Propuesta Determinística de Matrícula
                <span className="text-xs font-mono font-semibold bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded">
                  {data.periodo_proyectado}
                </span>
              </h3>
              <p className="text-xs text-slate-300 mt-0.5">
                Calculada en base al estado del historial, prerrequisitos cumplidos y límites de carga.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-1.5 text-violet-100 hover:text-white hover:bg-white/15 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Resumen de Carga Crediticia */}
        <div className="px-6 py-4 bg-violet-50/60 border-b border-violet-100 grid grid-cols-3 gap-4 text-center">
          <div>
            <span className="text-[11px] text-slate-500 font-medium block">Créditos Sugeridos</span>
            <span className="text-xl font-black text-slate-900 flex items-center justify-center gap-1 mt-0.5">
              <Award className="w-4 h-4 text-violet-600" />
              {data.creditos_totales_sugeridos} cr
            </span>
          </div>
          <div>
            <span className="text-[11px] text-slate-500 font-medium block">Rango Regular Permitido</span>
            <span className="text-sm font-bold text-slate-800 mt-1 block">
              {data.rango_creditos_permitido.minimo_regular} a {data.rango_creditos_permitido.maximo_regular} cr
            </span>
          </div>
          <div>
            <span className="text-[11px] text-slate-500 font-medium block">Cursos en el Bloque</span>
            <span className="text-sm font-bold text-emerald-700 mt-1 flex items-center justify-center gap-1">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              {data.cursos_sugeridos.length} Asignaturas
            </span>
          </div>
        </div>

        {/* Lista de Cursos Sugeridos */}
        <div className="p-6 max-h-[360px] overflow-y-auto space-y-3">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
            Bloque de Asignaturas Propuestas
          </h4>

          {data.cursos_sugeridos.map((curso: any, index: number) => (
            <div
              key={index}
              className="p-3.5 rounded-2xl border border-violet-100 bg-white/80 hover:border-violet-300 transition-colors flex items-start justify-between gap-3 shadow-sm"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono text-xs font-bold text-violet-800 bg-violet-50 px-1.5 py-0.5 rounded-lg">
                    {curso.codigo}
                  </span>
                  <span className="text-xs font-semibold text-slate-900">
                    {curso.nombre}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-slate-600 mt-1.5">
                  <span className="text-slate-400">Motivo de selección:</span>
                  <span className="font-medium text-violet-700 bg-violet-50 border border-violet-100 px-1.5 py-0.2 rounded-lg">
                    {curso.motivo_prioridad}
                  </span>
                </div>
              </div>

              <div className="text-right shrink-0">
                <span className="text-xs font-bold text-slate-900 block">
                  {curso.creditos} créditos
                </span>
                <span className="text-[10px] text-slate-500 block">
                  Ciclo {curso.ciclo_sugerido}
                </span>
                {curso.es_cuello_botella && (
                  <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-orange-700 bg-orange-50 border border-orange-200 px-1.5 py-0.2 rounded mt-1">
                    <Flame className="w-2.5 h-2.5 text-orange-600" />
                    Cuello
                  </span>
                )}
                {curso.es_reiteracion && (
                  <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-red-700 bg-red-50 border border-red-200 px-1.5 py-0.2 rounded mt-1">
                    <AlertTriangle className="w-2.5 h-2.5 text-red-600" />
                    Re-matrícula
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-violet-50/60 border-t border-violet-100 flex items-center justify-between">
          <p className="text-[11px] text-slate-500">
            * Motor determinístico de reglas según normativa de matrícula UP.
          </p>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold rounded-xl shadow shadow-violet-500/20 transition-colors"
          >
            Entendido
          </button>
        </div>
      </div>
    </div>
  );
};


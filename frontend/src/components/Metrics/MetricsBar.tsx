import React from 'react';
import { AcademicMetrics } from '../../types/curriculum';
import { Award, TrendingUp, Layers, CheckCircle2, Clock } from 'lucide-react';

interface MetricsBarProps {
  metrics: AcademicMetrics | null;
}

export const MetricsBar: React.FC<MetricsBarProps> = ({ metrics }) => {
  if (!metrics) return null;

  return (
    <div className="bg-slate-900 border-b border-slate-800 px-6 py-3 text-white flex flex-wrap items-center justify-between gap-4">
      {/* Barra de Porcentaje de Avance */}
      <div className="flex items-center gap-4 min-w-[260px] flex-1">
        <div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
            <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
            <span>Avance Curricular</span>
          </div>
          <span className="text-xl font-black text-white tracking-tight">
            {metrics.porcentaje_avance.toFixed(1)}%
          </span>
        </div>

        <div className="flex-1 max-w-xs">
          <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden border border-slate-700/80">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${Math.min(100, metrics.porcentaje_avance)}%` }}
            />
          </div>
          <span className="text-[10px] text-slate-400 mt-0.5 block">
            {metrics.creditos_aprobados} de {metrics.total_creditos_carrera} créditos
            {metrics.cursos_aprobados_count > 0 && (
              <span className="ml-1 text-emerald-300 font-medium">
                • {metrics.cursos_aprobados_count} materia{metrics.cursos_aprobados_count !== 1 ? 's' : ''} aprobada{metrics.cursos_aprobados_count !== 1 ? 's' : ''}
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Métricas Numéricas Rápidas */}
      <div className="flex items-center gap-6 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Materias Aprobadas</span>
            <div className="flex items-baseline gap-1">
              <span className="font-extrabold text-base text-white">
                {metrics.cursos_aprobados_count}
              </span>
              <span className="text-[11px] text-emerald-400 font-medium">
                ({metrics.creditos_aprobados} cr)
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Clock className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">En Curso</span>
            <div className="flex items-baseline gap-1">
              <span className="font-extrabold text-base text-white">
                {metrics.cursos_en_curso_count}
              </span>
              <span className="text-[11px] text-amber-400 font-medium">
                ({metrics.creditos_en_curso} cr)
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Ciclo Referencial</span>
            <span className="font-bold text-slate-100">
              {metrics.ciclo_referencial === 0 ? 'Ciclo 0 (Nivelación)' : `Ciclo ${metrics.ciclo_referencial}`}
            </span>
          </div>
        </div>

        {metrics.promedio_ponderado && (
          <div className="flex items-center gap-2 border-l border-slate-800 pl-6 hidden sm:flex">
            <div className="w-8 h-8 rounded-lg bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center text-yellow-400">
              <Award className="w-4 h-4" />
            </div>
            <div>
              <span className="text-slate-400 block text-[10px]">Promedio Acum.</span>
              <span className="font-bold text-slate-100">{metrics.promedio_ponderado.toFixed(2)}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};


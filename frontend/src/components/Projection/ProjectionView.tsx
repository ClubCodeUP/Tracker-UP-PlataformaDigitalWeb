import React from 'react';
import {
  Sparkles,
  Calendar,
  Layers,
  Award,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ArrowRight,
  TrendingUp,
  Compass,
  Lightbulb
} from 'lucide-react';
import { Asignatura } from '../../types/curriculum';

interface ProjectionViewProps {
  recommendationData: any;
  malla: Asignatura[];
  onNavigateToMap: () => void;
  onSelectCourse: (course: Asignatura) => void;
}

export const ProjectionView: React.FC<ProjectionViewProps> = ({
  recommendationData,
  malla,
  onNavigateToMap,
  onSelectCourse,
}) => {
  const data = recommendationData || {
    periodo_proyectado: '2024-2',
    creditos_totales_sugeridos: 18.0,
    rango_creditos_permitido: { minimo_regular: 12.0, maximo_regular: 22.0 },
    cantidad_cursos_sugeridos: 0,
    cursos_sugeridos: [],
    resumen_criterios_deterministicos: [
      '1. Prioridad de cursos que desbloquean múltiples materias posteriores.',
      '2. Coherencia con el ciclo curricular referencial.',
      '3. Balance de créditos dentro del rango regular estándar (12 a 22 créditos).'
    ],
  };

  const cursos = data.cursos_sugeridos || [];

  return (
    <div className="flex-1 overflow-y-auto bg-[#FBFBFE] px-6 py-8 text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Cabecera de la Sección */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Simulación Determinística de Matrícula</span>
            </div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
              Proyección de Matrícula para el Periodo {data.periodo_proyectado}
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Cálculo de asignaturas recomendadas para tu próximo ciclo con probabilidades estimadas de aprobación y sugerencias de estudio constructivas.
            </p>
          </div>

          <div className="flex items-center gap-3 self-start">
            <button
              onClick={onNavigateToMap}
              className="px-4 py-2.5 bg-white border border-violet-200 text-violet-700 font-bold rounded-2xl text-xs hover:bg-violet-50 transition-all flex items-center gap-2 shadow-sm"
            >
              <Compass className="w-4 h-4 text-violet-600" />
              Ver Prerrequisitos en el Mapa
            </button>
          </div>
        </div>

        {/* Resumen de Carga Crediticia Sugerida */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-violet-100 text-violet-700 flex items-center justify-center shrink-0">
              <Calendar className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-500">Periodo Destino</span>
              <div className="text-xl font-black text-slate-900">{data.periodo_proyectado}</div>
              <p className="text-[11px] text-slate-400">Próxima matrícula regular</p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center shrink-0">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-500">Créditos Sugeridos</span>
              <div className="text-xl font-black text-slate-900">
                {data.creditos_totales_sugeridos} cr.
              </div>
              <p className="text-[11px] text-indigo-600 font-semibold">
                Rango regular permitido: {data.rango_creditos_permitido?.minimo_regular} a {data.rango_creditos_permitido?.maximo_regular} cr.
              </p>
            </div>
          </div>

          <div className="bg-white p-5 rounded-3xl border border-violet-100 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <span className="text-xs font-semibold text-slate-500">Total de Cursos</span>
              <div className="text-xl font-black text-slate-900">
                {data.cantidad_cursos_sugeridos || cursos.length} asignaturas
              </div>
              <p className="text-[11px] text-emerald-600 font-semibold">
                Validado con prerrequisitos cumplidos
              </p>
            </div>
          </div>
        </div>

        {/* Lista de Cursos Sugeridos con Probabilidad en Positivo */}
        <div className="bg-white rounded-3xl border border-violet-100 p-6 md:p-8 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Award className="w-5 h-5 text-violet-600" />
                Bloque de Asignaturas Propuestas
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Seleccionadas determinísticamente respetando la cadena de dependencias y el plan curricular.
              </p>
            </div>
          </div>

          {cursos.length === 0 ? (
            <div className="text-center py-12 text-slate-400 text-xs">
              No hay recomendaciones pendientes en este momento.
              <br />
              Asegúrate de tener registrado tu historial de cursos aprobados en el mapa.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {cursos.map((c: any) => {
                const prob = c.probabilidad_aprobacion_estimada || 85.0;
                const isReiteracion = c.es_reiteracion;
                const isBottleneck = c.es_cuello_botella;

                return (
                  <div
                    key={c.asignatura_id || c.codigo}
                    className="p-5 rounded-2xl bg-slate-50/80 border border-slate-200 hover:border-violet-300 hover:bg-white transition-all shadow-sm flex flex-col justify-between"
                  >
                    <div>
                      {/* Cabecera del Curso */}
                      <div className="flex items-center justify-between text-xs mb-2">
                        <span className="font-mono font-bold text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                          {c.codigo}
                        </span>
                        <div className="flex items-center gap-1.5">
                          {isBottleneck && (
                            <span className="text-[10px] font-bold text-orange-700 bg-orange-100 border border-orange-200 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <Flame className="w-3 h-3 text-orange-600" />
                              Cuello de botella
                            </span>
                          )}
                          {isReiteracion && (
                            <span className="text-[10px] font-bold text-amber-800 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-full flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3 text-amber-600" />
                              Prioridad Máxima
                            </span>
                          )}
                          <span className="bg-violet-100 text-violet-800 px-2 py-0.5 rounded font-bold text-[11px]">
                            {c.creditos} cr
                          </span>
                        </div>
                      </div>

                      {/* Nombre del Curso */}
                      <h4 className="text-sm font-bold text-slate-900 mb-2 leading-snug">
                        {c.nombre}
                      </h4>

                      {/* Motivo de Prioridad */}
                      <p className="text-[11px] text-slate-500 mb-4 flex items-center gap-1">
                        <Layers className="w-3 h-3 text-slate-400 shrink-0" />
                        <span>{c.motivo_prioridad}</span>
                      </p>

                      {/* Indicador de Probabilidad de Aprobación en Positivo */}
                      <div className="p-3 bg-white rounded-xl border border-slate-200 mb-3">
                        <div className="flex items-center justify-between text-xs mb-1.5">
                          <span className="font-semibold text-slate-700 flex items-center gap-1.5">
                            <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                            Probabilidad estimada de aprobación:
                          </span>
                          <span className="font-black text-emerald-700 text-sm">
                            {prob}%
                          </span>
                        </div>
                        <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full transition-all"
                            style={{ width: `${prob}%` }}
                          />
                        </div>
                      </div>

                      {/* Consejo Estratégico Positivo */}
                      {c.consejo_estrategico && (
                        <div className="p-2.5 rounded-xl bg-violet-50/70 border border-violet-100 text-[11px] text-violet-900 flex items-start gap-2">
                          <Lightbulb className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                          <span className="leading-relaxed">{c.consejo_estrategico}</span>
                        </div>
                      )}
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between text-xs">
                      <span className="text-[11px] text-slate-400">Ciclo referencial: {c.ciclo_sugerido}</span>
                      <button
                        onClick={() => {
                          const fullCourse = malla.find((m) => m.id === c.asignatura_id || m.codigo === c.codigo);
                          if (fullCourse) onSelectCourse(fullCourse);
                        }}
                        className="text-violet-600 font-bold hover:text-violet-800 hover:underline flex items-center gap-1 text-[11px]"
                      >
                        Ver ficha técnica
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Resumen de Criterios del Algoritmo */}
        <div className="bg-slate-50 rounded-3xl border border-slate-200 p-6 text-xs text-slate-600">
          <h4 className="font-bold text-slate-800 mb-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            Criterios Determinísticos de Priorización:
          </h4>
          <ul className="space-y-1.5 list-disc list-inside">
            {data.resumen_criterios_deterministicos?.map((crit: string, idx: number) => (
              <li key={idx} className="leading-relaxed">
                {crit}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

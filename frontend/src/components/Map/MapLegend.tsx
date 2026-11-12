import React, { useState } from 'react';
import { CheckCircle2, Clock, Unlock, Lock, AlertTriangle, Flame, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface MapLegendProps {
  selectedConcentrationName?: string | null;
}

export const MapLegend: React.FC<MapLegendProps> = ({ selectedConcentrationName }) => {
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="absolute bottom-6 left-6 z-20 bg-white/90 backdrop-blur-md border border-white/80 rounded-2xl shadow-xl shadow-purple-500/10 text-xs overflow-hidden max-w-xs transition-all">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2.5 flex items-center justify-between font-bold text-slate-800 hover:bg-slate-50 transition-colors border-b border-slate-100"
      >
        <span className="flex items-center gap-1.5 text-xs">
          <span className="w-2 h-2 rounded-full bg-violet-600 animate-pulse" />
          Leyenda del Mapa Curricular
        </span>
        {isOpen ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronUp className="w-4 h-4 text-slate-400" />}
      </button>

      {isOpen && (
        <div className="p-3 space-y-2 text-[11px] text-slate-600">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-emerald-100 border border-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
            </span>
            <span className="font-medium text-slate-700">Aprobada:</span>
            <span>Créditos completados</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-indigo-100 border border-indigo-400 flex items-center justify-center">
              <Clock className="w-2.5 h-2.5 text-indigo-600" />
            </span>
            <span className="font-medium text-slate-700">En curso:</span>
            <span>Matriculado actualmente</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-amber-100 border border-amber-400 flex items-center justify-center">
              <Unlock className="w-2.5 h-2.5 text-amber-600" />
            </span>
            <span className="font-medium text-slate-700">Habilitada:</span>
            <span>Prerrequisitos listos para matricular</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-slate-100 border border-slate-300 flex items-center justify-center">
              <Lock className="w-2.5 h-2.5 text-slate-400" />
            </span>
            <span className="font-medium text-slate-700">Bloqueada:</span>
            <span>Exige prerrequisitos pendientes</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-amber-100 border border-amber-500 flex items-center justify-center">
              <AlertTriangle className="w-2.5 h-2.5 text-amber-600" />
            </span>
            <span className="font-medium text-slate-700">Reiteración:</span>
            <span>2ª o 3ª matrícula (atención prioritaria)</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full bg-orange-100 border border-orange-400 flex items-center justify-center">
              <Flame className="w-2.5 h-2.5 text-orange-600" />
            </span>
            <span className="font-medium text-slate-700">Cuello de botella:</span>
            <span>Desbloquea 2+ cursos futuros</span>
          </div>

          {selectedConcentrationName && (
            <div className="pt-2 border-t border-slate-100 flex items-center gap-2 text-violet-700 font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-violet-600 shrink-0" />
              <span className="truncate">Resaltado: {selectedConcentrationName}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

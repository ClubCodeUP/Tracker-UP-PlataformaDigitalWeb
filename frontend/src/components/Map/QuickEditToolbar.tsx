import React, { useState } from 'react';
import { Zap, CheckCheck, Trash2, X, ChevronDown, Plus, Minus } from 'lucide-react';
import { Asignatura } from '../../types/curriculum';

interface QuickEditToolbarProps {
  isOpen: boolean;
  onClose: () => void;
  defaultGrade: number;
  onChangeDefaultGrade: (grade: number) => void;
  allCourses: Asignatura[];
  onApproveCycle: (ciclo: number) => void;
  onClearCycle: (ciclo: number) => void;
  periodoIngreso?: string;
}

export const QuickEditToolbar: React.FC<QuickEditToolbarProps> = ({
  isOpen,
  onClose,
  defaultGrade,
  onChangeDefaultGrade,
  allCourses,
  onApproveCycle,
  onClearCycle,
  periodoIngreso,
}) => {
  const [isCycleDropdownOpen, setIsCycleDropdownOpen] = useState(false);

  if (!isOpen) return null;

  // Obtener ciclos únicos presentes en la malla actual
  const availableCycles = Array.from(new Set(allCourses.map((c) => c.ciclo))).sort((a, b) => a - b);

  const handleDecreaseGrade = () => {
    if (defaultGrade > 11) {
      onChangeDefaultGrade(defaultGrade - 1);
    }
  };

  const handleIncreaseGrade = () => {
    if (defaultGrade < 20) {
      onChangeDefaultGrade(defaultGrade + 1);
    }
  };

  return (
    <div className="absolute top-16 left-1/2 -translate-x-1/2 z-30 max-w-4xl w-[92%] sm:w-auto animate-in fade-in slide-in-from-top-3 duration-200">
      <div className="bg-slate-900/95 backdrop-blur-md border border-emerald-500/50 shadow-2xl shadow-emerald-950/40 rounded-2xl px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-white">
        
        {/* Indicador de Modo Rápido */}
        <div className="flex items-center gap-2 pr-3 border-r border-slate-700/80">
          <div className="w-8 h-8 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <Zap className="w-4 h-4 fill-emerald-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-bold text-emerald-400 tracking-tight">
                Modo Edición Rápida
              </span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-bold px-1.5 py-0.2 rounded border border-emerald-500/30">
                ACTIVO
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Haz clic en cualquier curso para marcarlo o desmarcarlo al instante
            </p>
          </div>
        </div>

        {/* Periodo de Ingreso informativo */}
        {periodoIngreso && (
          <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 bg-slate-800/60 px-2.5 py-1 rounded-xl border border-slate-700/60">
            <span className="text-[11px] text-slate-400">Ingreso:</span>
            <span className="font-mono text-emerald-400 font-bold text-xs">{periodoIngreso}</span>
          </div>
        )}

        {/* Control de Nota por Defecto */}
        <div className="flex items-center gap-2 bg-slate-800/80 border border-slate-700 rounded-xl px-2.5 py-1">
          <span className="text-xs text-slate-300 font-medium">Nota por defecto:</span>
          <div className="flex items-center gap-1">
            <button
              onClick={handleDecreaseGrade}
              disabled={defaultGrade <= 11}
              className="w-6 h-6 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center text-slate-200 transition-colors"
              title="Disminuir nota"
            >
              <Minus className="w-3 h-3" />
            </button>
            <span className="w-7 text-center font-mono font-bold text-xs text-emerald-400">
              {defaultGrade.toFixed(1)}
            </span>
            <button
              onClick={handleIncreaseGrade}
              disabled={defaultGrade >= 20}
              className="w-6 h-6 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center text-slate-200 transition-colors"
              title="Aumentar nota"
            >
              <Plus className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Acciones en Lote por Ciclo */}
        <div className="relative">
          <button
            onClick={() => setIsCycleDropdownOpen(!isCycleDropdownOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 transition-colors"
          >
            <CheckCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Aprobar Ciclo Completo</span>
            <ChevronDown className="w-3 h-3 text-slate-400 ml-0.5" />
          </button>

          {isCycleDropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-56 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-2 z-50 text-xs">
              <div className="px-3 py-1 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800 mb-1">
                Selecciona un ciclo
              </div>
              <div className="max-h-48 overflow-y-auto">
                {availableCycles.map((ciclo) => (
                  <div
                    key={ciclo}
                    className="flex items-center justify-between px-3 py-1.5 hover:bg-slate-800/80 transition-colors"
                  >
                    <span className="font-medium text-slate-200">
                      {ciclo === 0 ? 'Nivelación (Ciclo 0)' : `Ciclo ${ciclo}`}
                    </span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => {
                          onApproveCycle(ciclo);
                          setIsCycleDropdownOpen(false);
                        }}
                        title={`Marcar todos los cursos del ciclo ${ciclo} como aprobados`}
                        className="p-1 rounded hover:bg-emerald-500/20 text-emerald-400 font-medium text-[11px] flex items-center gap-0.5"
                      >
                        <CheckCheck className="w-3 h-3" /> Aprobar
                      </button>
                      <button
                        onClick={() => {
                          onClearCycle(ciclo);
                          setIsCycleDropdownOpen(false);
                        }}
                        title={`Desmarcar todos los cursos del ciclo ${ciclo}`}
                        className="p-1 rounded hover:bg-red-500/20 text-red-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Botón Salir / Terminar */}
        <button
          onClick={onClose}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-md transition-all active:scale-95"
          title="Salir del Modo Edición Rápida"
        >
          <X className="w-3.5 h-3.5" />
          <span>Listo</span>
        </button>

      </div>
    </div>
  );
};

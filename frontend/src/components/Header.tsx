import React from 'react';
import { Compass, Sparkles, UserCheck, GraduationCap } from 'lucide-react';
import { CareerSummary } from '../services/trackerApi';

interface HeaderProps {
  studentName?: string;
  careerName?: string;
  careers?: CareerSummary[];
  selectedCareerId?: number;
  onSelectCareer?: (careerId: number) => void;
  onOpenRecommendation?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  studentName = 'Estudiante UP',
  careerName = 'Ingeniería de la Información',
  careers = [],
  selectedCareerId,
  onSelectCareer,
  onOpenRecommendation,
}) => {
  return (
    <header className="bg-slate-950 border-b border-slate-800 px-6 py-3.5 flex items-center justify-between text-white select-none">
      {/* Logo y Nombre de Plataforma */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-md shadow-blue-500/20">
          <Compass className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-black tracking-tight text-white flex items-center gap-1.5">
              Tracker UP
              <span className="text-[10px] font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30 px-1.5 py-0.2 rounded-md uppercase tracking-wider">
                MVP
              </span>
            </h1>
          </div>
          <p className="text-[11px] text-slate-400 font-medium">
            Mapa Curricular Interactivo & Alertas de Avance
          </p>
        </div>
      </div>

      {/* Selector de Carrera, Datos del Estudiante y Botón de Recomendación */}
      <div className="flex items-center gap-4">
        {/* Selector Dinámico de Carrera (RF-02, CA-01) */}
        {careers.length > 0 && onSelectCareer && (
          <div className="hidden md:flex items-center gap-2 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1.5 shadow-sm">
            <GraduationCap className="w-4 h-4 text-indigo-400 shrink-0" />
            <select
              value={selectedCareerId}
              onChange={(e) => onSelectCareer(Number(e.target.value))}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none cursor-pointer pr-1"
            >
              {careers.map((c) => (
                <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                  {c.nombre} ({c.codigo})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Botón de Recomendación Determinística */}
        {onOpenRecommendation && (
          <button
            onClick={onOpenRecommendation}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-md shadow-indigo-500/20 transition-all active:scale-95"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Sugerir Matrícula</span>
          </button>
        )}

        {/* Perfil del Alumno */}
        <div className="border-l border-slate-800 pl-4 flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <UserCheck className="w-4 h-4 text-blue-400" />
          </div>
          <div className="hidden sm:block text-left">
            <span className="text-xs font-bold text-slate-100 block leading-tight">
              {studentName}
            </span>
            <span className="text-[10px] text-slate-400 block truncate max-w-[170px]">
              {careerName}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};

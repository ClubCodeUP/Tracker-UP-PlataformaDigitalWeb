import React from 'react';

interface CycleHeaderProps {
  maxCiclos?: number;
}

export const CycleHeader: React.FC<CycleHeaderProps> = ({ maxCiclos = 5 }) => {
  const ciclos = Array.from({ length: maxCiclos }, (_, i) => i + 1);

  return (
    <div className="flex pointer-events-none sticky top-0 z-10 pl-[30px] py-3 bg-slate-900/90 backdrop-blur-md border-b border-slate-700/60 shadow-md">
      {ciclos.map((ciclo) => (
        <div
          key={ciclo}
          style={{ width: '290px' }}
          className="flex-shrink-0 px-2"
        >
          <div className="bg-slate-800/80 border border-slate-700 rounded-lg px-3 py-1.5 flex items-center justify-between text-slate-200">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-100">
              Ciclo {ciclo}
            </span>
            <span className="text-[10px] text-slate-400 font-medium">
              Semestre regular
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};


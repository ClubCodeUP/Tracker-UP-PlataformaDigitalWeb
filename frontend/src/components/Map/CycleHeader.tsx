import React from 'react';
import { CYCLE_COL_WIDTH, MAP_OFFSET_X, NODE_WIDTH } from './mapConstants';

interface CycleHeaderProps {
  maxCiclos?: number;
  viewportX?: number;
  zoom?: number;
  activeCiclo?: number;
  onJumpToCiclo?: (ciclo: number) => void;
}

export const CycleHeader: React.FC<CycleHeaderProps> = ({
  maxCiclos = 10,
  viewportX = 0,
  zoom = 1,
  activeCiclo = 1,
  onJumpToCiclo,
}) => {
  const ciclos = Array.from({ length: maxCiclos }, (_, i) => i + 1);

  return (
    <div className="relative w-full overflow-hidden bg-white/95 backdrop-blur-md border-b border-violet-100/90 shadow-xs z-20">
      <div
        className="flex py-2 transition-transform duration-75 will-change-transform"
        style={{
          transform: `translateX(${viewportX + MAP_OFFSET_X * zoom}px)`,
        }}
      >
        {ciclos.map((ciclo) => {
          const baseWidth = CYCLE_COL_WIDTH * zoom;
          const cardWidth = NODE_WIDTH * zoom;
          const isCurrent = activeCiclo === ciclo;

          return (
            <div
              key={ciclo}
              style={{ width: `${baseWidth}px` }}
              className="flex-shrink-0"
            >
              <button
                type="button"
                style={{ width: `${cardWidth}px` }}
                onClick={() => onJumpToCiclo?.(ciclo)}
                className={`w-full group cursor-pointer rounded-xl px-3 py-1.5 flex items-center justify-center gap-2 transition-all whitespace-nowrap ${
                  isCurrent
                    ? 'bg-violet-600 text-white shadow-sm ring-1 ring-violet-500'
                    : 'bg-white hover:bg-violet-50/80 border border-violet-100/90 text-slate-700 hover:text-violet-900 shadow-2xs'
                }`}
                title={`Ver Ciclo ${ciclo}`}
              >
                <span
                  className={`text-xs font-bold uppercase tracking-wider ${
                    isCurrent ? 'text-white' : 'text-slate-800 group-hover:text-violet-900'
                  }`}
                >
                  Ciclo {ciclo}
                </span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};



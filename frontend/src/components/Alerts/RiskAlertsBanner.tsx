import React, { useState } from 'react';
import { RiskAlert } from '../../types/curriculum';
import { AlertTriangle, ChevronDown, ChevronUp, Flame, ShieldAlert } from 'lucide-react';

interface RiskAlertsBannerProps {
  alertas: RiskAlert[];
}

export const RiskAlertsBanner: React.FC<RiskAlertsBannerProps> = ({ alertas }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!alertas || alertas.length === 0) return null;

  const criticalCount = alertas.filter(a => a.nivel_severidad === 'CRITICA').length;
  const warningCount = alertas.filter(a => a.nivel_severidad === 'ADVERTENCIA').length;
  const infoCount = alertas.filter(a => a.nivel_severidad === 'INFORMATIVA').length;

  return (
    <div className="bg-slate-900/95 border-b border-slate-800 text-xs">
      {/* Barra de resumen colapsable */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="px-6 py-2.5 flex items-center justify-between cursor-pointer hover:bg-slate-800/50 transition-colors select-none"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-200 font-bold">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Diagnóstico de Riesgos Académicos ({alertas.length})</span>
          </div>

          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
              <span className="inline-flex items-center gap-1 bg-red-500/20 text-red-300 border border-red-500/30 px-2 py-0.5 rounded-full text-[10px] font-bold">
                <AlertTriangle className="w-3 h-3 text-red-400" />
                {criticalCount} Crítica{criticalCount > 1 ? 's' : ''}
              </span>
            )}
            {warningCount > 0 && (
              <span className="inline-flex items-center gap-1 bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full text-[10px] font-medium">
                <AlertTriangle className="w-3 h-3 text-amber-400" />
                {warningCount} Advertencia{warningCount > 1 ? 's' : ''}
              </span>
            )}
            {infoCount > 0 && (
              <span className="inline-flex items-center gap-1 bg-orange-500/20 text-orange-300 border border-orange-500/30 px-2 py-0.5 rounded-full text-[10px] font-medium hidden sm:inline-flex">
                <Flame className="w-3 h-3 text-orange-400" />
                {infoCount} Cuellos de botella
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 text-slate-400 hover:text-slate-200">
          <span className="text-[11px] font-medium">{isOpen ? 'Ocultar detalles' : 'Ver alertas detalladas'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Lista desplegable de alertas */}
      {isOpen && (
        <div className="px-6 py-4 bg-slate-950/80 border-t border-slate-800 space-y-2.5 max-h-60 overflow-y-auto">
          {alertas.map((alerta, index) => {
            const isCritica = alerta.nivel_severidad === 'CRITICA';
            const isAdvertencia = alerta.nivel_severidad === 'ADVERTENCIA';

            return (
              <div
                key={index}
                className={`p-3 rounded-lg border flex items-start gap-3 ${
                  isCritica 
                    ? 'bg-red-950/30 border-red-900/50 text-red-200' 
                    : isAdvertencia 
                    ? 'bg-amber-950/30 border-amber-900/50 text-amber-200' 
                    : 'bg-orange-950/30 border-orange-900/50 text-orange-200'
                }`}
              >
                {isCritica ? (
                  <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                ) : isAdvertencia ? (
                  <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                ) : (
                  <Flame className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                )}

                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="font-bold text-[11px] uppercase tracking-wide">
                      {alerta.tipo_alerta.replace(/_/g, ' ')}
                    </span>
                    {alerta.codigo_asignatura && (
                      <span className="font-mono text-[10px] bg-white/10 px-1.5 py-0.2 rounded font-semibold">
                        {alerta.codigo_asignatura}
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] leading-relaxed opacity-90">
                    {alerta.mensaje}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};


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
    <div className="bg-white/80 backdrop-blur-md border-b border-violet-100 text-xs shadow-sm">
      {/* Barra de resumen colapsable */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="px-6 py-2.5 flex items-center justify-between cursor-pointer hover:bg-violet-50/70 transition-colors select-none"
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-slate-800 font-bold">
            <ShieldAlert className="w-4 h-4 text-violet-600" />
            <span>Diagnóstico de Riesgos Académicos ({alertas.length})</span>
          </div>

          <div className="flex items-center gap-2">
            {criticalCount > 0 && (
                <span className="inline-flex items-center gap-1 bg-red-50 text-red-700 border border-red-200 px-2 py-0.5 rounded-full text-[10px] font-bold">
                <AlertTriangle className="w-3 h-3 text-red-600" />
                {criticalCount} Crítica{criticalCount > 1 ? 's' : ''}
              </span>
            )}
            {warningCount > 0 && (
                <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-700 border border-amber-200 px-2 py-0.5 rounded-full text-[10px] font-medium">
                <AlertTriangle className="w-3 h-3 text-amber-600" />
                {warningCount} Advertencia{warningCount > 1 ? 's' : ''}
              </span>
            )}
            {infoCount > 0 && (
                <span className="inline-flex items-center gap-1 bg-orange-50 text-orange-700 border border-orange-200 px-2 py-0.5 rounded-full text-[10px] font-medium hidden sm:inline-flex">
                <Flame className="w-3 h-3 text-orange-600" />
                {infoCount} Cuellos de botella
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1 text-slate-500 hover:text-violet-700">
          <span className="text-[11px] font-medium">{isOpen ? 'Ocultar detalles' : 'Ver alertas detalladas'}</span>
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Lista desplegable de alertas */}
      {isOpen && (
        <div className="px-6 py-4 bg-violet-50/40 border-t border-violet-100 space-y-2.5 max-h-60 overflow-y-auto">
          {alertas.map((alerta, index) => {
            const isCritica = alerta.nivel_severidad === 'CRITICA';
            const isAdvertencia = alerta.nivel_severidad === 'ADVERTENCIA';

            return (
              <div
                key={index}
                className={`p-3 rounded-lg border flex items-start gap-3 ${
                  isCritica 
                    ? 'bg-red-50 border-red-200 text-red-800' 
                    : isAdvertencia 
                    ? 'bg-amber-50 border-amber-200 text-amber-800' 
                    : 'bg-orange-50 border-orange-200 text-orange-800'
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


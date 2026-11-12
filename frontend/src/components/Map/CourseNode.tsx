import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { CourseNodeData } from '../../types/curriculum';
import { AlertTriangle, Flame, CheckCircle2, Clock, Layers, Lock, Unlock, Sparkles, Check, Info } from 'lucide-react';

export const CourseNode = memo(({ data }: NodeProps<any>) => {
  const nodeData = data as CourseNodeData;
  const {
    asignatura,
    visualState = 'HABILITADA',
    calificacion,
    numeroMatricula,
    alertas,
    isSelected,
    isConcentrationMatch,
    isHovered,
    isPrerequisiteOfHovered,
    isUnlockedByHovered,
    isDimmed,
    blockGroup,
    selectedBlockOption,
    onSelectBlockOption,
    onSelectCourse,
    onHoverCourse,
    isQuickEditMode = false,
    onQuickToggleCourse,
  } = nodeData;

  const isElectiva = asignatura.tipo === 'ELECTIVA';
  const isAprobada = visualState === 'APROBADA';
  const isEnCurso = visualState === 'EN_CURSO';
  const isHabilitada = visualState === 'HABILITADA';
  const isBloqueada = visualState === 'BLOQUEADA';
  const isReiteracion = visualState === 'REITERACION' || numeroMatricula >= 2;

  // Detección de banderas de riesgo
  const hasNotaLimite = alertas?.some(a => a.tipo_alerta === 'PRERREQUISITO_NOTA_LIMITE');
  const isBottleneck = asignatura.esCuelloBotella || alertas?.some(a => a.tipo_alerta === 'CUELLO_DE_BOTELLA');

  const handleCardClick = (e: React.MouseEvent) => {
    if (isQuickEditMode && onQuickToggleCourse) {
      e.stopPropagation();
      onQuickToggleCourse(asignatura);
    } else {
      onSelectCourse(asignatura);
    }
  };

  const handleQuickToggleBtn = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onQuickToggleCourse) {
      onQuickToggleCourse(asignatura);
    }
  };

  const handleOpenDrawerBtn = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelectCourse(asignatura);
  };

  // Clases condicionales según el estado visual
  let stateBorderClasses = 'border-2 border-violet-100 hover:border-violet-300';
  let cardBgClasses = 'bg-white';

  if (isQuickEditMode) {
    stateBorderClasses = isAprobada
      ? 'border-2 border-emerald-500 ring-2 ring-emerald-500/40 bg-emerald-50/20 hover:ring-red-400'
      : 'border-2 border-dashed border-emerald-400/80 hover:border-emerald-600 hover:ring-2 hover:ring-emerald-400/50 bg-emerald-50/10';
  } else if (isAprobada) {
    stateBorderClasses = 'border-2 border-emerald-400 bg-emerald-50/20 shadow-emerald-500/10';
  } else if (isEnCurso) {
    stateBorderClasses = 'border-2 border-indigo-400 bg-indigo-50/30 ring-2 ring-indigo-300/60 ring-offset-1';
  } else if (isReiteracion) {
    stateBorderClasses = 'border-2 border-amber-500 bg-amber-50/30 ring-2 ring-amber-400/80 animate-pulse';
  } else if (isHabilitada) {
    stateBorderClasses = 'border-2 border-amber-300 bg-amber-50/15 hover:border-amber-400 hover:shadow-amber-500/15';
  } else if (isBloqueada) {
    stateBorderClasses = 'border-2 border-slate-200 opacity-75 bg-slate-50/80 hover:opacity-95';
  }

  // Resaltado de relaciones de foco
  let focusRingClasses = '';
  if (isHovered || isSelected) {
    focusRingClasses = 'ring-4 ring-violet-600 shadow-2xl scale-[1.03] z-30';
  } else if (isPrerequisiteOfHovered) {
    focusRingClasses = 'ring-3 ring-purple-400 shadow-xl scale-[1.01] z-20';
  } else if (isUnlockedByHovered) {
    focusRingClasses = 'ring-3 ring-cyan-400 shadow-xl scale-[1.01] z-20';
  }

  return (
    <div
      onClick={handleCardClick}
      onMouseEnter={() => onHoverCourse?.(asignatura.id)}
      onMouseLeave={() => onHoverCourse?.(null)}
      title={
        isQuickEditMode
          ? isAprobada
            ? '⚡ Clic para desmarcar y dejar como pendiente'
            : '⚡ Clic para marcar como APROBADO al instante'
          : undefined
      }
      className={`
        relative w-[235px] rounded-2xl transition-all duration-200 cursor-pointer select-none text-left shadow-lg
        ${cardBgClasses}
        ${stateBorderClasses}
        ${focusRingClasses}
        ${isConcentrationMatch && !focusRingClasses ? 'ring-4 ring-violet-500/80 shadow-violet-500/30 scale-[1.02]' : ''}
        ${isDimmed ? 'opacity-25 grayscale-[40%] scale-[0.98]' : 'opacity-100'}
      `}
    >
      {/* Badge de relación cuando está en foco */}
      {isPrerequisiteOfHovered && (
        <div className="absolute -top-3 left-3 z-30 bg-purple-600 text-white text-[9px] font-bold uppercase px-2 py-0.5 rounded-full shadow flex items-center gap-1">
          ← Prerrequisito
        </div>
      )}
      {isUnlockedByHovered && (
        <div className="absolute -top-3 right-3 z-30 bg-cyan-600 text-white text-[9px] font-bold uppercase px-2 py-0.5 rounded-full shadow flex items-center gap-1">
          Desbloquea →
        </div>
      )}

      {/* Badge de Concentración Seleccionada */}
      {isConcentrationMatch && !isPrerequisiteOfHovered && !isUnlockedByHovered && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 z-20 bg-gradient-to-r from-violet-600 to-purple-600 text-white text-[9px] font-extrabold uppercase px-2.5 py-0.5 rounded-full shadow-md flex items-center gap-1 whitespace-nowrap">
          <Sparkles className="w-2.5 h-2.5 text-yellow-300" />
          Tu Concentración
        </div>
      )}

      {/* Handle entrante (invisibles para conectar líneas limpiamente sin círculos invasivos) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-0 !h-0 !min-w-0 !min-h-0 !border-0 !opacity-0 !pointer-events-none"
      />

      {/* Cabecera del Curso */}
      <div className={`
        px-3 py-2 rounded-t-[14px] flex items-center justify-between text-white
        ${isAprobada 
          ? 'bg-emerald-700' 
          : isEnCurso 
          ? 'bg-indigo-700' 
          : isReiteracion
          ? 'bg-amber-700'
          : isBloqueada 
          ? 'bg-slate-600' 
          : isElectiva 
          ? 'bg-violet-700' 
          : 'bg-slate-800'
        }
      `}>
        <div className="flex items-center gap-1.5 overflow-hidden">
          <span className="font-mono text-xs font-bold tracking-wider truncate">
            {selectedBlockOption ? selectedBlockOption.codigo : blockGroup ? 'BLOQUE' : asignatura.codigo}
          </span>
          {isElectiva && (
            <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded-lg font-medium text-violet-50">
              Electivo
            </span>
          )}
          {blockGroup && (
            <span className="text-[9px] bg-white/20 px-1.5 py-0.5 rounded-md font-semibold text-white/95 whitespace-nowrap">
              {blockGroup.minRequired > 1 ? `Mín. ${blockGroup.minRequired}` : '1 de 3'}
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <span className="text-[11px] font-semibold opacity-90 whitespace-nowrap bg-white/10 px-1.5 py-0.5 rounded">
            {asignatura.creditos} cr
          </span>

          {/* Botón de toggle rápido (1-clic aprobación) */}
          {onQuickToggleCourse && (
            <button
              onClick={handleQuickToggleBtn}
              title={isAprobada ? 'Desmarcar (volver a pendiente)' : 'Aprobar al instante (1 clic)'}
              className={`p-1 rounded-md transition-all active:scale-90 flex items-center justify-center ${
                isAprobada
                  ? 'bg-emerald-500 text-white hover:bg-red-500'
                  : 'bg-white/20 text-white hover:bg-emerald-500 hover:text-white'
              }`}
            >
              <Check className="w-3 h-3 stroke-[3]" />
            </button>
          )}

          {/* Botón de Ficha Técnica cuando está en modo rápido */}
          {isQuickEditMode && (
            <button
              onClick={handleOpenDrawerBtn}
              title="Abrir Ficha Técnica detallada"
              className="p-1 rounded-md bg-white/15 text-white/80 hover:text-white hover:bg-white/25 transition-all"
            >
              <Info className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Cuerpo de la tarjeta */}
      <div className="p-3">
        {/* Título de la Asignatura */}
        <h4 className={`text-xs font-semibold line-clamp-2 leading-snug min-h-[32px] ${blockGroup ? 'mb-1.5' : 'mb-2.5'} ${
          isBloqueada ? 'text-slate-600' : 'text-slate-800'
        }`}>
          {selectedBlockOption ? selectedBlockOption.nombre : asignatura.nombre}
        </h4>

        {/* Selector de curso para Bloques Sello UP */}
        {blockGroup && (
          <div
            className="mb-2 nodrag nopan"
            onClick={(e) => e.stopPropagation()}
            onMouseDown={(e) => e.stopPropagation()}
          >
            <select
              value={selectedBlockOption?.codigo || ''}
              onChange={(e) => onSelectBlockOption?.(asignatura.id, e.target.value || null)}
              className="w-full text-[10px] font-medium bg-violet-50/80 hover:bg-violet-50 border border-violet-200 text-violet-900 rounded-lg px-2 py-1 focus:outline-none focus:ring-1 focus:ring-violet-400 cursor-pointer truncate"
              title={`Elegir curso del ${blockGroup.title}`}
            >
              <option value="">Elegir curso del bloque...</option>
              {blockGroup.options.map((opt) => (
                <option key={opt.codigo} value={opt.codigo}>
                  {opt.codigo} — {opt.nombre}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Badges de Estado Académico (5 Estados Claros) */}
        <div className="flex flex-wrap items-center gap-1.5 mb-2">
          {isAprobada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-800 bg-emerald-100 border border-emerald-300 px-2 py-0.5 rounded-full">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              Aprobada {calificacion !== undefined && calificacion !== null ? `(${Number(calificacion).toFixed(1)})` : ''}
            </span>
          )}

          {isEnCurso && (
            <span className="inline-flex items-center gap-1 text-[10px] font-bold text-indigo-800 bg-indigo-100 border border-indigo-300 px-2 py-0.5 rounded-full">
              <Clock className="w-3 h-3 text-indigo-600 animate-spin" style={{ animationDuration: '4s' }} />
              En curso
            </span>
          )}

          {isReiteracion && (
            <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-amber-900 bg-amber-100 border border-amber-300 px-2 py-0.5 rounded-full">
              <AlertTriangle className="w-3 h-3 text-amber-600" />
              {numeroMatricula}ª Matrícula
            </span>
          )}

          {!isAprobada && !isEnCurso && !isReiteracion && isHabilitada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-amber-100/70 border border-amber-300 px-2 py-0.5 rounded-full">
              <Unlock className="w-3 h-3 text-amber-600" />
              Habilitada
            </span>
          )}

          {!isAprobada && !isEnCurso && !isReiteracion && isBloqueada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-slate-600 bg-slate-100 border border-slate-300 px-2 py-0.5 rounded-full" title="Requiere prerrequisitos pendientes">
              <Lock className="w-3 h-3 text-slate-400" />
              Bloqueada
            </span>
          )}

          {/* Cuello de botella badge */}
          {isBottleneck && (
            <span 
              title={`Condiciona el avance de ${asignatura.desbloqueaCount} materias posteriores`}
              className="inline-flex items-center gap-0.5 text-[10px] font-bold text-orange-700 bg-orange-50 border border-orange-200 px-1.5 py-0.5 rounded-full"
            >
              <Flame className="w-3 h-3 text-orange-600" />
              Cuello ({asignatura.desbloqueaCount})
            </span>
          )}

          {/* Prerrequisito Límite */}
          {hasNotaLimite && (
            <span 
              title="Prerrequisito aprobado con calificación en límite (11.00)"
              className="inline-flex items-center gap-0.5 text-[10px] font-medium text-yellow-800 bg-yellow-50 border border-yellow-200 px-1.5 py-0.5 rounded-full"
            >
              Nota Límite
            </span>
          )}
        </div>

        {/* Concentración (en electivas) o prerrequisitos resumidos */}
        <div className="pt-2 border-t border-violet-100 flex items-center justify-between text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <Layers className="w-3 h-3 text-violet-400" />
            Ciclo {asignatura.ciclo}
          </span>
          {asignatura.concentracionNombre || asignatura.concentracion ? (
            <span className="truncate max-w-[120px] text-violet-700 font-medium" title={asignatura.concentracionNombre || asignatura.concentracion || ''}>
              {asignatura.concentracionNombre || asignatura.concentracion}
            </span>
          ) : (
            <span>
              {asignatura.prerrequisitos && asignatura.prerrequisitos.length > 0
                ? `${asignatura.prerrequisitos.length} prereq.`
                : 'Sin prereq.'}
            </span>
          )}
        </div>
      </div>

      {/* Handle saliente (invisibles para conectar líneas limpiamente sin círculos invasivos) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-0 !h-0 !min-w-0 !min-h-0 !border-0 !opacity-0 !pointer-events-none"
      />
    </div>
  );
});

CourseNode.displayName = 'CourseNode';


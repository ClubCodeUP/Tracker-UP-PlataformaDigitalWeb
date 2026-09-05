import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { CourseNodeData } from '../../types/curriculum';
import { AlertTriangle, Flame, CheckCircle2, Clock, BookOpen, Layers } from 'lucide-react';

export const CourseNode = memo(({ data }: NodeProps<any>) => {
  const nodeData = data as CourseNodeData;
  const { asignatura, estado, calificacion, numeroMatricula, alertas, onSelectCourse } = nodeData;

  const isElectiva = asignatura.tipo === 'ELECTIVA';
  const isAprobada = estado === 'APROBADA';
  const isEnCurso = estado === 'EN_CURSO';
  const isDesaprobada = estado === 'DESAPROBADA';

  // Detección de banderas de riesgo
  const hasReiteracion = numeroMatricula >= 2 || alertas?.some(a => a.tipo_alerta === 'REITERACION_MATRICULA');
  const hasNotaLimite = alertas?.some(a => a.tipo_alerta === 'PRERREQUISITO_NOTA_LIMITE');
  const isBottleneck = asignatura.esCuelloBotella || alertas?.some(a => a.tipo_alerta === 'CUELLO_DE_BOTELLA');

  return (
    <div
      onClick={() => onSelectCourse(asignatura)}
      className={`
        relative w-[230px] rounded-xl bg-white transition-all duration-200 cursor-pointer select-none text-left shadow-sm hover:shadow-md
        ${isElectiva 
          ? 'border-2 border-dashed border-purple-400 hover:border-purple-600 bg-purple-50/20' 
          : 'border-2 border-solid border-slate-200 hover:border-slate-400'
        }
        ${isAprobada ? 'ring-1 ring-emerald-400/50' : ''}
        ${isEnCurso ? 'ring-2 ring-amber-400 ring-offset-1' : ''}
        ${hasReiteracion ? 'ring-2 ring-red-500 ring-offset-2 animate-pulse' : ''}
      `}
    >
      {/* Handle entrante (prerrequisitos que llegan por la izquierda) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-slate-400 !border-2 !border-white hover:!bg-blue-600"
      />

      {/* Cabecera del Curso */}
      <div className={`
        px-3 py-2 rounded-t-[10px] flex items-center justify-between
        ${isElectiva ? 'bg-purple-900 text-white' : 'bg-slate-900 text-white'}
      `}>
        <div className="flex items-center gap-1.5 overflow-hidden">
          <span className="font-mono text-xs font-bold tracking-wider truncate">
            {asignatura.codigo}
          </span>
          {isElectiva && (
            <span className="text-[10px] bg-purple-700/80 px-1.5 py-0.5 rounded font-medium text-purple-100">
              Electivo
            </span>
          )}
        </div>
        <span className="text-[11px] font-semibold opacity-90 whitespace-nowrap bg-white/10 px-1.5 py-0.5 rounded">
          {asignatura.creditos} cr
        </span>
      </div>

      {/* Cuerpo de la tarjeta */}
      <div className="p-3">
        {/* Título de la Asignatura */}
        <h4 className="text-xs font-semibold text-slate-800 line-clamp-2 leading-snug min-h-[32px] mb-2.5">
          {asignatura.nombre}
        </h4>

        {/* Badges de Estado Académico */}
        <div className="flex flex-wrap items-center gap-1.5 mb-2">
          {isAprobada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded-md">
              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
              Aprobada {calificacion !== undefined && calificacion !== null ? `(${calificacion.toFixed(1)})` : ''}
            </span>
          )}
          {isEnCurso && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-md">
              <Clock className="w-3 h-3 text-amber-600" />
              En curso
            </span>
          )}
          {isDesaprobada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-red-700 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded-md">
              <AlertTriangle className="w-3 h-3 text-red-600" />
              Desaprobada
            </span>
          )}
          {!isAprobada && !isEnCurso && !isDesaprobada && (
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded-md">
              <BookOpen className="w-3 h-3 text-slate-400" />
              Pendiente
            </span>
          )}

          {/* Cuello de botella badge (RF-16) */}
          {isBottleneck && (
            <span 
              title={`Condiciona el avance de ${asignatura.desbloqueaCount} materias posteriores`}
              className="inline-flex items-center gap-0.5 text-[10px] font-bold text-orange-700 bg-orange-100/80 border border-orange-300 px-1.5 py-0.5 rounded-md"
            >
              <Flame className="w-3 h-3 text-orange-600 animate-bounce" />
              Cuello ({asignatura.desbloqueaCount})
            </span>
          )}

          {/* Reiteración de matrícula (RF-13) */}
          {hasReiteracion && (
            <span className="inline-flex items-center gap-0.5 text-[10px] font-bold text-red-700 bg-red-100 border border-red-300 px-1.5 py-0.5 rounded-md">
              <AlertTriangle className="w-3 h-3 text-red-600" />
              {numeroMatricula}ª Matrícula
            </span>
          )}

          {/* Prerrequisito Límite (RF-14) */}
          {hasNotaLimite && (
            <span 
              title="Prerrequisito aprobado con calificación en límite (11.00)"
              className="inline-flex items-center gap-0.5 text-[10px] font-medium text-yellow-800 bg-yellow-100 border border-yellow-300 px-1.5 py-0.5 rounded-md"
            >
              Nota Límite
            </span>
          )}
        </div>

        {/* Concentración (en electivas) o prerrequisitos resumidos */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <Layers className="w-3 h-3 text-slate-400" />
            Ciclo {asignatura.ciclo}
          </span>
          {asignatura.concentracionNombre ? (
            <span className="truncate max-w-[120px] text-purple-700 font-medium" title={asignatura.concentracionNombre}>
              {asignatura.concentracionNombre}
            </span>
          ) : (
            <span>
              {asignatura.prerrequisitos.length > 0
                ? `${asignatura.prerrequisitos.length} prereq.`
                : 'Sin prereq.'}
            </span>
          )}
        </div>
      </div>

      {/* Handle saliente (cursos posteriores que salen por la derecha) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-slate-400 !border-2 !border-white hover:!bg-blue-600"
      />
    </div>
  );
});

CourseNode.displayName = 'CourseNode';


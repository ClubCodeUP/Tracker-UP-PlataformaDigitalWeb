import React, { useMemo, useState, useCallback } from 'react';
import {
  ReactFlow,
  ReactFlowProvider,
  useReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  Node,
  Edge,
  OnNodesChange,
  OnEdgesChange,
  Viewport,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CourseNode } from './CourseNode';
import { OrthogonalEdge } from './OrthogonalEdge';
import { CycleHeader } from './CycleHeader';
import { QuickEditToolbar } from './QuickEditToolbar';
import { Asignatura } from '../../types/curriculum';
import { MapLegend } from './MapLegend';
import { CYCLE_COL_WIDTH, MAP_OFFSET_X } from './mapConstants';

interface CurriculumMapProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange?: OnNodesChange;
  onEdgesChange?: OnEdgesChange;
  maxCiclos?: number;
  selectedConcentrationName?: string | null;
  isQuickEditMode?: boolean;
  onCloseQuickEdit?: () => void;
  defaultGrade?: number;
  onChangeDefaultGrade?: (grade: number) => void;
  allCourses?: Asignatura[];
  onApproveCycle?: (ciclo: number) => void;
  onClearCycle?: (ciclo: number) => void;
  periodoIngreso?: string;
}

// Componente interno que tiene acceso al contexto useReactFlow
const CurriculumMapInner: React.FC<CurriculumMapProps> = ({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  maxCiclos = 10,
  selectedConcentrationName,
  isQuickEditMode = false,
  onCloseQuickEdit,
  defaultGrade = 14,
  onChangeDefaultGrade,
  allCourses = [],
  onApproveCycle,
  onClearCycle,
  periodoIngreso,
}) => {
  const { setViewport } = useReactFlow();
  const [currentViewport, setCurrentViewport] = useState<Viewport>({ x: 20, y: 20, zoom: 0.85 });

  // Registrar los tipos personalizados memoizados
  const nodeTypes = useMemo(() => ({ courseNode: CourseNode as any }), []);
  const edgeTypes = useMemo(() => ({ orthogonal: OrthogonalEdge as any }), []);

  // Manejador del cambio de viewport (zoom / pan)
  const handleViewportChange = useCallback((viewport: Viewport) => {
    setCurrentViewport(viewport);
  }, []);

  // Función para saltar suavemente a un ciclo específico
  const jumpToCiclo = useCallback(
    (ciclo: number) => {
      const zoom = currentViewport.zoom || 0.85;
      const targetCycleX = (ciclo - 1) * CYCLE_COL_WIDTH + MAP_OFFSET_X;
      const newX = 40 - targetCycleX * zoom;
      setViewport({ x: newX, y: currentViewport.y, zoom }, { duration: 400 });
    },
    [currentViewport, setViewport]
  );

  // Barra de progreso de ciclos
  const totalCiclos = Math.max(1, maxCiclos);
  const zoom = currentViewport.zoom || 0.85;
  // Ciclo visible actual estimado
  const approxVisibleCiclo = Math.min(
    totalCiclos,
    Math.max(1, Math.round((Math.abs(currentViewport.x) / (CYCLE_COL_WIDTH * zoom)) + 1))
  );

  return (
    <div className="relative w-full h-full bg-[#FBFBFE] overflow-hidden flex flex-col select-none">
      {/* 1. Cabecera interactiva y sincronizada de ciclos */}
      <CycleHeader
        maxCiclos={maxCiclos}
        viewportX={currentViewport.x}
        zoom={currentViewport.zoom}
        activeCiclo={approxVisibleCiclo}
        onJumpToCiclo={jumpToCiclo}
      />

      {/* Barra Flotante de Edición Rápida */}
      <QuickEditToolbar
        isOpen={isQuickEditMode}
        onClose={onCloseQuickEdit || (() => {})}
        defaultGrade={defaultGrade}
        onChangeDefaultGrade={onChangeDefaultGrade || (() => {})}
        allCourses={allCourses}
        onApproveCycle={onApproveCycle || (() => {})}
        onClearCycle={onClearCycle || (() => {})}
        periodoIngreso={periodoIngreso}
      />

      {/* 2. Contenedor React Flow */}
      <div className="flex-1 w-full h-full relative">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onViewportChange={handleViewportChange}
          minZoom={0.3}
          maxZoom={1.5}
          defaultViewport={{ x: 20, y: 20, zoom: 0.85 }}
          fitViewOptions={{ padding: 0.15 }}
          panOnScroll={true}
          panOnDrag={true}
          zoomOnScroll={false}
          zoomOnPinch={true}
          preventScrolling={false}
          proOptions={{ hideAttribution: true }}
        >
          {/* Fondo cuadriculado moderno */}
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1.5}
            color="#DDD6FE"
          />

          {/* Controles de navegación y zoom en la esquina inferior izquierda */}
          <Controls
            showInteractive={false}
            position="bottom-left"
            className="!bg-white/90 !border-violet-200 !shadow-lg shadow-purple-500/10 [&>button]:!bg-white [&>button]:!border-violet-100 [&>button]:!text-violet-700 hover:[&>button]:!bg-violet-50"
          />
        </ReactFlow>
      </div>

      {/* 3. Barra de Desplazamiento Horizontal Inferior Estilo Scrollbar */}
      <div className="bg-white/95 border-t border-violet-100 px-6 py-2 flex items-center gap-4 z-20">
        <span className="text-[11px] font-semibold text-slate-500 whitespace-nowrap">
          Desplazamiento horizontal:
        </span>
        <div className="relative flex-1 flex items-center">
          <input
            type="range"
            min={0}
            max={Math.max(1, (totalCiclos - 1) * CYCLE_COL_WIDTH)}
            step={10}
            value={Math.min(
              Math.max(0, -currentViewport.x / (currentViewport.zoom || 0.85)),
              (totalCiclos - 1) * CYCLE_COL_WIDTH
            )}
            onChange={(e) => {
              const scrollPos = Number(e.target.value);
              const zoomVal = currentViewport.zoom || 0.85;
              setViewport({
                x: -scrollPos * zoomVal + 20,
                y: currentViewport.y,
                zoom: zoomVal,
              });
            }}
            className="w-full h-1.5 bg-violet-100 rounded-lg appearance-none cursor-pointer accent-violet-600 focus:outline-none"
          />
        </div>
        <span className="text-xs font-mono font-medium text-violet-700 bg-violet-50 px-2 py-0.5 rounded border border-violet-200 whitespace-nowrap">
          Ciclo {approxVisibleCiclo} de {totalCiclos}
        </span>
      </div>

      {/* Leyenda flotante fija */}
      <MapLegend selectedConcentrationName={selectedConcentrationName} />
    </div>
  );
};

export const CurriculumMap: React.FC<CurriculumMapProps> = (props) => {
  return (
    <ReactFlowProvider>
      <CurriculumMapInner {...props} />
    </ReactFlowProvider>
  );
};

import React, { useMemo } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  Node,
  Edge,
  OnNodesChange,
  OnEdgesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { CourseNode } from './CourseNode';
import { CycleHeader } from './CycleHeader';

interface CurriculumMapProps {
  nodes: Node[];
  edges: Edge[];
  onNodesChange?: OnNodesChange;
  onEdgesChange?: OnEdgesChange;
  maxCiclos?: number;
}

export const CurriculumMap: React.FC<CurriculumMapProps> = ({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  maxCiclos = 5,
}) => {
  // Registrar el tipo de nodo personalizado memoizado
  const nodeTypes = useMemo(() => ({ courseNode: CourseNode as any }), []);

  return (
    <div className="relative w-full h-full bg-slate-950 overflow-hidden flex flex-col">
      {/* Cabecera fija de ciclos académicos */}
      <CycleHeader maxCiclos={maxCiclos} />

      {/* Contenedor React Flow */}
      <div className="flex-1 w-full h-full">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          minZoom={0.3}
          maxZoom={1.5}
          defaultViewport={{ x: 20, y: 20, zoom: 0.85 }}
          fitViewOptions={{ padding: 0.15 }}
          proOptions={{ hideAttribution: true }}
        >
          {/* Fondo cuadriculado moderno */}
          <Background
            variant={BackgroundVariant.Dots}
            gap={20}
            size={1.5}
            color="#334155"
          />

          {/* Controles de navegación y zoom */}
          <Controls
            showInteractive={false}
            className="!bg-slate-900 !border-slate-700 !shadow-lg [&>button]:!bg-slate-800 [&>button]:!border-slate-700 [&>button]:!text-slate-200 hover:[&>button]:!bg-slate-700"
          />

          {/* MiniMap para orientación rápida */}
          <MiniMap
            zoomable
            pannable
            nodeStrokeWidth={3}
            nodeColor={(node) => {
              const data = node.data as any;
              if (data?.estado === 'APROBADA') return '#10b981';
              if (data?.estado === 'EN_CURSO') return '#f59e0b';
              if (data?.asignatura?.tipo === 'ELECTIVA') return '#a855f7';
              return '#64748b';
            }}
            className="!bg-slate-900/90 !border !border-slate-700 !rounded-xl !shadow-xl hidden md:block"
          />
        </ReactFlow>
      </div>
    </div>
  );
};


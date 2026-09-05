import { useMemo, useState } from 'react';
import { Node, Edge, MarkerType } from '@xyflow/react';
import { Asignatura, HistorialEntry, RiskAlert } from '../types/curriculum';

interface UseCurriculumMapProps {
  malla: Asignatura[];
  historial: HistorialEntry[];
  alertas: RiskAlert[];
}

export function useCurriculumMap({ malla, historial, alertas }: UseCurriculumMapProps) {
  const [selectedCourse, setSelectedCourse] = useState<Asignatura | null>(null);

  // Mapeo rápido de historial por id de asignatura
  const historyMap = useMemo(() => {
    const map = new Map<number, HistorialEntry>();
    for (const h of historial) {
      map.set(h.asignaturaId, h);
    }
    return map;
  }, [historial]);

  // Mapeo de alertas por código de asignatura
  const alertMap = useMemo(() => {
    const map = new Map<string, RiskAlert[]>();
    for (const a of alertas) {
      if (a.codigo_asignatura) {
        const existing = map.get(a.codigo_asignatura) || [];
        existing.push(a);
        map.set(a.codigo_asignatura, existing);
      }
    }
    return map;
  }, [alertas]);

  // Generación matemática determinística ultra-rápida de Nodos y Aristas (O(N) < 50ms)
  const { nodes, edges } = useMemo(() => {
    const cycleCounters = new Map<number, number>();
    const generatedNodes: Node[] = [];
    const generatedEdges: Edge[] = [];
    const courseCodeToId = new Map<string, number>();

    // 1. Crear Nodos
    for (const asig of malla) {
      courseCodeToId.set(asig.codigo, asig.id);

      const cycleIndex = cycleCounters.get(asig.ciclo) || 0;
      cycleCounters.set(asig.ciclo, cycleIndex + 1);

      // Posicionamiento en cuadrícula por ciclos: 280px horizontal, 170px vertical
      const x = (asig.ciclo - 1) * 290 + 30;
      const y = cycleIndex * 170 + 80;

      const userHistory = historyMap.get(asig.id);
      const courseAlerts = alertMap.get(asig.codigo) || [];

      generatedNodes.push({
        id: String(asig.id),
        type: 'courseNode',
        position: { x, y },
        data: {
          asignatura: asig,
          estado: userHistory?.estado || 'PENDIENTE',
          calificacion: userHistory?.calificacion,
          numeroMatricula: userHistory?.numeroMatricula || 1,
          alertas: courseAlerts,
          onSelectCourse: (selected: Asignatura) => setSelectedCourse(selected),
        },
      });
    }

    // 2. Crear Aristas de Prerrequisitos (Dependencias)
    for (const asig of malla) {
      for (const prereq of asig.prerrequisitos) {
        const sourceId = courseCodeToId.get(prereq.codigo);
        if (sourceId !== undefined) {
          const isPrereqAprobado = prereq.aprobado;

          generatedEdges.push({
            id: `edge-${sourceId}-${asig.id}`,
            source: String(sourceId),
            target: String(asig.id),
            type: 'smoothstep',
            animated: !isPrereqAprobado, // Animado si aún está pendiente
            style: {
              stroke: isPrereqAprobado ? '#10b981' : '#94a3b8',
              strokeWidth: isPrereqAprobado ? 2 : 1.5,
              opacity: isPrereqAprobado ? 0.9 : 0.6,
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: isPrereqAprobado ? '#10b981' : '#94a3b8',
              width: 14,
              height: 14,
            },
          });
        }
      }
    }

    return { nodes: generatedNodes, edges: generatedEdges };
  }, [malla, historyMap, alertMap]);

  return {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory: selectedCourse ? historyMap.get(selectedCourse.id) : undefined,
  };
}


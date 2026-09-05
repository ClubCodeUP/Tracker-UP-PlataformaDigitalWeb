import { useMemo, useState } from 'react';
import { Node, Edge, MarkerType } from '@xyflow/react';
import { Asignatura, HistorialEntry, RiskAlert } from '../types/curriculum';

interface UseCurriculumMapProps {
  malla: Asignatura[];
  historial: HistorialEntry[];
  alertas: RiskAlert[];
}

export function useCurriculumMap({ malla, historial, alertas }: UseCurriculumMapProps) {
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);

  // Mapeo rápido de historial por id de asignatura
  const historyMap = useMemo(() => {
    const map = new Map<number, HistorialEntry>();
    for (const h of historial) {
      map.set(h.asignaturaId, h);
    }
    return map;
  }, [historial]);

  // Mapeo rápido de código de asignatura a ID
  const courseCodeToId = useMemo(() => {
    const map = new Map<string, number>();
    for (const c of malla) {
      map.set(c.codigo, c.id);
    }
    return map;
  }, [malla]);

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

    // 1. Crear Nodos
    for (const asig of malla) {
      const cycleIndex = cycleCounters.get(asig.ciclo) || 0;
      cycleCounters.set(asig.ciclo, cycleIndex + 1);

      // Posicionamiento en cuadrícula por ciclos: 290px horizontal, 170px vertical
      const x = (asig.ciclo - 1) * 290 + 30;
      const y = cycleIndex * 170 + 80;

      const userHistory = historyMap.get(asig.id);
      const courseAlerts = alertMap.get(asig.codigo) || [];

      // Enriquecer los prerrequisitos con el historial del estudiante
      const enrichedPrereqs = (asig.prerrequisitos || []).map((p) => {
        const pId = (p as any).id || courseCodeToId.get(p.codigo);
        const pHist = pId ? historyMap.get(pId) : undefined;
        const isAprobado = p.aprobado || pHist?.estado === 'APROBADA';
        return {
          ...p,
          id: pId,
          aprobado: isAprobado,
          calificacion: p.calificacion ?? pHist?.calificacion ?? undefined,
        };
      });

      const enrichedAsig: Asignatura = {
        ...asig,
        prerrequisitos: enrichedPrereqs,
      };

      generatedNodes.push({
        id: String(asig.id),
        type: 'courseNode',
        position: { x, y },
        data: {
          asignatura: enrichedAsig,
          estado: userHistory?.estado || 'PENDIENTE',
          calificacion: userHistory?.calificacion,
          numeroMatricula: userHistory?.numeroMatricula || 1,
          alertas: courseAlerts,
          onSelectCourse: (selected: Asignatura) => setSelectedCourseId(selected.id),
        },
      });
    }

    // 2. Crear Aristas de Prerrequisitos (Dependencias)
    for (const asig of malla) {
      for (const prereq of asig.prerrequisitos) {
        const sourceId = (prereq as any).id || courseCodeToId.get(prereq.codigo);
        if (sourceId !== undefined) {
          const sourceHistory = historyMap.get(sourceId);
          const isPrereqAprobado = prereq.aprobado || sourceHistory?.estado === 'APROBADA';

          generatedEdges.push({
            id: `edge-${sourceId}-${asig.id}`,
            source: String(sourceId),
            target: String(asig.id),
            type: 'smoothstep',
            animated: !isPrereqAprobado, // Animado si aún está pendiente
            style: {
              stroke: isPrereqAprobado ? '#10b981' : '#94a3b8',
              strokeWidth: isPrereqAprobado ? 2.5 : 1.5,
              opacity: isPrereqAprobado ? 0.95 : 0.6,
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
  }, [malla, historyMap, alertMap, courseCodeToId]);

  const selectedCourse = useMemo(() => {
    if (selectedCourseId === null) return null;
    const asig = malla.find((c) => c.id === selectedCourseId);
    if (!asig) return null;

    const enrichedPrereqs = (asig.prerrequisitos || []).map((p) => {
      const pId = (p as any).id || courseCodeToId.get(p.codigo);
      const pHist = pId ? historyMap.get(pId) : undefined;
      const isAprobado = p.aprobado || pHist?.estado === 'APROBADA';
      return {
        ...p,
        id: pId,
        aprobado: isAprobado,
        calificacion: p.calificacion ?? pHist?.calificacion ?? undefined,
      };
    });

    return {
      ...asig,
      prerrequisitos: enrichedPrereqs,
    };
  }, [selectedCourseId, malla, historyMap, courseCodeToId]);

  const setSelectedCourse = (course: Asignatura | null) => {
    setSelectedCourseId(course ? course.id : null);
  };

  return {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory: selectedCourse ? historyMap.get(selectedCourse.id) : undefined,
  };
}


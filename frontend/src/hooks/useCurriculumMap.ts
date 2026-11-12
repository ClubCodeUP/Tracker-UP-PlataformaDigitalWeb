import { useCallback, useMemo, useState } from 'react';
import { Node, Edge, MarkerType } from '@xyflow/react';
import { Asignatura, HistorialEntry, RiskAlert, VisualCourseState } from '../types/curriculum';
import { getBlockGroupForCourse } from '../data/blockCourses';
import {
  CYCLE_COL_WIDTH,
  ROW_HEIGHT,
  MAP_OFFSET_X,
  MAP_OFFSET_Y,
} from '../components/Map/mapConstants';

const BLOCK_STORAGE_KEY = 'tracker_up_block_selections';

function loadBlockSelections(): Record<number, string> {
  try {
    const raw = localStorage.getItem(BLOCK_STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

interface UseCurriculumMapProps {
  malla: Asignatura[];
  historial: HistorialEntry[];
  alertas: RiskAlert[];
  selectedConcentrationId?: number | null;
  isQuickEditMode?: boolean;
  onQuickToggleCourse?: (asignatura: Asignatura) => void;
}

export function useCurriculumMap({
  malla,
  historial,
  alertas,
  selectedConcentrationId,
  isQuickEditMode = false,
  onQuickToggleCourse,
}: UseCurriculumMapProps) {
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [hoveredCourseId, setHoveredCourseId] = useState<number | null>(null);
  const [blockSelections, setBlockSelections] = useState<Record<number, string>>(loadBlockSelections);

  const handleSelectBlockOption = useCallback((asignaturaId: number, optionCodigo: string | null) => {
    setBlockSelections((prev) => {
      const next = { ...prev };
      if (optionCodigo) {
        next[asignaturaId] = optionCodigo;
      } else {
        delete next[asignaturaId];
      }
      try {
        localStorage.setItem(BLOCK_STORAGE_KEY, JSON.stringify(next));
      } catch {
        // Ignorar errores de almacenamiento
      }
      return next;
    });
  }, []);

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

  // Generación matemática determinística de Nodos y Aristas con enfoque dinámico
  const { nodes, edges } = useMemo(() => {
    // Curso enfocado (por hover o por selección)
    const activeFocusId = hoveredCourseId ?? selectedCourseId;

    // Calcular dependencias hacia atrás (prerrequisitos) y hacia adelante (desbloqueados) para activeFocusId
    const incomingPrereqIds = new Set<number>();
    const outgoingUnlockedIds = new Set<number>();

    if (activeFocusId !== null) {
      // 1. Cursos que son prerrequisitos del curso activo
      const activeCourse = malla.find((c) => c.id === activeFocusId);
      if (activeCourse) {
        for (const p of activeCourse.prerrequisitos || []) {
          const pId = (p as any).id || courseCodeToId.get(p.codigo);
          if (pId !== undefined) incomingPrereqIds.add(pId);
        }
      }

      // 2. Cursos que tienen a activeFocusId como prerrequisito (los que desbloquea)
      for (const course of malla) {
        for (const p of course.prerrequisitos || []) {
          const pId = (p as any).id || courseCodeToId.get(p.codigo);
          if (pId === activeFocusId) {
            outgoingUnlockedIds.add(course.id);
            break;
          }
        }
      }
    }

    const hasFocus = activeFocusId !== null;
    const generatedNodes: Node[] = [];
    const generatedEdges: Edge[] = [];

    // 1. Agrupar y ordenar cursos por ciclo (algoritmo barycenter para minimizar cruces de flechas)
    const coursesByCycle = new Map<number, Asignatura[]>();
    for (const asig of malla) {
      const list = coursesByCycle.get(asig.ciclo) || [];
      list.push(asig);
      coursesByCycle.set(asig.ciclo, list);
    }

    const sortedCycles = Array.from(coursesByCycle.keys()).sort((a, b) => a - b);
    const nodeLayoutMap = new Map<number, { ciclo: number; rowIndex: number; x: number; y: number }>();

    for (const ciclo of sortedCycles) {
      const cycleCourses = coursesByCycle.get(ciclo) || [];
      const scored = cycleCourses.map((asig, originalIdx) => {
        const prereqRows: number[] = [];
        for (const p of asig.prerrequisitos || []) {
          const pId = (p as any).id || courseCodeToId.get(p.codigo);
          if (pId !== undefined) {
            const layout = nodeLayoutMap.get(pId);
            if (layout) prereqRows.push(layout.rowIndex);
          }
        }
        const barycenter =
          prereqRows.length > 0
            ? prereqRows.reduce((sum, r) => sum + r, 0) / prereqRows.length
            : originalIdx;
        return { asig, barycenter, originalIdx };
      });

      scored.sort((a, b) => {
        if (Math.abs(a.barycenter - b.barycenter) > 0.01) {
          return a.barycenter - b.barycenter;
        }
        return a.originalIdx - b.originalIdx;
      });

      scored.forEach(({ asig }, rowIndex) => {
        const x = (asig.ciclo - 1) * CYCLE_COL_WIDTH + MAP_OFFSET_X;
        const y = rowIndex * ROW_HEIGHT + MAP_OFFSET_Y;
        nodeLayoutMap.set(asig.id, { ciclo: asig.ciclo, rowIndex, x, y });
      });
    }

    // 2. Crear Nodos con sus posiciones optimizadas
    for (const asig of malla) {
      const layout = nodeLayoutMap.get(asig.id)!;
      const { x, y } = layout;

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

      // Determinar estado visual enriquecido de 5 niveles
      const isAprobada = userHistory?.estado === 'APROBADA';
      const isEnCurso = userHistory?.estado === 'EN_CURSO';
      const isReiteracion = !isAprobada && ((userHistory?.numeroMatricula || 1) >= 2 || userHistory?.estado === 'DESAPROBADA');
      const allPrereqsMet = enrichedPrereqs.length === 0 || enrichedPrereqs.every((p) => p.aprobado);

      let visualState: VisualCourseState = 'HABILITADA';
      if (isAprobada) {
        visualState = 'APROBADA';
      } else if (isEnCurso) {
        visualState = 'EN_CURSO';
      } else if (isReiteracion) {
        visualState = 'REITERACION';
      } else if (allPrereqsMet) {
        visualState = 'HABILITADA';
      } else {
        visualState = 'BLOQUEADA';
      }

      const isConcentrationMatch = Boolean(
        selectedConcentrationId && asig.concentracionId === selectedConcentrationId
      );

      const isHovered = activeFocusId === asig.id;
      const isPrerequisiteOfHovered = incomingPrereqIds.has(asig.id);
      const isUnlockedByHovered = outgoingUnlockedIds.has(asig.id);
      const isRelated = isHovered || isPrerequisiteOfHovered || isUnlockedByHovered;
      const isDimmed = hasFocus && !isRelated;

      const blockGroup = getBlockGroupForCourse(asig.codigo, asig.nombre);
      const selectedOptionCode = blockSelections[asig.id];
      const selectedBlockOption =
        blockGroup?.options.find((opt) => opt.codigo === selectedOptionCode) || null;

      generatedNodes.push({
        id: String(asig.id),
        type: 'courseNode',
        position: { x, y },
        zIndex: isHovered || selectedCourseId === asig.id ? 30 : 10,
        data: {
          asignatura: enrichedAsig,
          estado: userHistory?.estado || 'PENDIENTE',
          visualState,
          calificacion: userHistory?.calificacion,
          numeroMatricula: userHistory?.numeroMatricula || 1,
          alertas: courseAlerts,
          isSelected: selectedCourseId === asig.id,
          isConcentrationMatch,
          isHovered,
          isPrerequisiteOfHovered,
          isUnlockedByHovered,
          isDimmed,
          blockGroup,
          selectedBlockOption,
          onSelectBlockOption: handleSelectBlockOption,
          onSelectCourse: (selected: Asignatura) => setSelectedCourseId(selected.id),
          onHoverCourse: (id: number | null) => setHoveredCourseId(id),
          isQuickEditMode,
          onQuickToggleCourse,
        },
      });
    }

    // 3. Crear Aristas Ortogonales con Carriles Separados (evita superposición)
    interface RawEdgeSpec {
      sourceId: number;
      targetId: number;
      isPrereqAprobado: boolean;
      isIncomingEdge: boolean;
      isFocusedEdge: boolean;
      sourceCycle: number;
      targetCycle: number;
      sourceRow: number;
      targetRow: number;
      skipCycles: number;
    }

    const rawEdges: RawEdgeSpec[] = [];
    for (const asig of malla) {
      for (const prereq of asig.prerrequisitos) {
        const sourceId = (prereq as any).id || courseCodeToId.get(prereq.codigo);
        if (sourceId !== undefined) {
          const sourceLayout = nodeLayoutMap.get(sourceId);
          const targetLayout = nodeLayoutMap.get(asig.id);
          if (!sourceLayout || !targetLayout) continue;

          const sourceHistory = historyMap.get(sourceId);
          const isPrereqAprobado = prereq.aprobado || sourceHistory?.estado === 'APROBADA';
          const isIncomingEdge = activeFocusId === asig.id && incomingPrereqIds.has(sourceId);
          const isOutgoingEdge = activeFocusId === sourceId && outgoingUnlockedIds.has(asig.id);
          const isFocusedEdge = isIncomingEdge || isOutgoingEdge;

          rawEdges.push({
            sourceId,
            targetId: asig.id,
            isPrereqAprobado,
            isIncomingEdge,
            isFocusedEdge,
            sourceCycle: sourceLayout.ciclo,
            targetCycle: targetLayout.ciclo,
            sourceRow: sourceLayout.rowIndex,
            targetRow: targetLayout.rowIndex,
            skipCycles: targetLayout.ciclo - sourceLayout.ciclo,
          });
        }
      }
    }

    // Agrupar aristas adyacentes por pasillo vertical (entre sourceCycle y sourceCycle + 1)
    const adjacentByCorridor = new Map<number, RawEdgeSpec[]>();
    // Agrupar aristas de largo alcance por corredor horizontal (fila base)
    const longSpanByRow = new Map<number, RawEdgeSpec[]>();

    for (const spec of rawEdges) {
      if (spec.skipCycles <= 1) {
        const list = adjacentByCorridor.get(spec.sourceCycle) || [];
        list.push(spec);
        adjacentByCorridor.set(spec.sourceCycle, list);
      } else {
        const baseRow = Math.min(spec.sourceRow, spec.targetRow);
        const list = longSpanByRow.get(baseRow) || [];
        list.push(spec);
        longSpanByRow.set(baseRow, list);
      }
    }

    const edgeDataMap = new Map<string, Record<string, number>>();

    // Asignar carriles verticales escalonados para aristas adyacentes
    for (const [, specs] of adjacentByCorridor) {
      specs.sort((a, b) => a.sourceRow - b.sourceRow || a.targetRow - b.targetRow);
      const total = specs.length;
      specs.forEach((spec, idx) => {
        const rawOffset = (idx - (total - 1) / 2) * 10;
        const laneOffset = Math.max(-38, Math.min(38, rawOffset));
        edgeDataMap.set(`${spec.sourceId}-${spec.targetId}`, {
          skipCycles: spec.skipCycles,
          laneOffset,
        });
      });
    }

    // Asignar pasillos horizontales escalonados para aristas de largo alcance
    for (const [baseRow, specs] of longSpanByRow) {
      specs.sort((a, b) => a.sourceCycle - b.sourceCycle || a.targetCycle - b.targetCycle);
      const total = specs.length;
      // Centro del pasillo vertical entre baseRow y baseRow + 1
      const baseCorridorY = MAP_OFFSET_Y + baseRow * ROW_HEIGHT + 172;
      specs.forEach((spec, idx) => {
        const rawHOffset = (idx - (total - 1) / 2) * 8;
        const hOffset = Math.max(-20, Math.min(20, rawHOffset));
        edgeDataMap.set(`${spec.sourceId}-${spec.targetId}`, {
          skipCycles: spec.skipCycles,
          corridorY: baseCorridorY + hOffset,
          exitOffset: 24 + (idx % 4) * 10,
          enterOffset: 24 + ((idx + 2) % 4) * 10,
        });
      });
    }

    for (const spec of rawEdges) {
      const { sourceId, targetId, isPrereqAprobado, isIncomingEdge, isFocusedEdge } = spec;

      const strokeColor = isFocusedEdge
        ? isIncomingEdge
          ? '#7c3aed' // Violeta nítido para prerrequisitos directos entrantes
          : '#0284c7' // Azul cielo nítido para materias que desbloquea
        : isPrereqAprobado
        ? '#94a3b8' // Slate legible para completadas
        : '#cbd5e1'; // Gris suave para pendientes

      const strokeWidth = isFocusedEdge ? 3 : 1.75;
      const opacity = hasFocus ? (isFocusedEdge ? 1 : 0.08) : 0.65;
      const zIndex = isFocusedEdge ? 25 : 0;

      generatedEdges.push({
        id: `edge-${sourceId}-${targetId}`,
        source: String(sourceId),
        target: String(targetId),
        type: 'orthogonal',
        animated: isFocusedEdge && !isPrereqAprobado,
        zIndex,
        data: edgeDataMap.get(`${sourceId}-${targetId}`),
        style: {
          stroke: strokeColor,
          strokeWidth,
          opacity,
          transition: 'opacity 0.2s ease, stroke 0.2s ease, stroke-width 0.2s ease',
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: isFocusedEdge ? 16 : 11,
          height: isFocusedEdge ? 16 : 11,
        },
      });
    }

    return { nodes: generatedNodes, edges: generatedEdges };
  }, [malla, historyMap, alertMap, courseCodeToId, selectedConcentrationId, hoveredCourseId, selectedCourseId, blockSelections, handleSelectBlockOption, isQuickEditMode, onQuickToggleCourse]);

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

  const reloadBlockSelections = useCallback(() => {
    setBlockSelections(loadBlockSelections());
  }, []);

  return {
    nodes,
    edges,
    selectedCourse,
    setSelectedCourse,
    selectedCourseHistory: selectedCourse ? historyMap.get(selectedCourse.id) : undefined,
    hoveredCourseId,
    setHoveredCourseId,
    reloadBlockSelections,
  };
}


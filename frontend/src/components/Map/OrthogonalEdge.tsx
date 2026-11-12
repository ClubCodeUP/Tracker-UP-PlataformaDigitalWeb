import React from 'react';
import { BaseEdge, EdgeProps, getSmoothStepPath } from '@xyflow/react';

export interface OrthogonalEdgeData {
  laneOffset?: number;
  skipCycles?: number;
  corridorY?: number;
  exitOffset?: number;
  enterOffset?: number;
}

interface Point {
  x: number;
  y: number;
}

/**
 * Construye un trazado SVG ortogonal (ángulos rectos) con esquinas sutilmente redondeadas.
 */
function buildRoundedOrthogonalPath(rawPoints: Point[], borderRadius = 6): string {
  if (rawPoints.length < 2) return '';

  // Eliminar puntos duplicados consecutivos
  const points: Point[] = [rawPoints[0]];
  for (let i = 1; i < rawPoints.length; i++) {
    const prev = points[points.length - 1];
    const curr = rawPoints[i];
    if (Math.abs(curr.x - prev.x) > 0.5 || Math.abs(curr.y - prev.y) > 0.5) {
      points.push(curr);
    }
  }

  if (points.length < 2) return '';
  if (points.length === 2) {
    return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  }

  const parts: string[] = [`M ${points[0].x} ${points[0].y}`];

  for (let i = 1; i < points.length - 1; i++) {
    const p0 = points[i - 1];
    const p1 = points[i];
    const p2 = points[i + 1];

    const dx1 = p1.x - p0.x;
    const dy1 = p1.y - p0.y;
    const dx2 = p2.x - p1.x;
    const dy2 = p2.y - p1.y;

    const len1 = Math.hypot(dx1, dy1);
    const len2 = Math.hypot(dx2, dy2);

    // Si los segmentos son colineales o muy cortos, ir directo al vértice
    if (len1 < 1 || len2 < 1 || (dx1 === 0 && dx2 === 0) || (dy1 === 0 && dy2 === 0)) {
      parts.push(`L ${p1.x} ${p1.y}`);
      continue;
    }

    const r = Math.min(borderRadius, len1 / 2, len2 / 2);

    const ux1 = dx1 / len1;
    const uy1 = dy1 / len1;
    const ux2 = dx2 / len2;
    const uy2 = dy2 / len2;

    const cornerStartX = p1.x - ux1 * r;
    const cornerStartY = p1.y - uy1 * r;
    const cornerEndX = p1.x + ux2 * r;
    const cornerEndY = p1.y + uy2 * r;

    parts.push(`L ${cornerStartX} ${cornerStartY}`);
    parts.push(`Q ${p1.x} ${p1.y} ${cornerEndX} ${cornerEndY}`);
  }

  const last = points[points.length - 1];
  parts.push(`L ${last.x} ${last.y}`);

  return parts.join(' ');
}

export const OrthogonalEdge: React.FC<EdgeProps> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  data,
}) => {
  const edgeData = (data || {}) as OrthogonalEdgeData;
  const { laneOffset = 0, skipCycles = 1, corridorY, exitOffset = 32, enterOffset = 32 } = edgeData;

  let edgePath = '';

  if (targetX > sourceX + 20) {
    if (skipCycles > 1 && corridorY !== undefined) {
      // Arista de largo alcance: sale al pasillo derecho, baja/sube al corredor horizontal entre filas y entra antes del destino
      const x1 = Math.min(sourceX + exitOffset, targetX - 24);
      const x2 = Math.max(targetX - enterOffset, x1 + 12);

      edgePath = buildRoundedOrthogonalPath([
        { x: sourceX, y: sourceY },
        { x: x1, y: sourceY },
        { x: x1, y: corridorY },
        { x: x2, y: corridorY },
        { x: x2, y: targetY },
        { x: targetX, y: targetY },
      ]);
    } else {
      // Arista entre ciclos adyacentes: dobla en un carril vertical escalonado dentro del pasillo
      const rawMidX = (sourceX + targetX) / 2 + laneOffset;
      const midX = Math.max(sourceX + 18, Math.min(targetX - 18, rawMidX));

      edgePath = buildRoundedOrthogonalPath([
        { x: sourceX, y: sourceY },
        { x: midX, y: sourceY },
        { x: midX, y: targetY },
        { x: targetX, y: targetY },
      ]);
    }
  } else {
    const [fallbackPath] = getSmoothStepPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition,
      borderRadius: 6,
    });
    edgePath = fallbackPath;
  }

  return <BaseEdge id={id} path={edgePath} style={style} markerEnd={markerEnd} />;
};

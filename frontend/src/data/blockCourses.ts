export interface BlockOption {
  codigo: string;
  nombre: string;
  departamento: string;
}

export interface BlockGroup {
  id: string;
  title: string;
  minRequired: number;
  options: BlockOption[];
}

export const BLOCK_GROUPS: Record<string, BlockGroup> = {
  QUEHACER_CIENTIFICO: {
    id: 'QUEHACER_CIENTIFICO',
    title: 'Bloque Introducción al Quehacer Científico',
    minRequired: 1,
    options: [
      { codigo: '124019', nombre: 'Historia y filosofía de la ciencia', departamento: 'HUM' },
      { codigo: '170354', nombre: 'Introducción a la cosmología y las ciencias de la vida', departamento: 'ING' },
      { codigo: '170334', nombre: 'Pensamiento sistémico', departamento: 'ING' },
    ],
  },
  DESARROLLO_PERSONAL: {
    id: 'DESARROLLO_PERSONAL',
    title: 'Bloque Desarrollo Personal',
    minRequired: 1,
    options: [
      { codigo: '142082', nombre: 'Emprendimiento e innovación', departamento: 'ADM' },
      { codigo: '124020', nombre: 'Literatura', departamento: 'HUM' },
      { codigo: '142095', nombre: 'Liderazgo', departamento: 'ADM' },
    ],
  },
  CIENCIAS_SOCIALES: {
    id: 'CIENCIAS_SOCIALES',
    title: 'Bloque Ciencias Sociales',
    minRequired: 1,
    options: [
      { codigo: '158109', nombre: 'Sociología', departamento: 'CS' },
      { codigo: '158143', nombre: 'Antropología', departamento: 'CS' },
      { codigo: '158000', nombre: 'Psicología', departamento: 'CS' },
    ],
  },
  PENSAMIENTO_CRITICO: {
    id: 'PENSAMIENTO_CRITICO',
    title: 'Bloque Pensamiento Crítico',
    minRequired: 2,
    options: [
      { codigo: '129007', nombre: 'Filosofía', departamento: 'HUM' },
      { codigo: '120125', nombre: 'Teología de las religiones', departamento: 'HUM' },
      { codigo: '157006', nombre: 'Pensamiento social contemporáneo', departamento: 'CS' },
    ],
  },
  PROCESOS_SOCIALES: {
    id: 'PROCESOS_SOCIALES',
    title: 'Bloque Procesos Sociales',
    minRequired: 2,
    options: [
      { codigo: '150004', nombre: 'Ciencia política', departamento: 'CS' },
      { codigo: '120070', nombre: 'Historia económica y empresarial', departamento: 'HUM' },
      { codigo: '122005', nombre: 'Historia crítica del Perú', departamento: 'HUM' },
    ],
  },
};

export function getBlockGroupForCourse(codigo: string, nombre: string): BlockGroup | null {
  const code = (codigo || '').toUpperCase();
  const norm = (nombre || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');

  if (code === '120020' || code.startsWith('SELLO-QC') || norm.includes('quehacer cientifico')) {
    return BLOCK_GROUPS.QUEHACER_CIENTIFICO;
  }
  if (code === '120030' || code.startsWith('SELLO-DP') || norm.includes('desarrollo personal')) {
    return BLOCK_GROUPS.DESARROLLO_PERSONAL;
  }
  if (code === '120040' || code.startsWith('SELLO-CS') || norm.includes('ciencias sociales')) {
    return BLOCK_GROUPS.CIENCIAS_SOCIALES;
  }
  if (
    code === '120045' ||
    code === '120047' ||
    code.startsWith('SELLO-PC') ||
    norm.includes('pensamiento critico')
  ) {
    return BLOCK_GROUPS.PENSAMIENTO_CRITICO;
  }
  if (
    code === '120046' ||
    code === '120048' ||
    code.startsWith('SELLO-PS') ||
    norm.includes('procesos sociales')
  ) {
    return BLOCK_GROUPS.PROCESOS_SOCIALES;
  }

  return null;
}

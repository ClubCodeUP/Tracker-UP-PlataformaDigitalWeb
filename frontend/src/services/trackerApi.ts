import { request } from './apiClient';
import { Asignatura, HistorialEntry, RiskAlert, AcademicMetrics } from '../types/curriculum';

export interface CurriculumEvaluationPayload {
  usuario_id: number;
  estudiante: string;
  recomendacion_matricula: any;
  alertas_riesgo: RiskAlert[];
  resumen_alertas: Record<string, number>;
}

export interface CareerSummary {
  id: number;
  codigo: string;
  nombre: string;
  total_creditos_graduacion: number;
  total_ciclos: number;
  max_creditos_ciclo_regular: number;
  concentraciones: Array<{
    id: number;
    codigo: string;
    nombre: string;
    descripcion?: string;
  }>;
}

export interface MallaResponse {
  carrera: {
    id: number;
    codigo: string;
    nombre: string;
    total_creditos: number;
    total_ciclos: number;
    max_creditos_regular: number;
  };
  cursos: Asignatura[];
}

export const trackerApi = {
  getMetrics: () => request<AcademicMetrics>('/metrics/me'),
  getHistory: () => request<HistorialEntry[]>('/history'),
  getCurriculumEvaluation: () => request<CurriculumEvaluationPayload>('/curriculum/evaluate'),
  getCareers: () => request<CareerSummary[]>('/curriculum/careers'),
  getMalla: (carreraId?: number) =>
    request<MallaResponse>(carreraId ? `/curriculum/malla?carrera_id=${carreraId}` : '/curriculum/malla'),
  updateCourseStatus: (historyId: number, estado: string, calificacion?: number) =>
    request(`/history/${historyId}`, {
      method: 'PUT',
      body: JSON.stringify({ estado, calificacion }),
    }),
};

// Datos maestros reales de la carrera de Ingeniería de la Información (UP)
export const DEFAULT_MALLA_UP: Asignatura[] = [
  // Ciclo 1 (18 créditos)
  {
    id: 1,
    codigo: 'MAT-1101',
    nombre: 'Álgebra y Geometría Analítica',
    creditos: 4.0,
    ciclo: 1,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 3,
    prerrequisitos: []
  },
  {
    id: 2,
    codigo: 'PRO-1101',
    nombre: 'Fundamentos de Programación',
    creditos: 4.0,
    ciclo: 1,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 4,
    prerrequisitos: []
  },
  {
    id: 3,
    codigo: 'COM-1101',
    nombre: 'Comunicación Académica',
    creditos: 3.0,
    ciclo: 1,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 4,
    codigo: 'ADM-1101',
    nombre: 'Administración y Organizaciones',
    creditos: 3.0,
    ciclo: 1,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 5,
    codigo: 'ECO-1101',
    nombre: 'Economía General',
    creditos: 4.0,
    ciclo: 1,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },

  // Ciclo 2 (15 créditos)
  {
    id: 6,
    codigo: 'MAT-1102',
    nombre: 'Cálculo Diferencial e Integral',
    creditos: 4.0,
    ciclo: 2,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 1,
    prerrequisitos: [{ codigo: 'MAT-1101', nombre: 'Álgebra y Geometría', aprobado: true, calificacion: 11.0 }]
  },
  {
    id: 7,
    codigo: 'PRO-1102',
    nombre: 'Algoritmos y Estructuras de Datos',
    creditos: 4.0,
    ciclo: 2,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: true, // Cuello de botella
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 5,
    prerrequisitos: [{ codigo: 'PRO-1101', nombre: 'Fundamentos de Programación', aprobado: true, calificacion: 16.0 }]
  },
  {
    id: 8,
    codigo: 'EST-1101',
    nombre: 'Estadística y Probabilidades',
    creditos: 4.0,
    ciclo: 2,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 2,
    prerrequisitos: [{ codigo: 'MAT-1101', nombre: 'Álgebra y Geometría', aprobado: true, calificacion: 11.0 }]
  },
  {
    id: 9,
    codigo: 'CON-1101',
    nombre: 'Contabilidad Financiera',
    creditos: 3.0,
    ciclo: 2,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'ADM-1101', nombre: 'Administración', aprobado: true, calificacion: 14.0 }]
  },

  // Ciclo 3 (16 créditos)
  {
    id: 10,
    codigo: 'MAT-1103',
    nombre: 'Álgebra Lineal Computacional',
    creditos: 4.0,
    ciclo: 3,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'MAT-1102', nombre: 'Cálculo', aprobado: false }]
  },
  {
    id: 11,
    codigo: 'BD-1101',
    nombre: 'Fundamentos de Bases de Datos',
    creditos: 4.0,
    ciclo: 3,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: true, // Cuello de botella
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 3,
    prerrequisitos: [{ codigo: 'PRO-1102', nombre: 'Algoritmos y Estructuras', aprobado: false }]
  },
  {
    id: 12,
    codigo: 'ARQ-1101',
    nombre: 'Arquitectura de Computadoras',
    creditos: 4.0,
    ciclo: 3,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 1,
    prerrequisitos: [{ codigo: 'PRO-1102', nombre: 'Algoritmos y Estructuras', aprobado: false }]
  },
  {
    id: 13,
    codigo: 'EST-1102',
    nombre: 'Estadística Inferencial',
    creditos: 4.0,
    ciclo: 3,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 1,
    prerrequisitos: [{ codigo: 'EST-1101', nombre: 'Estadística y Probabilidades', aprobado: false }]
  },

  // Ciclo 4 (12 créditos obligatorios)
  {
    id: 14,
    codigo: 'SOF-1101',
    nombre: 'Ingeniería de Software I',
    creditos: 4.0,
    ciclo: 4,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 2,
    prerrequisitos: [{ codigo: 'BD-1101', nombre: 'Fundamentos de Bases de Datos', aprobado: false }]
  },
  {
    id: 15,
    codigo: 'BD-1102',
    nombre: 'Bases de Datos NoSQL y Big Data',
    creditos: 4.0,
    ciclo: 4,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'BD-1101', nombre: 'Fundamentos de Bases de Datos', aprobado: false }]
  },
  {
    id: 16,
    codigo: 'RED-1101',
    nombre: 'Redes y Comunicaciones',
    creditos: 4.0,
    ciclo: 4,
    tipo: 'OBLIGATORIA',
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'ARQ-1101', nombre: 'Arquitectura de Computadoras', aprobado: false }]
  },

  // Ciclo 5 (Electivos de Especialidad con bolsa de 50 créditos)
  {
    id: 17,
    codigo: 'ELE-SW01',
    nombre: 'Arquitecturas Cloud y DevOps',
    creditos: 4.0,
    ciclo: 5,
    tipo: 'ELECTIVA',
    esCuelloBotella: false,
    concentracionId: 1,
    concentracionNombre: 'Ing. de Software y Cloud',
    creditosMinimosRequeridos: 50.0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'SOF-1101', nombre: 'Ingeniería de Software I', aprobado: false }]
  },
  {
    id: 18,
    codigo: 'ELE-DS01',
    nombre: 'Machine Learning Supervisado',
    creditos: 4.0,
    ciclo: 5,
    tipo: 'ELECTIVA',
    esCuelloBotella: false,
    concentracionId: 2,
    concentracionNombre: 'Ciencia de Datos e IA',
    creditosMinimosRequeridos: 50.0,
    desbloqueaCount: 0,
    prerrequisitos: [{ codigo: 'EST-1102', nombre: 'Estadística Inferencial', aprobado: false }]
  },
];


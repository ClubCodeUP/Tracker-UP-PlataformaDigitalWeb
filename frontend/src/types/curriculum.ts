import type { BlockGroup, BlockOption } from '../data/blockCourses';

export type EstadoAsignatura = 'PENDIENTE' | 'EN_CURSO' | 'APROBADA' | 'DESAPROBADA';

export type VisualCourseState = 'APROBADA' | 'EN_CURSO' | 'HABILITADA' | 'BLOQUEADA' | 'REITERACION';

export type TipoAsignatura = 'OBLIGATORIA' | 'ELECTIVA';

export type TipoAlerta = 
  | 'REITERACION_MATRICULA'
  | 'PRERREQUISITO_NOTA_LIMITE'
  | 'REZAGO_PERMANENCIA'
  | 'CUELLO_DE_BOTELLA';

export type SeveridadAlerta = 'CRITICA' | 'ADVERTENCIA' | 'INFORMATIVA';

export interface PrerrequisitoInfo {
  codigo: string;
  nombre: string;
  aprobado: boolean;
  calificacion?: number;
}

export interface Asignatura {
  id: number;
  codigo: string;
  nombre: string;
  creditos: number;
  ciclo: number;
  tipo: TipoAsignatura;
  esCuelloBotella: boolean;
  concentracionId?: number | null;
  concentracion?: string | null;
  concentracionNombre?: string | null;
  creditosMinimosRequeridos: number;
  prerrequisitos: PrerrequisitoInfo[];
  desbloqueaCount: number;
}

export interface HistorialEntry {
  id: number;
  asignaturaId: number;
  periodo: string;
  estado: EstadoAsignatura;
  calificacion?: number | null;
  numeroMatricula: number;
}

export interface RiskAlert {
  tipo_alerta: TipoAlerta;
  nivel_severidad: SeveridadAlerta;
  codigo_asignatura?: string;
  nombre_asignatura?: string;
  mensaje: string;
  detalles: Record<string, any>;
}

export interface AcademicMetrics {
  usuario_id: number;
  estudiante: string;
  carrera: string;
  total_creditos_carrera: number;
  creditos_aprobados: number;
  creditos_en_curso: number;
  creditos_pendientes: number;
  porcentaje_avance: number;
  ciclo_referencial: number;
  promedio_ponderado?: number | null;
  cursos_aprobados_count: number;
  cursos_en_curso_count: number;
  cursos_en_riesgo_count: number;
}

export interface CohortBenchmark {
  periodo_ingreso: string;
  semestres_transcurridos: number;
  estudiante_creditos_aprobados: number;
  estudiante_promedio_ponderado: number | null;
  estudiante_porcentaje_avance: number;
  cohorte_tamano: number;
  cohorte_media_creditos: number;
  cohorte_media_promedio: number | null;
  cohorte_media_avance: number;
  diferencia_creditos_cohorte: number;
  malla_creditos_esperados: number;
  malla_avance_esperado: number;
  diferencia_creditos_malla: number;
  estado_ritmo: 'ADELANTADO' | 'AL_DIA' | 'EN_PROGRESO';
  mensaje_evaluacion: string;
  recomendacion_constructiva: string;
}

export interface ConcentrationCourse {
  id: number;
  codigo: string;
  nombre: string;
  creditos: number;
  ciclo: number;
  tipo: string;
}

export interface ConcentrationDetail {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  cursos: ConcentrationCourse[];
  total_cursos: number;
  creditos_totales: number;
}

export interface CareerChangeRequest {
  id: number;
  usuario_id: number;
  estudiante_nombres: string;
  estudiante_apellidos: string;
  estudiante_email: string;
  carrera_actual_id: number;
  carrera_actual_nombre: string;
  carrera_destino_id: number;
  carrera_destino_nombre: string;
  motivo?: string | null;
  estado: 'PENDIENTE' | 'APROBADA' | 'RECHAZADA';
  respuesta_admin?: string | null;
  creado_en: string;
}

export interface CourseNodeData {
  asignatura: Asignatura;
  estado: EstadoAsignatura;
  visualState: VisualCourseState;
  calificacion?: number | null;
  numeroMatricula: number;
  alertas: RiskAlert[];
  isSelected?: boolean;
  isConcentrationMatch?: boolean;
  isHovered?: boolean;
  isPrerequisiteOfHovered?: boolean;
  isUnlockedByHovered?: boolean;
  isDimmed?: boolean;
  blockGroup?: BlockGroup | null;
  selectedBlockOption?: BlockOption | null;
  onSelectBlockOption?: (asignaturaId: number, optionCodigo: string | null) => void;
  onSelectCourse: (asignatura: Asignatura) => void;
  isQuickEditMode?: boolean;
  onQuickToggleCourse?: (asignatura: Asignatura) => void;
  onHoverCourse?: (asignaturaId: number | null) => void;
}


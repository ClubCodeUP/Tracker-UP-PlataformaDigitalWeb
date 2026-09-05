export type EstadoAsignatura = 'PENDIENTE' | 'EN_CURSO' | 'APROBADA' | 'DESAPROBADA';

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

export interface CourseNodeData {
  asignatura: Asignatura;
  estado: EstadoAsignatura;
  calificacion?: number | null;
  numeroMatricula: number;
  alertas: RiskAlert[];
  isSelected?: boolean;
  onSelectCourse: (asignatura: Asignatura) => void;
}


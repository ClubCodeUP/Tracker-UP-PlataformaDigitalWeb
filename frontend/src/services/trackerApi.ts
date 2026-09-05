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

export interface UserProfile {
  id: number;
  email: string;
  nombres: string;
  apellidos: string;
  carrera_id: number;
  carrera_nombre?: string;
  carrera_codigo?: string;
  concentracion_id?: number | null;
  concentracion_nombre?: string | null;
  periodo_ingreso: string;
  activo: boolean;
}

export interface RegisterPayload {
  email: string;
  password: string;
  nombres: string;
  apellidos: string;
  carrera_id: number;
  concentracion_id?: number | null;
  periodo_ingreso: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: number;
  email: string;
  nombres: string;
  apellidos: string;
}

export const trackerApi = {
  // Autenticación y Perfil
  login: async (payload: LoginPayload): Promise<AuthResponse> => {
    const res = await request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (res?.access_token) {
      localStorage.setItem('tracker_up_token', res.access_token);
    }
    return res;
  },

  register: async (payload: RegisterPayload): Promise<AuthResponse> => {
    const res = await request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (res?.access_token) {
      localStorage.setItem('tracker_up_token', res.access_token);
    }
    return res;
  },

  logout: () => {
    localStorage.removeItem('tracker_up_token');
  },

  getProfile: () => request<UserProfile>('/profile/me'),

  updateProfile: (data: {
    carrera_id?: number;
    concentracion_id?: number | null;
    periodo_ingreso?: string;
  }) =>
    request<UserProfile>('/profile/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Métricas y Evaluación Curricular
  getMetrics: () => request<AcademicMetrics>('/metrics/me'),
  getCurriculumEvaluation: () => request<CurriculumEvaluationPayload>('/curriculum/evaluate'),

  // Historial Académico
  getHistory: async (): Promise<HistorialEntry[]> => {
    const raw = await request<any[]>('/history');
    if (!Array.isArray(raw)) return [];
    return raw.map((item) => ({
      id: item.id,
      asignaturaId: item.asignatura_id,
      periodo: item.periodo_academico,
      estado: item.estado,
      calificacion: item.calificacion,
      numeroMatricula: item.numero_matricula,
    }));
  },

  saveCourseHistory: async (params: {
    asignaturaId: number;
    periodo: string;
    estado: string;
    calificacion?: number | null;
    numeroMatricula?: number;
    existingHistoryId?: number | null;
  }) => {
    if (params.existingHistoryId) {
      return request(`/history/${params.existingHistoryId}`, {
        method: 'PUT',
        body: JSON.stringify({
          estado: params.estado,
          calificacion: params.calificacion,
          numero_matricula: params.numeroMatricula ?? 1,
        }),
      });
    } else {
      return request('/history', {
        method: 'POST',
        body: JSON.stringify({
          asignatura_id: params.asignaturaId,
          periodo_academico: params.periodo,
          estado: params.estado,
          calificacion: params.calificacion,
          numero_matricula: params.numeroMatricula ?? 1,
        }),
      });
    }
  },

  deleteCourseHistory: (historyId: number) =>
    request(`/history/${historyId}`, { method: 'DELETE' }),

  updateCourseStatus: (historyId: number, estado: string, calificacion?: number) =>
    request(`/history/${historyId}`, {
      method: 'PUT',
      body: JSON.stringify({ estado, calificacion }),
    }),

  // Catálogos
  getCareers: () => request<CareerSummary[]>('/curriculum/careers'),
  getMalla: (carreraId?: number) =>
    request<MallaResponse>(carreraId ? `/curriculum/malla?carrera_id=${carreraId}` : '/curriculum/malla'),
};

// Datos maestros reales de la carrera de Ingeniería de la Información (UP)
export const DEFAULT_MALLA_UP: Asignatura[] = [
  {
    id: 19,
    codigo: "134654",
    nombre: "Nivelación en Matemáticas",
    creditos: 0.0,
    ciclo: 0,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: []
  },
  {
    id: 20,
    codigo: "170131",
    nombre: "Nivelación en Informática",
    creditos: 0.0,
    ciclo: 0,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: []
  },
  {
    id: 21,
    codigo: "120000",
    nombre: "Nivelación en Lenguaje",
    creditos: 0.0,
    ciclo: 0,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 23,
    codigo: "120001",
    nombre: "Lenguaje I",
    creditos: 4.0,
    ciclo: 1,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "120000", "nombre": "Nivelación en Lenguaje", "aprobado": false}]
  },
  {
    id: 24,
    codigo: "138649",
    nombre: "Matemáticas I",
    creditos: 5.0,
    ciclo: 1,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 5,
    prerrequisitos: [{"codigo": "134654", "nombre": "Nivelación en Matemáticas", "aprobado": false}]
  },
  {
    id: 25,
    codigo: "132641",
    nombre: "Economía General I",
    creditos: 5.0,
    ciclo: 1,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: [{"codigo": "134654", "nombre": "Nivelación en Matemáticas", "aprobado": false}]
  },
  {
    id: 123,
    codigo: "170001",
    nombre: "Introducción a la Ingeniería",
    creditos: 4.0,
    ciclo: 1,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 26,
    codigo: "120006",
    nombre: "Lenguaje II",
    creditos: 4.0,
    ciclo: 2,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: [{"codigo": "120001", "nombre": "Lenguaje I", "aprobado": false}]
  },
  {
    id: 27,
    codigo: "138650",
    nombre: "Matemáticas II",
    creditos: 5.0,
    ciclo: 2,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 7,
    prerrequisitos: [{"codigo": "138649", "nombre": "Matemáticas I", "aprobado": false}]
  },
  {
    id: 30,
    codigo: "160092",
    nombre: "Fundamentos de Contabilidad",
    creditos: 4.0,
    ciclo: 2,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 5,
    prerrequisitos: [{"codigo": "141038", "nombre": "Fundamentos de las Ciencias Empresariales", "aprobado": false}]
  },
  {
    id: 124,
    codigo: "170002",
    nombre: "Herramientas de Programación",
    creditos: 4.0,
    ciclo: 2,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "170131", "nombre": "Nivelación en Informática", "aprobado": false}]
  },
  {
    id: 125,
    codigo: "132642",
    nombre: "Economía General II",
    creditos: 5.0,
    ciclo: 2,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 8,
    prerrequisitos: [{"codigo": "132641", "nombre": "Economía General I", "aprobado": false}]
  },
  {
    id: 33,
    codigo: "130224",
    nombre: "Estadística I",
    creditos: 4.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 10,
    prerrequisitos: [{"codigo": "138649", "nombre": "Matemáticas I", "aprobado": false}, {"codigo": "138652", "nombre": "Matemáticas para los Negocios", "aprobado": false}, {"codigo": "138650", "nombre": "Matemáticas II", "aprobado": false}, {"codigo": "138651", "nombre": "Matemáticas para los Negocios", "aprobado": false}]
  },
  {
    id: 126,
    codigo: "170003",
    nombre: "Algoritmos y Estructura de Datos",
    creditos: 4.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: [{"codigo": "170002", "nombre": "Herramientas de Programación", "aprobado": false}]
  },
  {
    id: 127,
    codigo: "160093",
    nombre: "Contabilidad Financiera Intermedia",
    creditos: 5.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 4,
    prerrequisitos: [{"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "aprobado": false}]
  },
  {
    id: 128,
    codigo: "120020",
    nombre: "Introducción al Quehacer Científico",
    creditos: 4.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 129,
    codigo: "120030",
    nombre: "Desarrollo Personal",
    creditos: 4.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 130,
    codigo: "120015",
    nombre: "Investigación Académica",
    creditos: 3.0,
    ciclo: 3,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "120006", "nombre": "Lenguaje II", "aprobado": false}]
  },
  {
    id: 22,
    codigo: "141040",
    nombre: "Marketing Estratégico",
    creditos: 4.0,
    ciclo: 4,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 50.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "170131", "nombre": "Nivelación en Informática", "aprobado": false}, {"codigo": "141061", "nombre": "Diseño Organizacional y Estrategia", "aprobado": false}]
  },
  {
    id: 40,
    codigo: "130225",
    nombre: "Estadística II",
    creditos: 4.0,
    ciclo: 4,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 4,
    prerrequisitos: [{"codigo": "130224", "nombre": "Estadística I", "aprobado": false}]
  },
  {
    id: 131,
    codigo: "170004",
    nombre: "Ingeniería de Procesos",
    creditos: 4.0,
    ciclo: 4,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 4,
    prerrequisitos: [{"codigo": "170001", "nombre": "Introducción a la Ingeniería", "aprobado": false}]
  },
  {
    id: 132,
    codigo: "170005",
    nombre: "Matemáticas Discretas para la Computación",
    creditos: 4.0,
    ciclo: 4,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "138650", "nombre": "Matemáticas II", "aprobado": false}, {"codigo": "138649", "nombre": "Matemáticas I", "aprobado": false}]
  },
  {
    id: 133,
    codigo: "170006",
    nombre: "Arquitectura del Sistema de Información",
    creditos: 4.0,
    ciclo: 4,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: [{"codigo": "170003", "nombre": "Algoritmos y Estructura de Datos", "aprobado": false}, {"codigo": "170002", "nombre": "Herramientas de Programación", "aprobado": false}, {"codigo": "170004", "nombre": "Ingeniería de Procesos", "aprobado": false}]
  },
  {
    id: 134,
    codigo: "170007",
    nombre: "Fundamentos de Analítica",
    creditos: 4.0,
    ciclo: 5,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "130225", "nombre": "Estadística II", "aprobado": false}, {"codigo": "130224", "nombre": "Estadística I", "aprobado": false}]
  },
  {
    id: 135,
    codigo: "170008",
    nombre: "Programación Avanzada para la Ciencia de Datos",
    creditos: 4.0,
    ciclo: 5,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170003", "nombre": "Algoritmos y Estructura de Datos", "aprobado": false}]
  },
  {
    id: 136,
    codigo: "170009",
    nombre: "Álgebra Lineal Aplicada",
    creditos: 4.0,
    ciclo: 5,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "138650", "nombre": "Matemáticas II", "aprobado": false}]
  },
  {
    id: 137,
    codigo: "170010",
    nombre: "Ingeniería de Datos",
    creditos: 4.0,
    ciclo: 5,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 3,
    prerrequisitos: [{"codigo": "170003", "nombre": "Algoritmos y Estructura de Datos", "aprobado": false}, {"codigo": "120113", "nombre": "Análisis de Datos Multimedia", "aprobado": false}, {"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "aprobado": false}]
  },
  {
    id: 138,
    codigo: "150020",
    nombre: "Fundamentos de Finanzas",
    creditos: 4.0,
    ciclo: 5,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 5,
    prerrequisitos: [{"codigo": "160093", "nombre": "Contabilidad Financiera Intermedia", "aprobado": false}, {"codigo": "132642", "nombre": "Economía General II", "aprobado": false}, {"codigo": "160092", "nombre": "Fundamentos de Contabilidad", "aprobado": false}]
  },
  {
    id: 139,
    codigo: "170011",
    nombre: "Física",
    creditos: 5.0,
    ciclo: 6,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 75.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 140,
    codigo: "170012",
    nombre: "Data Mining",
    creditos: 4.0,
    ciclo: 6,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "130225", "nombre": "Estadística II", "aprobado": false}]
  },
  {
    id: 141,
    codigo: "170013",
    nombre: "Machine Learning",
    creditos: 4.0,
    ciclo: 6,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170005", "nombre": "Matemáticas Discretas para la Computación", "aprobado": false}]
  },
  {
    id: 142,
    codigo: "141045",
    nombre: "Gestión del Capital Humano",
    creditos: 4.0,
    ciclo: 6,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "120030", "nombre": "Desarrollo Personal", "aprobado": false}]
  },
  {
    id: 143,
    codigo: "120040",
    nombre: "Ciencias Sociales",
    creditos: 4.0,
    ciclo: 6,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 75.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 144,
    codigo: "170014",
    nombre: "Analítica de la Web",
    creditos: 4.0,
    ciclo: 7,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170007", "nombre": "Fundamentos de Analítica", "aprobado": false}]
  },
  {
    id: 145,
    codigo: "170015",
    nombre: "Inteligencia Computacional",
    creditos: 4.0,
    ciclo: 7,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170009", "nombre": "Álgebra Lineal Aplicada", "aprobado": false}]
  },
  {
    id: 146,
    codigo: "170016",
    nombre: "Desarrollo de Soluciones Empresariales",
    creditos: 4.0,
    ciclo: 7,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "170004", "nombre": "Ingeniería de Procesos", "aprobado": false}, {"codigo": "170010", "nombre": "Ingeniería de Datos", "aprobado": false}]
  },
  {
    id: 147,
    codigo: "141050",
    nombre: "Estrategia",
    creditos: 3.0,
    ciclo: 7,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 2,
    prerrequisitos: [{"codigo": "150020", "nombre": "Fundamentos de Finanzas", "aprobado": false}, {"codigo": "141040", "nombre": "Marketing Estratégico", "aprobado": false}]
  },
  {
    id: 148,
    codigo: "120045",
    nombre: "Pensamiento Crítico 1",
    creditos: 4.0,
    ciclo: 7,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 90.0,
    desbloqueaCount: 1,
    prerrequisitos: []
  },
  {
    id: 67,
    codigo: "ELE-INF01",
    nombre: "Electivo I (Especialidad)",
    creditos: 3.0,
    ciclo: 8,
    tipo: "ELECTIVA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 105.0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 149,
    codigo: "170017",
    nombre: "Tecnología para el Desarrollo Sostenible",
    creditos: 3.0,
    ciclo: 8,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170011", "nombre": "Física", "aprobado": false}]
  },
  {
    id: 150,
    codigo: "170018",
    nombre: "Computación de Alto Desempeño y Cloud Computing",
    creditos: 4.0,
    ciclo: 8,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    concentracionNombre: "Ingeniería de Software y Sistemas Cloud",
    concentracionId: 1,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170008", "nombre": "Programación Avanzada para la Ciencia de Datos", "aprobado": false}]
  },
  {
    id: 151,
    codigo: "170019",
    nombre: "Deep Learning",
    creditos: 4.0,
    ciclo: 8,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    concentracionNombre: "Ciencia de Datos e Inteligencia Artificial",
    concentracionId: 1,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170013", "nombre": "Machine Learning", "aprobado": false}]
  },
  {
    id: 152,
    codigo: "170020",
    nombre: "Infraestructura Tecnológica",
    creditos: 4.0,
    ciclo: 8,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170006", "nombre": "Arquitectura del Sistema de Información", "aprobado": false}, {"codigo": "170016", "nombre": "Desarrollo de Soluciones Empresariales", "aprobado": false}]
  },
  {
    id: 153,
    codigo: "120046",
    nombre: "Procesos Sociales 1",
    creditos: 4.0,
    ciclo: 8,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "120040", "nombre": "Ciencias Sociales", "aprobado": false}]
  },
  {
    id: 68,
    codigo: "ELE-INF02",
    nombre: "Electivo II",
    creditos: 3.0,
    ciclo: 9,
    tipo: "ELECTIVA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 120.0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 154,
    codigo: "170021",
    nombre: "Big Data Analytics",
    creditos: 4.0,
    ciclo: 9,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170010", "nombre": "Ingeniería de Datos", "aprobado": false}]
  },
  {
    id: 155,
    codigo: "170022",
    nombre: "Business Intelligence",
    creditos: 3.0,
    ciclo: 9,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170012", "nombre": "Data Mining", "aprobado": false}]
  },
  {
    id: 156,
    codigo: "170023",
    nombre: "Trabajo Final de Ingeniería de la Información I",
    creditos: 4.0,
    ciclo: 9,
    tipo: "OBLIGATORIA",
    esCuelloBotella: true,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "170015", "nombre": "Inteligencia Computacional", "aprobado": false}, {"codigo": "170016", "nombre": "Desarrollo de Soluciones Empresariales", "aprobado": false}, {"codigo": "141050", "nombre": "Estrategia", "aprobado": false}, {"codigo": "170019", "nombre": "Deep Learning", "aprobado": false}]
  },
  {
    id: 157,
    codigo: "120047",
    nombre: "Pensamiento Crítico 2",
    creditos: 4.0,
    ciclo: 9,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "120045", "nombre": "Pensamiento Crítico 1", "aprobado": false}]
  },
  {
    id: 160,
    codigo: "120048",
    nombre: "Procesos Sociales 2",
    creditos: 4.0,
    ciclo: 9,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "120046", "nombre": "Procesos Sociales 1", "aprobado": false}]
  },
  {
    id: 72,
    codigo: "ELE-INF03",
    nombre: "Electivo III",
    creditos: 3.0,
    ciclo: 10,
    tipo: "ELECTIVA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 135.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170201", "nombre": "Comportamiento del Consumidor", "aprobado": false}]
  },
  {
    id: 73,
    codigo: "ELE-INF04",
    nombre: "Electivo IV",
    creditos: 3.0,
    ciclo: 10,
    tipo: "ELECTIVA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 135.0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 158,
    codigo: "170024",
    nombre: "Trabajo Final de Ingeniería de la Información II",
    creditos: 4.0,
    ciclo: 10,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 0,
    prerrequisitos: [{"codigo": "170023", "nombre": "Trabajo Final de Ingeniería de la Información I", "aprobado": false}]
  },
  {
    id: 159,
    codigo: "120060",
    nombre: "Proyección Social",
    creditos: 4.0,
    ciclo: 10,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 135.0,
    desbloqueaCount: 0,
    prerrequisitos: []
  },
  {
    id: 161,
    codigo: "120050",
    nombre: "Ética",
    creditos: 4.0,
    ciclo: 10,
    tipo: "OBLIGATORIA",
    esCuelloBotella: false,
    creditosMinimosRequeridos: 0.0,
    desbloqueaCount: 1,
    prerrequisitos: [{"codigo": "120047", "nombre": "Pensamiento Crítico 2", "aprobado": false}]
  },
];

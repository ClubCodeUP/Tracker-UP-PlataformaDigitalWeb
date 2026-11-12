import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Upload,
  CheckCircle2,
  XCircle,
  Clock,
  FileText,
  Users,
  GraduationCap,
  AlertCircle
} from 'lucide-react';
import { CareerChangeRequest } from '../../types/curriculum';
import { trackerApi } from '../../services/trackerApi';

export const AdminPanelView: React.FC = () => {
  const [requests, setRequests] = useState<CareerChangeRequest[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState<'requests' | 'curriculum'>('requests');

  // Estado para subida de malla
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Estado para procesar solicitud
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [adminNote, setAdminNote] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [reqList, statsData] = await Promise.all([
        trackerApi.getAdminCareerRequests().catch(() => []),
        trackerApi.getAdminStats().catch(() => null),
      ]);
      setRequests(reqList);
      setStats(statsData);
    } catch (err) {
      console.error('Error cargando datos de administración:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAction = async (requestId: number, accion: 'APROBAR' | 'RECHAZAR') => {
    setProcessingId(requestId);
    try {
      await trackerApi.handleAdminCareerRequest(requestId, accion, adminNote);
      setAdminNote('');
      await loadData();
    } catch (err: any) {
      alert(`Error al procesar: ${err.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setUploadMessage(null);
    try {
      const res = await trackerApi.uploadAdminCurriculum(selectedFile);
      setUploadMessage({
        type: 'success',
        text: `¡Malla cargada exitosamente! ${res.cursos_cargados} cursos y ${res.prerrequisitos_procesados} dependencias procesadas para ${res.carrera_nombre}.`,
      });
      setSelectedFile(null);
      await loadData();
    } catch (err: any) {
      setUploadMessage({
        type: 'error',
        text: err.message || 'Error al validar y subir la malla curricular.',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#FBFBFE] px-6 py-8 text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Cabecera del Panel de Administración */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-rose-600" />
              <span>Personal Autorizado UP</span>
            </div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">
              Panel Administrativo de Gestión Académica
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              Control centralizado de mallas curriculares, actualización del catálogo y solicitudes de cambio de carrera.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-2xl border border-slate-200">
            <button
              onClick={() => setActiveSubTab('requests')}
              className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all ${
                activeSubTab === 'requests'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Solicitudes de Carrera ({requests.filter((r) => r.estado === 'PENDIENTE').length})
            </button>
            <button
              onClick={() => setActiveSubTab('curriculum')}
              className={`px-3.5 py-1.5 text-xs font-bold rounded-xl transition-all ${
                activeSubTab === 'curriculum'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Carga de Mallas Curriculares
            </button>
          </div>
        </div>

        {/* Estadísticas Rápidas */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between text-slate-500 mb-1">
                <span className="text-xs font-semibold">Alumnos Registrados</span>
                <Users className="w-4 h-4 text-violet-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_estudiantes}</div>
            </div>

            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between text-slate-500 mb-1">
                <span className="text-xs font-semibold">Carreras Activas</span>
                <GraduationCap className="w-4 h-4 text-indigo-600" />
              </div>
              <div className="text-2xl font-black text-slate-900">{stats.total_carreras}</div>
            </div>

            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between text-slate-500 mb-1">
                <span className="text-xs font-semibold">Solicitudes Pendientes</span>
                <Clock className="w-4 h-4 text-amber-600" />
              </div>
              <div className="text-2xl font-black text-amber-600">{stats.solicitudes_pendientes}</div>
            </div>

            <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between text-slate-500 mb-1">
                <span className="text-xs font-semibold">Solicitudes Aprobadas</span>
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              </div>
              <div className="text-2xl font-black text-emerald-600">{stats.solicitudes_aprobadas}</div>
            </div>
          </div>
        )}

        {/* Pestaña 1: Solicitudes de Cambio de Carrera */}
        {activeSubTab === 'requests' && (
          <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
              <FileText className="w-4 h-4 text-violet-600" />
              Bandeja de Solicitudes de Cambio de Carrera
            </h3>

            {loading ? (
              <div className="py-12 text-center text-slate-400 text-xs">Cargando solicitudes...</div>
            ) : requests.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs">
                No hay solicitudes de cambio de carrera registradas.
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {requests.map((req) => {
                  const isPending = req.estado === 'PENDIENTE';
                  const isApproved = req.estado === 'APROBADA';

                  return (
                    <div key={req.id} className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-bold text-slate-900 text-sm">
                            {req.estudiante_nombres} {req.estudiante_apellidos}
                          </span>
                          <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                            {req.estudiante_email}
                          </span>
                          <span
                            className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full ${
                              isPending
                                ? 'bg-amber-100 text-amber-800 border border-amber-300'
                                : isApproved
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                                : 'bg-rose-100 text-rose-800 border border-rose-300'
                            }`}
                          >
                            {req.estado}
                          </span>
                        </div>

                        <div className="text-xs text-slate-600 mt-1">
                          <span className="font-medium text-slate-800">Carrera actual:</span>{' '}
                          {req.carrera_actual_nombre}{' '}
                          <span className="text-violet-600 font-bold mx-1">➔</span>{' '}
                          <span className="font-medium text-slate-800">Carrera solicitada:</span>{' '}
                          <strong className="text-violet-800">{req.carrera_destino_nombre}</strong>
                        </div>

                        {req.motivo && (
                          <p className="text-xs text-slate-500 mt-1 italic">
                            "{req.motivo}"
                          </p>
                        )}

                        {req.respuesta_admin && (
                          <div className="text-[11px] text-slate-600 mt-1 bg-slate-50 p-2 rounded-xl">
                            <strong>Respuesta del admin:</strong> {req.respuesta_admin}
                          </div>
                        )}
                      </div>

                      {/* Acciones de Aprobación */}
                      {isPending && (
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={() => handleAction(req.id, 'APROBAR')}
                            disabled={processingId === req.id}
                            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Aprobar Cambio
                          </button>
                          <button
                            onClick={() => handleAction(req.id, 'RECHAZAR')}
                            disabled={processingId === req.id}
                            className="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold text-xs rounded-xl transition-all flex items-center gap-1"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Rechazar
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Pestaña 2: Carga de Mallas Curriculares */}
        {activeSubTab === 'curriculum' && (
          <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Upload className="w-4 h-4 text-violet-600" />
              Actualización de Mallas Curriculares ("Curriculum as Code")
            </h3>
            <p className="text-xs text-slate-500 mb-6 max-w-2xl">
              Carga un archivo JSON estructurado de malla curricular. El sistema validará automáticamente que no contenga ciclos infinitos de prerrequisitos (DAG acíclico) y actualizará el catálogo institucional.
            </p>

            <form onSubmit={handleFileUpload} className="space-y-4 max-w-xl">
              <div className="border-2 border-dashed border-violet-200 rounded-3xl p-8 text-center hover:border-violet-400 transition-colors bg-violet-50/20">
                <Upload className="w-8 h-8 text-violet-500 mx-auto mb-2" />
                <label className="block text-xs font-bold text-slate-800 cursor-pointer mb-1">
                  {selectedFile ? selectedFile.name : 'Selecciona un archivo JSON de malla curricular'}
                  <input
                    type="file"
                    accept=".json"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="hidden"
                  />
                </label>
                <p className="text-[11px] text-slate-400">
                  Formato JSON oficial con códigos, créditos, ciclos y prerrequisitos.
                </p>
              </div>

              {uploadMessage && (
                <div
                  className={`p-3 rounded-2xl text-xs flex items-center gap-2 ${
                    uploadMessage.type === 'success'
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-rose-50 text-rose-800 border border-rose-200'
                  }`}
                >
                  {uploadMessage.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
                  )}
                  <span>{uploadMessage.text}</span>
                </div>
              )}

              <button
                type="submit"
                disabled={!selectedFile || uploading}
                className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-bold text-xs rounded-xl shadow-md shadow-violet-500/20 transition-all disabled:opacity-50 flex items-center gap-2"
              >
                <Upload className="w-4 h-4" />
                {uploading ? 'Validando e Ingestando...' : 'Subir y Actualizar Malla'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

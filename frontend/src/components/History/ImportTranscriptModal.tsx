import React, { useState, useRef } from 'react';
import { X, Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { trackerApi } from '../../services/trackerApi';

interface ImportTranscriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess: () => Promise<void> | void;
}

type ImportSummary = Awaited<ReturnType<typeof trackerApi.importTranscriptPdf>>;

export const ImportTranscriptModal: React.FC<ImportTranscriptModalProps> = ({
  isOpen,
  onClose,
  onImportSuccess,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (file: File | null) => {
    setError(null);
    setSummary(null);
    if (!file) {
      setSelectedFile(null);
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Por favor selecciona un archivo en formato PDF (.pdf).');
      return;
    }
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setError(null);

    try {
      const res = await trackerApi.importTranscriptPdf(selectedFile);

      // Guardar selecciones de Bloques Sello UP detectadas en el transcript
      if (res.block_selections && Object.keys(res.block_selections).length > 0) {
        try {
          const existingRaw = localStorage.getItem('tracker_up_block_selections');
          const existing = existingRaw ? JSON.parse(existingRaw) : {};
          const merged = { ...existing, ...res.block_selections };
          localStorage.setItem('tracker_up_block_selections', JSON.stringify(merged));
        } catch {
          // Ignorar errores de almacenamiento local
        }
      }

      setSummary(res);
      await onImportSuccess();
    } catch (err: any) {
      setError(err?.message || 'Error al procesar el PDF del transcript.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleResetAndClose = () => {
    setSelectedFile(null);
    setError(null);
    setSummary(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-3xl shadow-2xl border border-violet-100 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Cabecera */}
        <div className="px-6 py-4 bg-gradient-to-r from-violet-600 to-purple-600 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-white/20 flex items-center justify-center">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-bold">Importar Unofficial Transcript</h3>
              <p className="text-[11px] text-violet-100">
                Sincroniza automáticamente tu avance desde Autoservicio UP
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleResetAndClose}
            className="p-1.5 rounded-xl hover:bg-white/20 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Cuerpo */}
        <div className="p-6 space-y-4">
          {!summary ? (
            <>
              <p className="text-xs text-slate-600 leading-relaxed">
                Sube el PDF de tu <strong>Unofficial Transcript</strong> descargado de Autoservicio UP.
                El archivo se procesa únicamente en memoria para extraer tus cursos aprobados, notas,
                cursos en matrícula actual y bloques Sello UP; <strong>no se almacena en el servidor</strong>.
              </p>

              {/* Zona de carga */}
              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  const file = e.dataTransfer.files?.[0] || null;
                  handleFileChange(file);
                }}
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                  selectedFile
                    ? 'border-violet-400 bg-violet-50/60'
                    : 'border-slate-200 hover:border-violet-300 hover:bg-slate-50/70'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,application/pdf"
                  className="hidden"
                  onChange={(e) => handleFileChange(e.target.files?.[0] || null)}
                />
                <Upload className="w-8 h-8 text-violet-500 mx-auto mb-2" />
                {selectedFile ? (
                  <div>
                    <p className="text-xs font-bold text-violet-900">{selectedFile.name}</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      {(selectedFile.size / 1024).toFixed(1)} KB · Listo para importar
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-xs font-semibold text-slate-700">
                      Haz clic para seleccionar o arrastra tu PDF aquí
                    </p>
                    <p className="text-[11px] text-slate-400 mt-1">Formato .pdf (máx. 10 MB)</p>
                  </div>
                )}
              </div>

              {error && (
                <div className="flex items-start gap-2 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl p-3">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={handleResetAndClose}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="button"
                  disabled={!selectedFile || isUploading}
                  onClick={handleUpload}
                  className="px-4 py-2 text-xs font-bold text-white bg-violet-600 hover:bg-violet-700 disabled:opacity-50 rounded-xl shadow-sm transition flex items-center gap-1.5 cursor-pointer"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Extrayendo...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-3.5 h-3.5" />
                      Importar Avance
                    </>
                  )}
                </button>
              </div>
            </>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-2.5 bg-emerald-50 border border-emerald-200 rounded-2xl p-3.5 text-emerald-900">
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <div>
                  <p className="text-xs font-bold">
                    ¡Se importaron {summary.imported_count} asignaturas a tu malla!
                  </p>
                  {summary.detected_program && (
                    <p className="text-[11px] text-emerald-700">
                      Programa detectado: {summary.detected_program}
                    </p>
                  )}
                </div>
              </div>

              {/* Resumen numérico */}
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-emerald-50/70 border border-emerald-100 rounded-xl p-2.5">
                  <div className="text-base font-black text-emerald-700">{summary.approved_count}</div>
                  <div className="text-[10px] font-semibold text-emerald-600 uppercase">Aprobadas</div>
                </div>
                <div className="bg-indigo-50/70 border border-indigo-100 rounded-xl p-2.5">
                  <div className="text-base font-black text-indigo-700">{summary.in_progress_count}</div>
                  <div className="text-[10px] font-semibold text-indigo-600 uppercase">En Curso</div>
                </div>
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-2.5">
                  <div className="text-base font-black text-slate-700">{summary.retired_skipped_count}</div>
                  <div className="text-[10px] font-semibold text-slate-500 uppercase">Retiros (RET)</div>
                </div>
              </div>

              {/* Lista breve de cursos fuera de malla (electivos o externos) */}
              {summary.unmatched_courses.length > 0 && (
                <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-3">
                  <p className="text-[11px] font-bold text-amber-900 mb-1">
                    Cursos fuera de la malla obligatoria ({summary.unmatched_courses.length}):
                  </p>
                  <div className="max-h-24 overflow-y-auto space-y-1 text-[11px] text-amber-800">
                    {summary.unmatched_courses.map((u) => (
                      <div key={`${u.codigo}-${u.periodo}`} className="flex justify-between gap-2">
                        <span className="truncate">
                          <strong className="font-mono">{u.codigo}</strong> {u.titulo}
                        </span>
                        <span className="shrink-0 font-semibold">{u.estado}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end pt-1">
                <button
                  type="button"
                  onClick={handleResetAndClose}
                  className="px-5 py-2 text-xs font-bold text-white bg-violet-600 hover:bg-violet-700 rounded-xl shadow-sm transition cursor-pointer"
                >
                  Ver Mapa Actualizado
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

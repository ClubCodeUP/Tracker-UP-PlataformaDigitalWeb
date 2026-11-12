import React, { useEffect, useState } from 'react';
import { Target, CheckCircle2, BookOpen, Layers, Sparkles, Compass } from 'lucide-react';
import { ConcentrationDetail } from '../../types/curriculum';
import { UserProfile, trackerApi } from '../../services/trackerApi';

interface ConcentrationsViewProps {
  currentUser: UserProfile | null;
  careerId: number;
  careerName: string;
  selectedConcentrationId: number | null;
  onSelectConcentration: (concentrationId: number | null) => Promise<void>;
  onNavigateToMap: () => void;
  onOpenLogin: () => void;
}

export const ConcentrationsView: React.FC<ConcentrationsViewProps> = ({
  currentUser,
  careerId,
  careerName,
  selectedConcentrationId,
  onSelectConcentration,
  onNavigateToMap,
  onOpenLogin,
}) => {
  const [concentrations, setConcentrations] = useState<ConcentrationDetail[]>([]);
  const [generalElectives, setGeneralElectives] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<number | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await trackerApi.getCareerConcentrations(careerId);
        if (res) {
          setConcentrations(res.concentraciones || []);
          setGeneralElectives(res.electivos_generales || []);
        }
      } catch (err) {
        console.error('Error cargando concentraciones:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [careerId]);

  const handleChoose = async (concId: number | null) => {
    if (!currentUser) {
      onOpenLogin();
      return;
    }
    setSavingId(concId);
    try {
      await onSelectConcentration(concId);
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-[#FBFBFE] px-6 py-8 text-slate-800">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Cabecera de la Sección */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
              <Target className="w-3.5 h-3.5" />
              <span>Especialización Académica</span>
            </div>
            <h2 className="text-2xl font-black text-slate-900 tracking-tight">
              Concentraciones de {careerName}
            </h2>
            <p className="text-xs text-slate-500 mt-1 max-w-2xl">
              Elige tu concentración temática para resaltar automáticamente los cursos electivos recomendados en tu mapa curricular y proyecciones de matrícula.
            </p>
          </div>

          <button
            onClick={onNavigateToMap}
            className="px-4 py-2.5 bg-white border border-violet-200 text-violet-700 font-bold rounded-2xl text-xs hover:bg-violet-50 transition-all flex items-center gap-2 self-start shadow-sm"
          >
            <Compass className="w-4 h-4 text-violet-600" />
            Ver en el Mapa Académico
          </button>
        </div>

        {/* Loading state */}
        {loading ? (
          <div className="py-20 text-center text-slate-400 text-xs">
            Cargando especialidades y asignaturas electivas...
          </div>
        ) : concentrations.length === 0 ? (
          <div className="p-12 text-center bg-white rounded-3xl border border-violet-100 text-slate-500 text-xs">
            No se encontraron concentraciones específicas precargadas para esta carrera.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {concentrations.map((conc) => {
              const isSelected = selectedConcentrationId === conc.id;
              const isSaving = savingId === conc.id;

              return (
                <div
                  key={conc.id}
                  className={`
                    relative rounded-3xl p-6 bg-white border transition-all duration-300 flex flex-col justify-between shadow-sm
                    ${isSelected
                      ? 'border-2 border-violet-600 ring-4 ring-violet-500/10 shadow-xl shadow-purple-500/10'
                      : 'border-violet-100 hover:border-violet-300 hover:shadow-md'
                    }
                  `}
                >
                  {/* Badge de Seleccionado */}
                  {isSelected && (
                    <div className="absolute top-4 right-4 bg-emerald-100 text-emerald-800 border border-emerald-300 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-sm">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      Concentración Activa
                    </div>
                  )}

                  <div>
                    <div className="flex items-center gap-2 text-xs font-bold text-violet-600 mb-1">
                      <span className="font-mono bg-violet-50 px-2 py-0.5 rounded border border-violet-200">
                        {conc.codigo}
                      </span>
                    </div>

                    <h3 className="text-lg font-black text-slate-900 mt-1 mb-2 pr-28">
                      {conc.nombre}
                    </h3>

                    <p className="text-xs text-slate-600 leading-relaxed mb-4">
                      {conc.descripcion || 'Especialización temática oficial para profundizar competencias profesionales.'}
                    </p>

                    {/* Resumen de cursos */}
                    <div className="pt-4 border-t border-slate-100">
                      <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-3">
                        <span className="flex items-center gap-1.5">
                          <BookOpen className="w-3.5 h-3.5 text-violet-500" />
                          Asignaturas Vinculadas ({conc.cursos.length})
                        </span>
                        <span className="text-slate-500 text-[11px]">
                          {conc.creditos_totales} créditos disponibles
                        </span>
                      </div>

                      {conc.cursos.length === 0 ? (
                        <p className="text-[11px] text-slate-400 italic">
                          Los cursos electivos se asignan según la oferta semestral de la facultad.
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {conc.cursos.map((course) => (
                            <div
                              key={course.id}
                              className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between text-xs"
                            >
                              <div className="flex items-center gap-2 overflow-hidden">
                                <span className="font-mono text-[10px] font-bold text-slate-500 shrink-0">
                                  {course.codigo}
                                </span>
                                <span className="font-medium text-slate-800 truncate" title={course.nombre}>
                                  {course.nombre}
                                </span>
                              </div>
                              <div className="flex items-center gap-2 shrink-0 text-[10px] text-slate-500">
                                <span>Ciclo {course.ciclo}</span>
                                <span className="bg-white px-1.5 py-0.5 rounded border border-slate-200 font-semibold">
                                  {course.creditos} cr
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Botón de Selección */}
                  <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
                    <span className="text-[11px] text-slate-400">
                      {isSelected ? 'Tu preferencia actual' : 'Disponible para tu carrera'}
                    </span>

                    {isSelected ? (
                      <button
                        onClick={() => handleChoose(null)}
                        disabled={isSaving}
                        className="px-3.5 py-2 text-xs font-bold text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-all"
                      >
                        Quitar Selección
                      </button>
                    ) : (
                      <button
                        onClick={() => handleChoose(conc.id)}
                        disabled={isSaving}
                        className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white text-xs font-bold rounded-xl shadow-md shadow-violet-500/20 transition-all flex items-center gap-1.5"
                      >
                        <Sparkles className="w-3.5 h-3.5" />
                        {isSaving ? 'Guardando...' : 'Elegir Concentración'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Sección de Electivos Generales si existen */}
        {generalElectives.length > 0 && (
          <div className="bg-white rounded-3xl border border-violet-100 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-2 flex items-center gap-2">
              <Layers className="w-4 h-4 text-violet-600" />
              Electivos de Libre Elección / Generales ({generalElectives.length})
            </h3>
            <p className="text-xs text-slate-500 mb-4">
              Cursos electivos comunes que pueden ser cursados independientemente de la concentración seleccionada.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {generalElectives.map((c) => (
                <div key={c.id} className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs">
                  <div className="flex justify-between text-[10px] text-slate-500 mb-1">
                    <span className="font-mono font-bold text-slate-700">{c.codigo}</span>
                    <span>{c.creditos} cr</span>
                  </div>
                  <div className="font-bold text-slate-800 line-clamp-1">{c.nombre}</div>
                  <div className="text-[10px] text-slate-400 mt-1">Ciclo sugerido: {c.ciclo}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

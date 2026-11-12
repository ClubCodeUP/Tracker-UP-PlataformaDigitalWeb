import React from 'react';
import { Compass, GraduationCap, LogIn, UserPlus, LogOut, Zap, FileUp } from 'lucide-react';
import { CareerSummary, UserProfile } from '../services/trackerApi';
import { NavbarTabs, ActiveTab } from './Navigation/NavbarTabs';

interface HeaderProps {
  currentUser: UserProfile | null;
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  studentName?: string;
  careerName?: string;
  careers?: CareerSummary[];
  selectedCareerId?: number;
  onSelectCareer?: (careerId: number) => void;
  onOpenRecommendation?: () => void;
  isQuickEditMode?: boolean;
  onToggleQuickEdit?: () => void;
  onOpenLogin?: () => void;
  onOpenRegister?: () => void;
  onLogout?: () => void;
  onOpenImportTranscript?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentUser,
  activeTab,
  onTabChange,
  studentName = 'Estudiante UP',
  careerName = 'Ingeniería de la Información',
  careers = [],
  selectedCareerId,
  onSelectCareer,
  isQuickEditMode = false,
  onToggleQuickEdit,
  onOpenLogin,
  onOpenRegister,
  onLogout,
  onOpenImportTranscript,
}) => {
  const isAuth = !!currentUser;
  const isAdmin = currentUser?.rol === 'ADMIN';
  const displayName = isAuth ? `${currentUser.nombres} ${currentUser.apellidos}` : studentName;
  const displayCareer = isAuth ? (currentUser.carrera_nombre || careerName) : careerName;

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-violet-100 px-6 py-2.5 flex items-center justify-between text-slate-900 select-none shadow-sm z-30">
      {/* Logo y Nombre de Plataforma */}
      <div className="flex items-center gap-3 shrink-0">
        <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-violet-600 to-purple-500 flex items-center justify-center shadow-md shadow-purple-500/20">
          <Compass className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-base font-black tracking-tight text-slate-900 flex items-center gap-1.5">
              Tracker UP
              <span className="text-[10px] font-bold bg-violet-100 text-violet-700 border border-violet-200 px-1.5 py-0.2 rounded-lg uppercase tracking-wider">
                v2.0
              </span>
            </h1>
          </div>
          <p className="text-[10px] text-slate-400 font-medium hidden sm:block">
            Seguimiento de Carrera & Proyecciones
          </p>
        </div>
      </div>

      {/* Pestañas de Navegación Centrales */}
      <div className="hidden md:block">
        <NavbarTabs activeTab={activeTab} onTabChange={onTabChange} isAdmin={isAdmin} />
      </div>

      {/* Selector de Carrera, Acciones y Perfil */}
      <div className="flex items-center gap-2.5 shrink-0">
        {/* Selector Dinámico de Carrera */}
        {careers.length > 0 && onSelectCareer && (
          <div className="hidden xl:flex items-center gap-2 bg-white/70 border border-violet-100 rounded-2xl px-2.5 py-1.5 shadow-sm">
            <GraduationCap className="w-4 h-4 text-violet-600 shrink-0" />
            <select
              value={selectedCareerId}
              onChange={(e) => onSelectCareer(Number(e.target.value))}
              className="bg-transparent text-xs font-semibold text-slate-700 focus:outline-none cursor-pointer pr-1 max-w-[210px] truncate"
            >
              {careers.map((c) => (
                <option key={c.id} value={c.id} className="bg-white text-slate-800">
                  {c.nombre} ({c.codigo})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Botón Importar Transcript PDF */}
        {onOpenImportTranscript && (
          <button
            type="button"
            onClick={onOpenImportTranscript}
            title="Importar avance desde Unofficial Transcript (PDF)"
            className="px-3 py-1.5 text-xs font-semibold text-violet-700 bg-violet-50 hover:bg-violet-100 border border-violet-200 rounded-2xl transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <FileUp className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Importar PDF</span>
          </button>
        )}

        {/* Botón de Modo Edición Rápida (Opción 1) */}
        {onToggleQuickEdit && (
          <button
            onClick={onToggleQuickEdit}
            title={
              isQuickEditMode
                ? 'Desactivar Modo Edición Rápida'
                : 'Activar Modo Edición Rápida (Aprobar cursos con 1 solo clic)'
            }
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95 border ${
              isQuickEditMode
                ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/30 ring-2 ring-emerald-400/50'
                : 'bg-slate-900 hover:bg-slate-800 text-slate-200 border-slate-700 hover:border-slate-600'
            }`}
          >
            <Zap
              className={`w-3.5 h-3.5 ${
                isQuickEditMode ? 'fill-slate-950 text-slate-950' : 'text-emerald-400'
              }`}
            />
            <span className="hidden sm:inline">Edición Rápida</span>
            {isQuickEditMode && (
              <span className="w-1.5 h-1.5 rounded-full bg-slate-950 animate-ping ml-0.5" />
            )}
          </button>
        )}

        {/* Sección de Autenticación / Perfil */}
        {isAuth ? (
          <div className="border-l border-violet-100 pl-3 flex items-center gap-2">
            <div className={`w-8 h-8 rounded-full border flex items-center justify-center font-bold text-xs ${
              isAdmin 
                ? 'bg-rose-100 border-rose-300 text-rose-800' 
                : 'bg-violet-100 border-violet-200 text-violet-700'
            }`}>
              {isAdmin ? 'A' : (currentUser?.nombres?.charAt(0) || 'U')}
            </div>
            <div className="hidden sm:block text-left">
              <span className="text-xs font-bold text-slate-800 block leading-tight max-w-[150px] truncate">
                {displayName}
              </span>
              <span className="text-[10px] text-slate-500 block truncate max-w-[150px]" title={`${currentUser?.email} · ${displayCareer}`}>
                {isAdmin ? 'Administrador UP' : displayCareer}
              </span>
            </div>
            {onLogout && (
              <button
                onClick={onLogout}
                title="Cerrar Sesión"
                className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors ml-1"
              >
                <LogOut className="w-4 h-4" />
              </button>
            )}
          </div>
        ) : (
          <div className="border-l border-violet-100 pl-3 flex items-center gap-2">
            {onOpenLogin && (
              <button
                onClick={onOpenLogin}
                className="px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-violet-700 bg-white/70 hover:bg-violet-50 border border-violet-100 rounded-2xl transition-colors flex items-center gap-1.5"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Ingresar</span>
              </button>
            )}
            {onOpenRegister && (
              <button
                onClick={onOpenRegister}
                className="px-3 py-1.5 text-xs font-bold text-white bg-violet-600 hover:bg-violet-700 rounded-2xl shadow-sm shadow-violet-500/20 transition-all active:scale-95 flex items-center gap-1.5"
              >
                <UserPlus className="w-3.5 h-3.5" />
                <span>Registrarse</span>
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  );
};

import React, { useState, useEffect } from 'react';
import { X, Mail, Lock, User, GraduationCap, Calendar, Sparkles, AlertCircle, LogIn, UserPlus } from 'lucide-react';
import { CareerSummary, trackerApi, UserProfile } from '../../services/trackerApi';

interface AuthModalProps {
  isOpen: boolean;
  initialMode?: 'login' | 'register';
  careers: CareerSummary[];
  onClose: () => void;
  onSuccess: (profile: UserProfile) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  initialMode = 'login',
  careers,
  onClose,
  onSuccess,
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nombres, setNombres] = useState('');
  const [apellidos, setApellidos] = useState('');
  const [carreraId, setCarreraId] = useState<number>(careers[0]?.id || 1);
  const [concentracionId, setConcentracionId] = useState<number | null>(null);
  const [periodoIngreso, setPeriodoIngreso] = useState('2024-1');

  useEffect(() => {
    setMode(initialMode);
    setError(null);
  }, [initialMode, isOpen]);

  // Si cambia la carrera en registro, actualizar concentración si aplica
  useEffect(() => {
    if (careers.length > 0 && !carreraId) {
      setCarreraId(careers[0].id);
    }
    const currentCareer = careers.find((c) => c.id === carreraId);
    if (currentCareer && currentCareer.concentraciones && currentCareer.concentraciones.length > 0) {
      setConcentracionId(currentCareer.concentraciones[0].id);
    } else {
      setConcentracionId(null);
    }
  }, [carreraId, careers]);

  if (!isOpen) return null;

  const currentCareer = careers.find((c) => c.id === carreraId);
  const availableConcentraciones = currentCareer?.concentraciones || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const cleanEmail = email.trim().toLowerCase();
      if (!cleanEmail.endsWith('@up.edu.pe')) {
        throw new Error('El correo debe pertenecer al dominio institucional de la Universidad del Pacífico (@up.edu.pe).');
      }

      if (mode === 'login') {
        await trackerApi.login({
          email: cleanEmail,
          password,
        });
      } else {
        if (!nombres.trim() || !apellidos.trim()) {
          throw new Error('Por favor ingresa tus nombres y apellidos completos.');
        }
        if (password.length < 6) {
          throw new Error('La contraseña debe tener al menos 6 caracteres.');
        }

        await trackerApi.register({
          email: cleanEmail,
          password,
          nombres: nombres.trim(),
          apellidos: apellidos.trim(),
          carrera_id: carreraId,
          concentracion_id: concentracionId || null,
          periodo_ingreso: periodoIngreso,
        });
      }

      // Obtener el perfil recién autenticado
      const profile = await trackerApi.getProfile();
      onSuccess(profile);
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Ocurrió un error al procesar la solicitud.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity duration-300"
      />

      {/* Contenedor del Modal */}
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl shadow-blue-500/10 overflow-hidden z-10 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Encabezado con Gradiente */}
        <div className="px-6 pt-6 pb-4 bg-gradient-to-b from-blue-950/40 to-transparent border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-600/30">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">
                {mode === 'login' ? 'Iniciar Sesión en Tracker UP' : 'Crear Cuenta Estudiantil UP'}
              </h2>
              <p className="text-[11px] text-slate-400">
                Universidad del Pacífico · Plataforma Académica
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Selector de Modo (Pestañas) */}
        <div className="px-6 pt-4">
          <div className="grid grid-cols-2 gap-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/70">
            <button
              type="button"
              onClick={() => { setMode('login'); setError(null); }}
              className={`py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === 'login'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LogIn className="w-3.5 h-3.5" />
              Iniciar Sesión
            </button>
            <button
              type="button"
              onClick={() => { setMode('register'); setError(null); }}
              className={`py-2 text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition-all ${
                mode === 'register'
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserPlus className="w-3.5 h-3.5" />
              Registrarse
            </button>
          </div>
        </div>

        {/* Mensaje de Error */}
        {error && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          {/* Campos adicionales de Registro */}
          {mode === 'register' && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Nombres *
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                    <input
                      type="text"
                      required
                      value={nombres}
                      onChange={(e) => setNombres(e.target.value)}
                      placeholder="ej. Fernando"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Apellidos *
                  </label>
                  <input
                    type="text"
                    required
                    value={apellidos}
                    onChange={(e) => setApellidos(e.target.value)}
                    placeholder="ej. Sánchez"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Programa Académico (Carrera UP) *
                </label>
                <div className="relative">
                  <GraduationCap className="w-4 h-4 text-slate-500 absolute left-3 top-2.5 pointer-events-none" />
                  <select
                    value={carreraId}
                    onChange={(e) => setCarreraId(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-8 py-2 text-xs text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 appearance-none cursor-pointer"
                  >
                    {careers.map((c) => (
                      <option key={c.id} value={c.id} className="bg-slate-900 text-white">
                        {c.nombre} ({c.codigo})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {availableConcentraciones.length > 0 && (
                <div>
                  <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                    Línea de Concentración / Especialidad
                  </label>
                  <select
                    value={concentracionId || ''}
                    onChange={(e) => setConcentracionId(e.target.value ? Number(e.target.value) : null)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 appearance-none cursor-pointer"
                  >
                    <option value="" className="bg-slate-900 text-slate-400">
                      Sin concentración definida / General
                    </option>
                    {availableConcentraciones.map((co) => (
                      <option key={co.id} value={co.id} className="bg-slate-900 text-white">
                        {co.nombre}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div>
                <label className="block text-[11px] font-semibold text-slate-300 mb-1">
                  Periodo de Ingreso *
                </label>
                <div className="relative">
                  <Calendar className="w-4 h-4 text-slate-500 absolute left-3 top-2.5 pointer-events-none" />
                  <select
                    value={periodoIngreso}
                    onChange={(e) => setPeriodoIngreso(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-8 py-2 text-xs text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 appearance-none cursor-pointer"
                  >
                    <option value="2026-1" className="bg-slate-900">2026-1 (Ingresante actual)</option>
                    <option value="2025-2" className="bg-slate-900">2025-2</option>
                    <option value="2025-1" className="bg-slate-900">2025-1</option>
                    <option value="2024-2" className="bg-slate-900">2024-2</option>
                    <option value="2024-1" className="bg-slate-900">2024-1</option>
                    <option value="2023-2" className="bg-slate-900">2023-2</option>
                    <option value="2023-1" className="bg-slate-900">2023-1</option>
                    <option value="2022-2" className="bg-slate-900">2022-2</option>
                    <option value="2022-1" className="bg-slate-900">2022-1</option>
                    <option value="2021-1" className="bg-slate-900">2021-1</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {/* Correo Institucional */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Correo Institucional UP *
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ej. 20240001@up.edu.pe"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all font-mono"
              />
            </div>
            <p className="text-[10px] text-slate-500 mt-1">
              Obligatorio: debe terminar en <span className="text-blue-400 font-mono">@up.edu.pe</span>
            </p>
          </div>

          {/* Contraseña */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-300 mb-1">
              Contraseña *
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
            </div>
            {mode === 'register' && (
              <p className="text-[10px] text-slate-500 mt-1">
                Mínimo 6 caracteres
              </p>
            )}
          </div>

          {/* Botón de Enviar */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-blue-500/20 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-2"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : mode === 'login' ? (
              <>
                <LogIn className="w-4 h-4" />
                <span>Ingresar a Mi Tracker</span>
              </>
            ) : (
              <>
                <UserPlus className="w-4 h-4" />
                <span>Registrar Mi Cuenta</span>
              </>
            )}
          </button>

          {/* Switch de modo al fondo */}
          <div className="text-center pt-2">
            {mode === 'login' ? (
              <p className="text-xs text-slate-400">
                ¿Eres nuevo en la plataforma?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('register'); setError(null); }}
                  className="text-blue-400 font-semibold hover:underline"
                >
                  Regístrate aquí
                </button>
              </p>
            ) : (
              <p className="text-xs text-slate-400">
                ¿Ya tienes una cuenta registrada?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('login'); setError(null); }}
                  className="text-blue-400 font-semibold hover:underline"
                >
                  Inicia sesión aquí
                </button>
              </p>
            )}
          </div>

        </form>

      </div>
    </div>
  );
};


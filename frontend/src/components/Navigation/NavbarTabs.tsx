import React from 'react';
import { LayoutDashboard, Compass, Target, Sparkles, ShieldCheck } from 'lucide-react';

export type ActiveTab = 'dashboard' | 'map' | 'concentrations' | 'projection' | 'admin';

interface NavbarTabsProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
  isAdmin?: boolean;
}

export const NavbarTabs: React.FC<NavbarTabsProps> = ({
  activeTab,
  onTabChange,
  isAdmin = false,
}) => {
  const tabs = [
    { id: 'dashboard' as ActiveTab, label: 'Inicio', icon: LayoutDashboard },
    { id: 'map' as ActiveTab, label: 'Mapa Académico', icon: Compass },
    { id: 'concentrations' as ActiveTab, label: 'Concentraciones', icon: Target },
    { id: 'projection' as ActiveTab, label: 'Proyección', icon: Sparkles },
    ...(isAdmin ? [{ id: 'admin' as ActiveTab, label: 'Administración', icon: ShieldCheck }] : []),
  ];

  return (
    <nav className="flex items-center gap-1 bg-slate-100/80 p-1 rounded-2xl border border-slate-200/80 shadow-inner">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        const isSpecialAdmin = tab.id === 'admin';

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all select-none
              ${isActive
                ? isSpecialAdmin
                  ? 'bg-rose-600 text-white shadow-md shadow-rose-500/20'
                  : 'bg-white text-violet-700 shadow-sm shadow-purple-500/10'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/50'
              }
            `}
          >
            <Icon className={`w-3.5 h-3.5 ${isActive ? (isSpecialAdmin ? 'text-white' : 'text-violet-600') : 'text-slate-400'}`} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
};

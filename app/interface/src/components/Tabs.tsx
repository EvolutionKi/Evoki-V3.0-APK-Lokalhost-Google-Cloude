/**
 * Evoki V3.0 - Tabs Component
 * ORIGINAL V2.0 DESIGN mit Icons!
 */
import { Tab } from '../types';

interface TabsProps {
    activeTab: Tab;
    onTabChange: (tab: Tab) => void;
}

// Tab Configuration (ORIGINAL V2.0!)
const TABS_CONFIG = [
    { id: Tab.Temple, label: 'Evoki\'s Tempel (Alt)', icon: '🏛️' },
    { id: Tab.EngineConsole, label: 'Engine-Konsole', icon: '🖥️' },
    { id: Tab.Trialog, label: 'Trialog', icon: '💬' },
    { id: Tab.API, label: 'Agenten & Teams', icon: '👥' },
    { id: Tab.RuleSearch, label: 'Index', icon: '📖' },
    { id: Tab.VoiceSettings, label: 'Daten-Upload', icon: '📁' },
    { id: Tab.Metrics, label: 'Metrik-Tuning', icon: '⚙️' },
    { id: Tab.Analysis, label: 'Analyse', icon: '📊' },
    { id: Tab.ErrorLog, label: 'Analyse (Einheitlich)', icon: '📈' },
    { id: Tab.DeepStorage, label: 'HyperV3.0 Deep Storage', icon: '🗄️' },
    { id: Tab.Settings, label: 'Fehlerprotokoll', icon: '⚠️' },
];

export default function Tabs({ activeTab, onTabChange }: TabsProps) {
    return (
        <nav className="flex-shrink-0 bg-navy-800 border-b border-navy-700">
            <div className="flex space-x-1 px-3 overflow-x-auto">
                {TABS_CONFIG.map(({ id, label, icon }) => (
                    <button
                        key={id}
                        onClick={() => onTabChange(id)}
                        className={`flex-shrink-0 flex items-center gap-2 px-3 py-2 text-xs font-medium transition-colors duration-200 border-b-2
                            ${activeTab === id
                                ? 'border-cyan-400 text-cyan-400'
                                : 'border-transparent text-gray-400 hover:text-white hover:border-gray-500'
                            }
                        `}
                    >
                        <span>{icon}</span>
                        <span className="hidden lg:inline whitespace-nowrap">{label}</span>
                    </button>
                ))}
            </div>
        </nav>
    );
}

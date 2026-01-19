/**
 * Evoki V3.0 - Main App Component
 * ORIGINAL V2.0 NAVY DESIGN!
 */
import { useState } from 'react';
import { Tab } from './types';
import Tabs from './components/Tabs';
import TempleTab from './components/core/TempleTab';
import {
  MetricsTab,
  TrialogTab,
  AnalysisTab,
  RuleSearchTab,
  APITab,
  VoiceSettingsTab,
  DeepStorageTab,
  PipelineLogTab,
  EngineConsoleTab,
  ErrorLogTab,
  SettingsTab,
  AboutTab
} from './components/TabPanels';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>(Tab.Temple);

  const renderTabContent = () => {
    switch (activeTab) {
      case Tab.Temple: return <TempleTab />;
      case Tab.Metrics: return <MetricsTab />;
      case Tab.Trialog: return <TrialogTab />;
      case Tab.Analysis: return <AnalysisTab />;
      case Tab.RuleSearch: return <RuleSearchTab />;
      case Tab.API: return <APITab />;
      case Tab.VoiceSettings: return <VoiceSettingsTab />;
      case Tab.DeepStorage: return <DeepStorageTab />;
      case Tab.PipelineLog: return <PipelineLogTab />;
      case Tab.EngineConsole: return <EngineConsoleTab />;
      case Tab.ErrorLog: return <ErrorLogTab />;
      case Tab.Settings: return <SettingsTab />;
      case Tab.About: return <AboutTab />;
      default: return <TempleTab />;
    }
  };

  return (
    <div
      className="flex flex-col h-screen text-white"
      style={{ backgroundColor: 'var(--bg-primary)' }}
    >
      {/* Header - Theme Aware */}
      <header
        className="flex-shrink-0 px-4 md:px-6 py-3 flex items-center justify-between"
        style={{
          backgroundColor: 'var(--bg-primary)',
          borderBottom: '1px solid var(--border-primary)'
        }}
      >
        <div className="flex items-center gap-4">
          <h1
            className="text-xl md:text-2xl font-bold"
            style={{ color: 'var(--accent-primary)' }}
          >
            EVOKI
          </h1>
          <span
            className="hidden md:inline text-sm"
            style={{ color: 'var(--text-secondary)' }}
          >
            V3.0 DeepEarth
          </span>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <div
            className="hidden md:flex items-center gap-2 px-3 py-1 rounded-full"
            style={{
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--status-success)'
            }}
          >
            <div className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--status-success)' }}></div>
            <span className="text-xs" style={{ color: 'var(--status-success)' }}>Backend Online</span>
          </div>
          <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>Phase 0-3 Complete</span>
        </div>
      </header>

      {/* Tabs Navigation */}
      <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Content Area */}
      <main
        className="flex-1 overflow-y-auto"
        style={{ backgroundColor: 'var(--bg-primary)' }}
      >
        {renderTabContent()}
      </main>

      {/* Footer */}
      <footer
        className="flex-shrink-0 px-4 md:px-6 py-2"
        style={{
          backgroundColor: 'var(--bg-primary)',
          borderTop: '1px solid var(--border-primary)'
        }}
      >
        <div className="flex items-center justify-between text-xs" style={{ color: 'var(--text-secondary)' }}>
          <span>Evoki V3.0.0-alpha | Skeleton-First Protocol</span>
          <span>Built with React + FastAPI</span>
        </div>
      </footer>
    </div>
  );
}

export default App;

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
    <div className="flex flex-col h-screen bg-navy-900 text-white">
      {/* Header - V2.0 ORIGINAL Navy Style */}
      <header className="flex-shrink-0 bg-navy-900 border-b border-navy-700 px-4 md:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl md:text-2xl font-bold text-cyan-400">EVOKI</h1>
          <span className="hidden md:inline text-sm text-gray-400">V3.0 DeepEarth</span>
        </div>

        {/* Status Badge */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 bg-navy-800/50 border border-green-500/30 px-3 py-1 rounded-full">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-400">Backend Online</span>
          </div>
          <span className="text-xs text-gray-500">Phase 0-3 Complete</span>
        </div>
      </header>

      {/* Tabs Navigation */}
      <Tabs activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Content Area */}
      <main className="flex-1 overflow-y-auto bg-navy-900">
        {renderTabContent()}
      </main>

      {/* Footer */}
      <footer className="flex-shrink-0 bg-navy-900 border-t border-navy-700 px-4 md:px-6 py-2">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Evoki V3.0.0-alpha | Skeleton-First Protocol</span>
          <span>Built with React + FastAPI</span>
        </div>
      </footer>
    </div>
  );
}

export default App;

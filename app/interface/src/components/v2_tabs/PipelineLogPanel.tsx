/**
 * PipelineLogPanel.tsx
 * 
 * Zeigt detaillierte Pipeline-Logs mit allen Text-Übergaben.
 * Split-View: Links Übersicht der Sessions, Rechts detaillierte Logs.
 * 
 * Protokolliert jeden Übergabepunkt:
 * 1. User Input → Frontend
 * 2. Frontend → Backend (/api/bridge/process)
 * 3. Backend → Python CLI (query.py)
 * 4. Python FAISS → JSON Output
 * 5. Backend Parse → DualBackendBridge
 * 6. DualBackendBridge → Trinity Engines
 * 7. Trinity Results → A65 Candidate Selection
 * 8. A65 → GeminiContextBridge
 * 9. Context Building → Gemini Prompt
 * 10. Gemini API Call → Response
 * 11. Response → Vector Storage (12 DBs)
 * 12. Final Response → Frontend
 */

import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
// import { PipelineLogEntry } from '../types'; // Type does not exist - component not used
import { FileText, Search, Download, RefreshCw, Copy, Check } from './icons';

// Temporary local type definition until component is properly integrated or removed
interface PipelineLogEntry {
  id: string;
  timestamp: string;
  session_id: string;
  message_id: string;
  step_number: number; // 1-12
  step_name: string;
  data_transfer: {
    from: string;
    to: string;
    text_preview: string; // Erste 200 Zeichen
    full_text: string;
    size_bytes: number;
    token_count?: number;
  };
  metadata?: Record<string, any>;
}

interface Props {
  pipelineLog: PipelineLogEntry[];
  onLogUpdate?: (entry: PipelineLogEntry) => void;
  backendApiUrl: string;
}

interface SessionGroup {
  session_id: string;
  message_count: number;
  first_timestamp: string;
  last_timestamp: string;
  total_steps: number;
}

const ChevronRight = ({ className = '' }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const PipelineLogPanel = ({ pipelineLog, backendApiUrl }: Props) => {
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [selectedEntry, setSelectedEntry] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Gruppiere Logs nach Session
  const sessions: SessionGroup[] = React.useMemo(() => {
    const sessionMap = new Map<string, SessionGroup>();
    
    pipelineLog.forEach(entry => {
      if (!sessionMap.has(entry.session_id)) {
        sessionMap.set(entry.session_id, {
          session_id: entry.session_id,
          message_count: 0,
          first_timestamp: entry.timestamp,
          last_timestamp: entry.timestamp,
          total_steps: 0,
        });
      }
      
      const session = sessionMap.get(entry.session_id)!;
      session.message_count++;
      session.total_steps++;
      session.last_timestamp = entry.timestamp;
    });
    
    return Array.from(sessionMap.values()).sort((a, b) => 
      new Date(b.last_timestamp).getTime() - new Date(a.last_timestamp).getTime()
    );
  }, [pipelineLog]);

  // Filtere Logs für ausgewählte Session
  const filteredLogs = React.useMemo(() => {
    let logs = pipelineLog;
    
    if (selectedSession) {
      logs = logs.filter(log => log.session_id === selectedSession);
    }
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      logs = logs.filter(log => 
        log.step_name.toLowerCase().includes(term) ||
        log.data_transfer.from.toLowerCase().includes(term) ||
        log.data_transfer.to.toLowerCase().includes(term) ||
        log.data_transfer.text_preview.toLowerCase().includes(term)
      );
    }
    
    return logs.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }, [pipelineLog, selectedSession, searchTerm]);

  // Auto-Refresh Backend Logs
  useEffect(() => {
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(async () => {
        try {
          const response = await fetch(`${backendApiUrl}/api/pipeline/logs`);
          if (response.ok) {
            const data = await response.json();
            // Update logs würde hier propagiert werden
            console.log('[PipelineLog] Auto-refresh:', data.length, 'entries');
          }
        } catch (error) {
          console.error('[PipelineLog] Auto-refresh error:', error);
        }
      }, 5000); // Alle 5 Sekunden
    } else {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
        refreshIntervalRef.current = null;
      }
    }
    
    return () => {
      if (refreshIntervalRef.current) clearInterval(refreshIntervalRef.current);
    };
  }, [autoRefresh, backendApiUrl]);

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleExport = () => {
    const data = filteredLogs.map(log => ({
      timestamp: log.timestamp,
      session: log.session_id,
      message: log.message_id,
      step: `${log.step_number}. ${log.step_name}`,
      from: log.data_transfer.from,
      to: log.data_transfer.to,
      size: log.data_transfer.size_bytes,
      tokens: log.data_transfer.token_count,
      preview: log.data_transfer.text_preview,
      full_text: log.data_transfer.full_text,
    }));
    
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pipeline_log_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStepColor = (stepNumber: number): string => {
    const colors = [
      'text-blue-400',    // 1. User Input
      'text-cyan-400',    // 2. Frontend → Backend
      'text-green-400',   // 3. Backend → Python
      'text-emerald-400', // 4. Python FAISS
      'text-teal-400',    // 5. Backend Parse
      'text-sky-400',     // 6. Trinity Engines
      'text-indigo-400',  // 7. A65 Selection
      'text-violet-400',  // 8. GeminiContext
      'text-purple-400',  // 9. Prompt Build
      'text-fuchsia-400', // 10. Gemini API
      'text-pink-400',    // 11. Vector Storage
      'text-rose-400',    // 12. Final Response
    ];
    return colors[stepNumber - 1] || 'text-gray-400';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-3 mb-2">
          <FileText className="w-7 h-7 text-green-400" />
          Pipeline Logs & Text-Übergaben
        </h2>
        <p className="text-gray-400">
          Detaillierte Protokollierung aller Text-Übergaben an jedem Punkt der RAG-Pipeline (12 Schritte)
        </p>
      </div>

      {/* Controls */}
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Suche nach Schritt, Quelle, Ziel oder Text..."
                className="w-full bg-gray-900 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Auto-Refresh */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-colors ${
              autoRefresh
                ? 'bg-green-600 border-green-500 text-white'
                : 'bg-gray-900 border-gray-600 text-gray-300 hover:border-green-500'
            }`}
          >
            <RefreshCw className={`w-5 h-5 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto-Refresh {autoRefresh ? 'AN' : 'AUS'}
          </button>

          {/* Export */}
          <button
            onClick={handleExport}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Download className="w-5 h-5" />
            Export JSON
          </button>

          {/* Stats */}
          <div className="text-sm text-gray-400">
            {filteredLogs.length} Einträge | {sessions.length} Sessions
          </div>
        </div>
      </div>

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Session Overview */}
        <div className="lg:col-span-1">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              Sessions ({sessions.length})
            </h3>
            
            {/* "Alle" Option */}
            <button
              onClick={() => setSelectedSession(null)}
              className={`w-full text-left p-3 rounded-lg mb-2 transition-colors ${
                selectedSession === null
                  ? 'bg-blue-600 border border-blue-500'
                  : 'bg-gray-900 border border-gray-600 hover:border-blue-500'
              }`}
            >
              <div className="font-semibold text-white">Alle Sessions</div>
              <div className="text-sm text-gray-400">{pipelineLog.length} Einträge gesamt</div>
            </button>

            {/* Session List */}
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {sessions.map(session => (
                <button
                  key={session.session_id}
                  onClick={() => setSelectedSession(session.session_id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedSession === session.session_id
                      ? 'bg-blue-600 border border-blue-500'
                      : 'bg-gray-900 border border-gray-600 hover:border-blue-500'
                  }`}
                >
                  <div className="font-semibold text-white mb-1">
                    {session.session_id.slice(0, 12)}...
                  </div>
                  <div className="text-sm text-gray-400">
                    {session.total_steps} Schritte | {session.message_count} Messages
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(session.last_timestamp).toLocaleString('de-DE')}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Detailed Logs */}
        <div className="lg:col-span-2">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <ChevronRight className="w-5 h-5 text-green-400" />
              Log-Einträge ({filteredLogs.length})
            </h3>

            {/* Log Entries */}
            <div className="space-y-4 max-h-[700px] overflow-y-auto">
              {filteredLogs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  Keine Logs vorhanden. Starte eine Konversation im Tempel-Tab.
                </div>
              ) : (
                filteredLogs.map(entry => (
                  <div
                    key={entry.id}
                    onClick={() => setSelectedEntry(entry.id === selectedEntry ? null : entry.id)}
                    className={`bg-gray-900 border rounded-lg p-4 cursor-pointer transition-all ${
                      selectedEntry === entry.id
                        ? 'border-blue-500 shadow-lg'
                        : 'border-gray-600 hover:border-gray-500'
                    }`}
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className={`font-semibold ${getStepColor(entry.step_number)}`}>
                          Schritt {entry.step_number}: {entry.step_name}
                        </div>
                        <div className="text-sm text-gray-400 mt-1">
                          {new Date(entry.timestamp).toLocaleString('de-DE', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                          })}.${new Date(entry.timestamp).getMilliseconds().toString().padStart(3, '0')}
                        </div>
                      </div>
                      
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopyText(entry.data_transfer.full_text, entry.id);
                        }}
                        className="text-gray-400 hover:text-white transition-colors"
                        title="Text kopieren"
                      >
                        {copiedId === entry.id ? (
                          <Check className="w-5 h-5 text-green-400" />
                        ) : (
                          <Copy className="w-5 h-5" />
                        )}
                      </button>
                    </div>

                    {/* Transfer Info */}
                    <div className="flex items-center gap-2 mb-3 text-sm">
                      <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded border border-blue-600/40">
                        {entry.data_transfer.from}
                      </span>
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded border border-green-600/40">
                        {entry.data_transfer.to}
                      </span>
                      <span className="ml-auto text-gray-500">
                        {entry.data_transfer.size_bytes} bytes
                        {entry.data_transfer.token_count && ` | ${entry.data_transfer.token_count}t`}
                      </span>
                    </div>

                    {/* Text Preview */}
                    <div className="bg-gray-950 border border-gray-700 rounded p-3">
                      <div className="text-sm text-gray-300 mb-2">
                        {selectedEntry === entry.id ? (
                          <pre className="whitespace-pre-wrap font-mono text-xs text-gray-300 leading-relaxed">
                            {entry.data_transfer.full_text}
                          </pre>
                        ) : (
                          <div className="text-gray-400">
                            {entry.data_transfer.text_preview}
                            {entry.data_transfer.full_text.length > entry.data_transfer.text_preview.length && (
                              <span className="text-blue-400 ml-2">... (klicken für vollständigen Text)</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Metadata */}
                    {entry.metadata && Object.keys(entry.metadata).length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-700">
                        <div className="text-xs text-gray-500">
                          Metadata: {JSON.stringify(entry.metadata, null, 2)}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineLogPanel;

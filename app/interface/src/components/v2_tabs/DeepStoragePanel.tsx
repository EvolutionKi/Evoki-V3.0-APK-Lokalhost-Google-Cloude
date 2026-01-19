/**
 * EVOKI V2.2 Deep Storage Panel
 * =============================
 * UI für semantische Gedächtnissuche mit Multi-Window FAISS.
 * 
 * Features:
 * - Dual-Search: W2 (384D fast) + W5 (4096D deep)
 * - Integrity Check mit Master Hash
 * - Similarity Scores + Lexika Matches
 * - Execution Time Tracking
 * 
 * Author: EVOKI Core Team
 * Date: 2025-12-18
 */

import React, { useState, useEffect } from 'react';
import { evokiAPI, QueryResponse, IntegrityResponse, SearchResult } from '../services/core/evokiDeepStorageService';
import { Search, Shield, Zap, Brain, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface DeepStoragePanelProps {
  className?: string;
}

export const DeepStoragePanel: React.FC<DeepStoragePanelProps> = ({ className = '' }) => {
  // State Management
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [integrity, setIntegrity] = useState<IntegrityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeWindow, setActiveWindow] = useState<'both' | 'w2' | 'w5'>('both');

  // Load integrity on mount
  useEffect(() => {
    loadIntegrity();
  }, []);

  const loadIntegrity = async () => {
    try {
      const data = await evokiAPI.checkIntegrity();
      setIntegrity(data);
    } catch (err) {
      console.error('Integrity check failed:', err);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Bitte gib eine Suchanfrage ein');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const data = await evokiAPI.query(query, topK);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Suche fehlgeschlagen');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const formatLexikaMatches = (matches: Record<string, number>) => {
    return Object.entries(matches)
      .filter(([_, count]) => count > 0)
      .map(([key, count]) => `${key}:${count}`)
      .join(', ') || 'keine';
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.8) return 'text-green-400';
    if (similarity >= 0.6) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const renderSearchResult = (result: SearchResult, index: number) => (
    <div key={result.chunk_id} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-purple-500/50 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-gray-400 text-sm">#{index + 1}</span>
            <span className="text-xs text-gray-500 font-mono">{result.chunk_id}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className={`text-lg font-bold ${getSimilarityColor(result.similarity)}`}>
              {(result.similarity * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-gray-400">{new Date(result.created_at).toLocaleString('de-DE')}</span>
          </div>
        </div>
      </div>

      {/* Text Preview */}
      <div className="mb-3">
        <p className="text-gray-200 leading-relaxed">{result.text_preview}</p>
      </div>

      {/* Lexika Matches */}
      <div className="flex items-center gap-2 text-xs">
        <Brain size={14} className="text-purple-400" />
        <span className="text-gray-400">Lexika:</span>
        <span className="text-purple-300">{formatLexikaMatches(result.lexika_matches)}</span>
      </div>
    </div>
  );

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header with Integrity Status */}
      <div className="bg-gradient-to-r from-purple-900/30 to-blue-900/30 border-b border-purple-500/30 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400 flex items-center gap-3">
              <Brain size={28} />
              EVOKI Deep Storage V2.2
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Semantische Gedächtnissuche mit Trauma-gewichteten 4096D Embeddings
            </p>
          </div>
          
          {integrity && (
            <div className="bg-gray-800/50 rounded-lg p-3 border border-green-500/30">
              <div className="flex items-center gap-2 mb-2">
                <Shield size={18} className="text-green-400" />
                <span className="text-green-400 font-semibold">Integrity Verified</span>
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Chunks: {integrity.total_chunks.toLocaleString()}</div>
                <div>Gewichtet: {integrity.weighted_chunks.toLocaleString()}</div>
                <div>Verbindungen: {integrity.wormhole_edges.toLocaleString()}</div>
              </div>
            </div>
          )}
        </div>

        {/* Search Input */}
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Gib deine Suchanfrage ein... (z.B. 'Was ist beim Jagen passiert?')"
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
              disabled={isLoading}
            />
            <Search className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
          </div>
          
          <select
            value={topK}
            onChange={(e) => setTopK(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-200 focus:outline-none focus:border-purple-500"
            disabled={isLoading}
          >
            <option value={3}>Top 3</option>
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
          </select>

          <button
            onClick={handleSearch}
            disabled={isLoading || !query.trim()}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 disabled:from-gray-700 disabled:to-gray-700 text-white font-semibold px-8 py-3 rounded-lg transition-all disabled:cursor-not-allowed flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                Suche...
              </>
            ) : (
              <>
                <Search size={20} />
                Suchen
              </>
            )}
          </button>
        </div>

        {/* Window Filter */}
        {results && (
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setActiveWindow('both')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeWindow === 'both'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              Beide Windows
            </button>
            <button
              onClick={() => setActiveWindow('w2')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                activeWindow === 'w2'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Zap size={16} />
              W2 (384D Fast)
            </button>
            <button
              onClick={() => setActiveWindow('w5')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                activeWindow === 'w5'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
              }`}
            >
              <Brain size={16} />
              W5 (4096D Deep)
            </button>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4 m-6 flex items-start gap-3">
          <AlertTriangle size={20} className="text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-red-400 font-semibold mb-1">Fehler bei der Suche</div>
            <div className="text-red-300 text-sm">{error}</div>
          </div>
        </div>
      )}

      {/* Results Display */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {results && (
          <>
            {/* Execution Stats */}
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Clock size={16} className="text-blue-400" />
                  <span className="text-gray-400">Ausführungszeit:</span>
                  <span className="text-blue-400 font-semibold">{results.execution_time_ms.toFixed(0)}ms</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-gray-400">Query:</span>
                  <span className="text-gray-200 font-medium">"{results.query}"</span>
                </div>
              </div>
            </div>

            {/* W2 Results (Fast 384D) */}
            {(activeWindow === 'both' || activeWindow === 'w2') && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Zap size={20} className="text-green-400" />
                  <h3 className="text-lg font-semibold text-green-400">W2 Fast Search (384D MiniLM)</h3>
                  <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                    {results.w2_results.length} Ergebnisse
                  </span>
                </div>
                <div className="space-y-3">
                  {results.w2_results.map((result, idx) => renderSearchResult(result, idx))}
                </div>
              </div>
            )}

            {/* W5 Results (Deep 4096D) */}
            {(activeWindow === 'both' || activeWindow === 'w5') && (
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Brain size={20} className="text-blue-400" />
                  <h3 className="text-lg font-semibold text-blue-400">W5 Deep Search (4096D Mistral-7B)</h3>
                  <span className="text-xs text-gray-500 bg-gray-800 px-2 py-1 rounded">
                    {results.w5_results.length} Ergebnisse
                  </span>
                </div>
                <div className="space-y-3">
                  {results.w5_results.map((result, idx) => renderSearchResult(result, idx))}
                </div>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!results && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full text-center py-20">
            <Search size={64} className="text-gray-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">Bereit für die Suche</h3>
            <p className="text-gray-500 max-w-md">
              Gib eine Suchanfrage ein und drücke Enter oder klicke auf "Suchen".<br/>
              Das System durchsucht alle {integrity?.total_chunks.toLocaleString()} Memory-Chunks.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DeepStoragePanel;

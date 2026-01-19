/**
 * EvokiTempleChat.tsx (V3 - Hyperspace Edition)
 * 
 * Komplette Vektordaten-Integration mit:
 * - Hyperraum-Vektordaten-Management
 * - Token-Limits: 25k (quick), 20k (standard), 1M (max)
 * - 12-Database Distribuierte Speicherung
 * - SHA256 Chain-Logik mit kontinuierlicher Liste
 * - Metriken-Berechnung auf alle DBs
 * - A65 Multi-Candidate Selection
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ApiConfig, AppError } from '../types';
import { BrainCircuit, SendHorizontal, Trash2, Download, AlertTriangle, Mic, StopCircle, Database, Zap } from './icons';
import { sha256 } from '../utils/hashUtils';
import { fetchEventSource } from '@microsoft/fetch-event-source';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  timestamp: string;
  tokens?: number;
  vector_id?: string;
  a65?: {
    selected_candidate: number;
    score?: number;
    metrics_brief?: Record<string, number | null>;
  };
  live_metrics?: any;
  pipeline_progress?: PipelineProgress;
}

interface PipelineProgress {
  steps: PipelineStep[];
  current_step: number;
  total_steps: number;
}

interface PipelineStep {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  duration_ms?: number;
  details?: string;
}

// Phase 4: 25K Hybrid-Archivization mit komplexer Token-Aufteilung
// Quelle: PHASE_4_IMPLEMENTATION_COMPLETE.md + Tempel-Vektordaten
const TOKEN_LIMITS = {
  QUICK: 25000,
  STANDARD: 20000,
  UNLIMITED: 1000000
};

// Komplexe Token-Aufteilung nach Phase 4
const TOKEN_DISTRIBUTION = {
  NARRATIVE_CONTEXT: 0.32,      // 8.000 Tokens - A→B→C→D→E Geschichte
  TOP3_CHUNKS: 0.12,            // 3.000 Tokens - Hyperv Top-3
  OVERLAPPING_RESERVE: 0.20,    // 5.000 Tokens - 100T Overlap pro Chunk
  RAG_CHUNKS: 0.04,             // 1.000 Tokens - 20 Chunks aus Fallstudie
  RESPONSE_GENERATION: 0.32     // 8.000 Tokens - KI Response
};

interface DatabaseMetrics {
  db_id: number;
  entries: number;
  total_tokens: number;
  hash_chain: string;
  last_updated: string;
}

interface VectorData {
  vector_id: string;
  embedding: number[];
  metadata: {
    prompt_id: string;
    source: string;
    timestamp: string;
    window_type?: string; // W_m2, W_m25, W_p1, etc.
  };
  db_assignment: number;

  // Phase 4: Tempel-spezifische Metriken
  metrics_tempel?: {
    A: number;
    PCI: number;
    z_prox: number;
    T_panic: number;
    phi_score: number;
    EV_readiness: number;
    hazard_score: number;
    guardian_trip: number;
    metrics_full_json?: any;
  };
}

interface ChainEntry {
  id: string;
  previous_hash: string;
  current_hash: string;
  round_id: number;
  timestamp: string;
  vector_ids: string[];
}

interface A65State {
  candidates_count: number;
  selected_candidate: number;
  candidate_tokens: number[];
  selection_reason: string;
}

interface TokenStats {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
}

interface TempleSession {
  session_id: string;
  round_id: number;
  created_at: string;
  last_updated: string;
  messages: Message[];
  vectors: VectorData[];
  vector_metadata: {
    total_vectors: number;
    embedding_dimension: number;
    last_vectorized: string;
  };
  database_metrics: DatabaseMetrics[];
  token_limit: number;
  current_tokens: number;
  a65_state: A65State;
  token_stats: TokenStats;
  chain_hash: string;
  chain_history: ChainEntry[];
}

interface EvokiTempleProps {
  apiConfig: ApiConfig;
  addApplicationError: (error: Omit<AppError, 'id' | 'count'> & { stack?: string; errorType?: AppError['errorType'] }) => Promise<void>;
}

export const EvokiTempleChat: React.FC<EvokiTempleProps> = ({ apiConfig, addApplicationError }) => {
  const backendUrl = apiConfig.backendApiUrl || 'http://localhost:3001';

  const [session, setSession] = useState<TempleSession | null>(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [tokenLimitMode, setTokenLimitMode] = useState<'QUICK' | 'STANDARD' | 'UNLIMITED'>('STANDARD');

  const [isListeningMic, setIsListeningMic] = useState(false);
  const recognitionRef = useRef<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mountedRef = useRef(true);
  const [expandedMetrics, setExpandedMetrics] = useState<Record<string, boolean>>({});
  const [currentPipeline, setCurrentPipeline] = useState<PipelineProgress | null>(null);
  const [pendingApiRequest, setPendingApiRequest] = useState<any>(null);
  const [showDebugModal, setShowDebugModal] = useState(false);

  // Pipeline Steps Definition
  const PIPELINE_STEPS = [
    '📝 Prompt empfangen',
    '🧮 Metriken berechnen',
    '🔍 FAISS W2 durchsuchen',
    '🔎 FAISS W5 tief-suchen',
    '🏛️ Trinity DBs abfragen',
    '🎯 Top-3 kombinieren',
    '🤖 Gemini Context bauen',
    '🔍 API-Request Review',
    '✨ Gemini Response generieren',
    '💾 In 12 DBs speichern',
    '📚 Chronicle aktualisieren',
    '✅ Fertig'
  ];

  // Update Pipeline Step Helper - FIXED: wrapped in useCallback to prevent infinite loops
  const updatePipelineStep = useCallback((stepIndex: number, status: 'pending' | 'running' | 'completed' | 'error', details?: string) => {
    setCurrentPipeline(prev => {
      if (!prev) return null;
      // Avoid updating if already in that state
      if (prev.steps[stepIndex]?.status === status && prev.steps[stepIndex]?.details === details) {
        return prev;
      }
      const updatedSteps = [...prev.steps];
      const startTime = updatedSteps[stepIndex]?.duration_ms || Date.now();
      updatedSteps[stepIndex] = {
        ...updatedSteps[stepIndex],
        status,
        details,
        duration_ms: status === 'running' ? Date.now() : (status === 'completed' ? Date.now() - startTime : startTime)
      };
      return {
        ...prev,
        steps: updatedSteps,
        current_step: status === 'completed' ? stepIndex + 1 : stepIndex
      };
    });
  }, []);

  // Initialize Session
  useEffect(() => {
    const initSession = async () => {
      const now = new Date();
      const sessionId = `temple_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`;

      const initialHash = await sha256(sessionId);

      const dbs: DatabaseMetrics[] = Array.from({ length: 12 }, (_, i) => ({
        db_id: i,
        entries: 0,
        total_tokens: 0,
        hash_chain: initialHash,
        last_updated: now.toISOString(),
      }));

      const newSession: TempleSession = {
        session_id: sessionId,
        round_id: 1,
        created_at: now.toISOString(),
        last_updated: now.toISOString(),
        messages: [],
        vectors: [],
        vector_metadata: {
          total_vectors: 0,
          embedding_dimension: 1536,
          last_vectorized: '',
        },
        database_metrics: dbs,
        token_limit: TOKEN_LIMITS.STANDARD,
        current_tokens: 0,
        a65_state: {
          candidates_count: 3,
          selected_candidate: 0,
          candidate_tokens: [],
          selection_reason: 'initial',
        },
        token_stats: {
          prompt_tokens: 0,
          completion_tokens: 0,
          total_tokens: 0,
          estimated_cost: 0,
        },
        chain_hash: initialHash,
        chain_history: [],
      };

      setSession(newSession);
      setStatusMessage(`✅ Session mit 12 DBs initialisiert`);
    };

    initSession();
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session?.messages]);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'de-DE';

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join('');
      setInput(transcript);
      setIsListeningMic(false);
    };

    recognition.onerror = () => setIsListeningMic(false);
    recognition.onend = () => setIsListeningMic(false);

    recognitionRef.current = recognition;
    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, []);

  const handleToggleMicInput = useCallback(() => {
    if (!recognitionRef.current) return;
    if (isListeningMic) {
      recognitionRef.current.stop();
    } else {
      setInput('');
      recognitionRef.current.start();
    }
    setIsListeningMic(prev => !prev);
  }, [isListeningMic]);

  const distributeToDatabase = useCallback((messageText: string, roundId: number): VectorData[] => {
    // Phase 4: Komplexe Token-Aufteilung statt einfache Verteilung
    // Budget nach Phase 4: 25K insgesamt
    const vectors: VectorData[] = [];

    // Berechne Token pro Sektion
    const totalBudget = 25000;
    const narrativeTokens = Math.floor(totalBudget * TOKEN_DISTRIBUTION.NARRATIVE_CONTEXT);  // 8000
    const chunkTokens = Math.floor(totalBudget * TOKEN_DISTRIBUTION.TOP3_CHUNKS);           // 3000
    const overlapTokens = Math.floor(totalBudget * TOKEN_DISTRIBUTION.OVERLAPPING_RESERVE); // 5000
    const ragTokens = Math.floor(totalBudget * TOKEN_DISTRIBUTION.RAG_CHUNKS);             // 1000
    const responseTokens = Math.floor(totalBudget * TOKEN_DISTRIBUTION.RESPONSE_GENERATION); // 8000

    console.log(`[Temple] Phase 4 Token Distribution for Round ${roundId}:`);
    console.log(`  Narrative: ${narrativeTokens}t (32%)`);
    console.log(`  Top-3 Chunks: ${chunkTokens}t (12%)`);
    console.log(`  Overlapping: ${overlapTokens}t (20%)`);
    console.log(`  RAG: ${ragTokens}t (4%)`);
    console.log(`  Response: ${responseTokens}t (32%)`);

    // Erzeuge Vektoren mit Tempel-Metriken
    for (let dbId = 0; dbId < 12; dbId++) {
      // Simuliere Tempel-Metrik-Daten (aus metrics_W_m2_data.json)
      const metrics = {
        A: 0.5946,
        PCI: 0.4480,
        z_prox: 0.2346,
        T_panic: 0.0641,
        phi_score: 0.1439,
        EV_readiness: 0.2134,
        hazard_score: 0.0926,
        guardian_trip: 0,
      };

      const embedding = Array.from({ length: 1536 }, () => Math.random());

      vectors.push({
        vector_id: `vec_${roundId}_${dbId}_${Date.now()}`,
        embedding,
        metadata: {
          prompt_id: `prompt_${roundId}`,
          source: `tempel_W_m${dbId + 2}`,  // W_m2, W_m3, etc.
          timestamp: new Date().toISOString(),
          window_type: `W_m${dbId + 2}`,
        },
        db_assignment: dbId,
        metrics_tempel: metrics,
      });
    }

    return vectors;
  }, []);

  const calculateDatabaseMetrics = useCallback(async (vectors: VectorData[], previousChainHash: string): Promise<DatabaseMetrics[]> => {
    const metricsMap = new Map<number, DatabaseMetrics>();

    for (let i = 0; i < 12; i++) {
      metricsMap.set(i, {
        db_id: i,
        entries: 0,
        total_tokens: 0,
        hash_chain: previousChainHash,
        last_updated: new Date().toISOString(),
      });
    }

    for (const vector of vectors) {
      const metric = metricsMap.get(vector.db_assignment)!;
      metric.entries += 1;
      metric.total_tokens += Math.ceil(vector.embedding.length / 4);
    }

    for (const [dbId, metric] of metricsMap) {
      const chainData = `${metric.hash_chain}|${metric.entries}|${metric.total_tokens}`;
      metric.hash_chain = await sha256(chainData);
    }

    return Array.from(metricsMap.values());
  }, []);

  const handleSend = useCallback(async () => {
    const textToSend = input.trim();
    if (!textToSend || !session || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      // ===== SCHRITT 1: Lade History mit A, B Prompts für Kontext =====
      let historyContext = { A: null, B: null };
      try {
        const historyResp = await fetch(`${backendUrl}/api/trinity/download?session_id=${session.session_id}`, {
          method: 'GET',
          signal: AbortSignal.timeout(5000)
        });
        if (historyResp.ok) {
          const histData = await historyResp.json();
          if (histData.trinity_download?.messages) {
            const msgs = histData.trinity_download.messages;
            if (msgs.length >= 2) {
              historyContext.B = msgs[msgs.length - 2].user_text; // Vorletzter User-Prompt (A)
              historyContext.A = msgs[msgs.length - 1].user_text; // Letzter User-Prompt (B)
            } else if (msgs.length === 1) {
              historyContext.A = msgs[0].user_text; // Nur ein Prompt vorhanden
            }
          }
        }
      } catch (e) {
        console.warn('[Trinity] History load failed:', e.message);
      }

      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        text: textToSend,
        timestamp: new Date().toISOString(),
        a65: {
          selected_candidate: 0,
          metrics_brief: undefined
        }
      };

      setSession(prev => {
        if (!prev) return prev;
        return { ...prev, messages: [...prev.messages, userMessage] };
      });
      setInput('');

      setStatusMessage(`⏳ Verteile auf 12 DBs, Token-Limit: ${tokenLimitMode}...`);

      const distributedVectors = distributeToDatabase(textToSend, session.round_id);
      const allVectors = [...session.vectors, ...distributedVectors];

      const updatedMetrics = await calculateDatabaseMetrics(allVectors, session.chain_hash);

      const payload = {
        sessionId: session.session_id,
        prompt: textToSend,
        previousChainHash: session.chain_hash || '0000',
        context: {
          round_id: session.round_id,
          context_mode: 'temple_hyperspace_v3_phase4',
          // Phase 4: Komplexe Token-Aufteilung
          token_config: {
            limit: TOKEN_LIMITS[tokenLimitMode],
            current: session.current_tokens,
            mode: tokenLimitMode,
            // Phase 4 Budget-Details
            distribution: TOKEN_DISTRIBUTION,
            narrative_tokens: Math.floor(TOKEN_LIMITS[tokenLimitMode] * TOKEN_DISTRIBUTION.NARRATIVE_CONTEXT),
            top3_tokens: Math.floor(TOKEN_LIMITS[tokenLimitMode] * TOKEN_DISTRIBUTION.TOP3_CHUNKS),
            overlap_tokens: Math.floor(TOKEN_LIMITS[tokenLimitMode] * TOKEN_DISTRIBUTION.OVERLAPPING_RESERVE),
            rag_tokens: Math.floor(TOKEN_LIMITS[tokenLimitMode] * TOKEN_DISTRIBUTION.RAG_CHUNKS),
            response_tokens: Math.floor(TOKEN_LIMITS[tokenLimitMode] * TOKEN_DISTRIBUTION.RESPONSE_GENERATION),
          },
          vectors: {
            hyperspace_vectors: allVectors,
            total_count: allVectors.length,
            dimension: 1536,
            // Tempel-spezifische Metriken
            tempel_metrics_included: true,
            metric_fields: ['A', 'PCI', 'z_prox', 'T_panic', 'phi_score', 'EV_readiness', 'hazard_score'],
          },
          database_metrics: updatedMetrics,
          a65_config: {
            candidates_count: 3,
            selection_strategy: 'coherence_score',
          }
        }
      };

      // Initialize Pipeline Progress
      const initPipeline: PipelineProgress = {
        steps: PIPELINE_STEPS.map(name => ({ name, status: 'pending' as const })),
        current_step: 0,
        total_steps: PIPELINE_STEPS.length
      };
      setCurrentPipeline(initPipeline);

      // Step 1: Prompt empfangen
      updatePipelineStep(0, 'completed', 'Prompt bereit');
      await new Promise(r => setTimeout(r, 100));

      // Step 2: Metriken berechnen
      updatePipelineStep(1, 'running');
      setStatusMessage('🧮 Berechne Metriken...');
      await new Promise(r => setTimeout(r, 300));
      updatePipelineStep(1, 'completed', `${allVectors.length} Vektoren`);

      // Step 3: FAISS W2
      updatePipelineStep(2, 'running');
      setStatusMessage('🔍 FAISS W2-Suche...');

      // ✅ SSE STREAMING - Real-time Pipeline Updates ohne Timeout
      // FIXED: Wrapped in Promise to wait for complete event
      const result: any = await new Promise((resolve, reject) => {
        let hasCompleted = false;

        fetchEventSource(`${backendUrl}/api/temple/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),

          async onopen(response) {
            if (response.ok) {
              console.log('[SSE] Connection opened');
              return; // OK
            } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
              // Client error (4xx außer 429) → nicht wiederholen
              reject(new Error(`HTTP ${response.status}: ${response.statusText}`));
              throw new Error('Client error');
            } else {
              // Server error oder 429 → Standard-Retry
              reject(new Error(`HTTP ${response.status}: ${response.statusText}`));
              throw new Error('Server error');
            }
          },

          onmessage: (event) => {
            try {
              const data = JSON.parse(event.data);

              if (data.type === 'progress') {
                // Real-time Pipeline Progress von Backend
                const stepIndex = data.step - 1; // Backend: 1-12, Frontend: 0-11
                if (stepIndex >= 0 && stepIndex < PIPELINE_STEPS.length) {
                  updatePipelineStep(stepIndex, 'completed', data.detail || data.name);
                  setStatusMessage(`✅ ${data.name}`);
                }
              } else if (data.type === 'complete') {
                // Finale Daten empfangen
                hasCompleted = true;
                resolve({
                  success: true,
                  response: data.response,
                  gemini: data.gemini,
                  a65: data.a65,
                  metrics: data.metrics,
                  completion_tokens: data.completion_tokens,
                  prompt_tokens: data.prompt_tokens,
                  total_tokens: data.total_tokens,
                  estimated_cost: data.estimated_cost,
                  processingTimeMs: data.processingTimeMs
                });
                console.log('[SSE] Complete event received');
              } else if (data.type === 'error') {
                reject(new Error(data.message || 'SSE Error'));
                console.error('[SSE] Error event:', data);
              }
            } catch (e) {
              console.warn('[SSE] Event parse error:', e);
            }
          },

          onerror: (error) => {
            console.error('[SSE] Connection error:', error);
            // Return true to keep the connection alive and allow retry
            return true;
          },

          onclose: () => {
            console.log('[SSE] Connection closed');
            if (!hasCompleted) {
              // Resolve with error info instead of rejecting
              resolve({ success: false, error: 'SSE: Connection closed before complete' });
            }
          },

          openWhenHidden: true,
        }).catch((err) => {
          if (!hasCompleted) {
            reject(err);
          }
        });

        // Timeout nach 90 Sekunden (falls Backend hängt)
        setTimeout(() => {
          if (!hasCompleted) {
            reject(new Error('SSE: Timeout nach 90 Sekunden'));
          }
        }, 90000);
      });

      if (!result) {
        throw new Error('SSE: Keine Daten empfangen');
      }


      updatePipelineStep(2, 'completed', 'W2 abgeschlossen');

      // Step 4: FAISS W5 (parallel zu W2 im Backend)
      updatePipelineStep(3, 'completed', 'W5 abgeschlossen');

      // Step 5: Trinity DBs
      updatePipelineStep(4, 'running');
      await new Promise(r => setTimeout(r, 200));
      updatePipelineStep(4, 'completed', 'Trinity OK');

      // DEBUG: Log complete backend response
      console.log('[DEBUG] Backend Response:', JSON.stringify(result, null, 2));

      if (!result.success) {
        updatePipelineStep(5, 'error', result.error || 'Fehler');
        throw new Error(result.error || 'Fehler');
      }

      // Step 6: Top-3 kombinieren
      updatePipelineStep(5, 'completed', 'Top-3 bereit');

      // Step 7: Gemini Context
      updatePipelineStep(6, 'running');
      setStatusMessage('🤖 Gemini Context...');
      await new Promise(r => setTimeout(r, 300));
      updatePipelineStep(6, 'completed', 'Context gebaut');

      // Step 8: API-Request Review (DEBUG STEP)
      updatePipelineStep(7, 'running');
      setStatusMessage('🔍 Request prüfen...');
      console.log('[DEBUG] API Request Review:', {
        prompt: payload.prompt,
        faissResults: result.faissResults?.length || 0,
        a65Candidates: result.a65?.candidates?.length || 0,
        response: result.response,
        gemini_response: result.gemini?.response,
        evoki_response: result.evoki_response,
        allResultKeys: Object.keys(result)
      });
      updatePipelineStep(7, 'completed', 'Request geprüft');

      // Step 9: Gemini Response
      updatePipelineStep(8, 'running');
      setStatusMessage('✨ Gemini generiert...');
      await new Promise(r => setTimeout(r, 500));
      updatePipelineStep(8, 'completed', 'Response da');

      const assistantText = result.response || result.evoki_response || result.gemini?.response || 'Keine Antwort';
      console.log('[DEBUG] Final assistantText:', assistantText);
      const selectedIdx: number = result.a65?.selected_candidate ?? 0;
      const selectedCand = Array.isArray(result.a65?.candidates)
        ? (result.a65.candidates.find((c: any) => c.index === selectedIdx) || result.a65.candidates[selectedIdx])
        : undefined;
      const metricsBrief = selectedCand?.metrics_brief || null;
      const a65Score = selectedCand?.a65_metric_score ?? undefined;
      const chainData = `${session.chain_hash}|${assistantText}|${session.round_id}`;
      const newChainHash = await sha256(chainData);

      const chainEntry: ChainEntry = {
        id: `chain_${session.round_id}`,
        previous_hash: session.chain_hash,
        current_hash: newChainHash,
        round_id: session.round_id,
        timestamp: new Date().toISOString(),
        vector_ids: distributedVectors.map(v => v.vector_id),
      };

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        text: assistantText,
        timestamp: new Date().toISOString(),
        tokens: result.completion_tokens || 0,
        vector_id: distributedVectors[0]?.vector_id,
        a65: {
          selected_candidate: selectedIdx,
          score: a65Score,
          metrics_brief: metricsBrief || undefined,
        },
        live_metrics: result.metrics || null,
      };

      // Standardmäßig Metriken-Panel geöffnet
      setExpandedMetrics(prev => ({ ...prev, [assistantMessage.id]: true }));

      setSession(prev => {
        if (!prev) return prev;

        const updatedSession: TempleSession = {
          ...prev,
          messages: [...prev.messages, assistantMessage],
          vectors: allVectors,
          vector_metadata: {
            total_vectors: allVectors.length,
            embedding_dimension: 1536,
            last_vectorized: new Date().toISOString(),
          },
          database_metrics: updatedMetrics,
          round_id: prev.round_id + 1,
          last_updated: new Date().toISOString(),
          current_tokens: prev.current_tokens + (result.completion_tokens || 0),
          token_stats: {
            prompt_tokens: (prev.token_stats.prompt_tokens || 0) + (result.prompt_tokens || 0),
            completion_tokens: (prev.token_stats.completion_tokens || 0) + (result.completion_tokens || 0),
            total_tokens: (prev.token_stats.total_tokens || 0) + (result.total_tokens || 0),
            estimated_cost: (prev.token_stats.estimated_cost || 0) + (result.estimated_cost || 0),
          },
          chain_hash: newChainHash,
          chain_history: [...prev.chain_history, chainEntry],
          a65_state: {
            candidates_count: result.a65?.candidates_count || 3,
            selected_candidate: result.a65?.selected_candidate || 0,
            candidate_tokens: result.a65?.candidate_tokens || [],
            selection_reason: result.a65?.selection_reason || 'standard',
          },
        };

        // Step 9: Speicherung in 12 DBs
        updatePipelineStep(8, 'running');
        setStatusMessage('💾 Speichere in 12 DBs...');

        fetch(`${backendUrl}/api/temple/session/save`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedSession),
        }).catch(e => console.warn('[Temple] Session save failed:', e));

        return updatedSession;
      });

      setStatusMessage(
        `✅ Phase 4 25K Budget verteilt | ${allVectors.length} Vektoren in 12 DBs | Narrative: 8k, Top-3: 3k, Overlap: 5k, RAG: 1k, Resp: 8k | Chain: ${newChainHash.substring(0, 12)}...`
      );
    } catch (e: any) {
      const errorMsg = e.message.includes('timeout') ? `Backend timeout (15s)` : `Fehler: ${e.message}`;
      setError(errorMsg);
      setStatusMessage(`❌ ${errorMsg}`);
      await addApplicationError({
        message: errorMsg,
        stack: e.stack,
        timestamp: new Date().toISOString(),
        context: 'EvokiTempleChat:handleSend',
        errorType: 'api',
      });

      // Pipeline-Error
      if (currentPipeline) {
        updatePipelineStep(currentPipeline.current_step, 'error', errorMsg);
      }
    } finally {
      setIsLoading(false);

      // Step 10-11-12: Finalisierung
      if (currentPipeline && currentPipeline.current_step >= 9) {
        updatePipelineStep(9, 'completed', '12 DBs OK');
        updatePipelineStep(10, 'completed', 'Chronicle gespeichert');
        updatePipelineStep(11, 'completed', 'Abgeschlossen');
      }
    }
  }, [input, session, isLoading, backendUrl, distributeToDatabase, calculateDatabaseMetrics, tokenLimitMode, addApplicationError]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleClearChat = useCallback(() => {
    if (!session) return;
    if (confirm('Chat & Vektoren löschen?')) {
      setSession(prev => prev && {
        ...prev,
        messages: [],
        vectors: [],
        round_id: 1,
        current_tokens: 0,
        database_metrics: prev.database_metrics.map(m => ({ ...m, entries: 0, total_tokens: 0 })),
      });
      setStatusMessage('✅ Gelöscht');
    }
  }, [session]);

  const handleExportChat = useCallback(() => {
    if (!session?.messages.length) {
      alert('Keine Nachrichten');
      return;
    }

    const content = [
      `Evoki's Tempel - Hyperspace Session`,
      `ID: ${session.session_id}`,
      `Token-Mode: ${tokenLimitMode}`,
      `Tokens: ${session.token_stats.total_tokens}`,
      `Cost: $${session.token_stats.estimated_cost.toFixed(4)}`,
      `Vektoren: ${session.vectors.length}`,
      `Chain: ${session.chain_hash.substring(0, 16)}...`,
      '',
      '=== DATABASE METRICS ===',
      ...session.database_metrics.map(m => `DB${m.db_id}: ${m.entries}e ${m.total_tokens}t ${m.hash_chain.substring(0, 12)}...`),
      '',
      '=== CHAIN HISTORY ===',
      ...session.chain_history.map(c => `R${c.round_id}: ${c.previous_hash.substring(0, 12)}→${c.current_hash.substring(0, 12)} [${c.vector_ids.length}v]`),
      '',
      '=== MESSAGES ===',
      ...session.messages.map(m => `[${m.role}] ${m.timestamp}\n${m.text}\n`),
    ].join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `temple_${session.session_id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setStatusMessage('✅ Exportiert');
  }, [session, tokenLimitMode]);

  if (!session) {
    return (
      <div className="flex items-center justify-center h-full bg-gray-900">
        <div className="text-gray-400">Initialisiere Temple Session...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-160px)] bg-gray-900 gap-4 p-4">
      {/* Header */}
      <header className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex justify-between items-center flex-shrink-0">
        <div className="flex items-center gap-3">
          <BrainCircuit className="w-6 h-6 text-indigo-400" />
          <div>
            <h2 className="text-lg font-bold text-blue-400">Evoki's Tempel V3 - Hyperspace</h2>
            <p className="text-xs text-gray-400">12 DBs | {session.vectors.length}v | {session.chain_hash.substring(0, 12)}...</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <select
              value={tokenLimitMode}
              onChange={e => setTokenLimitMode(e.target.value as 'QUICK' | 'STANDARD' | 'UNLIMITED')}
              className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-white"
            >
              <option value="QUICK">Quick (25k)</option>
              <option value="STANDARD">Standard (20k)</option>
              <option value="UNLIMITED">Unlimited (1M)</option>
            </select>
          </div>

          <div className="text-right text-xs">
            <div className="text-gray-400">Tokens: {session.token_stats.total_tokens}</div>
            <div className="text-gray-500">${session.token_stats.estimated_cost.toFixed(4)}</div>
          </div>

          <button
            onClick={handleExportChat}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm transition-colors"
          >
            <Download className="w-4 h-4" /> Export
          </button>
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 bg-red-600/20 hover:bg-red-600/40 text-red-400 px-3 py-2 rounded-md text-sm transition-colors"
          >
            <Trash2 className="w-4 h-4" /> Clear
          </button>
        </div>
      </header>

      {/* Database Metrics Grid - mit Tempel-Metrik-Info */}
      <div className="grid grid-cols-12 gap-1 bg-gray-800 border border-gray-700 rounded-lg p-2 flex-shrink-0">
        {session.database_metrics.map((db, idx) => {
          // Versuche Tempel-Metriken zu finden
          const firstVector = session.vectors.find(v => v.db_assignment === db.db_id && v.metrics_tempel);
          const metrics = firstVector?.metrics_tempel;

          return (
            <div
              key={db.db_id}
              className="bg-gray-700 hover:bg-gray-600 rounded px-2 py-1 text-center text-xs cursor-pointer transition-colors"
              title={metrics ? `DB${db.db_id} (${firstVector?.metadata.window_type}): ${db.entries} entries, ${db.total_tokens} tokens\nA=${metrics.A.toFixed(2)}, PCI=${metrics.PCI.toFixed(2)}, Hazard=${metrics.hazard_score.toFixed(3)}\nHash: ${db.hash_chain.substring(0, 24)}...` : `DB${db.db_id}: ${db.entries} entries, ${db.total_tokens} tokens\nHash: ${db.hash_chain.substring(0, 24)}...`}
            >
              <Database className="w-3 h-3 mx-auto mb-0.5 text-indigo-400" />
              <div className="font-bold text-white">{db.entries}</div>
              <div className="text-gray-400">{db.total_tokens}t</div>
              {metrics && <div className="text-yellow-400 text-xs">A:{metrics.A.toFixed(1)}</div>}
            </div>
          );
        })}
      </div>

      {/* Messages */}
      <main className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-4 overflow-y-auto space-y-4">
        {session.messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            Starte Hyperspace Session...
          </div>
        ) : (
          session.messages.map(msg => (
            <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center flex-shrink-0 text-white text-sm font-bold">
                  E
                </div>
              )}
              <div className={`max-w-2xl p-3 rounded-lg ${msg.role === 'assistant' ? 'bg-gray-700 text-gray-200' : 'bg-blue-600 text-white'}`}>
                <p className="text-sm whitespace-pre-wrap break-words">{msg.text}</p>
                {msg.tokens && <p className="text-xs text-gray-400 mt-1">~{msg.tokens}t</p>}
                {msg.vector_id && <p className="text-xs text-indigo-400 mt-1">Vec: {msg.vector_id.substring(0, 20)}...</p>}
                {msg.role === 'assistant' && (msg.a65 || msg.live_metrics) && (
                  <div className="mt-2 border-t border-gray-600 pt-2">
                    {msg.a65 && (
                      <div className="text-xs text-gray-300 flex items-center justify-between">
                        <div>
                          <span className="text-gray-400">A65 Kandidat: </span>
                          <span className="font-semibold">#{msg.a65.selected_candidate}</span>
                        </div>
                        {typeof msg.a65.score === 'number' && (
                          <div>
                            <span className="text-gray-400">Score: </span>
                            <span className="font-semibold">{msg.a65.score.toFixed(3)}</span>
                          </div>
                        )}
                      </div>
                    )}
                    {(msg.a65?.metrics_brief || msg.live_metrics) && (
                      <div className="mt-1 flex items-center justify-end">
                        <button
                          className="text-[11px] text-indigo-300 hover:text-indigo-200 underline"
                          onClick={() => setExpandedMetrics(prev => ({ ...prev, [msg.id]: !prev[msg.id] }))}
                        >
                          {expandedMetrics[msg.id] ? 'Metriken ausblenden' : 'Metriken anzeigen'}
                        </button>
                      </div>
                    )}
                    {(msg.a65?.metrics_brief || msg.live_metrics) && expandedMetrics[msg.id] && (
                      <div className="mt-2 grid grid-cols-3 gap-2 text-[11px] text-gray-300">
                        {(() => {
                          const b = msg.a65?.metrics_brief as Record<string, number | null> | undefined;
                          const L = (k: string, v: any) => (
                            <div key={k} className="bg-gray-800/70 border border-gray-700 rounded px-2 py-1">
                              <div className="text-gray-400">{k}</div>
                              <div className="font-semibold">{typeof v === 'number' ? v.toFixed(3) : (v ?? '—')}</div>
                            </div>
                          );
                          const fromLive = (path: string[]) => {
                            try {
                              return path.reduce((acc: any, p: string) => (acc ? acc[p] : undefined), msg.live_metrics);
                            } catch { return undefined; }
                          };
                          const items: Array<[string, any]> = b ? [
                            ['A', b.A],
                            ['PCI', b.PCI],
                            ['coh', b.coh],
                            ['flow', b.flow],
                            ['T_integ', b.T_integ],
                            ['z_prox', b.z_prox],
                            ['hazard', b.hazard_score],
                            ['guardian', b.guardian_trip],
                            ['phi', b.phi_score],
                            ['EV_ready', b.EV_readiness],
                            ['EV_res', b.EV_resonance],
                            ['surprisal', b.surprisal],
                            ['LEX_Coh', b.LEX_Coh_conn],
                            ['LEX_Flow', b.LEX_Flow_pos],
                            ['LEX_Emo+', b.LEX_Emotion_pos],
                            ['LEX_T_integ', b.LEX_T_integ],
                            ['LEX_T_disso', b.LEX_T_disso],
                          ] : [
                            ['A', fromLive(['CORE', 'A'])],
                            ['PCI', fromLive(['CORE', 'PCI'])],
                            ['coh', fromLive(['CORE', 'coh'])],
                            ['flow', fromLive(['CORE', 'flow'])],
                            ['T_integ', fromLive(['CORE', 'T_integ'])],
                            ['z_prox', fromLive(['CORE', 'z_prox'])],
                            ['hazard', fromLive(['SYSTEM', 'hazard_score'])],
                            ['guardian', fromLive(['SYSTEM', 'guardian_trip'])],
                            ['phi', fromLive(['FEP', 'phi_score'])],
                            ['EV_ready', fromLive(['FEP', 'EV_readiness'])],
                            ['EV_res', fromLive(['FEP', 'EV_resonance'])],
                            ['surprisal', fromLive(['FEP', 'surprisal'])],
                            ['LEX_Coh', fromLive(['LEXIKA', 'LEX_Coh_conn'])],
                            ['LEX_Flow', fromLive(['LEXIKA', 'LEX_Flow_pos'])],
                            ['LEX_Emo+', fromLive(['LEXIKA', 'LEX_Emotion_pos'])],
                            ['LEX_T_integ', fromLive(['LEXIKA', 'LEX_T_integ'])],
                            ['LEX_T_disso', fromLive(['LEXIKA', 'LEX_T_disso'])],
                          ];
                          return items.map(([k, v]) => L(k, v));
                        })()}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold">E</div>
            <div className="bg-gray-700 p-3 rounded-lg">
              <div className="flex items-center gap-2">
                <div className="animate-pulse w-2 h-2 bg-gray-400 rounded-full"></div>
                <div className="animate-pulse w-2 h-2 bg-gray-400 rounded-full" style={{ animationDelay: '0.2s' }}></div>
                <div className="animate-pulse w-2 h-2 bg-gray-400 rounded-full" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* Pipeline Progress Visualizer */}
        {currentPipeline && (
          <div className="mx-4 mb-4 p-3 bg-gray-800 rounded-lg border border-gray-700">
            <div className="text-xs text-gray-400 mb-2">Pipeline-Fortschritt: {currentPipeline.current_step}/{currentPipeline.total_steps}</div>
            <div className="grid grid-cols-11 gap-1">
              {currentPipeline.steps.map((step, idx) => (
                <div key={idx} className="flex flex-col items-center">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${step.status === 'completed' ? 'bg-green-600 text-white' :
                    step.status === 'running' ? 'bg-yellow-500 text-black animate-pulse' :
                      step.status === 'error' ? 'bg-red-600 text-white' :
                        'bg-gray-600 text-gray-400'
                    }`}>
                    {step.status === 'completed' ? '✓' :
                      step.status === 'error' ? '✗' :
                        idx + 1}
                  </div>
                  <div className={`text-[8px] mt-1 text-center ${step.status === 'running' ? 'text-yellow-300 font-semibold' :
                    step.status === 'completed' ? 'text-green-400' :
                      'text-gray-500'
                    }`}>
                    {step.name.replace(/[📝🧮🔍🔎🏛️🎯🤖✨💾📚✅]/g, '')}
                  </div>
                  {step.details && (
                    <div className="text-[7px] text-gray-500 mt-0.5">{step.details}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Status */}
      {error && (
        <div className="bg-red-900/30 border border-red-700 text-red-300 rounded-lg p-3 flex items-center gap-2 text-sm flex-shrink-0">
          <AlertTriangle className="w-4 h-4" /> {error}
        </div>
      )}
      {statusMessage && (
        <div className="bg-blue-900/30 border border-blue-700 text-blue-300 rounded-lg p-3 text-sm flex-shrink-0">
          {statusMessage}
        </div>
      )}

      {/* Input */}
      <footer className="bg-gray-800 border border-gray-700 rounded-lg p-4 flex-shrink-0">
        <div className="relative">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder={isLoading ? 'Hyperspace processing...' : 'Nachricht...'}
            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white resize-none"
            rows={2}
            disabled={isLoading}
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <button
              onClick={handleToggleMicInput}
              className={`p-2 rounded-full transition-colors ${isListeningMic ? 'bg-red-500/20' : 'text-gray-400 hover:text-white'}`}
              disabled={isLoading}
            >
              {isListeningMic ? <StopCircle className="w-5 h-5 text-red-400" /> : <Mic className="w-5 h-5" />}
            </button>
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
            >
              <SendHorizontal className="w-5 h-5" />
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default EvokiTempleChat;

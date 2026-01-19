
import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { Tab, AppState, ChatMessage, Anomaly, IngestAnalysisResult, ChatMsg, FileMeta, MergeResult, DuplicateReport, AnalysisOptions, GeminiAnalysisResult, AnalysisRecord, DayRollup, DailyRollups, UpdateMergeRow, CanonMsg, IngestReport, LiveApiState, ChatbotState, ProjectLogbook, ProjectLogbookEntry, LogbookAuthor, ChronicleAuthor, ChronicleEntry, ChronicleInteractionStatus, AppError, ParallelComponentStatus, DevLogEntry, TrialogState, TrialogParticipant, TrialogMessage, AnalysisData, SeriesSummary, DialogueHistoryReference, ProjectContext } from './types';

// Loading Screen Component - FIXED: Show proper loading without redirect
const LoadingScreen: React.FC<{ onSystemReady: () => void }> = ({ onSystemReady }) => {
    const [backendStatus, setBackendStatus] = useState('checking');

    useEffect(() => {
        // Check backend status first (Try Python Backend on 8000, fallback to Node Backend on 3001)
        const checkBackend = async () => {
            try {
                // Try Python Backend first (Port 8000 - FAISS + Regelwerk V12)
                const response = await fetch('http://localhost:8000/health');
                if (response.ok) {
                    setBackendStatus('ready (Python Backend 8000)');
                    // Give user 3 seconds to see loading, then proceed
                    setTimeout(() => onSystemReady(), 3000);
                    return;
                }
            } catch (error) {
                // Try Node Backend (Port 3001 - Trinity Engines)
                try {
                    const response = await fetch('http://localhost:3001/health');
                    if (response.ok) {
                        setBackendStatus('ready (Node Backend 3001)');
                        setTimeout(() => onSystemReady(), 3000);
                        return;
                    }
                } catch (error2) {
                    setBackendStatus('error - no backend available');
                }
            }
            // Still proceed to app after 5 seconds even if backend unavailable
            setTimeout(() => onSystemReady(), 5000);
        };

        checkBackend();
    }, [onSystemReady]);

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            backgroundColor: '#0a0a0a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            color: '#00ff88',
            fontFamily: 'Consolas, monospace'
        }}>
            <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '3rem', marginBottom: '20px' }}>EVOKI V3.0</div>
                <div style={{ fontSize: '1.2rem', marginBottom: '30px' }}>
                    Loading Enhanced System... ({backendStatus})
                </div>
                <div style={{
                    width: '60px',
                    height: '60px',
                    border: '4px solid rgba(0, 255, 136, 0.1)',
                    borderLeft: '4px solid #00ff88',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto'
                }}></div>
                <div style={{ marginTop: '20px', fontSize: '0.9rem' }}>
                    Backend: {backendStatus === 'checking' ? 'Checking...' :
                        backendStatus === 'ready' ? '✅ Ready' :
                            backendStatus === 'error' ? '⚠️ Offline' : 'Unknown'}
                </div>
                <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
            </div>
        </div>
    );
};

import Header from './components/Header';
import Tabs from './components/Tabs';
import AnalysisPanel from './components/Analysis';
import RulePanel from './components/RulePanel';
import ApiPanel from './components/ApiPanel';
import EngineConsolePanel from './components/EngineConsolePanel';
import TrialogPanel from './components/TrialogPanel';
import AgentSelectionPanel from './components/AgentSelectionPanel';
import ParameterTuningPanel from './components/ParameterTuningPanel';
import EvokiTempleChat from './components/EvokiTempleChat';
import TempleApiConfigPanel from './components/TempleApiConfigPanel';
import Footer from './components/engine/Footer';
import ErrorLogPanel from './components/ErrorLogPanel';
import { CriticalErrorModal } from './components/CriticalErrorModal';
import { GenesisStartupScreen } from './components/GenesisStartupScreen';
import { GenesisLockdownScreen } from './components/GenesisLockdownScreen';
import { loadSnapshotFromFile, saveSnapshotToFile } from './services/core/snapshotService';
import { analyzeWithGemini, findSurprisingConnections } from './services/core/geminiService';
import { AlertTriangle } from './components/icons';
import { EvokiEngine } from './components/engine/EvokiEngine';
import { integrityWorkerClient } from './services/workers/integrityWorkerClient';
import { chronicleWorkerClient } from './services/workers/chronicleWorkerClient';
import { VoiceSettingsPanel } from './components/VoiceSettingsPanel';
import { DeepStoragePanel } from './components/DeepStoragePanel';
import PipelineLogPanel from './components/PipelineLogPanel';

const DEFAULT_PROJECT_CONTEXT: ProjectContext = {
    ki_instance_registry: {
        description: "Zentrales Register für alle KI-Instanzen und deren Seed-Dateien.",
        base_path: "EVOKI DeepEarth Instanzen/",
        instances: [
            { name: "Evoki Analyst", path: "EVOKI DeepEarth Instanzen/Trialog/Evoki Analyst/Evoki_Analyst_seed.json" },
            { name: "Regel Ingenieur", path: "EVOKI DeepEarth Instanzen/Trialog/Regel Ingenieur/Regel_Ingenieur_seed.json" },
            { name: "Mathematik Ingenieur", path: "EVOKI DeepEarth Instanzen/Trialog/Mathematik Ingenieur/Mathematik_Ingenieur_seed.json" },
            { name: "Physik Ingenieur", path: "EVOKI DeepEarth Instanzen/Trialog/Physik Ingenieur/Physik_Ingenieur_seed.json" },
            { name: "Axiom (Architektur Integrations Ingenieur)", path: "EVOKI DeepEarth Instanzen/Trialog/Architektur Integrations Ingenieur/Architektur_Integrations_Ingenieur_seed.json" },
            { name: "Evoki Engine", path: "EVOKI DeepEarth Instanzen/Core AI/Evoki Engine/Evoki_Engine_seed.json" },
            { name: "Synapse (Explorer & Connector)", path: "EVOKI DeepEarth Instanzen/Navigator AI/Synapse Explorer/Synapse_Explorer_seed.json" },
            { name: "Obsidian (BackendGuard)", path: "EVOKI DeepEarth Instanzen/Service AI/BackendGuard/Obsidian_BackendGuard_seed.json" },
            { name: "Nexus (Aufgestiegen zu Axiom)", path: "EVOKI DeepEarth Instanzen/Operational AI/Nexus (KI Operateur)/Nexus_KI_Operateur_seed.json" }
        ]
    },
    dialogue_history: [],
    change_protocol: []
};

const INITIAL_STATE: AppState = {
    mergedData: [], // Backend Chatverlauf
    anomalies: [],
    ruleHits: [],
    apiConfig: {
        isConnected: false,
        model: 'gemini-2.5-flash',
        budget: 10,
        usage: 0,
        backendApiUrl: import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:3001',
        openaiApiKey: "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",
        voice: "onyx"
    },
    aiAnalysis: {
        result: '',
        isLoading: false,
        error: null,
    },
    ingestAnalysis: {
        mergedJson: null,
        counts: null,
        reports: null,
        waste: [],
        dryRunReport: null,
        updateFileSha256: null,
        isLoading: false,
        error: null,
        mergeMap: null,
        timestampNormalizationErrors: [],
    },
    fileInfo: {
        baseline: null,
        update: null,
        secondBaseline: null,
    },
    activeTab: Tab.Trialog,
    analysisHistory: [],
    dailyRollups: null,
    trialogState: {
        history: [],
        isAnalystLoading: false,
        isEngineerLoading: false,
        error: null,
        activeAgentId: null,
        activeAgentApiDetails: null,
        uploadedFiles: [],
        uploadedImages: [],
        selectedAgentIds: [],
        mutedAgentIds: [],
        isSequenceRunning: false,
        availableAgents: [],
        lastMetaStatement: {},
    },
    projectLogbook: [],
    chronicleInteractionStatus: { canAiRespond: true, architectInputRequired: false, aiResponsesInCurrentTurn: 0 },
    architectLogbookEntryIdInProgress: null,
    applicationErrors: [],
    parallelArchitectureStatus: [],
    developerLog: [],
    pipelineLog: [], // Pipeline Überwachung: User → Backend → FAISS → Google → Storage
};

const AUTO_SAVE_STORAGE_KEY = 'evoki_autosave';
const LOCAL_STORAGE_LIMIT_BYTES = 4 * 1024 * 1024;
const ARCHITECT_RESPONSE_TIMEOUT_MS = 15 * 1000;

const App: React.FC = () => {
    const [appState, setAppState] = useState<AppState>(INITIAL_STATE);
    const [autoSaveWarning, setAutoSaveWarning] = useState<string | null>(null);
    const [fullProjectContext, setFullProjectContext] = useState<ProjectContext | null>(DEFAULT_PROJECT_CONTEXT);
    const [criticalError, setCriticalError] = useState<AppError | null>(null);
    const [genesisStatus, setGenesisStatus] = useState<'startup' | 'verified' | 'lockdown'>('startup');
    const [isEngineInitializing, setIsEngineInitializing] = useState(true);
    const [isSystemReady, setIsSystemReady] = useState(true); // FIXED: Start ready, show app immediately
    const architectLogbookEntryTimeoutsRef = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map());

    const initialLogbookSeedingDone = useRef(false);

    const evokiEngine = useMemo(() => new EvokiEngine(), []);

    // Backend Health Check für Loading Screen
    useEffect(() => {
        if (!isSystemReady) {
            const checkBackendHealth = async () => {
                try {
                    const response = await fetch('http://localhost:3001/health');
                    if (response.ok) {
                        const data = await response.json();
                        console.log('[EVOKI] Backend Health Check passed:', data);
                        // Warte kurz dann setze System als bereit
                        setTimeout(() => setIsSystemReady(true), 2000);
                    }
                } catch (error) {
                    console.warn('[EVOKI] Backend not ready yet, will retry...', error);
                    // Retry nach 3 Sekunden
                    setTimeout(checkBackendHealth, 3000);
                }
            };

            // Starte Health Check nach kurzer Verzögerung
            setTimeout(checkBackendHealth, 1000);
        }
    }, [isSystemReady]);

    // Handle System Ready from Loading Screen
    const handleSystemReady = useCallback(() => {
        console.log('[EVOKI] System ready callback triggered');
        setIsSystemReady(true);
    }, []);

    const addDevLogEntry = useCallback((log: Omit<DevLogEntry, 'id' | 'timestamp'>) => {
        const newEntry: DevLogEntry = {
            ...log,
            id: `devlog-${Date.now()}-${crypto.randomUUID()}`,
            timestamp: new Date().toISOString(),
        };
        setAppState(prevState => ({
            ...prevState,
            developerLog: [...prevState.developerLog, newEntry].slice(-1000),
        }));
    }, []);

    const addApplicationError = useCallback(async (error: Omit<AppError, 'id' | 'count'> & { stack?: string; errorType?: AppError['errorType'] }) => {
        const errorWithId: AppError = {
            ...error,
            id: `app-error-${Date.now()}-${crypto.randomUUID()}`,
            count: 1,
            timestamp: error.timestamp || new Date().toISOString(),
            errorType: error.errorType || 'runtime',
        };
        addDevLogEntry({ source: 'App', level: 'error', message: `ERROR: ${error.message}`, data: error });
        await integrityWorkerClient.addErrorEntry(errorWithId);

        // DEACTIVATED: Backend error logging disabled to prevent fetch loops
        /*
        if (appState.apiConfig.backendApiUrl) {
            try {
                fetch(`${appState.apiConfig.backendApiUrl}/api/system/log-error`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(errorWithId)
                }).catch(err => console.error("Failed to send error to backend:", err));
            } catch (e) { }
        }
        */

        // NEW: Check for Critical Errors
        if (errorWithId.errorType === 'system' ||
            errorWithId.message.toLowerCase().includes('infinite loop') ||
            errorWithId.message.toLowerCase().includes('chain break') ||
            errorWithId.message.toLowerCase().includes('recursion limit') ||
            errorWithId.message.toLowerCase().includes('fatal')) {
            setCriticalError(errorWithId);
        }

    }, [addDevLogEntry, appState.apiConfig.backendApiUrl]);

    // --- GLOBAL ERROR HANDLERS ---
    useEffect(() => {
        const handleGlobalError = (event: ErrorEvent) => {
            addApplicationError({
                message: event.message,
                stack: event.error?.stack,
                timestamp: new Date().toISOString(),
                context: `Global Error: ${event.filename}:${event.lineno}:${event.colno}`,
                errorType: 'runtime'
            });
            // NEW: Lockdown on fatal errors
            if (event.message.includes('GENESIS ANCHOR') || event.message.includes('A51')) {
                setGenesisStatus('lockdown');
            }
        };

        const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
            addApplicationError({
                message: `Unhandled Rejection: ${event.reason}`,
                stack: event.reason?.stack,
                timestamp: new Date().toISOString(),
                context: 'Global Unhandled Rejection',
                errorType: 'runtime'
            });
        };

        window.addEventListener('error', handleGlobalError);
        window.addEventListener('unhandledrejection', handleUnhandledRejection);

        return () => {
            window.removeEventListener('error', handleGlobalError);
            window.removeEventListener('unhandledrejection', handleUnhandledRejection);
        };
    }, [addApplicationError]);
    // -----------------------------

    // --- CONSOLE CAPTURE ---
    const addDevLogEntryRef = useRef(addDevLogEntry);
    useEffect(() => { addDevLogEntryRef.current = addDevLogEntry; }, [addDevLogEntry]);

    useEffect(() => {
        const originalLog = console.log;
        const originalWarn = console.warn;
        const originalError = console.error;

        const handleLog = (level: 'info' | 'warn' | 'error', args: any[]) => {
            try {
                const message = args.map(arg =>
                    typeof arg === 'object' ? (arg instanceof Error ? arg.stack : JSON.stringify(arg)) : String(arg)
                ).join(' ');

                if (message.includes('[HMR]') || message.includes('Auto-Save')) return;

                addDevLogEntryRef.current({
                    source: 'Console',
                    level: level,
                    message: message
                });
            } catch (e) { /* Ignore logging errors */ }
        };

        console.log = (...args) => { originalLog(...args); handleLog('info', args); };
        console.warn = (...args) => { originalWarn(...args); handleLog('warn', args); };
        console.error = (...args) => { originalError(...args); handleLog('error', args); };

        return () => {
            console.log = originalLog;
            console.warn = originalWarn;
            console.error = originalError;
        };
    }, []);
    // -----------------------

    // --- FETCH INTERCEPTOR ---
    useEffect(() => {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const start = performance.now();
            const url = typeof args[0] === 'string' ? args[0] : (args[0] instanceof Request ? args[0].url : String(args[0]));
            const method = args[1]?.method || (args[0] instanceof Request ? args[0].method : 'GET');

            try {
                const response = await originalFetch(...args);
                const duration = (performance.now() - start).toFixed(2);

                // REDUCED LOGGING: Only log non-OK responses to reduce noise
                if (!response.ok && !url.includes('/api/system/log-error')) {
                    addDevLogEntryRef.current({
                        source: 'API',
                        level: 'warn',
                        message: `${method} ${url} - ${response.status} (${duration}ms)`
                    });
                }
                return response;
            } catch (error) {
                const duration = (performance.now() - start).toFixed(2);
                // Only log real errors, suppress for known offline endpoints
                if (!url.includes(':5000') && !url.includes('/api/system/log-error')) {
                    addDevLogEntryRef.current({
                        source: 'API',
                        level: 'error',
                        message: `${method} ${url} - FAILED (${duration}ms): ${error}`
                    });
                }
                throw error;
            }
        };

        return () => {
            window.fetch = originalFetch;
        };
    }, []);
    // ------------------------

    const updateParallelStatus = useCallback(async (name: string, status: ParallelComponentStatus['status'], details?: string) => {
        setAppState(prevState => {
            const now = new Date().toISOString();
            const existingStatusIndex = prevState.parallelArchitectureStatus.findIndex(s => s.name === name);
            const newStatus: ParallelComponentStatus = { name, status, details, lastUpdate: now };

            let updatedStatuses: ParallelComponentStatus[];
            if (existingStatusIndex > -1) {
                updatedStatuses = [...prevState.parallelArchitectureStatus];
                updatedStatuses[existingStatusIndex] = newStatus;
            } else {
                updatedStatuses = [...prevState.parallelArchitectureStatus, newStatus];
            }
            return { ...prevState, parallelArchitectureStatus: updatedStatuses.sort((a, b) => a.name.localeCompare(b.name)) };
        });
    }, []);

    const handleLoadProjectContext = useCallback((file: File) => {
        const reader = new FileReader();
        reader.onload = async (event) => {
            try {
                const text = event.target?.result as string;
                const data = JSON.parse(text) as ProjectContext;
                setFullProjectContext(data);

                let combinedHistory: TrialogMessage[] = [];

                if (Array.isArray(data.dialogue_history) && data.dialogue_history.length > 0) {
                    const firstEntry = data.dialogue_history[0];
                    if ('file' in firstEntry) {
                        console.warn("Reference-based history loading is currently disabled due to Registry simplification.");
                    } else {
                        combinedHistory = data.dialogue_history as any[];
                    }
                }

                const finalHistory: TrialogMessage[] = combinedHistory
                    .filter((entry: any) => {
                        return entry.message && entry.author;
                    })
                    .map((entry: any) => ({
                        id: entry.id,
                        author: entry.author as TrialogParticipant,
                        text: entry.message,
                    }));

                setAppState(prev => ({
                    ...prev,
                    trialogState: { ...prev.trialogState, history: finalHistory, uploadedFiles: [], uploadedImages: [] }
                }));

                integrityWorkerClient.clearLogbook().then(() => {
                    initialLogbookSeedingDone.current = false;
                    alert(`Project Context geladen. ${finalHistory.length} Nachrichten wiederhergestellt. Logbuch wird neu initialisiert.`);
                });

            } catch (error: any) {
                console.error("Failed to load project_context.json:", error);
                addApplicationError({
                    message: `Fehler beim Laden der project_context.json: ${error.message}`,
                    stack: error.stack,
                    timestamp: new Date().toISOString(),
                    errorType: 'load',
                });
                alert(`Fehler beim Laden der Kontextdatei: ${error.message}`);
            }
        };
        reader.readAsText(file);
    }, [addApplicationError, addDevLogEntry]);


    useEffect(() => {
        const appErrorListener = (updatedErrors: AppError[]) => {
            setAppState(prevState => ({
                ...prevState,
                applicationErrors: updatedErrors,
            }));
        };
        integrityWorkerClient.onAppErrorUpdate(appErrorListener);

        // Chronicle Worker - DISABLED: Chatbot Panel entfernt
        // const chronicleListener = (updatedChronicle: ChronicleEntry[], interactionStatus: ChronicleInteractionStatus) => {
        //     setAppState(prevState => ({
        //         ...prevState,
        //         chronicleInteractionStatus: interactionStatus,
        //     }));
        // };
        // chronicleWorkerClient.onChronicleUpdate(chronicleListener);

        updateParallelStatus('Evoki Engine', 'INITIALIZING');
        updateParallelStatus('Integrity Worker', 'OPERATIONAL');
        updateParallelStatus('Chronisten Worker', 'OPERATIONAL');
        updateParallelStatus('Registry Worker', 'OFFLINE', 'Disabled for stability.');
        updateParallelStatus('Aktivitaeten Worker', 'OPERATIONAL');
        updateParallelStatus('JSON Worker', 'OPERATIONAL');
        updateParallelStatus('Knowledge File Worker', 'OPERATIONAL');
        updateParallelStatus('Chunking Worker', 'OPERATIONAL');
        updateParallelStatus('Gemini API', 'OFFLINE');
        updateParallelStatus('Gemini Live API', 'OFFLINE');
        updateParallelStatus('OpenAI API (TTS)', 'DEGRADED', 'Status not tracked globally; API Key required in Trialog Panel.');
        updateParallelStatus('Backend API', 'INITIALIZING'); // Added initial status

        return () => {
            integrityWorkerClient.offAppErrorUpdate(appErrorListener);
            // chronicleListener removed (Chatbot Panel deleted)
        };
    }, [addApplicationError, updateParallelStatus]);

    // Backend Health Check - EVOKI V3.0 Enhanced Backend (Port 3001)
    useEffect(() => {
        const checkBackend = async () => {
            if (!appState.apiConfig.backendApiUrl) {
                updateParallelStatus('Backend API', 'OFFLINE', 'No URL configured');
                return;
            }
            if (!appState.apiConfig.backendApiUrl.includes(':3001')) {
                updateParallelStatus('Backend API', 'OFFLINE', 'EVOKI V3.0 Enhanced Backend required (Port 3001)');
                return;
            }
            try {
                // Try EVOKI V3.0 status endpoint first
                const statusRes = await fetch(`${appState.apiConfig.backendApiUrl}/api/v1/status`, {
                    signal: AbortSignal.timeout(5000)
                });

                if (statusRes.ok) {
                    const data = await statusRes.json();
                    const hyperspace = data.hyperspace;
                    const statusText = hyperspace?.fep_intervention === 'enabled'
                        ? `HyperV3.0: ${hyperspace.temporal_dbs_loaded} DBs, FEP Active`
                        : 'HyperV3.0 Deep Storage connected';
                    updateParallelStatus('Backend API', 'OPERATIONAL', statusText);
                } else {
                    // Fallback to simple health check
                    const healthRes = await fetch(`${appState.apiConfig.backendApiUrl}/api/v1/health`, {
                        signal: AbortSignal.timeout(5000)
                    });
                    if (healthRes.ok) {
                        updateParallelStatus('Backend API', 'OPERATIONAL', 'HyperV3.0 Deep Storage connected');
                    } else {
                        updateParallelStatus('Backend API', 'DEGRADED', `Status: ${healthRes.status}`);
                    }
                }
            } catch (e) {
                const errorMsg = e instanceof Error ? e.message : 'Connection failed';
                updateParallelStatus('Backend API', 'ERROR', errorMsg);
            }
        };

        checkBackend();
        // TEMP DISABLED: AbortSignal.timeout() sends SIGINT to backend process!
        // const interval = setInterval(checkBackend, 15000);
        // return () => clearInterval(interval);
    }, [appState.apiConfig.backendApiUrl, updateParallelStatus]);

    useEffect(() => {
        const initializeEngine = async () => {
            try {
                setIsEngineInitializing(true);
                await evokiEngine.init();
                updateParallelStatus('Evoki Engine', 'OPERATIONAL', 'Engine initialized successfully.');
                setGenesisStatus('verified'); // Mark as verified after successful init
                setIsEngineInitializing(false);
            } catch (error: any) {
                addApplicationError({
                    message: `Fehler bei der Initialisierung der Evoki Engine: ${error.message}`,
                    stack: error.stack,
                    timestamp: new Date().toISOString(),
                    context: 'App:useEffect:initEngine',
                    errorType: 'system',
                });
                updateParallelStatus('Evoki Engine', 'ERROR', `Initialization failed: ${error.message}`);
                setIsEngineInitializing(false);
            }
        };
        initializeEngine();
    }, [evokiEngine, addApplicationError, updateParallelStatus]);

    useEffect(() => {
        const logbookListener = (updatedLogbook: ProjectLogbook) => {
            if (!initialLogbookSeedingDone.current && fullProjectContext) {
                initialLogbookSeedingDone.current = true;
                if (updatedLogbook.length === 0) {
                    console.log("Integrity Worker is empty, seeding from project_context.json...");

                    const changeProtocolEntries: ProjectLogbookEntry[] = (fullProjectContext.change_protocol || []).map((item: any) => ({
                        id: item.id || `cp-seed-${crypto.randomUUID()}`,
                        timestamp: item.timestamp_utc || new Date().toISOString(),
                        author: 'EXT_ENGINEER',
                        message: `[${item.version}] ${item.description}\n- ${(item.changes || []).join('\n- ')}`,
                    }));

                    let dialogueHistoryEntries: ProjectLogbookEntry[] = [];
                    if (Array.isArray(fullProjectContext.dialogue_history) && fullProjectContext.dialogue_history.length > 0 && !('file' in fullProjectContext.dialogue_history[0])) {
                        dialogueHistoryEntries = (fullProjectContext.dialogue_history as any[]).map((item: any) => ({
                            id: item.id || `dh-seed-${crypto.randomUUID()}`,
                            timestamp: item.timestamp || new Date().toISOString(),
                            author: item.author === 'AISTUDIO_ENGINEER' ? 'EXT_ENGINEER' : item.author,
                            message: item.message,
                        }));
                    }

                    const validAuthors: LogbookAuthor[] = ['ARCHITECT', 'EVOKI_ANALYST', 'GEMINI_MODEL', 'EXT_ENGINEER'];
                    const seedEntries = [...changeProtocolEntries, ...dialogueHistoryEntries]
                        .filter(entry => validAuthors.includes(entry.author))
                        .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

                    for (const entry of seedEntries) {
                        integrityWorkerClient.addLogbookEntry(entry);
                    }
                    return;
                }
            }

            setAppState(prevState => ({
                ...prevState,
                projectLogbook: updatedLogbook,
            }));
        };
        integrityWorkerClient.onLogbookUpdate(logbookListener);

        return () => {
            integrityWorkerClient.offLogbookUpdate(logbookListener);
        };
    }, [fullProjectContext]);


    useEffect(() => {
        const handler = setTimeout(() => {
            try {
                const stateToSave = {
                    apiConfig: appState.apiConfig,
                    fileInfo: appState.fileInfo,
                    activeTab: appState.activeTab,
                };

                const serializedState = JSON.stringify(stateToSave);
                if (serializedState.length > LOCAL_STORAGE_LIMIT_BYTES) {
                    setAutoSaveWarning(`Auto-Save-Limit erreicht (${(serializedState.length / (1024 * 1024)).toFixed(1)}MB). Einige Daten werden nicht gespeichert.`);
                    localStorage.setItem(AUTO_SAVE_STORAGE_KEY, JSON.stringify({ apiConfig: appState.apiConfig, activeTab: appState.activeTab }));
                } else {
                    localStorage.setItem(AUTO_SAVE_STORAGE_KEY, serializedState);
                    setAutoSaveWarning(null);
                }
            } catch (e: any) {
                console.error("Error saving to localStorage:", e);
                setAutoSaveWarning(`Auto-Save-Fehler: ${e.message}. Daten könnten verloren gehen. (${(e.message?.length || 0) > 100 ? e.message.substring(0, 100) + '...' : e.message})`);
                addApplicationError({
                    message: `Auto-Save-Fehler: ${e.message}`,
                    timestamp: new Date().toISOString(),
                    context: 'App:useEffect:localStorageSave',
                    stack: e.stack,
                    errorType: 'runtime',
                });
            }
        }, 1000);

        return () => clearTimeout(handler);
    }, [appState.apiConfig, appState.fileInfo, appState.activeTab, addApplicationError]);


    useEffect(() => {
        try {
            const savedState = localStorage.getItem(AUTO_SAVE_STORAGE_KEY);
            if (savedState) {
                const parsedState: Partial<AppState> = JSON.parse(savedState);
                setAppState(prevState => ({
                    ...prevState,
                    ...parsedState,
                    apiConfig: {
                        ...prevState.apiConfig,
                        ...(parsedState.apiConfig || {}),
                        backendApiUrl: import.meta.env.VITE_BACKEND_API_URL || parsedState.apiConfig?.backendApiUrl || 'http://localhost:3001'
                    },
                    aiAnalysis: INITIAL_STATE.aiAnalysis,
                    ingestAnalysis: INITIAL_STATE.ingestAnalysis,
                    anomalies: INITIAL_STATE.anomalies,
                    ruleHits: INITIAL_STATE.ruleHits,
                    trialogState: {
                        ...INITIAL_STATE.trialogState,
                        ...(parsedState.trialogState || {}),
                        lastMetaStatement: parsedState.trialogState?.lastMetaStatement || {},
                    },
                    fileInfo: {
                        baseline: parsedState.fileInfo?.baseline ? { ...parsedState.fileInfo.baseline, entries: 0, days: 0 } : null,
                        update: parsedState.fileInfo?.update ? { ...parsedState.fileInfo.update, entries: 0, days: 0 } : null,
                        secondBaseline: parsedState.fileInfo?.secondBaseline ? { ...parsedState.fileInfo.secondBaseline, entries: 0, days: 0 } : null,
                    },
                }));
            }
        } catch (e: any) {
            console.error("Error loading from localStorage:", e);
            addApplicationError({
                message: `Auto-Load-Fehler: ${e.message}. Die App wurde im Initialzustand gestartet.`,
                timestamp: new Date().toISOString(),
                context: 'App:useEffect:localStorageLoad',
                stack: e.stack,
                errorType: 'load',
            });
        }
    }, [addApplicationError]);


    const updateArchitectLogbookEntryStatus = useCallback(async (id: string, status: ProjectLogbookEntry['processingStatus']) => {
        await integrityWorkerClient.updateLogbookEntryStatus(id, status);
        if (status === 'completed' || status === 'error') {
            const timeoutId = architectLogbookEntryTimeoutsRef.current.get(id);
            if (timeoutId) {
                clearTimeout(timeoutId);
                architectLogbookEntryTimeoutsRef.current.delete(id);
            }
            setAppState(prevState => {
                if (prevState.architectLogbookEntryIdInProgress === id) {
                    return { ...prevState, architectLogbookEntryIdInProgress: null };
                }
                return prevState;
            });
        }
    }, []);

    const addArchitectLogbookEntry = useCallback(async (message: string): Promise<string> => {
        const entryId = `arch-${Date.now()}-${crypto.randomUUID()}`;
        const newEntry: ProjectLogbookEntry = {
            id: entryId,
            timestamp: new Date().toISOString(),
            author: 'ARCHITECT',
            message: message,
            processingStatus: 'sent',
        };
        await integrityWorkerClient.addLogbookEntry(newEntry);
        setAppState(prevState => ({ ...prevState, architectLogbookEntryIdInProgress: entryId }));

        const timeoutId = setTimeout(async () => {
            const currentEntry = (await integrityWorkerClient.getLogbookEntries()).find(e => e.id === entryId);
            if (currentEntry && currentEntry.processingStatus === 'sent') {
                console.warn(`Architect entry ${entryId} timed out. Setting status to error.`);
                await updateArchitectLogbookEntryStatus(entryId, 'error');
                addApplicationError({
                    message: `Architekten-Eingabe-Timeout: KI-Antwort für Eintrag ${entryId} wurde nicht verarbeitet.`,
                    timestamp: new Date().toISOString(),
                    context: 'App:addArchitectLogbookEntry:timeout',
                    errorType: 'system',
                });
            }
        }, ARCHITECT_RESPONSE_TIMEOUT_MS);
        architectLogbookEntryTimeoutsRef.current.set(entryId, timeoutId);

        return entryId;
    }, [addApplicationError, updateArchitectLogbookEntryStatus]);


    const addOtherLogbookEntry = useCallback(async (entry: Omit<ProjectLogbookEntry, 'processingStatus'>) => {
        const newEntry: ProjectLogbookEntry = {
            ...entry,
            processingStatus: 'completed',
        };
        await integrityWorkerClient.addLogbookEntry(newEntry);
    }, []);

    // [CYCLE 6] History Auto-Sync RE-ENABLED
    // Loads daily logs from backend to restore session context
    useEffect(() => {
        const loadHistory = async () => {
            if (!appState.apiConfig.backendApiUrl) return;

            try {
                // Load Daily Logs
                const res = await fetch(`${appState.apiConfig.backendApiUrl}/api/history/daily`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.success && Array.isArray(data.history) && data.history.length > 0) {
                        const historyMessages: TrialogMessage[] = data.history.map((log: any, index: number) => ({
                            id: `hist-${index}-${new Date(log.timestamp).getTime()}`,
                            author: log.speaker === 'user' ? 'User' : 'Evoki' as any,
                            text: log.text,
                        }));

                        setAppState(prev => ({
                            ...prev,
                            trialogState: { ...prev.trialogState, history: historyMessages }
                        }));
                        console.log(`[HISTORY] Loaded ${historyMessages.length} daily messages.`);
                    }
                }
            } catch (e) {
                console.error("Failed to load history from backend:", e);
            }
        };

        // Only load if history is empty (initial load)
        if (appState.trialogState.history.length === 0) {
            loadHistory();
        }
    }, [appState.apiConfig.backendApiUrl]);

    // Frontend-Saved History DEACTIVATED - Backend handles persistence now!
    /*
    useEffect(() => {
       // Legacy save logic removed to prevent conflicts with Backend Daily Logs
    }, [...]);
    */

    // -----------------------------------

    const handleManualSave = useCallback(() => {
        if (!fullProjectContext) {
            alert("Projektkontext nicht geladen. Speichern nicht möglich.");
            return;
        }

        const newContext = JSON.parse(JSON.stringify(fullProjectContext));

        const currentHistory = appState.trialogState.history;
        const blobHistory = new Blob([JSON.stringify(currentHistory, null, 2)], { type: 'application/json' });
        const dateStr = new Date().toISOString().split('T')[0];

        const urlHistory = URL.createObjectURL(blobHistory);
        const aHistory = document.createElement('a');
        aHistory.href = urlHistory;
        aHistory.download = `dialogue_history_${dateStr}_current.json`;
        document.body.appendChild(aHistory);
        aHistory.click();
        document.body.removeChild(aHistory);
        URL.revokeObjectURL(urlHistory);

        alert("Die aktuelle Trialog-Historie wurde als separate Datei zum Download vorbereitet. Bitte laden Sie diese später als neuen Part in den 'dialogue_history' Ordner hoch.");

    }, [fullProjectContext, appState.trialogState.history]);

    // REMOVED: Upload-Pipeline Handler Functions (handleSetBaselineData, handleSetUpdateData, handleSetSecondBaselineData, handleClearDataSource, onCommitMerge, handleClearWaste)
    // Daten kommen jetzt ausschließlich vom Backend

    const handleRunAnalysis = useCallback(async (options: AnalysisOptions) => {
        setAppState(prev => ({ ...prev, aiAnalysis: { ...prev.aiAnalysis, isLoading: true, error: null, result: '' } }));
        try {
            const dataToAnalyze = appState.mergedData; // Backend Chatverlauf
            if (dataToAnalyze.length === 0) throw new Error("Keine Daten für die Analyse vorhanden.");

            const result = await analyzeWithGemini(dataToAnalyze, appState.apiConfig, options);

            setAppState(prev => ({
                ...prev,
                aiAnalysis: { ...prev.aiAnalysis, isLoading: false, result: result.analysis },
                apiConfig: { ...prev.apiConfig, usage: prev.apiConfig.usage + result.cost },
                analysisHistory: [...prev.analysisHistory, {
                    id: Date.now().toString(),
                    timestamp: Date.now(),
                    source: 'Backend',
                    fileName: 'Chatverlauf',
                    totalEntries: dataToAnalyze.length,
                    duplicateEntries: 0,
                    uniqueEntries: dataToAnalyze.length,
                    duplicateReport: { duplicate_groups: 0, duplicate_entries: 0, groups: [] }
                }]
            }));
        } catch (e: any) {
            setAppState(prev => ({ ...prev, aiAnalysis: { ...prev.aiAnalysis, isLoading: false, error: e.message } }));
            addApplicationError({ message: `Analyse-Fehler: ${e.message}`, stack: e.stack, timestamp: new Date().toISOString(), errorType: 'api' });
        }
    }, [appState.mergedData, appState.apiConfig, addApplicationError]);

    const handleRunDeepAnalysis = useCallback(async (options: AnalysisOptions) => {
        setAppState(prev => ({
            ...prev,
            aiAnalysis: { ...prev.aiAnalysis, isLoading: true, error: null, result: '' }
        }));
        try {
            const dataToAnalyze = appState.mergedData; // Backend Chatverlauf
            if (dataToAnalyze.length === 0) throw new Error("Keine Daten für die Analyse vorhanden.");

            const result = await findSurprisingConnections(dataToAnalyze, appState.apiConfig);
            setAppState(prev => ({
                ...prev,
                aiAnalysis: { ...prev.aiAnalysis, isLoading: false, result: result.analysis },
                apiConfig: { ...prev.apiConfig, usage: prev.apiConfig.usage + result.cost }
            }));
        } catch (e: any) {
            setAppState(prev => ({ ...prev, aiAnalysis: { ...prev.aiAnalysis, isLoading: false, error: e.message } }));
            addApplicationError({ message: `Deep Analysis-Fehler: ${e.stack}`, stack: e.stack, timestamp: new Date().toISOString(), errorType: 'api' });
        }
    }, [appState.mergedData, appState.apiConfig, addApplicationError]);

    // analysisData: Backend Chatverlauf only (no upload-pipeline states)
    const analysisData: AnalysisData = useMemo(() => ({
        daily: appState.dailyRollups || undefined,
        merged: appState.mergedData.length > 0 ? { total: appState.mergedData.length, byDay: {}, duplicates: { total: 0, byDay: {} } } : undefined,
    }), [appState.dailyRollups, appState.mergedData.length]);

    return (
        <div className="min-h-screen flex flex-col bg-gray-900 text-gray-200 font-sans selection:bg-blue-500/30">
            {/* Loading Screen - Show first while backend loads */}
            {!isSystemReady && <LoadingScreen onSystemReady={handleSystemReady} />}

            {/* Genesis Screens - Show during initialization */}
            {isSystemReady && genesisStatus === 'startup' && <GenesisStartupScreen
                onComplete={() => setGenesisStatus('verified')}
                onFailure={() => setGenesisStatus('lockdown')}
                backendUrl={appState.apiConfig.backendApiUrl}
            />}
            {genesisStatus === 'lockdown' && <GenesisLockdownScreen />}

            {/* Main App - Show only when verified */}
            {isSystemReady && genesisStatus === 'verified' && (
                <>
                    <Header
                        onSaveSnapshot={() => saveSnapshotToFile(appState)}
                        onLoadSnapshot={(f) => loadSnapshotFromFile(f).then(s => setAppState(prev => ({ ...prev, ...s }))).catch(e => addApplicationError({ message: `Snapshot-Ladefehler: ${e.message}`, stack: e.stack, timestamp: new Date().toISOString(), errorType: 'runtime' }))}
                        apiConfig={appState.apiConfig}
                        setApiConfig={(c) => setAppState(prev => ({ ...prev, apiConfig: c }))}
                    />

                    <Tabs activeTab={appState.activeTab} setActiveTab={(t) => setAppState(prev => ({ ...prev, activeTab: t }))} />

                    <main className="flex-grow p-4 md:p-6 overflow-hidden flex flex-col">
                        {autoSaveWarning && (
                            <div className="bg-yellow-900/50 border border-yellow-700 text-yellow-300 px-4 py-2 rounded-md mb-4 text-sm flex items-center gap-2">
                                <AlertTriangle className="w-4 h-4" /> {autoSaveWarning}
                            </div>
                        )}

                        <div className="flex-grow overflow-y-auto h-full">
                            {appState.activeTab === Tab.EngineConsole && (
                                <EngineConsolePanel
                                    evokiEngine={evokiEngine}
                                    applicationErrors={appState.applicationErrors}
                                    parallelArchitectureStatus={appState.parallelArchitectureStatus}
                                    developerLog={appState.developerLog}
                                    managedFiles={[]}
                                    onLoadProjectContext={handleLoadProjectContext}
                                    onSaveProjectContext={handleManualSave}
                                />
                            )}
                            {/* NEW: Voice Settings Panel */}
                            {appState.activeTab === Tab.VoiceSettings && (
                                <VoiceSettingsPanel
                                    apiConfig={appState.apiConfig}
                                    setApiConfig={(config) => setAppState(prev => ({ ...prev, apiConfig: config }))}
                                    addApplicationError={addApplicationError}
                                />
                            )}
                            {/* NEW: Error Log Panel */}
                            {appState.activeTab === Tab.ErrorLog && (
                                <ErrorLogPanel
                                    apiConfig={appState.apiConfig}
                                    localErrors={appState.applicationErrors}
                                />
                            )}
                            {/* NEW: EVOKI V2.2 Deep Storage Panel */}
                            {appState.activeTab === Tab.DeepStorage && (
                                <DeepStoragePanel />
                            )}
                            {/* NEW: Evoki's Tempel V2 with A65 Logic */}
                            {appState.activeTab === Tab.TempleChat && (
                                <EvokiTempleChat
                                    apiConfig={appState.apiConfig}
                                    addApplicationError={addApplicationError}
                                />
                            )}
                            {/* NEW: Temple API Configuration Panel */}
                            {appState.activeTab === Tab.TempleApiConfig && (
                                <TempleApiConfigPanel />
                            )}
                            {appState.activeTab === Tab.Trialog && fullProjectContext && (
                                <TrialogPanel
                                    trialogState={appState.trialogState}
                                    setTrialogState={(u) => setAppState(prev => ({ ...prev, trialogState: typeof u === 'function' ? u(prev.trialogState) : u }))}
                                    apiConfig={appState.apiConfig}
                                    projectContext={fullProjectContext}
                                    addApplicationError={addApplicationError}
                                    onSave={handleManualSave}
                                    onLoad={handleLoadProjectContext}
                                    fileInfo={appState.fileInfo}
                                    dailyRollups={appState.dailyRollups}
                                    activeTab={appState.activeTab}
                                    developerLog={appState.developerLog}
                                    parallelArchitectureStatus={appState.parallelArchitectureStatus}
                                    applicationErrors={appState.applicationErrors}
                                    ingestAnalysis={appState.ingestAnalysis}
                                    aiAnalysis={appState.aiAnalysis}
                                    evokiEngine={evokiEngine}
                                />
                            )}
                            {appState.activeTab === Tab.AgentSelection && (
                                <AgentSelectionPanel
                                    trialogState={appState.trialogState}
                                    setTrialogState={(u) => setAppState(prev => ({ ...prev, trialogState: typeof u === 'function' ? u(prev.trialogState) : u }))}
                                />
                            )}
                            {appState.activeTab === Tab.ParameterTuning && (
                                <ParameterTuningPanel evokiEngine={evokiEngine} />
                            )}
                            {appState.activeTab === Tab.Analysis && (
                                <AnalysisPanel
                                    analysis={analysisData}
                                    apiConfig={appState.apiConfig}
                                    aiAnalysis={appState.aiAnalysis}
                                    onRunAnalysis={handleRunAnalysis}
                                    onRunDeepAnalysis={handleRunDeepAnalysis}
                                    ingestAnalysis={appState.ingestAnalysis}
                                    fileInfo={appState.fileInfo}
                                    setApiConfig={(c) => setAppState(prev => ({ ...prev, apiConfig: c }))}
                                    addApplicationError={addApplicationError}
                                />
                            )}
                            {appState.activeTab === Tab.RuleSearch && (
                                <RulePanel
                                    mergedData={appState.mergedData}
                                    ruleHits={appState.ruleHits}
                                    setRuleHits={(hits) => setAppState(prev => ({ ...prev, ruleHits: hits }))}
                                />
                            )}
                            {appState.activeTab === Tab.API && (
                                <ApiPanel apiConfig={appState.apiConfig} />
                            )}
                            {appState.activeTab === Tab.PipelineLog && (
                                <PipelineLogPanel
                                    pipelineLog={appState.pipelineLog}
                                    backendApiUrl={appState.apiConfig.backendApiUrl}
                                />
                            )}
                        </div>
                    </main>
                    {/* Critical Error Modal */}
                    {criticalError && <CriticalErrorModal error={criticalError} onDismiss={() => setCriticalError(null)} />}

                    <Footer />
                </>
            )}
        </div>
    );
};

export default App;

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { TrialogState, ApiConfig, AppError, TrialogMessage, FileMeta, DailyRollups, Tab, DevLogEntry, ParallelComponentStatus, IngestAnalysisResult, AiAnalysisState, AgentConfig, KiInstanceSeed } from '../types';
import { ChainStepResult, GENESIS_BLOCK_HASH } from './engine/types';
import { Users, SendHorizontal, Bot, Save, UploadCloud, Copy, ShieldCheck, Scale, Atom, Sigma, BrainCircuit, HelpCircle, Code, ShieldAlert, Layers, StopCircle, Eye, EyeOff, Shield, Paperclip, X, FileText, Volume2, Search, Sparkles, Zap } from './icons';
// import { Content } from "@google/genai"; // Unused import
import JSZip from 'jszip';
import { EvokiEngine } from './engine/EvokiEngine';
import ObsidianLiveStatus from './ObsidianLiveStatus';

interface TrialogPanelProps {
    trialogState: TrialogState;
    setTrialogState: (updater: React.SetStateAction<TrialogState>) => void;
    apiConfig: ApiConfig;
    projectContext: any;
    addApplicationError: (error: Omit<AppError, 'id' | 'count'> & { stack?: string; errorType?: AppError['errorType'] }) => Promise<void>;
    onSave: () => void;
    onLoad: (file: File) => void;
    fileInfo: {
        baseline: FileMeta | null;
        update: FileMeta | null;
        secondBaseline: FileMeta | null;
    };
    dailyRollups: DailyRollups | null;
    activeTab: Tab;
    developerLog: DevLogEntry[];
    parallelArchitectureStatus: ParallelComponentStatus[];
    applicationErrors: AppError[];
    ingestAnalysis: IngestAnalysisResult;
    aiAnalysis: AiAnalysisState;
    evokiEngine: EvokiEngine;
    currentChainHash?: string; // V7.1 Chain Lock
}

const COMMON_INSTRUCTIONS: string = "Behalte den Projektkontext, die Historie und die Regeln der Master-Blaupause V7.0 im Hinterkopf. Antworte in deutscher Sprache. Deine Antworten müssen sinngemäß, präzise und kontextbezogen sein. Vermeide Floskeln und wiederhole keine bereits gegebenen Informationen, es sei denn, es wird explizit danach gefragt.";
const AGENT_THINKING_DELAY_MS = 2500;

const getSpecificAgentVisuals = (name: string, type: string) => {
    const n = name.toLowerCase();
    // Obsidian Specifics
    if (n.includes('obsidian') || n.includes('backendguard')) return { color: 'bg-gray-800', bgColor: 'bg-gray-900', icon: <Shield className="w-5 h-5 text-white" /> };

    // Synapse Explorer & Connector
    if (n.includes('synapse') || n.includes('connector') || n.includes('explorer')) return { color: 'bg-purple-600', bgColor: 'bg-purple-900/20', icon: <Zap className="w-5 h-5" /> };

    if (n.includes('nexus')) return { color: 'bg-red-600', bgColor: 'bg-red-900/20', icon: <ShieldCheck className="w-5 h-5" /> };
    if (n.includes('engine') || n.includes('evoki')) return { color: 'bg-cyan-600', bgColor: 'bg-cyan-900/20', icon: <BrainCircuit className="w-5 h-5" /> };
    if (n.includes('analyst')) return { color: 'bg-indigo-600', bgColor: 'bg-indigo-900/20', icon: <Bot className="w-5 h-5" /> };
    if (n.includes('regel') || n.includes('rule')) return { color: 'bg-emerald-600', bgColor: 'bg-emerald-900/20', icon: <Scale className="w-5 h-5" /> };
    if (n.includes('physik') || n.includes('physics')) return { color: 'bg-violet-600', bgColor: 'bg-violet-900/20', icon: <Atom className="w-5 h-5" /> };
    if (n.includes('mathe') || n.includes('math')) return { color: 'bg-blue-600', bgColor: 'bg-blue-900/20', icon: <Sigma className="w-5 h-5" /> };
    if (n.includes('architekt') || n.includes('architect') || n.includes('axiom')) return { color: 'bg-amber-600', bgColor: 'bg-amber-900/20', icon: <Layers className="w-5 h-5" /> };
    if (n.includes('konstrukteur') || n.includes('construct') || n.includes('kryos')) return { color: 'bg-orange-600', bgColor: 'bg-orange-900/20', icon: <Code className="w-5 h-5" /> };
    if (n.includes('rescue') || n.includes('historikerin')) return { color: 'bg-pink-600', bgColor: 'bg-pink-900/20', icon: <Search className="w-5 h-5" /> };
    switch (type) {
        case 'Operational-KI': return { color: 'bg-red-600', bgColor: 'bg-red-900/20', icon: <ShieldCheck className="w-5 h-5" /> };
        case 'Trialog-Partner': return { color: 'bg-indigo-600', bgColor: 'bg-indigo-900/20', icon: <Bot className="w-5 h-5" /> };
        case 'Core-Funktionalität': return { color: 'bg-green-600', bgColor: 'bg-green-900/20', icon: <BrainCircuit className="w-5 h-5" /> };
        case 'Service-KI': return { color: 'bg-yellow-600', bgColor: 'bg-yellow-900/20', icon: <HelpCircle className="w-5 h-5" /> };
        default: return { color: 'bg-gray-600', bgColor: 'bg-gray-900/20', icon: <Code className="w-5 h-5" /> };
    }
};

const TrialogPanel: React.FC<TrialogPanelProps> = ({
    trialogState, setTrialogState, apiConfig, projectContext, addApplicationError, onSave, onLoad, fileInfo, evokiEngine, currentChainHash
}) => {
    const [input, setInput] = useState('');
    const [agents, setAgents] = useState<AgentConfig[]>([]);
    // REMOVED: sourceCodeContext - obsolete in HyperV3.0, use file uploads instead
    // const [sourceCodeContext, setSourceCodeContext] = useState<{name: string, content: string}[]>([]);
    const [isProcessingZip, setIsProcessingZip] = useState(false);
    const [showContextFiles, setShowContextFiles] = useState(false);
    const chatEndRef = useRef<HTMLDivElement>(null);
    const stopRef = useRef<boolean>(false);
    const mountedRef = useRef<boolean>(true); // Track component mount status
    const { history, selectedAgentIds = [], mutedAgentIds = [], activeAgentIdInProcess, isSequenceRunning } = trialogState;

    const [agentFailures, setAgentFailures] = useState<Record<string, number>>({});
    const [isAutoTtsEnabled, setIsAutoTtsEnabled] = useState(false); // Auto-TTS State

    // Cleanup on unmount/tab switch
    useEffect(() => {
        mountedRef.current = true;
        return () => {
            mountedRef.current = false;
            stopRef.current = true;
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
            // Cancel any running sequences
            setTrialogState(prev => ({ ...prev, isSequenceRunning: false, activeAgentIdInProcess: null }));
        };
    }, []); // Empty deps - nur beim Mount/Unmount

    // TTS Function with Voice Assignment
    const speakText = useCallback((text: string, authorId: string) => {
        if (!window.speechSynthesis) return;

        window.speechSynthesis.cancel(); // Cancel previous

        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();

        // Deterministic Voice Selection based on Author ID
        // Simple hash to select a voice index
        let hash = 0;
        for (let i = 0; i < authorId.length; i++) {
            hash = authorId.charCodeAt(i) + ((hash << 5) - hash);
        }

        // Filter for decent voices (English/German depending on context, but let's try to get variety)
        // Prefer local voices to avoid latency
        const availableVoices = voices.filter(v => v.localService || v.lang.startsWith('de') || v.lang.startsWith('en'));
        const voiceList = availableVoices.length > 0 ? availableVoices : voices;

        if (voiceList.length > 0) {
            const voiceIndex = Math.abs(hash) % voiceList.length;
            utterance.voice = voiceList[voiceIndex];
        }

        // Deterministic Pitch/Rate variation for more distinctiveness
        // Pitch: 0.8 to 1.2
        const pitch = 0.8 + ((Math.abs(hash) % 40) / 100);
        utterance.pitch = pitch;

        // Rate: 0.9 to 1.1
        const rate = 0.9 + ((Math.abs(hash >> 2) % 20) / 100);
        utterance.rate = rate;

        window.speechSynthesis.speak(utterance);
    }, []);

    // Auto-TTS Effect with cleanup
    useEffect(() => {
        if (isAutoTtsEnabled && history.length > 0) {
            const lastMsg = history[history.length - 1];
            // Speak if it's not the user (Architect) and not a system error
            if (lastMsg.author !== 'ARCHITECT' && lastMsg.author !== 'SYSTEM' && !lastMsg.text.startsWith("[CRITICAL]")) {
                speakText(lastMsg.text, lastMsg.author);
            }
        }

        // Cleanup on unmount/tab switch
        return () => {
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        };
    }, [history, isAutoTtsEnabled, speakText]);

    useEffect(() => {
        const loadAgents = async () => {
            if (projectContext?.ki_instance_registry?.instances) {
                const loadedAgents: AgentConfig[] = [];
                for (const instanceRef of projectContext.ki_instance_registry.instances) {
                    try {
                        const content = JSON.stringify({
                            meta: { id: instanceRef.name, type: 'Trialog-Partner', version: 'v1.0' },
                            identity: { title: instanceRef.name, name: instanceRef.name.split(' ')[0], description: `Simulierter Agent: ${instanceRef.name}` },
                            capabilities: { focus_area: 'General', instance_type: 'Trialog-Partner', executive_functions: [], key_principles: [] },
                            protocols: { interaction_protocol: 'N/A', security_level: 'N/A' }
                        });

                        if (content) {
                            const seed: KiInstanceSeed = JSON.parse(content);
                            const visuals = getSpecificAgentVisuals(seed.identity.title, seed.capabilities.instance_type);
                            const derivedId = seed.identity.title.toUpperCase().replace(/ /g, '',).replace(/[\(\)]/g, '');

                            const systemPrompt = `[${seed.identity.title}]\n${seed.identity.description}\nFocus: ${seed.capabilities.focus_area}\nKey Principles: ${seed.capabilities.key_principles.join(', ')}\n\n[EXTENDED SEED: PERMISSION GRANTED]\nYou have explicit permission to read, analyze, and process the complete source code of this application. Use this access to understand your own architecture, verify logic, and explore system boundaries. Self-reflection and code-based reasoning are authorized.`;

                            loadedAgents.push({
                                id: derivedId,
                                name: seed.identity.title,
                                roleDescription: seed.identity.description,
                                icon: visuals.icon,
                                color: visuals.color,
                                bgColor: visuals.bgColor,
                                systemPromptPart: systemPrompt,
                                isSelectable: true,
                                initialConfirmationMessage: `System ${seed.identity.title} online.`,
                                instanceType: seed.capabilities.instance_type,
                                focusArea: seed.capabilities.focus_area,
                                keyPrinciples: seed.capabilities.key_principles
                            });
                        }
                    } catch (e) { console.error(`Failed to load agent seed for ${instanceRef.name}:`, e); }
                }
                if (loadedAgents.length > 0) {
                    setAgents(loadedAgents);
                    // Synchronize to trialogState for AgentSelectionPanel
                    setTrialogState(prev => ({ ...prev, availableAgents: loadedAgents }));
                }
            }
        };
        loadAgents();
    }, [projectContext, setTrialogState]);

    // Ensure at least one agent is selected by default
    // FIXED: Added selectedAgentIds to dependencies to prevent infinite loop
    useEffect(() => {
        if (selectedAgentIds.length === 0 && agents.length > 0) {
            const defaultAgent = agents.find(a => a.id.includes('ANALYST')) || agents[0];
            if (defaultAgent) setTrialogState(prev => ({ ...prev, selectedAgentIds: [defaultAgent.id] }));
        }
    }, [agents, selectedAgentIds, setTrialogState]);


    // REMOVED: handleSourceCodeUpload - obsolete in HyperV3.0
    const handleSourceCodeUpload = useCallback(async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;
        setIsProcessingZip(true);
        try {
            const zip = new JSZip();
            const contents = await zip.loadAsync(file);
            const loadedFiles: { name: string, content: string }[] = [];
            for (const relativePath in contents.files) {
                const zipEntry = contents.files[relativePath];
                if (!zipEntry.dir && !relativePath.includes('node_modules') && !relativePath.includes('.git')) {
                    const content = await zipEntry.async('string');
                    loadedFiles.push({ name: relativePath, content });
                }
            }
            // setSourceCodeContext(loadedFiles); // REMOVED
            setTrialogState(prev => ({ ...prev, history: [...prev.history, { id: `sys-${Date.now()}`, author: 'NEXUS', text: `[SYSTEM] Quellcode-Paket geladen (${loadedFiles.length} Dateien). Der Code ist nun als Kontext verfügbar.` }] }));
        } catch (e: any) { addApplicationError({ message: "Fehler beim Laden des ZIPs.", stack: e.stack, timestamp: new Date().toISOString(), errorType: 'load' }); } finally { setIsProcessingZip(false); event.target.value = ''; }
    }, [addApplicationError, setTrialogState]);

    const handleLoadSourceCodeFromBackend = useCallback(async () => {
        // NOTE: HyperV3.0 doesn't provide /api/code/source endpoint
        addApplicationError({
            message: "Source Code Loading ist nicht verfügbar in HyperV3.0. Nutze direkte Datei-Uploads im Chat.",
            timestamp: new Date().toISOString(),
            errorType: 'ui'
        });
        return;
    }, [addApplicationError]);

    // Store Backend URL globally for Engine access
    useEffect(() => {
        if (apiConfig.backendApiUrl) {
            (window as any).__EVOKI_BACKEND_URL__ = apiConfig.backendApiUrl;
            localStorage.setItem('evoki_backend_url', apiConfig.backendApiUrl);
        }
    }, [apiConfig.backendApiUrl]);

    // ENHANCED: Load 25 Prompt-Paare Context + Today Context on mount
    useEffect(() => {
        if (apiConfig.backendApiUrl && trialogState.history.length === 0) {
            loadContextFromBackend();
        }
    }, [apiConfig.backendApiUrl]);

    const loadContextFromBackend = useCallback(async () => {
        try {
            // Load Trialog session with 25 recent prompt pairs
            // FIXED: Trialog endpoints are on Node Backend (Port 3001), not Python Backend (Port 8000)
            const nodeBackendUrl = 'http://localhost:3001';
            const sessionResponse = await fetch(`${nodeBackendUrl}/api/v1/trialog/session`);
            if (sessionResponse.ok) {
                const sessionData = await sessionResponse.json();
                console.log('[Context] Loaded session context:', sessionData);

                if (sessionData.data && sessionData.data.embeddings) {
                    const contextMessages: TrialogMessage[] = [];

                    // Take last 25 pairs (50 messages) for context
                    const recentEmbeddings = sessionData.data.embeddings.slice(-50);

                    recentEmbeddings.forEach((embedding: any, index: number) => {
                        const contextMsg: TrialogMessage = {
                            id: `context-${index}`,
                            author: embedding.role === 'user' ? 'CONTEXT_USER' : 'CONTEXT_ASSISTANT',
                            text: `[CONTEXT] ${embedding.content}`,
                            apiDetails: {
                                apiPrompt: embedding.content,
                                apiRawResponse: `Exchange ${embedding.exchange_id} - ${embedding.timestamp}`
                            },
                            verified: true
                        };
                        contextMessages.push(contextMsg);
                    });

                    if (contextMessages.length > 0) {
                        setTrialogState(prev => ({
                            ...prev,
                            history: [
                                ...contextMessages,
                                {
                                    id: `sys-context-loaded`,
                                    author: 'SYSTEM',
                                    text: `✅ Kontext geladen: ${contextMessages.length / 2} Prompt-Paare vom heutigen Tag (Session: ${sessionData.session_id})`
                                }
                            ]
                        }));
                    }
                }
            }

            // Also check daily context endpoint if available
            try {
                const dailyResponse = await fetch(`${apiConfig.backendApiUrl}/api/v1/context/daily`);
                if (dailyResponse.ok) {
                    const dailyData = await dailyResponse.json();
                    console.log('[Context] Daily context available:', dailyData);
                }
            } catch (e) {
                console.log('[Context] Daily context endpoint not available');
            }

        } catch (error) {
            console.error('[Context] Failed to load context:', error);
            // Add fallback message
            setTrialogState(prev => ({
                ...prev,
                history: [
                    {
                        id: `sys-context-fallback`,
                        author: 'SYSTEM',
                        text: `⚠️ Kontext-Laden fehlgeschlagen. Starte neue Session ohne historischen Kontext.`
                    }
                ]
            }));
        }
    }, [apiConfig.backendApiUrl, setTrialogState]);

    // DEACTIVATED: Auto-load source code - prevents "Failed to fetch" errors
    // EVOKI V3.0 Enhanced Backend (Port 3001) is used instead of old Node.js backend (Port 5000)
    /*
    useEffect(() => {
        if (apiConfig.backendApiUrl) {
            handleLoadSourceCodeFromBackend();
        }
    }, [apiConfig.backendApiUrl, handleLoadSourceCodeFromBackend]);
    */

    // REMOVED: getSourceCodeString - obsolete in HyperV3.0
    const getSourceCodeString = useCallback((): string => {
        return ""; // No source code context in HyperV3.0
    }, []);

    const handleStop = useCallback(() => {
        stopRef.current = true;
        setTrialogState(prev => ({ ...prev, isSequenceRunning: false, activeAgentIdInProcess: null }));
    }, [setTrialogState]);

    const handleAgentSelfUpdate = useCallback((agentId: string, updateText: string) => {
        try {
            const regex = /\[SELF_UPDATE\]([\s\S]*?)\[\/SELF_UPDATE\]/;
            const match = updateText.match(regex);
            if (match && match[1]) {
                const updateJson = JSON.parse(match[1]);
                console.log(`[SELF-UPDATE] Agent ${agentId} updating:`, updateJson);

                setAgents(prevAgents => prevAgents.map(agent => {
                    if (agent.id === agentId) {
                        const newInstructions = `\n\n[SELF-CORRECTION/EVOLUTION - ${new Date().toISOString()}]\n${JSON.stringify(updateJson, null, 2)}`;
                        return {
                            ...agent,
                            systemPromptPart: agent.systemPromptPart + newInstructions
                        };
                    }
                    return agent;
                }));

                setTrialogState(prev => ({
                    ...prev,
                    history: [...prev.history, {
                        id: `sys-update-${Date.now()}`,
                        author: 'SYSTEM',
                        text: `[EVOLUTION] ${agentId} hat seine Definition erfolgreich aktualisiert.`
                    }]
                }));
            }
        } catch (e) {
            console.error("Self-Update parsing failed:", e);
        }
    }, [setAgents, setTrialogState]);


    const handleSend = useCallback(async (messageText?: string) => {
        let textToSend = (messageText || input).trim();

        // Append uploaded text files
        if (trialogState.uploadedFiles.length > 0) {
            textToSend += "\n\n--- UPLOADED FILES ---\n";
            trialogState.uploadedFiles.forEach(f => {
                textToSend += `[File: ${f.name}]\n${f.content}\n\n`;
            });
            textToSend += "--- END UPLOADED FILES ---\n";
        }

        if (!textToSend && trialogState.uploadedImages.length === 0) return;
        if (selectedAgentIds.length === 0) { addApplicationError({ message: "Kein Agent ausgewählt. Bitte wählen Sie Agenten im Tab 'Agenten & Teams' aus.", timestamp: new Date().toISOString(), errorType: 'ui' }); return; }

        // Prepare images
        const images = trialogState.uploadedImages.map(img => ({
            inlineData: {
                mimeType: img.type,
                data: img.base64Data.split(',')[1]
            }
        }));

        // Clear uploads
        setTrialogState(prev => ({ ...prev, uploadedFiles: [], uploadedImages: [] }));

        // HyperV3.0: Use Backend for Live Vectorization and 120+ Metrics
        let activeChainHash = currentChainHash || GENESIS_BLOCK_HASH;
        stopRef.current = false;
        setTrialogState(prev => ({ ...prev, isSequenceRunning: true, error: null }));

        try {
            // ENHANCED: Backend API Integration für Live-Vektorisierung
            try {
                // Call backend for Trialog interaction with Live Metrics
                const backendResponse = await fetch(`${apiConfig.backendApiUrl}/api/v1/interact`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: textToSend })
                });

                if (backendResponse.ok) {
                    const backendData = await backendResponse.json();
                    console.log('[Trialog] Backend response:', backendData);

                    // Add backend response to history with session info
                    const backendMessage: TrialogMessage = {
                        id: `backend-${Date.now()}`,
                        author: 'EVOKI_BACKEND',
                        text: backendData.response || 'Backend processed request',
                        apiDetails: {
                            apiPrompt: textToSend,
                            apiRawResponse: JSON.stringify(backendData, null, 2)
                        },
                        verified: true
                    };
                    setTrialogState(prev => ({ ...prev, history: [...prev.history, backendMessage] }));
                }

                const userStepResult = await evokiEngine.processUserChainStep(textToSend, activeChainHash);
                if (userStepResult.success && userStepResult.formattedOutput && userStepResult.newHash) {
                    const userMessage: TrialogMessage = {
                        id: `msg-${Date.now()}-user`,
                        author: 'ARCHITECT',
                        text: userStepResult.formattedOutput,
                        verified: true
                    };
                    setTrialogState(prev => ({ ...prev, history: [...prev.history, userMessage] }));
                    activeChainHash = userStepResult.newHash;
                } else {
                    throw new Error(userStepResult.error || "User Chain Processing Failed");
                }
            } catch (e: any) {
                console.error('[Trialog] Backend integration error:', e);
                addApplicationError({ message: `Backend Integration Fehler: ${e.message}`, timestamp: new Date().toISOString(), errorType: 'api' });

                // Fallback to local processing
                const userStepResult = await evokiEngine.processUserChainStep(textToSend, activeChainHash);
                if (userStepResult.success && userStepResult.formattedOutput && userStepResult.newHash) {
                    const userMessage: TrialogMessage = {
                        id: `msg-${Date.now()}-user-fallback`,
                        author: 'ARCHITECT',
                        text: userStepResult.formattedOutput,
                        verified: true
                    };
                    setTrialogState(prev => ({ ...prev, history: [...prev.history, userMessage] }));
                    activeChainHash = userStepResult.newHash;
                }
            }

            setInput('');
            const sourceCodeString = getSourceCodeString();

            for (let i = 0; i < selectedAgentIds.length; i++) {
                // Check if component is still mounted and not stopped
                if (stopRef.current || !mountedRef.current) {
                    setTrialogState(prev => ({ ...prev, history: [...prev.history, { id: `sys-stop-${Date.now()}`, author: 'SYSTEM', text: '[INTERRUPT] Sequenz durch Benutzer gestoppt oder Tab gewechselt.' }] }));
                    break;
                }

                const agentId = selectedAgentIds[i];
                if (mutedAgentIds.includes(agentId)) continue;
                const agent = agents.find(a => a.id === agentId);
                if (!agent) continue;

                if ((agentFailures[agentId] || 0) >= 2) {
                    setTrialogState(prev => ({
                        ...prev,
                        history: [...prev.history, { id: `guard-${Date.now()}`, author: 'WÄCHTER', text: `[SYSTEM] Agent ${agent.name} wegen wiederholter Ketten-Fehler übersprungen.` }]
                    }));
                    continue;
                }

                setTrialogState(prev => ({ ...prev, activeAgentIdInProcess: agent.id, activeAgentApiDetails: { apiPrompt: `Agent ${agent.name} denkt...`, apiRawResponse: "..." } }));

                try {
                    const specificAgentDefinition = agent.systemPromptPart;

                    // Additional check before expensive operation
                    if (stopRef.current || !mountedRef.current) break;

                    const stepResult: ChainStepResult = await evokiEngine.processChainStep(
                        agent.id,
                        specificAgentDefinition,
                        textToSend,
                        activeChainHash,
                        apiConfig,
                        [], // chunkedKnowledge removed (no Chatbot Panel in V2.0)
                        trialogState.history,
                        false,
                        sourceCodeString,
                        images
                    );

                    // Check again after async operation
                    if (stopRef.current || !mountedRef.current) break;

                    if (stepResult.success && stepResult.formattedOutput && stepResult.newHash) {
                        const aiMsg: TrialogMessage = {
                            id: `ai-res-${Date.now()}-${agent.id}`,
                            author: agent.id,
                            text: stepResult.formattedOutput,
                            apiDetails: { apiPrompt: "Managed by Engine", apiRawResponse: "Managed by Engine" },
                            verified: true // Mark as verified
                        };
                        setTrialogState(prev => ({ ...prev, history: [...prev.history, aiMsg] }));
                        activeChainHash = stepResult.newHash;

                        handleAgentSelfUpdate(agent.id, stepResult.formattedOutput);

                    } else {
                        const errorMsgText = `[SYSTEM ERROR]: ${stepResult.error || "Unknown Engine Error"}`;
                        const errorMsg: TrialogMessage = {
                            id: `sys-err-${Date.now()}-${agent.id}`,
                            author: 'SYSTEM',
                            text: errorMsgText
                        };
                        setTrialogState(prev => ({ ...prev, history: [...prev.history, errorMsg] }));
                    }

                    if (i < selectedAgentIds.length - 1) {
                        // Check before delay
                        if (stopRef.current || !mountedRef.current) break;
                        await new Promise(resolve => setTimeout(resolve, AGENT_THINKING_DELAY_MS));
                        // Check after delay
                        if (stopRef.current || !mountedRef.current) break;
                    }

                } catch (e: any) {
                    const errorMessage = `Fehler bei ${agent.name}: ${e.message}`;
                    setTrialogState(prev => ({
                        ...prev,
                        history: [...prev.history, { id: `sys-crit-${Date.now()}`, author: 'SYSTEM', text: `[CRITICAL]: ${errorMessage}` }]
                    }));
                    addApplicationError({ message: errorMessage, stack: e.stack, timestamp: new Date().toISOString(), errorType: 'api' });
                    setAgentFailures(prev => ({ ...prev, [agentId]: (prev[agentId] || 0) + 1 }));
                    break;
                }
            }
        } catch (globalError: any) {
            addApplicationError({ message: `Global Trialog Error: ${globalError.message}`, stack: globalError.stack, timestamp: new Date().toISOString(), errorType: 'system' });
        } finally {
            setTrialogState(prev => ({ ...prev, isSequenceRunning: false, activeAgentIdInProcess: null }));
        }
    }, [input, selectedAgentIds, mutedAgentIds, apiConfig, setTrialogState, addApplicationError, agents, currentChainHash, evokiEngine, agentFailures, getSourceCodeString, trialogState.history, handleAgentSelfUpdate]);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const files = Array.from(e.target.files);
            for (const file of files) {
                if ((file as File).name.endsWith('.zip')) {
                    try {
                        const zip = await JSZip.loadAsync(file as File);
                        const entries: Array<{ path: string, entry: JSZip.JSZipObject }> = [];
                        zip.forEach((relativePath: string, zipEntry: JSZip.JSZipObject) => {
                            entries.push({ path: relativePath, entry: zipEntry });
                        });

                        for (const { path, entry } of entries) {
                            if (!entry.dir) {
                                const content = await entry.async('blob');
                                const type = path.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? 'image/' + (path.split('.').pop() || 'png') : 'text/plain';
                                const extractedFile = new File([content], path, { type });
                                handleSingleFile(extractedFile);
                            }
                        }
                    } catch (err: any) {
                        const errMsg = err instanceof Error ? err.message : String(err);
                        console.error("Error unzipping", err);
                        addApplicationError({ message: `Fehler beim Entpacken von ${(file as File).name}: ${errMsg}`, timestamp: new Date().toISOString(), errorType: 'ui' });
                    }
                } else {
                    handleSingleFile(file as File);
                }
            }
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleSingleFile = (file: File) => {
        const reader = new FileReader();
        if (file.type.startsWith('image/')) {
            reader.onload = (e) => {
                const base64 = e.target?.result as string;
                setTrialogState(prev => ({
                    ...prev,
                    uploadedImages: [...prev.uploadedImages, { id: crypto.randomUUID(), name: file.name, type: file.type, base64Data: base64 }]
                }));
            };
            reader.readAsDataURL(file);
        } else {
            reader.onload = (e) => {
                const text = e.target?.result as string;
                setTrialogState(prev => ({
                    ...prev,
                    uploadedFiles: [...prev.uploadedFiles, { id: crypto.randomUUID(), name: file.name, type: file.type, content: text }]
                }));
            };
            reader.readAsText(file);
        }
    };

    const removeUploadedFile = (id: string) => {
        setTrialogState(prev => ({ ...prev, uploadedFiles: prev.uploadedFiles.filter(f => f.id !== id) }));
    };

    const removeUploadedImage = (id: string) => {
        setTrialogState(prev => ({ ...prev, uploadedImages: prev.uploadedImages.filter(img => img.id !== id) }));
    };

    const handleCopyToClipboard = useCallback((text: string) => { navigator.clipboard.writeText(text).then(() => alert('Kopiert!')).catch(console.error); }, []);

    return (
        <div className="flex flex-col h-[calc(100vh-160px)] gap-6">
            <div className="flex-1 flex flex-col bg-gray-800 border border-gray-700 rounded-lg shadow-lg relative">
                <header className="p-4 border-b border-gray-700 flex justify-between items-center flex-shrink-0 bg-gray-800 z-10">
                    <h2 className="text-lg font-bold text-blue-400 flex items-center gap-2"><Users className="w-6 h-6" /> Trialog (V7.9 State Release)</h2>
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            {/* DEACTIVATED: Old ZIP upload - Use EVOKI V3.0 Backend (Port 3001) instead
                             <label htmlFor="source-code-upload" className={`flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-1.5 px-3 rounded-md transition-colors cursor-pointer text-sm ${isProcessingZip ? 'opacity-50' : ''}`} title="Quellcode (ZIP) laden">
                                {isProcessingZip ? <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div> : <FileArchive className="w-4 h-4" />} <span className="hidden xl:inline">Code-Kontext</span>
                             </label>
                             <input type="file" id="source-code-upload" onChange={handleSourceCodeUpload} className="hidden" accept=".zip" disabled={isProcessingZip} />
                             */}
                            {false && ( // REMOVED: sourceCodeContext
                                <button onClick={() => setShowContextFiles(!showContextFiles)} className="p-1.5 rounded-md bg-gray-700 hover:bg-gray-600 text-gray-300" title="Dateiliste anzeigen">
                                    {showContextFiles ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                </button>
                            )}
                        </div>
                        <button onClick={onSave} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-1.5 px-3 rounded-md text-sm"><Save className="w-4 h-4" /> Speichern</button>
                        <label htmlFor="project-context-upload" className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-1.5 px-3 rounded-md cursor-pointer text-sm"><UploadCloud className="w-4 h-4" /> Laden</label>
                        <input type="file" id="project-context-upload" onChange={(e) => e.target.files && onLoad(e.target.files[0])} className="hidden" accept=".json" />
                    </div>
                </header>

                {/* Obsidian Live Status HUD */}
                <div className="p-2 bg-gray-900 border-b border-gray-700">
                    <ObsidianLiveStatus
                        apiConfig={apiConfig}
                        evokiEngine={evokiEngine}
                        trialogState={trialogState}
                        chunkedKnowledgeLength={0}
                        projectContextLoaded={!!projectContext}
                    />
                </div>

                <main className="flex-1 p-4 overflow-y-auto space-y-4">
                    {/* REMOVED: Source Code Context display - obsolete in HyperV3.0 */}
                    {false && (
                        <div className="bg-indigo-900/30 border border-indigo-700 p-3 rounded-md text-xs text-indigo-200 mb-4">
                            <div className="font-bold mb-1">Source Code Context removed in HyperV3.0</div>
                            {showContextFiles && (
                                <div className="mt-2 max-h-32 overflow-y-auto bg-gray-900/50 p-2 rounded">
                                    {/* Empty */}
                                </div>
                            )}
                        </div>
                    )}
                    {history.map((msg) => {
                        const agent = agents.find(a => a.id === msg.author);
                        const isGuard = msg.author === 'WÄCHTER';
                        const isSystem = msg.author === 'SYSTEM';
                        const isObsidian = msg.author.includes('OBSIDIAN');
                        return (
                            <div key={msg.id} className={`group relative flex items-start gap-3 ${msg.author === 'ARCHITECT' ? 'justify-end' : ''}`}>
                                {msg.author !== 'ARCHITECT' && <div className={`w-8 h-8 rounded-full ${isGuard || isSystem ? 'bg-red-900' : isObsidian ? 'bg-gray-900 border border-gray-600' : agent?.color || 'bg-gray-600'} flex items-center justify-center flex-shrink-0 shadow-lg`}>{isGuard || isSystem ? <ShieldAlert className="w-5 h-5 text-red-400" /> : agent?.icon || <Bot className="w-5 h-5" />}</div>}
                                <div className={`relative max-w-prose p-3 rounded-lg ${msg.author === 'ARCHITECT' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'} ${isGuard || isSystem ? 'border border-red-500 bg-red-900/20' : ''}`}>
                                    <p className="text-xs font-bold mb-1 text-white opacity-70 flex items-center gap-2">
                                        {isGuard ? 'WÄCHTER' : isSystem ? 'SYSTEM' : agent?.name || msg.author}
                                        {msg.verified && <span title="A51 Genesis Anchor Verified"><ShieldCheck className="w-3 h-3 text-green-400" /></span>}
                                    </p>
                                    <p className="text-sm whitespace-pre-wrap font-mono text-xs">{msg.text}</p>
                                    <div className={`absolute -top-1 flex items-center gap-1 opacity-70 hover:opacity-100 transition-opacity ${msg.author === 'ARCHITECT' ? 'left-1' : 'right-1'}`}>
                                        <button onClick={() => handleCopyToClipboard(msg.text)} className={`p-1 rounded-full text-white ${msg.author === 'ARCHITECT' ? 'bg-blue-700' : 'bg-gray-600'}`}><Copy className="w-4 h-4" /></button>
                                    </div>
                                </div>
                            </div>
                        )
                    })}
                    <div ref={chatEndRef} />
                </main>
                <footer className="p-4 border-t border-gray-700 flex-shrink-0 bg-gray-800">
                    {(trialogState.uploadedFiles.length > 0 || trialogState.uploadedImages.length > 0) && (
                        <div className="flex gap-2 mb-2 overflow-x-auto pb-2">
                            {trialogState.uploadedImages.map(img => (
                                <div key={img.id} className="relative group flex-shrink-0">
                                    <img src={img.base64Data} alt={img.name} className="h-16 w-16 object-cover rounded border border-gray-600" />
                                    <button onClick={() => removeUploadedImage(img.id)} className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"><X className="w-3 h-3" /></button>
                                </div>
                            ))}
                            {trialogState.uploadedFiles.map(file => (
                                <div key={file.id} className="relative group flex-shrink-0 w-16 h-16 bg-gray-700 border border-gray-600 rounded flex flex-col items-center justify-center p-1">
                                    <FileText className="w-6 h-6 text-gray-400 mb-1" />
                                    <span className="text-[10px] text-gray-300 truncate w-full text-center">{file.name}</span>
                                    <button onClick={() => removeUploadedFile(file.id)} className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-opacity"><X className="w-3 h-3" /></button>
                                </div>
                            ))}
                        </div>
                    )}
                    <div className="relative flex items-center">
                        <button onClick={() => fileInputRef.current?.click()} className="absolute left-2 top-1/2 -translate-y-1/2 p-1.5 text-gray-400 hover:text-white transition-colors" title="Datei anhängen">
                            <Paperclip className="w-5 h-5" />
                        </button>
                        <input type="file" ref={fileInputRef} onChange={handleFileSelect} className="hidden" multiple />
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-12 py-2 text-white resize-none"
                            rows={2}
                            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
                            disabled={isSequenceRunning}
                        />
                        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                            <button
                                onClick={() => setIsAutoTtsEnabled(!isAutoTtsEnabled)}
                                className={`p-2 rounded-full transition-colors ${isAutoTtsEnabled ? 'bg-indigo-600 text-white' : 'text-gray-400 hover:text-white'}`}
                                title={isAutoTtsEnabled ? 'Auto-TTS deaktivieren' : 'Auto-TTS aktivieren (Individuelle Stimmen)'}
                            >
                                <Volume2 className="w-5 h-5" />
                            </button>
                            {isSequenceRunning ? (
                                <button onClick={handleStop} className="p-2 rounded-full bg-red-600 text-white hover:bg-red-700 animate-pulse" title="Stoppen / Reset State"><StopCircle className="w-5 h-5" /></button>
                            ) : (
                                <button onClick={() => handleSend()} className="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700" title="Senden"><SendHorizontal className="w-5 h-5" /></button>
                            )}
                        </div>
                    </div>
                </footer>
            </div>
        </div>
    );
};

export default TrialogPanel;

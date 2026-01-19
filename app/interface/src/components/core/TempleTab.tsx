/**
 * EVOKI TEMPLE TAB - PHASE 0 SKELETON MODE
 * 
 * SSE-basiertes Chat-Interface OHNE echte Engines:
 * - KEINE FAISS
 * - KEINE Metriken-Berechnung
 * - KEIN LLM
 * 
 * Nur: Echtzeit SSE-Verbindung zwischen Frontend ↔ Backend
 * 
 * Was funktioniert:
 * ✅ User schreibt Nachricht → POST an Backend
 * ✅ Backend sendet SSE-Events (Status, Metriken, Token)
 * ✅ Frontend zeigt Events LIVE an
 * ✅ Guardian-Veto bei Krisenprompts
 */
import { useState, useRef } from 'react';
import { consumeSSEStream } from '../../utils/sse-parser';
import SettingsPanel from './SettingsPanel';
import { useTheme } from '../../hooks/useTheme'; // Fix: Load theme on app start

interface Message {
    role: 'user' | 'evoki' | 'system';
    content: string;
    color?: string;
}

interface Metrics {
    A: number;
    T_panic: number;
    B_align: number;
    F_risk: number;
    PCI: number;
}

export default function TempleTab() {
    const [prompt, setPrompt] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [currentResponse, setCurrentResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

    // Initialize theme hook with custom theme + display mode support
    const {
        currentTheme, switchTheme, availableThemes, customTheme, updateCustomTheme,
        displayMode, switchDisplayMode, availableDisplayModes
    } = useTheme();

    const abortControllerRef = useRef<AbortController | null>(null);

    const handleSend = async () => {
        if (!prompt.trim() || loading) return;

        setLoading(true);
        setStatus('Verbinde mit Backend...');
        setCurrentResponse('');
        setMetrics(null);

        // User-Nachricht anzeigen
        setMessages(prev => [...prev, {
            role: 'user',
            content: prompt
        }]);

        const userPrompt = prompt;
        setPrompt(''); // Input leeren

        try {
            // Abort-Controller für Cancel-Funktion
            abortControllerRef.current = new AbortController();

            // POST Request mit SSE-Streaming
            const response = await fetch('http://localhost:8000/api/temple/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: userPrompt }),
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                throw new Error(`Backend Error: ${response.status}`);
            }

            // Local response buffer (fixes React state timing issue!)
            let responseBuffer = '';

            // SSE-Stream konsumieren
            await consumeSSEStream(
                response,
                // onEvent
                (event) => {
                    switch (event.event) {
                        case 'status':
                            setStatus(event.data);
                            break;

                        case 'thought':
                            setStatus(`💭 ${event.data}`);
                            break;

                        case 'metrics_preview':
                            // Phase 1: Dummy metrics (deprecated)
                            setMetrics(event.data);
                            break;

                        case 'metrics':
                            // Phase 2: REAL Metrics!
                            setMetrics(event.data);
                            break;

                        case 'gate_a':
                            // Phase 2: Gate A Result
                            if (!event.data.passed) {
                                const gateText = `🔴 GATE A VETO:\n` +
                                    `Rules: ${event.data.rule_violations.join(', ')}\n` +
                                    event.data.veto_reasons.map((r: string) => `  • ${r}`).join('\n');

                                setMessages(prev => [...prev, {
                                    role: 'system',
                                    content: gateText,
                                    color: '#f00'
                                }]);
                            }
                            break;

                        case 'gate_b':
                            // Phase 2: Gate B Result
                            if (!event.data.passed) {
                                const gateText = `🟠 GATE B VETO:\n` +
                                    `Rules: ${event.data.rule_violations.join(', ')}\n` +
                                    event.data.veto_reasons.map((r: string) => `  • ${r}`).join('\n');

                                setMessages(prev => [...prev, {
                                    role: 'system',
                                    content: gateText,
                                    color: '#ff8800'
                                }]);
                            }
                            break;

                        case 'faiss_results':
                            // Phase 1: FAISS Top-3 Results
                            const faissData = event.data;
                            const faissText = `🔍 FAISS Top-${faissData.count}:\n` +
                                faissData.top3.map((r: any) =>
                                    `  • ${r.chunk_id} (Similarity: ${r.similarity})`
                                ).join('\n');

                            setMessages(prev => [...prev, {
                                role: 'system',
                                content: faissText,
                                color: '#0cf'
                            }]);
                            break;

                        case 'wpf_context':
                            // Phase 1: W-P-F Zeitmaschine
                            const wpf = event.data;
                            const wpfText = `⏱️ W-P-F Zeitmaschine:\n` +
                                `  Past -25: ${wpf.P_m25}\n` +
                                `  Past -5:  ${wpf.P_m5}\n` +
                                `  Now (W):  ${wpf.W}\n` +
                                `  Future +5:  ${wpf.F_p5}\n` +
                                `  Future +25: ${wpf.F_p25}`;

                            setMessages(prev => [...prev, {
                                role: 'system',
                                content: wpfText,
                                color: '#f80'
                            }]);
                            break;

                        case 'token':
                            responseBuffer += event.data; // Synchron!
                            setCurrentResponse(responseBuffer); // Async für UI
                            break;

                        case 'veto':
                            // Phase 0/1/2: Veto handling
                            const vetoColor = event.data.gate === 'A' ? '#f00' : '#ff8800';
                            const vetoText = `${event.data.gate === 'A' ? '🔴' : '🟠'} ${event.data.message}\n` +
                                (event.data.reasons ? event.data.reasons.map((r: string) => `  • ${r}`).join('\n') : '');

                            setMessages(prev => [...prev, {
                                role: 'system',
                                content: vetoText,
                                color: vetoColor
                            }]);
                            setStatus(`Veto aktiviert (Gate ${event.data.gate})`);
                            setLoading(false);
                            break;

                        case 'complete':
                            // responseBuffer hat ALLE tokens gesammelt!
                            if (responseBuffer) {
                                setMessages(prev => [...prev, {
                                    role: 'evoki',
                                    content: responseBuffer
                                }]);
                            }
                            setStatus('✅ Fertig!');
                            setCurrentResponse('');
                            setLoading(false);
                            break;
                    }
                },
                // onError
                (error) => {
                    console.error('SSE Error:', error);
                    setMessages(prev => [...prev, {
                        role: 'system',
                        content: `❌ Fehler: ${error.message}`,
                        color: 'red'
                    }]);
                    setLoading(false);
                }
            );

        } catch (error: any) {
            if (error.name === 'AbortError') {
                setMessages(prev => [...prev, {
                    role: 'system',
                    content: '⚠️ Request abgebrochen',
                    color: 'orange'
                }]);
            } else {
                setMessages(prev => [...prev, {
                    role: 'system',
                    content: `❌ Fehler: ${error.message}`,
                    color: 'red'
                }]);
            }
            setLoading(false);
        }
    };

    return (
        <div
            className="p-5 flex flex-col h-full"
            style={{
                background: `linear-gradient(to bottom, var(--bg-primary), var(--bg-secondary))`
            }}
        >
            {/* HEADER */}
            <div className="mb-5 flex items-center justify-between">
                <div>
                    <h1
                        className="font-bold bg-clip-text text-transparent"
                        style={{
                            fontSize: 'var(--font-size-heading)',
                            background: `linear-gradient(to right, var(--accent-primary), var(--accent-secondary))`,
                            WebkitBackgroundClip: 'text',
                            backgroundClip: 'text'
                        }}
                    >
                        🏛️ EVOKI TEMPLE [PHASE 3]
                    </h1>
                    <p
                        className="font-mono"
                        style={{
                            fontSize: 'var(--font-size-small)',
                            color: 'var(--text-accent)'
                        }}
                    >
                        "The divine void is also a computational state." - Kryos
                    </p>
                </div>

                {/* Settings Button */}
                <button
                    onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                    className="text-black font-bold rounded transition-colors"
                    style={{
                        padding: 'var(--spacing-sm) var(--spacing-md)',
                        fontSize: 'var(--font-size-base)',
                        backgroundColor: 'var(--accent-primary)'
                    }}
                >
                    ⚙️ Settings
                </button>
            </div>

            {/* STATUS BAR */}
            {status && (
                <div
                    className="px-3 py-2 rounded-lg mb-3 font-mono text-sm"
                    style={{
                        backgroundColor: 'var(--accent-primary)' + '1A',
                        border: '1px solid var(--accent-primary)',
                        color: 'var(--accent-primary)'
                    }}
                >
                    {status}
                </div>
            )}

            {/* METRICS PREVIEW */}
            {metrics && (
                <div className="p-3 bg-gray-800/30 border border-gray-700 rounded-lg mb-3 text-gray-400 text-xs font-mono">
                    <strong className="text-cyan-400">Metriken (Simulation):</strong>
                    {' '}
                    A={metrics.A.toFixed(2)}
                    {' | '}
                    T_panic={metrics.T_panic.toFixed(2)}
                    {' | '}
                    B_align={metrics.B_align.toFixed(2)}
                    {' | '}
                    F_risk={metrics.F_risk.toFixed(2)}
                    {' | '}
                    PCI={metrics.PCI.toFixed(2)}
                </div>
            )}

            {/* CHAT MESSAGES - V2.0 Card Style */}
            <div className="flex-1 bg-black/50 p-5 mb-5 rounded-lg overflow-y-auto border border-gray-800">
                {messages.length === 0 && !currentResponse && (
                    <div className="text-gray-600 italic text-center mt-12">
                        Konversation erscheint hier...
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        className={`mb-4 p-3 rounded-lg ${msg.role === 'user'
                            ? 'bg-blue-500/10 border-l-4 border-blue-400'
                            : msg.role === 'system'
                                ? 'bg-red-500/10 border-l-4 border-red-400'
                                : 'bg-green-500/10 border-l-4 border-green-400'
                            }`}
                    >
                        <div className="text-xs text-gray-400 mb-2 font-mono">
                            {msg.role === 'user' ? '👤 User' : msg.role === 'system' ? '⚙️ System' : '🏛️ Evoki'}
                        </div>
                        <div className="text-white whitespace-pre-wrap"
                            style={{ color: msg.color || '#fff' }}>
                            {msg.content}
                        </div>
                    </div>
                ))}

                {/* CURRENT TYPING RESPONSE */}
                {currentResponse && (
                    <div className="mb-4 p-3 rounded-lg bg-green-500/10 border-l-4 border-green-400">
                        <div className="text-xs text-gray-400 mb-2 font-mono">
                            🏛️ Evoki <span className="text-green-400">●</span>
                        </div>
                        <div className="text-white whitespace-pre-wrap">
                            {currentResponse}
                            <span className="opacity-70 animate-pulse">▊</span>
                        </div>
                    </div>
                )}
            </div>

            {/* INPUT */}
            <div style={{ display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Deine Frage an EVOKI..."
                    className="flex-1 bg-transparent border-0 outline-none font-mono"
                    style={{
                        fontSize: 'var(--font-size-base)',
                        padding: 'var(--spacing-sm)',
                        color: 'var(--text-primary)'
                    }}
                    disabled={loading}
                />
                <button
                    onClick={handleSend}
                    disabled={loading || !prompt.trim()}
                    className="font-bold rounded-lg transition-all text-black disabled:opacity-50"
                    style={{
                        padding: 'var(--spacing-sm) var(--spacing-lg)',
                        fontSize: 'var(--font-size-base)',
                        background: `linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))`,
                    }}
                >
                    {loading ? '⏳' : '➡️'} SENDEN
                </button>
            </div>

            {/* BLINK ANIMATION FOR CURSOR */}
            <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>

            {/* Settings Panel with Tabs */}
            <SettingsPanel
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                currentTheme={currentTheme}
                availableThemes={availableThemes}
                onThemeChange={switchTheme}
                customTheme={customTheme}
                onCustomThemeUpdate={updateCustomTheme}
                displayMode={displayMode}
                availableDisplayModes={availableDisplayModes}
                onDisplayModeChange={switchDisplayMode}
            />
        </div>
    );
}

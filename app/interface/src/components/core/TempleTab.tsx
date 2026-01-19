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
                            setMetrics(event.data);
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
                            setMessages(prev => [...prev, {
                                role: 'system',
                                content: `🔴 GUARDIAN-VETO (Gate ${event.data.gate}): ${event.data.reason}`,
                                color: 'red'
                            }]);
                            setStatus('Veto aktiviert - Request gestoppt');
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
        <div style={{
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            height: '100%',
            background: 'linear-gradient(180deg, #0a0a0a 0%, #1a0a1a 100%)'
        }}>
            {/* HEADER */}
            <div style={{ marginBottom: '20px' }}>
                <h1 style={{
                    fontSize: '2rem',
                    background: 'linear-gradient(90deg, #0cf 0%, #f0f 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 'bold'
                }}>
                    🏛️ EVOKI TEMPLE [PHASE 1]
                </h1>
                <p style={{
                    color: '#f80',
                    fontSize: '0.9rem',
                    fontFamily: 'monospace'
                }}>
                    ⚡ Phase 1: FAISS Active + 21 DBs | LLM noch Mock (Phase 3!)
                </p>
            </div>

            {/* STATUS BAR */}
            {status && (
                <div style={{
                    padding: '12px',
                    background: 'rgba(0, 204, 255, 0.1)',
                    border: '1px solid rgba(0, 204, 255, 0.3)',
                    borderRadius: '6px',
                    marginBottom: '10px',
                    color: '#0cf',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem'
                }}>
                    {status}
                </div>
            )}

            {/* METRICS PREVIEW */}
            {metrics && (
                <div style={{
                    padding: '10px',
                    background: 'rgba(50, 50, 50, 0.3)',
                    border: '1px solid #333',
                    borderRadius: '6px',
                    marginBottom: '10px',
                    color: '#888',
                    fontSize: '0.8rem',
                    fontFamily: 'monospace'
                }}>
                    <strong style={{ color: '#0cf' }}>Metriken (Simulation):</strong>
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

            {/* CHAT MESSAGES */}
            <div style={{
                flex: 1,
                background: 'rgba(0, 0, 0, 0.5)',
                padding: '20px',
                marginBottom: '20px',
                borderRadius: '8px',
                overflowY: 'auto',
                border: '1px solid #222'
            }}>
                {messages.length === 0 && !currentResponse && (
                    <div style={{
                        color: '#444',
                        fontStyle: 'italic',
                        textAlign: 'center',
                        marginTop: '50px'
                    }}>
                        Konversation erscheint hier...
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div
                        key={i}
                        style={{
                            marginBottom: '15px',
                            padding: '12px',
                            borderRadius: '6px',
                            background: msg.role === 'user'
                                ? 'rgba(0, 100, 200, 0.1)'
                                : msg.role === 'system'
                                    ? 'rgba(200, 50, 50, 0.1)'
                                    : 'rgba(0, 200, 100, 0.1)',
                            borderLeft: `3px solid ${msg.role === 'user' ? '#0cf' : msg.color || '#0f0'
                                }`
                        }}
                    >
                        <div style={{
                            fontSize: '0.8rem',
                            color: '#888',
                            marginBottom: '5px',
                            fontFamily: 'monospace'
                        }}>
                            {msg.role === 'user' ? '👤 User' : msg.role === 'system' ? '⚙️ System' : '🏛️ Evoki'}
                        </div>
                        <div style={{
                            color: msg.color || '#fff',
                            whiteSpace: 'pre-wrap',
                            fontFamily: 'system-ui'
                        }}>
                            {msg.content}
                        </div>
                    </div>
                ))}

                {/* CURRENT TYPING RESPONSE */}
                {currentResponse && (
                    <div style={{
                        marginBottom: '15px',
                        padding: '12px',
                        borderRadius: '6px',
                        background: 'rgba(0, 200, 100, 0.1)',
                        borderLeft: '3px solid #0f0'
                    }}>
                        <div style={{
                            fontSize: '0.8rem',
                            color: '#888',
                            marginBottom: '5px',
                            fontFamily: 'monospace'
                        }}>
                            🏛️ Evoki <span style={{ color: '#0f0' }}>●</span>
                        </div>
                        <div style={{
                            color: '#fff',
                            whiteSpace: 'pre-wrap',
                            fontFamily: 'system-ui'
                        }}>
                            {currentResponse}
                            <span style={{
                                opacity: 0.7,
                                animation: 'blink 1s infinite'
                            }}>▊</span>
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
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Schreib mir..."
                    disabled={loading}
                    style={{
                        flex: 1,
                        padding: '15px',
                        background: '#222',
                        border: '1px solid #333',
                        color: '#fff',
                        borderRadius: '6px',
                        fontSize: '1rem',
                        outline: 'none',
                        transition: 'border-color 0.3s'
                    }}
                />
                <button
                    onClick={handleSend}
                    disabled={loading || !prompt.trim()}
                    style={{
                        padding: '15px 30px',
                        background: loading ? '#333' : 'linear-gradient(135deg, #0cf 0%, #f0f 100%)',
                        color: loading ? '#666' : '#000',
                        border: 'none',
                        borderRadius: '6px',
                        fontWeight: 'bold',
                        fontSize: '1rem',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        transition: 'all 0.3s'
                    }}
                >
                    {loading ? 'LÄDT...' : 'SENDEN'}
                </button>
            </div>

            {/* BLINK ANIMATION FOR CURSOR */}
            <style>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
        </div>
    );
}

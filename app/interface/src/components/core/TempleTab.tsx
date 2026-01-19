import { useState, useEffect } from 'react';

export default function TempleTab() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<any[]>([]);
    const [history, setHistory] = useState<any>(null);

    const performSearch = async () => {
        if (!query) return;
        try {
            const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(query)}`);
            const data = await res.json();
            setResults(data);
        } catch (e) {
            console.error(e);
        }
    };

    const fetchHistory = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/history');
            const data = await res.json();
            setHistory(data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchHistory();
        const interval = setInterval(fetchHistory, 5000); // Live poll
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="temple-container" style={{ padding: '20px', color: '#e0e0e0', background: '#0f0f0f', height: '100%' }}>
            <h1>🏛️ THE TEMPLE (Synapse Core)</h1>

            <div className="search-section" style={{ marginBottom: '30px' }}>
                <h2>🔍 Genesis Search</h2>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && performSearch()}
                    placeholder="Search memory stream..."
                    style={{ padding: '10px', width: '300px', marginRight: '10px' }}
                />
                <button onClick={performSearch} style={{ padding: '10px 20px' }}>SEARCH</button>

                <div className="results" style={{ marginTop: '20px' }}>
                    {results.map((r, i) => (
                        <div key={i} style={{ border: '1px solid #333', padding: '10px', margin: '5px 0', borderRadius: '4px' }}>
                            <strong>{r.source_type}</strong>: {r.preview}
                            <pre style={{ fontSize: '10px', color: '#888' }}>{r.chunk_id}</pre>
                        </div>
                    ))}
                </div>
            </div>

            <div className="history-section">
                <h2>📜 Live Chain Status</h2>
                {history ? (
                    <div>
                        <p><strong>Total Entries:</strong> {history.entries?.length || 0}</p>
                        <p><strong>Last Hash:</strong> {history.entries?.[history.entries.length - 1]?.window_hash || 'N/A'}</p>
                        <div style={{ maxHeight: '400px', overflowY: 'auto', background: '#000', padding: '10px' }}>
                            {history.entries?.slice(-5).reverse().map((e: any, i: number) => (
                                <div key={i} style={{ borderBottom: '1px solid #444', marginBottom: '10px', paddingBottom: '10px' }}>
                                    <div style={{ color: '#0f0' }}>STATUS: {e.status_window.goal}</div>
                                    <div style={{ fontSize: '11px' }}>CONFIDENCE: {e.status_window.confidence} | HASH: {e.window_hash.substring(0, 16)}...</div>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div>Loading chain...</div>
                )}
            </div>
        </div>
    );
}

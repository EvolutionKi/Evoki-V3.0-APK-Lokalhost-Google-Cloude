import { useState, useEffect } from 'react';

export default function MetricsDashboard() {
    const [metrics, setMetrics] = useState<any>({});

    const fetchMetrics = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/metrics');
            const data = await res.json();
            setMetrics(data);
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 1000);
        return () => clearInterval(interval);
    }, []);

    const categories = {
        "Physical System": Object.keys(metrics).filter(k => k.startsWith('sys_')),
        "Synapse Memory": Object.keys(metrics).filter(k => k.startsWith('synapse_')),
        "Deep Earth Layers": Object.keys(metrics).filter(k => k.startsWith('layer_') || k.startsWith('deep_')),
        "Resonance Fields": Object.keys(metrics).filter(k => k.startsWith('resonance_') || !k.includes('_')),
        "Temporal": Object.keys(metrics).filter(k => k.startsWith('time_')),
    };

    return (
        <div style={{ padding: '20px', background: '#1a1a1a', color: '#fff', minHeight: '100vh' }}>
            <h1>📊 Evoki V3.0 Live Metrics Engine</h1>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                {Object.entries(categories).map(([cat, keys]) => (
                    <div key={cat} style={{ background: '#222', padding: '15px', borderRadius: '8px', border: '1px solid #333' }}>
                        <h3 style={{ borderBottom: '1px solid #444', paddingBottom: '10px' }}>{cat}</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '5px', fontSize: '12px' }}>
                            {keys.map(k => (
                                <div key={k} style={{ display: 'contents' }}>
                                    <span style={{ color: '#aaa', overflow: 'hidden', textOverflow: 'ellipsis' }}>{k}</span>
                                    <span style={{ textAlign: 'right', fontFamily: 'monospace', color: '#00ccff' }}>
                                        {typeof metrics[k] === 'number' ? metrics[k].toLocaleString() : metrics[k]}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

import { useState, useEffect } from 'react';

const LAYERS = [
    "01_surface", "02_shallow", "03_sediment", "04_bedrock",
    "05_fault", "06_mantle", "07_magma", "08_trench",
    "09_pressure", "10_crystal", "11_glacier", "12_abyss"
];

export default function DeepEarthTab({ activeLayer }: { activeLayer: string }) {
    const [data, setData] = useState<any>(null);

    useEffect(() => {
        if (!activeLayer) return;
        fetch(`http://localhost:8000/api/layers/${activeLayer}`)
            .then(res => res.json())
            .then(d => setData(d))
            .catch(e => console.error(e));
    }, [activeLayer]);

    return (
        <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: `linear-gradient(to bottom, #111, #000)` }}>
            <h1 style={{ fontSize: '4rem', opacity: 0.1, position: 'absolute' }}>{activeLayer.toUpperCase()}</h1>
            <div style={{ zIndex: 1, textAlign: 'center', border: '1px solid #333', padding: '40px', background: 'rgba(0,0,0,0.8)', borderRadius: '12px' }}>
                <h2 style={{ color: '#0cf' }}>Layer: {activeLayer}</h2>
                {data ? (
                    <div style={{ textAlign: 'left', marginTop: '20px' }}>
                        <p>Status: <span style={{ color: '#0f0' }}>{data.status}</span></p>
                        <p>Path: <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>{data.path}</span></p>
                        <p>Size: {data.size} bytes</p>
                        <p><i>Direct SQL Interface Ready</i></p>
                    </div>
                ) : (
                    <p>Establishing Connection to Core...</p>
                )}
            </div>
        </div>
    );
}

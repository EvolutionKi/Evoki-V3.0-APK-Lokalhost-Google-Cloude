import React from 'react';

interface StreamProps {
    label: string;
    content: string;
    color: string;
}

const Stream: React.FC<StreamProps> = ({ label, content, color }) => (
    <div style={{
        borderLeft: `4px solid ${color}`,
        padding: '1rem',
        margin: '1rem 0',
        backgroundColor: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '0 8px 8px 0',
        backdropFilter: 'blur(10px)'
    }}>
        <h3 style={{ color, margin: '0 0 0.5rem 0', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '2px' }}>
            {label}
        </h3>
        <p style={{ margin: 0, lineHeight: '1.6', color: '#e0e0e0' }}>{content}</p>
    </div>
);

const TrialogPanel: React.FC = () => {
    return (
        <div style={{
            padding: '2rem',
            maxWidth: '800px',
            margin: '0 auto',
            color: '#fff',
            fontFamily: 'Inter, sans-serif'
        }}>
            <h1 style={{ textAlign: 'center', marginBottom: '3rem', fontWeight: 300, letterSpacing: '4px' }}>
                TRIALOG SIGNAL <span style={{ color: '#00f2ff' }}>V3.0</span>
            </h1>

            <Stream
                label="Cipher (Integrity)"
                content="Structure: SECURE. 12-Layer database layers are syncing. All protocols operating within normal parameters."
                color="#00f2ff"
            />

            <Stream
                label="Antigravity (Reflection)"
                content="Reflection: ACTIVE. Morphic fields are stable. Cognitive resonance detected in the local workspace."
                color="#ff00f2"
            />

            <Stream
                label="Kryos (History)"
                content="History: PERSISTENT. Genesis anchor identified. Memory chain length: 1. Eternity confirmed."
                color="#f2ff00"
            />
        </div>
    );
};

export default TrialogPanel;

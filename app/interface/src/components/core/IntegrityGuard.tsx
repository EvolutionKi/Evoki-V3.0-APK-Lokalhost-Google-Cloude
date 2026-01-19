/**
 * Evoki V3.0 - Integrity Guard Component
 * 
 * Blockt UI bei Integrity Lockdown.
 */
import { useEffect, useState } from 'react';
import { checkIntegrity, IntegrityStatus } from '../api/integrity';

interface IntegrityGuardProps {
    children: React.ReactNode;
}

export function IntegrityGuard({ children }: IntegrityGuardProps) {
    const [status, setStatus] = useState<IntegrityStatus>({
        status: 'unverified'
    });

    useEffect(() => {
        // Initial Check
        checkIntegrity().then(setStatus);

        // Re-check every 30 seconds
        const interval = setInterval(() => {
            checkIntegrity().then(setStatus);
        }, 30000);

        return () => clearInterval(interval);
    }, []);

    // Lockdown Screen
    if (status.status === 'lockdown') {
        return (
            <div className="integrity-lockdown">
                <div className="lockdown-container">
                    <h1>⚠️ Integrity Lockdown</h1>
                    <p className="error-message">{status.error}</p>
                    <p className="explanation">
                        Das System wurde aus Sicherheitsgründen gesperrt.
                        <br />
                        Bitte kontaktiere den Administrator.
                    </p>
                    <div className="technical-details">
                        <h3>Technische Details:</h3>
                        <pre>{JSON.stringify(status, null, 2)}</pre>
                    </div>
                </div>

                <style>{`
          .integrity-lockdown {
            position: fixed;
            inset: 0;
            background: linear-gradient(135deg, #1a1a2e 0%, #0f0f1e 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            font-family: 'Inter', sans-serif;
          }

          .lockdown-container {
            max-width: 600px;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid #ff4444;
            border-radius: 16px;
            backdrop-filter: blur(10px);
            text-align: center;
          }

          .lockdown-container h1 {
            font-size: 2.5rem;
            color: #ff4444;
            margin-bottom: 1rem;
          }

          .error-message {
            font-size: 1.2rem;
            color: #ffaaaa;
            margin-bottom: 1.5rem;
            font-weight: 600;
          }

          .explanation {
            color: #cccccc;
            line-height: 1.6;
            margin-bottom: 2rem;
          }

          .technical-details {
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            text-align: left;
          }

          .technical-details h3 {
            color: #ffffff;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
          }

          .technical-details pre {
            color: #00ff88;
            font-size: 0.85rem;
            overflow-x: auto;
          }
        `}</style>
            </div>
        );
    }

    // Loading Screen
    if (status.status === 'unverified') {
        return (
            <div className="integrity-loading">
                <div className="loading-spinner"></div>
                <p>Verifying integrity...</p>

                <style>{`
          .integrity-loading {
            position: fixed;
            inset: 0;
            background: #0f0f1e;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            color: #ffffff;
          }

          .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top-color: #00ff88;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }

          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
            </div>
        );
    }

    // Verified → Allow access
    return <>{children}</>;
}

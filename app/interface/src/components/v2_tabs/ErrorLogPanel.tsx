
import React, { useState, useEffect } from 'react';
import { AlertTriangle, RefreshCw, Server } from './icons';
import { ApiConfig, AppError } from '../types';

interface ErrorLogPanelProps {
    apiConfig: ApiConfig;
    localErrors: AppError[];
}

const ErrorLogPanel: React.FC<ErrorLogPanelProps> = ({ apiConfig, localErrors }) => {
    const [backendErrors, setBackendErrors] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchBackendErrors = async () => {
        if (!apiConfig.backendApiUrl) return;
        setIsLoading(true);
        try {
            // Try new Backend endpoint first (Port 3001)
            const hyperspaceRes = await fetch(`${apiConfig.backendApiUrl}/api/v1/system/errors`);
            if (hyperspaceRes.ok) {
                const data = await hyperspaceRes.json();
                if (data.success) {
                    setBackendErrors(data.errors);
                    setIsLoading(false);
                    return;
                }
            }
            
            // Fallback to old endpoint (Port 3001/5000)
            const res = await fetch(`${apiConfig.backendApiUrl}/api/system/errors`);
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    setBackendErrors(data.errors);
                }
            }
        } catch (e) {
            console.error("Failed to fetch backend errors", e);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchBackendErrors();
        // Poll every 30 seconds
        const interval = setInterval(fetchBackendErrors, 30000);
        return () => clearInterval(interval);
    }, [apiConfig.backendApiUrl]);

    return (
        <div className="space-y-6 h-full flex flex-col">
             <div>
                <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-3">
                    <AlertTriangle className="w-7 h-7 text-red-500" /> Fehlerprotokoll (Black Box)
                </h2>
                <p className="text-gray-400">
                    Zentraler Speicher für alle Systemfehler. Fehler werden sowohl lokal erfasst als auch persistent im Backend gespeichert.
                </p>
            </div>

            <div className="flex-grow grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
                {/* Local Errors */}
                <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-900/50">
                         <h3 className="text-lg font-bold text-orange-400">Laufzeit-Fehler (Session)</h3>
                         <span className="text-xs px-2 py-1 bg-orange-900/30 rounded border border-orange-800 text-orange-200">{localErrors.length} Events</span>
                    </div>
                    <div className="flex-grow overflow-y-auto p-4 space-y-3">
                        {localErrors.length === 0 && <p className="text-gray-500 text-center italic mt-10">Keine Fehler in dieser Sitzung.</p>}
                        {localErrors.slice().reverse().map((err) => (
                            <div key={err.id} className="bg-gray-900 p-3 rounded border-l-4 border-orange-500 text-sm">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                    <span>{new Date(err.timestamp).toLocaleTimeString()}</span>
                                    <span className="font-mono">{err.errorType || 'runtime'}</span>
                                </div>
                                <p className="font-semibold text-gray-200">{err.message}</p>
                                {err.context && <p className="text-xs text-gray-400 mt-1 font-mono">Context: {err.context}</p>}
                                <div className="mt-2 text-[10px] text-gray-500 font-mono whitespace-pre-wrap overflow-x-auto">
                                    {err.stack?.split('\n')[0]}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Backend Errors */}
                <div className="bg-gray-800 rounded-lg border border-gray-700 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-900/50">
                         <h3 className="text-lg font-bold text-red-400 flex items-center gap-2">
                            <Server className="w-4 h-4"/> Backend Persistence Log
                         </h3>
                         <button onClick={fetchBackendErrors} className="p-1 hover:bg-gray-700 rounded transition-colors">
                             <RefreshCw className={`w-4 h-4 text-gray-400 ${isLoading ? 'animate-spin' : ''}`} />
                         </button>
                    </div>
                    <div className="flex-grow overflow-y-auto p-4 space-y-3">
                        {!apiConfig.backendApiUrl && <p className="text-gray-500 text-center italic mt-10">Backend nicht verbunden.</p>}
                        {apiConfig.backendApiUrl && backendErrors.length === 0 && !isLoading && <p className="text-gray-500 text-center italic mt-10">Backend Log leer.</p>}
                        
                        {backendErrors.map((err, i) => (
                            <div key={i} className="bg-black/40 p-3 rounded border border-red-900/30 text-sm opacity-80 hover:opacity-100 transition-opacity">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                    <span>{err.timestamp ? new Date(err.timestamp).toLocaleString() : 'Unknown'}</span>
                                    <span className="font-mono uppercase text-red-900">{err.errorType || 'System'}</span>
                                </div>
                                <p className="text-red-200 font-mono text-xs">{err.message}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ErrorLogPanel;

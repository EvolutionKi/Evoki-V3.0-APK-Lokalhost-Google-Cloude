
import React, { useState, useEffect, useRef } from 'react';
import { EvokiEngine } from './engine/EvokiEngine';
import { TerminalSquare, Layers, Download, UploadCloud, FileCode, ChevronDown } from './icons';
import { AppError, ParallelComponentStatus, DevLogEntry } from '../types';

interface EngineConsolePanelProps {
    evokiEngine: EvokiEngine;
    applicationErrors: AppError[];
    parallelArchitectureStatus: ParallelComponentStatus[];
    developerLog: DevLogEntry[];
    managedFiles: string[];
    onLoadProjectContext: (file: File) => void;
    onSaveProjectContext: () => void;
}

const EngineStatusDisplay: React.FC<{ statusString: string | null }> = ({ statusString }) => {
    if (!statusString) {
        return <div className="font-mono text-xs text-gray-500">Engine status initializing...</div>;
    }
    const lines = statusString.split('\n');
    const metricsL1 = lines[0]?.split(' | ') || [];
    const metricsL2 = lines[1]?.split(' | ') || [];

    return (
        <div className="bg-gray-900/50 p-3 rounded-lg border border-gray-700 font-mono text-xs">
            <div className="flex flex-wrap gap-x-4 gap-y-1">
                {metricsL1.map(metric => {
                    const [key, ...valueParts] = metric.split(': ');
                    const value = valueParts.join(': ');
                    let color = 'text-gray-300';
                    if (key === 'A') color = 'text-green-400';
                    if (key === '∇A') {
                        const numVal = parseFloat(value);
                        if (numVal > 0) color = 'text-green-400';
                        else if (numVal < 0) color = 'text-red-400';
                    }
                    if (key === 'Status' && value !== 'OPERATIONAL') color = 'text-red-500 font-bold';
                    return <span key={key} className={color}><span className="text-gray-500">{key}:</span> {value}</span>;
                })}
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 border-t border-gray-700/50 pt-1">
                {metricsL2.map(metric => {
                    const [key, ...valueParts] = metric.split(': ');
                    const value = valueParts.join(': ');
                    return <span key={key} className="text-gray-300"><span className="text-gray-500">{key}:</span> {value}</span>;
                })}
            </div>
        </div>
    );
};


const DeveloperLiveLogPanel: React.FC<{ logEntries: DevLogEntry[] }> = ({ logEntries }) => {
    const logEndRef = useRef<HTMLDivElement>(null);
    const logContainerRef = useRef<HTMLDivElement>(null);

     useEffect(() => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    }, [logEntries]);

    return (
        <div className="bg-gray-800 rounded-lg border border-gray-700 flex-grow flex flex-col h-full overflow-hidden">
            <h4 className="text-lg font-semibold text-blue-400 p-3 border-b border-gray-700 flex items-center gap-2 bg-gray-800 z-10">
                <TerminalSquare className="w-5 h-5" /> Developer Live Log
            </h4>
            <div ref={logContainerRef} className="p-3 text-xs font-mono text-gray-400 overflow-y-auto flex-grow scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
                {logEntries.map(entry => (
                    <div key={entry.id} className="flex gap-2 items-start mb-1">
                        <span className="text-gray-600 flex-shrink-0 select-none">{entry.timestamp.slice(11, 19)}</span>
                        <span className={`flex-shrink-0 font-bold w-16 text-right ${entry.source === 'API' ? 'text-green-500' : entry.source === 'Engine' ? 'text-blue-400' : 'text-purple-400'}`}>[{entry.source}]</span>
                        <span className={`whitespace-pre-wrap break-all ${entry.message.includes('ERROR') ? 'text-red-400' : ''}`}>{entry.message}</span>
                    </div>
                ))}
                <div ref={logEndRef} />
            </div>
        </div>
    );
};

const SystemStatusPanel: React.FC<{ parallelStatus: ParallelComponentStatus[] }> = ({ parallelStatus }) => {
    return (
        <div className="bg-gray-800 rounded-lg border border-gray-700 h-full flex flex-col overflow-hidden">
            <h4 className="text-md font-semibold text-blue-400 p-3 border-b border-gray-700 flex items-center gap-2 bg-gray-800 z-10">
                <Layers className="w-5 h-5" /> System-Status
            </h4>
            <div className="p-3 space-y-2 flex-grow overflow-y-auto">
                {parallelStatus.map(component => {
                    let statusColor = 'text-gray-400';
                    let statusBg = 'bg-gray-700';
                    
                    if (component.status === 'OPERATIONAL') { statusColor = 'text-green-400'; statusBg = 'bg-green-900/30 border-green-800'; }
                    else if (component.status === 'ERROR') { statusColor = 'text-red-400'; statusBg = 'bg-red-900/30 border-red-800'; }
                    else if (component.status === 'INITIALIZING') { statusColor = 'text-blue-400'; statusBg = 'bg-blue-900/30 border-blue-800'; }
                    
                    return (
                        <div key={component.name} className={`flex justify-between items-center p-2 rounded border border-transparent ${statusBg}`}>
                            <span className="text-gray-200 font-medium text-sm">{component.name}</span>
                            <span className={`font-mono text-xs font-bold ${statusColor}`}>{component.status}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

const EngineConsolePanel: React.FC<EngineConsolePanelProps> = ({
    evokiEngine, parallelArchitectureStatus, developerLog, managedFiles,
    onLoadProjectContext, onSaveProjectContext
}) => {
    const [engineStatus, setEngineStatus] = useState<string | null>(null);

    useEffect(() => {
        const fetchStatus = async () => {
            const status = await evokiEngine.generate_statusfenster_A61();
            setEngineStatus(status);
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 10000); // Reduced from 2s to 10s - less CPU load
        return () => clearInterval(interval);
    }, [evokiEngine]);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            onLoadProjectContext(file);
            event.target.value = '';
        }
    };

    const startGpu = async () => {
        alert('GPU Vectorizer: Nutze START_EVOKI_V3.bat im Root-Verzeichnis');
        // HyperV3.0 doesn't provide remote start endpoints
    };

    const startEngine = async () => {
        alert('Evoki Engine: Nutze START_EVOKI_V3.bat im Root-Verzeichnis');
        // HyperV3.0 doesn't provide remote start endpoints
    };

    return (
        <div className="h-[calc(100vh-140px)] flex flex-col gap-4">
            {/* Header & Controls */}
            <div className="flex justify-between items-center flex-shrink-0">
                <div>
                    <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                        <TerminalSquare className="w-7 h-7 text-blue-400" /> Engine-Konsole
                    </h2>
                </div>
                 <div className="flex gap-2">
                    <button onClick={startGpu} className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold py-2 px-3 rounded transition-colors">
                        <TerminalSquare className="w-4 h-4" />
                        Start GPU
                    </button>
                    <button onClick={startEngine} className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white text-xs font-semibold py-2 px-3 rounded transition-colors">
                        <TerminalSquare className="w-4 h-4" />
                        Start Engine
                    </button>
                    <label htmlFor="context-upload" className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white text-xs font-semibold py-2 px-3 rounded transition-colors cursor-pointer">
                        <UploadCloud className="w-4 h-4" />
                        Kontext laden
                    </label>
                    <input type="file" id="context-upload" onChange={handleFileChange} className="hidden" accept=".json" />

                    <button onClick={onSaveProjectContext} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold py-2 px-3 rounded transition-colors">
                        <Download className="w-4 h-4" />
                        Backup
                    </button>
                 </div>
            </div>

            {/* EKG Display */}
            <div className="flex-shrink-0">
                 <EngineStatusDisplay statusString={engineStatus} />
            </div>

            {/* Main Split View */}
            <div className="flex-grow flex gap-4 min-h-0">
                {/* Left Column: System Status */}
                <div className="w-1/3 min-w-[250px] flex flex-col">
                    <SystemStatusPanel parallelStatus={parallelArchitectureStatus} />
                </div>
                
                {/* Right Column: Live Log */}
                <div className="flex-1 flex flex-col">
                     <DeveloperLiveLogPanel logEntries={developerLog} />
                </div>
            </div>
            
            {/* Footer: Monitored Files Dropdown */}
            <div className="flex-shrink-0">
                <details className="bg-gray-900 rounded border border-gray-800 group">
                    <summary className="cursor-pointer p-2 text-xs text-gray-500 flex items-center gap-2 hover:text-gray-300 transition-colors">
                        <ChevronDown className="w-4 h-4 transition-transform group-open:rotate-180" />
                        <FileCode className="w-4 h-4" /> 
                        Überwachte Dateien ({managedFiles?.length || 0})
                    </summary>
                    <div className="p-2 bg-black/20 max-h-32 overflow-y-auto grid grid-cols-2 md:grid-cols-4 gap-2 text-[10px] font-mono text-gray-600">
                        {managedFiles && managedFiles.length > 0 ? managedFiles.map(f => (
                            <div key={f} className="truncate" title={f}>{f}</div>
                        )) : <div className="col-span-full text-center italic">Keine Dateien geladen.</div>}
                    </div>
                </details>
            </div>
        </div>
    );
};

export default EngineConsolePanel;

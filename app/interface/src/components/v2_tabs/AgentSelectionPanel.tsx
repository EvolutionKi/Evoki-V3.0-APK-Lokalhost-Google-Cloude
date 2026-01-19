
import React from 'react';
import { TrialogState, TrialogParticipant } from '../types';
import { Mic, MicOff, Bot, ShieldAlert, Shield } from './icons';

interface AgentSelectionPanelProps {
    trialogState: TrialogState;
    setTrialogState: (updater: React.SetStateAction<TrialogState>) => void;
}

const AgentSelectionPanel: React.FC<AgentSelectionPanelProps> = ({ trialogState, setTrialogState }) => {
    const { availableAgents = [], selectedAgentIds = [], mutedAgentIds = [] } = trialogState;

    const handleAgentToggle = (agentId: TrialogParticipant) => {
        setTrialogState(prev => {
            const current = prev.selectedAgentIds || [];
            return current.includes(agentId)
                ? { ...prev, selectedAgentIds: current.filter(id => id !== agentId), mutedAgentIds: (prev.mutedAgentIds || []).filter(id => id !== agentId) }
                : { ...prev, selectedAgentIds: [...current, agentId] };
        });
    };

    const handleMuteToggle = (agentId: TrialogParticipant, e: React.MouseEvent) => {
        e.stopPropagation();
        setTrialogState(prev => {
            const current = prev.mutedAgentIds || [];
            return current.includes(agentId)
                ? { ...prev, mutedAgentIds: current.filter(id => id !== agentId) }
                : { ...prev, mutedAgentIds: [...current, agentId] };
        });
    };

    return (
        <div className="p-6 bg-gray-800 rounded-lg border border-gray-700 shadow-lg h-[calc(100vh-160px)] overflow-y-auto">
            <header className="mb-6 border-b border-gray-700 pb-4">
                <h2 className="text-xl font-bold text-blue-400 flex items-center gap-2">
                    <Shield className="w-6 h-6 text-blue-400" /> Agenten & Teams Verwaltung
                </h2>
                <p className="text-gray-400 mt-1">
                    Konfigurieren Sie hier das Team für den Trialog. Aktivieren oder stummschalten Sie spezifische Instanzen.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {availableAgents.map(agent => {
                    const isSelected = selectedAgentIds.includes(agent.id);
                    const isMuted = mutedAgentIds.includes(agent.id);
                    
                    return (
                        <div 
                            key={agent.id} 
                            onClick={() => handleAgentToggle(agent.id)} 
                            className={`flex flex-col p-4 rounded-lg border cursor-pointer transition-all duration-200 hover:shadow-md ${isSelected ? 'border-blue-500 bg-blue-900/20' : 'border-gray-700 bg-gray-900/50 hover:bg-gray-800'}`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div className={`w-12 h-12 rounded-full ${agent.color} flex items-center justify-center shadow-lg border border-gray-600/50`}>
                                    {agent.icon || <Bot className="w-6 h-6 text-white"/>}
                                </div>
                                {isSelected && (
                                    <button 
                                        onClick={(e) => handleMuteToggle(agent.id, e)} 
                                        className={`p-2 rounded-full transition-colors ${isMuted ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'}`}
                                        title={isMuted ? "Stummschaltung aufheben" : "Agent stummschalten (Read-Only)"}
                                    >
                                        {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
                                    </button>
                                )}
                            </div>
                            
                            <h3 className={`font-bold text-lg ${isSelected ? 'text-blue-300' : 'text-gray-300'}`}>{agent.name}</h3>
                            <p className="text-xs text-gray-500 uppercase tracking-wider font-semibold mt-1 mb-2">{agent.instanceType || "Agent"}</p>
                            <p className="text-sm text-gray-400 line-clamp-3">{agent.roleDescription}</p>
                            
                            {isSelected && (
                                <div className="mt-auto pt-4 flex items-center gap-2 text-xs font-mono text-green-500">
                                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                    Aktiv im Trialog
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default AgentSelectionPanel;

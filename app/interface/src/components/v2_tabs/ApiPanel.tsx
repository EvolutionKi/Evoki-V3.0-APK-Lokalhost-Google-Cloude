import React from 'react';
import { ApiConfig } from '../types';
import { Bot, CheckCircle, XCircle, DollarSign } from './icons';

const InfoCard: React.FC<{ title: string, value: string | React.ReactNode, icon: React.ReactNode }> = ({ title, value, icon }) => (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 flex items-center gap-4">
        <div className="bg-blue-900/50 p-3 rounded-md">{icon}</div>
        <div>
            <p className="text-sm text-gray-400">{title}</p>
            <div className="text-xl font-bold text-white">{value}</div>
        </div>
    </div>
);

const ApiPanel: React.FC<{ apiConfig: ApiConfig }> = ({ apiConfig }) => {
    const { isConnected, model, budget, usage } = apiConfig;
    const remainingBudget = budget - usage;
    const usagePercentage = budget > 0 ? (usage / budget) * 100 : 0;

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div>
                <h2 className="text-2xl font-bold mb-2 text-white">Gemini API-Integration</h2>
                <p className="text-gray-400">Übersicht über den Verbindungsstatus, das ausgewählte Modell und die Kostenkontrolle für die Gemini API.</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InfoCard 
                    title="Verbindungsstatus"
                    icon={isConnected ? <CheckCircle className="w-8 h-8 text-green-400" /> : <XCircle className="w-8 h-8 text-red-400" />}
                    value={isConnected ? <span className="text-green-400">Verbunden</span> : <span className="text-red-400">Getrennt</span>}
                />
                <InfoCard
                    title="Ausgewähltes Modell"
                    icon={<Bot className="w-8 h-8 text-blue-400" />}
                    value={<span className="font-mono">{model}</span>}
                />
                <div className="md:col-span-2">
                    <InfoCard
                        title="Budget-Verbrauch"
                        icon={<DollarSign className="w-8 h-8 text-yellow-400" />}
                        value={
                            <div>
                                <p>${usage.toFixed(2)} / ${budget.toFixed(2)}</p>
                                <div className="w-full bg-gray-700 rounded-full h-2.5 mt-2">
                                    <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${Math.min(usagePercentage, 100)}%` }}></div>
                                </div>
                                <p className="text-xs text-gray-400 mt-1">Verbleibend: ${remainingBudget.toFixed(2)}</p>
                            </div>
                        }
                    />
                </div>
            </div>
        </div>
    );
};

export default ApiPanel;
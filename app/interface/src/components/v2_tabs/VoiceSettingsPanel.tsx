import React, { useState, useEffect } from 'react';
import { ApiConfig } from '../types';
import { Volume2, Save, Key, Mic } from './icons';

interface VoiceSettingsPanelProps {
    apiConfig: ApiConfig;
    setApiConfig: (config: ApiConfig) => void;
    addApplicationError: (error: any) => Promise<void>;
}

export const VoiceSettingsPanel: React.FC<VoiceSettingsPanelProps> = ({ apiConfig, setApiConfig, addApplicationError }) => {
    const [apiKey, setApiKey] = useState(apiConfig.openaiApiKey || '');
    const [selectedVoice, setSelectedVoice] = useState(apiConfig.voice || 'onyx');
    const [isSaving, setIsSaving] = useState(false);

    const voices = [
        { id: 'alloy', name: 'Alloy (Neutral)' },
        { id: 'echo', name: 'Echo (Neutral)' },
        { id: 'fable', name: 'Fable (British)' },
        { id: 'onyx', name: 'Onyx (Deep/Calm)' },
        { id: 'nova', name: 'Nova (Energetic)' },
        { id: 'shimmer', name: 'Shimmer (Clear)' }
    ];

    const handleSave = () => {
        setIsSaving(true);
        try {
            setApiConfig({
                ...apiConfig,
                openaiApiKey: apiKey,
                voice: selectedVoice
            });
            // Optional: Persist to local storage or backend if needed
            localStorage.setItem('openai_api_key', apiKey);
            localStorage.setItem('evoki_voice', selectedVoice);
        } catch (e: any) {
            addApplicationError({
                message: `Fehler beim Speichern der Spracheinstellungen: ${e.message}`,
                timestamp: new Date().toISOString(),
                errorType: 'ui'
            });
        } finally {
            setIsSaving(false);
        }
    };

    useEffect(() => {
        // Load from local storage on mount if available and not in config
        const storedKey = localStorage.getItem('openai_api_key');
        const storedVoice = localStorage.getItem('evoki_voice');
        
        if (storedKey && !apiConfig.openaiApiKey) {
            setApiKey(storedKey);
            setApiConfig({ ...apiConfig, openaiApiKey: storedKey });
        }
        if (storedVoice && !apiConfig.voice) {
            setSelectedVoice(storedVoice);
            setApiConfig({ ...apiConfig, voice: storedVoice });
        }
    }, []);

    const testVoice = async () => {
        if (!apiKey) return;
        try {
            const response = await fetch("https://api.openai.com/v1/audio/speech", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${apiKey}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    model: "tts-1",
                    input: "Hallo, ich bin Evoki. Dies ist meine Stimme.",
                    voice: selectedVoice,
                }),
            });

            if (!response.ok) throw new Error("TTS Request failed");

            const blob = await response.blob();
            const audio = new Audio(URL.createObjectURL(blob));
            audio.play();
        } catch (e: any) {
            addApplicationError({
                message: `Test-Sprachausgabe fehlgeschlagen: ${e.message}`,
                timestamp: new Date().toISOString(),
                errorType: 'api'
            });
        }
    };

    return (
        <div className="p-6 bg-gray-800 rounded-lg shadow-lg max-w-2xl mx-auto mt-10">
            <h2 className="text-2xl font-bold text-blue-400 mb-6 flex items-center gap-3">
                <Volume2 className="w-8 h-8" /> Spracheinstellungen (OpenAI TTS)
            </h2>

            <div className="space-y-6">
                {/* API Key Input */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-300 flex items-center gap-2">
                        <Key className="w-4 h-4" /> OpenAI API Key
                    </label>
                    <input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-..."
                        className="w-full bg-gray-700 border border-gray-600 rounded-md px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <p className="text-xs text-gray-500">
                        Der Key wird lokal im Browser gespeichert und nur für die Sprachausgabe verwendet.
                    </p>
                </div>

                {/* Voice Selection */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-300 flex items-center gap-2">
                        <Mic className="w-4 h-4" /> Stimme auswählen
                    </label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {voices.map((v) => (
                            <div 
                                key={v.id}
                                onClick={() => setSelectedVoice(v.id)}
                                className={`p-4 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                                    selectedVoice === v.id 
                                    ? 'bg-blue-600/20 border-blue-500 text-white' 
                                    : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                                }`}
                            >
                                <span className="font-medium">{v.name}</span>
                                {selectedVoice === v.id && <div className="w-3 h-3 bg-blue-500 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)]"></div>}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Actions */}
                <div className="pt-6 border-t border-gray-700 flex items-center justify-between">
                    <button
                        onClick={testVoice}
                        disabled={!apiKey}
                        className="px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                        <Volume2 className="w-4 h-4" /> Testen
                    </button>

                    <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-md transition-all shadow-lg hover:shadow-blue-500/30 flex items-center gap-2"
                    >
                        <Save className="w-4 h-4" /> {isSaving ? 'Speichere...' : 'Einstellungen Speichern'}
                    </button>
                </div>
            </div>
        </div>
    );
};

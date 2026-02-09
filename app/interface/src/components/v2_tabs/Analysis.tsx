
import React, { useMemo, useState, useEffect, useRef, useCallback } from 'react';
import { ApiConfig, AiAnalysisState, AnalysisOptions, DuplicateReport, IngestAnalysisResult, FileMeta, UpdateMergeRow, DayRollup, AppError, AnalysisData } from '../types';
import { AlertTriangle, CheckCircle, FileText, Bot, FileBadge, Sparkles, Wand, Info, FileJson, GitMerge, Trash2, ChevronDown, LineChart, Volume2, X, StopCircle } from './icons';
import DuplicateTable from './DuplicateTable';
import { WasteCenter } from './WasteCenter';
import { exportJson } from '../services/exportService';
import AnalysisChart from './AnalysisChart';
import { GoogleGenAI, Modality } from "@google/genai";
import { getAi } from '../services/core/geminiService';

interface AnalysisPanelProps {
    analysis: AnalysisData;
    apiConfig: ApiConfig;
    aiAnalysis: AiAnalysisState;
    onRunAnalysis: (options: AnalysisOptions) => void;
    onRunDeepAnalysis: (options: AnalysisOptions) => void;
    ingestAnalysis: IngestAnalysisResult;
    fileInfo: {
        baseline: FileMeta | null;
        update: FileMeta | null;
        secondBaseline: FileMeta | null;
    };
    onClearWaste: () => void;
    setApiConfig: (config: ApiConfig) => void;
    addApplicationError: (error: Omit<AppError, 'id' | 'count'> & { stack?: string; errorType?: AppError['errorType'] }) => Promise<void>;
}

function decode(base64: string) {
  const binaryString = atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

async function decodeAudioData(
  data: Uint8Array,
  ctx: AudioContext,
  sampleRate: number = 24000, 
  numChannels: number = 1,
): Promise<AudioBuffer> {
  const dataInt16 = new Int16Array(data.buffer);
  const frameCount = dataInt16.length / numChannels;
  const buffer = ctx.createBuffer(numChannels, frameCount, sampleRate);

  for (let channel = 0; channel < numChannels; channel++) {
    const channelData = buffer.getChannelData(channel);
    for (let i = 0; i < frameCount; i++) {
      channelData[i] = dataInt16[i * numChannels + channel] / 32768.0;
    }
  }
  return buffer;
}


const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
    analysis, apiConfig, aiAnalysis, onRunAnalysis, onRunDeepAnalysis,
    ingestAnalysis, fileInfo, onClearWaste, setApiConfig, addApplicationError
}) => {
    const [dateRange, setDateRange] = useState({ start: '', end: '' });
    const [customPrompt, setCustomPrompt] = useState('');
    const [responseLength, setResponseLength] = useState<'short' | 'medium' | 'detailed'>('medium');
    const [analysisCriteria, setAnalysisCriteria] = useState({
        scientific: false, psychological: false, conversationFlow: false,
        userKiRelationship: false, development: false, languageStyle: false,
        keyTopics: false, actionItems: false,
    });

    const [isSpeaking, setIsSpeaking] = useState(false);
    const [speechError, setSpeechError] = useState<string | null>(null);
    const outputAudioContextRef = useRef<AudioContext | null>(null);
    const nextStartTimeRef = useRef(0);
    const audioSourceNodesRef = useRef<Set<AudioBufferSourceNode>>(new Set());

    const hasIngestResults = ingestAnalysis.counts !== null;
    const hasAnalysisResults = aiAnalysis.isLoading || aiAnalysis.error || aiAnalysis.result;
    const hasTimestampNormalizationErrors = (ingestAnalysis.timestampNormalizationErrors?.length || 0) > 0;

    const totalIngestedEntries = useMemo(() => {
        return (ingestAnalysis.counts?.baseline || 0) + (ingestAnalysis.counts?.added || 0);
    }, [ingestAnalysis.counts]);

    const handleRunAnalysisClick = () => {
        onRunAnalysis({ dateRange, customPrompt, responseLength, analysisCriteria });
    };

    const handleRunDeepAnalysisClick = () => {
        onRunDeepAnalysis({ dateRange, customPrompt, responseLength, analysisCriteria });
    };

    const handleCriterionChange = (criterion: keyof typeof analysisCriteria) => {
        setAnalysisCriteria(prev => ({ ...prev, [criterion]: !prev[criterion] }));
    };

    const handleStopSpeech = useCallback(() => {
      for (const sourceNode of audioSourceNodesRef.current.values()) {
        sourceNode.stop();
      }
      audioSourceNodesRef.current.clear();
      nextStartTimeRef.current = 0;
      setIsSpeaking(false);
    }, []);

    const handleTextToSpeech = async (textToSpeak: string) => {
      handleStopSpeech();
      if (!textToSpeak.trim()) {
        setSpeechError("Kein Text zum Vorlesen vorhanden.");
        return;
      }
      setIsSpeaking(true);
      setSpeechError(null);
      
      try {
        if (!outputAudioContextRef.current || outputAudioContextRef.current.state === 'closed') {
          outputAudioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 24000 });
        }
        const audioCtx = outputAudioContextRef.current;
        if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
        }


        const genAI = await getAi();
        if (!genAI) {
            throw new Error("Gemini AI Client konnte nicht initialisiert werden. Ist der API_KEY gesetzt?");
        }
        if (!apiConfig.isConnected) {
            throw new Error("Gemini API ist nicht verbunden.");
        }
        if (apiConfig.usage >= apiConfig.budget) {
            throw new Error("API-Budget aufgebraucht.");
        }

        const response = await genAI.models.generateContent({
            model: "gemini-2.5-flash-preview-tts",
            contents: [{ parts: [{ text: textToSpeak }] }],
            config: {
                responseModalities: [Modality.AUDIO],
                speechConfig: {
                    voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Zephyr' } },
                },
            },
        });

        const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
        if (base64Audio && audioCtx) {
            const estimatedCost = (textToSpeak.length / 1000) * 0.000001; 
            setApiConfig({ ...apiConfig, usage: apiConfig.usage + estimatedCost });

            nextStartTimeRef.current = Math.max(nextStartTimeRef.current, audioCtx.currentTime);
            const audioBuffer = await decodeAudioData(
                decode(base64Audio),
                audioCtx,
                24000,
                1,
            );
            const source = audioCtx.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(audioCtx.destination);
            
            source.addEventListener('ended', () => {
                audioSourceNodesRef.current.delete(source);
                if (audioSourceNodesRef.current.size === 0) {
                    setIsSpeaking(false);
                }
            });

            source.start(nextStartTimeRef.current);
            nextStartTimeRef.current = nextStartTimeRef.current + audioBuffer.duration;
            audioSourceNodesRef.current.add(source);

        } else {
            throw new Error("Keine Audiodaten von Gemini erhalten.");
        }
      } catch (e: any) {
        console.error("Speech Synthesis Error:", e);
        setSpeechError(e.message || "Fehler bei der Sprachsynthese.");
        setIsSpeaking(false);
        addApplicationError({ message: `Sprachsynthese-Fehler: ${e.message}`, stack: e.stack, timestamp: new Date().toISOString(), context: 'AnalysisPanel:handleTextToSpeech', errorType: 'api' });
      }
    };

    useEffect(() => {
        return () => {
            handleStopSpeech();
            if (outputAudioContextRef.current && outputAudioContextRef.current.state !== 'closed') {
                outputAudioContextRef.current.close();
                outputAudioContextRef.current = null;
            }
        };
    }, [handleStopSpeech]);

    return (
        <div className="space-y-8">
            <div>
                <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-3">
                    <LineChart className="w-7 h-7 text-blue-400" /> KI-Analyse & Metriken
                </h2>
                <p className="text-gray-400">
                    Führen Sie eine tiefgehende Analyse Ihrer Chat-Daten mit Gemini durch und visualisieren Sie Metriken.
                </p>
            </div>

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold text-blue-400 mb-4">Analyse-Optionen</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                    <div>
                        <label htmlFor="custom-prompt" className="block text-sm font-medium text-gray-300">Benutzerdefinierter Prompt (optional)</label>
                        <textarea
                            id="custom-prompt"
                            value={customPrompt}
                            onChange={(e) => setCustomPrompt(e.target.value)}
                            rows={3}
                            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-blue-500 focus:border-blue-500"
                            placeholder="Z.B. 'Identifiziere wiederkehrende Muster im Kommunikationsstil...'"
                        ></textarea>
                    </div>
                    <div>
                        <label htmlFor="response-length" className="block text-sm font-medium text-gray-300">Antwortlänge</label>
                        <select
                            id="response-length"
                            value={responseLength}
                            onChange={(e) => setResponseLength(e.target.value as 'short' | 'medium' | 'detailed')}
                            className="mt-1 block w-full bg-gray-700 border border-gray-600 rounded-md shadow-sm p-2 text-white focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="short">Kurz</option>
                            <option value="medium">Mittel</option>
                            <option value="detailed">Detailliert</option>
                        </select>
                    </div>
                </div>
                
                <div className="mt-6">
                    <h4 className="text-md font-semibold text-gray-300 mb-2">Analyse-Kriterien (Standard)</h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                        {Object.entries(analysisCriteria).map(([key, value]) => (
                            <label key={key} className="flex items-center text-gray-400 text-sm">
                                <input
                                    type="checkbox"
                                    checked={value}
                                    onChange={() => handleCriterionChange(key as keyof typeof analysisCriteria)}
                                    className="h-4 w-4 rounded border-gray-500 bg-gray-700 text-blue-600 focus:ring-blue-600"
                                />
                                <span className="ml-2 capitalize">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</span>
                            </label>
                        ))}
                    </div>
                </div>

                <div className="mt-6 flex flex-wrap gap-3">
                    <button 
                        onClick={handleRunAnalysisClick} 
                        disabled={aiAnalysis.isLoading || !apiConfig.isConnected}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                    >
                        {aiAnalysis.isLoading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                            <Bot className="w-5 h-5"/>
                        )}
                        Standard-Analyse starten
                    </button>
                    <button 
                        onClick={handleRunDeepAnalysisClick} 
                        disabled={aiAnalysis.isLoading || !apiConfig.isConnected}
                        className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-md transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                    >
                        {aiAnalysis.isLoading ? (
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        ) : (
                            <Sparkles className="w-5 h-5"/>
                        )}
                        Deep-Analyse starten
                    </button>
                    <button
                        onClick={() => handleTextToSpeech(aiAnalysis.result)}
                        disabled={!aiAnalysis.result || isSpeaking}
                        className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-md transition-colors disabled:bg-gray-600 disabled:cursor-not-allowed"
                    >
                        {isSpeaking ? <StopCircle className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
                        {isSpeaking ? 'Stoppen' : 'Vorlesen'}
                    </button>
                </div>
                {speechError && (
                    <div className="p-2 text-xs bg-red-900/50 text-red-300 border border-red-700 rounded-md mt-2">
                        <AlertTriangle className="inline w-3 h-3 mr-1" /> {speechError}
                    </div>
                )}
            </div>
            
            {hasAnalysisResults && (
                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                        <Wand className="w-5 h-5"/> KI-Analyse-Ergebnisse
                    </h3>
                    {aiAnalysis.isLoading ? (
                        <div className="flex items-center justify-center h-32 text-gray-400">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400 mr-3"></div>
                            Analyse wird erstellt...
                        </div>
                    ) : aiAnalysis.error ? (
                        <div className="p-4 bg-red-900/50 border border-red-700 rounded-md text-red-300 text-sm">
                            <AlertTriangle className="inline w-4 h-4 mr-2" />Fehler bei der KI-Analyse: {aiAnalysis.error}
                        </div>
                    ) : (
                        <div className="prose prose-invert max-w-none">
                            <p>{aiAnalysis.result}</p>
                            <p className="mt-4 text-xs text-gray-500 italic">Geschätzte Kosten: ${apiConfig.usage.toFixed(6)}</p>
                        </div>
                    )}
                </div>
            )}

            {ingestAnalysis.counts && (
                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                        <GitMerge className="w-5 h-5"/> Ingest & Merge Statistiken
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Baseline Einträge</p>
                            <p className="text-xl font-bold text-white">{ingestAnalysis.counts.baseline}</p>
                        </div>
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Update Einträge (Total)</p>
                            <p className="text-xl font-bold text-white">{ingestAnalysis.counts.updateTotal}</p>
                        </div>
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Neue Einträge (nach Merge)</p>
                            <p className="text-xl font-bold text-green-400">{ingestAnalysis.counts.added}</p>
                        </div>
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Duplikate in Baseline</p>
                            <p className="text-xl font-bold text-yellow-400">{ingestAnalysis.counts.duplicatesInBaseline}</p>
                        </div>
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Ignorierte Einträge (Waste)</p>
                            <p className="text-xl font-bold text-red-400">{ingestAnalysis.counts.waste}</p>
                        </div>
                        <div className="p-3 bg-gray-900/50 border border-gray-700 rounded-md">
                            <p className="text-sm text-gray-400">Einträge nach Merge</p>
                            <p className="text-xl font-bold text-white">{ingestAnalysis.counts.merged}</p>
                        </div>
                    </div>
                </div>
            )}

            {hasTimestampNormalizationErrors && (
                 <div className="p-4 bg-red-900/50 border border-red-700 rounded-md text-red-300 text-sm">
                    <AlertTriangle className="inline w-4 h-4 mr-2" /> Es wurden Zeitstempel-Normalisierungsfehler in der Update-Datei gefunden. <a href="#timestamp-errors" className="underline">Details hier</a>
                </div>
            )}

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                    <FileBadge className="w-5 h-5"/> Duplikat-Berichte
                </h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {ingestAnalysis.reports?.baseline && (
                        <DuplicateTable 
                            report={ingestAnalysis.reports.baseline} 
                            title={`Duplikate in Baseline (${fileInfo.baseline?.name || 'N/A'})`} 
                        />
                    )}
                    {ingestAnalysis.reports?.update && (
                        <DuplicateTable 
                            report={ingestAnalysis.reports.update} 
                            title={`Duplikate in Update (${fileInfo.update?.name || 'N/A'})`} 
                        />
                    )}
                    {ingestAnalysis.reports?.comparison && (
                        <DuplicateTable 
                            report={ingestAnalysis.reports.comparison} 
                            title={`Duplikate in Zweiter Baseline (${fileInfo.secondBaseline?.name || 'N/A'})`} 
                        />
                    )}
                </div>
            </div>

            {ingestAnalysis.waste.length > 0 && (
                <WasteCenter 
                    waste={ingestAnalysis.waste}
                    onClearWaste={onClearWaste}
                />
            )}

            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                    <LineChart className="w-5 h-5"/> Metrik-Visualisierung
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                    Visualisieren Sie die Entwicklung der Einträge über die Zeit für verschiedene Datenquellen.
                </p>
                <div className="h-[500px]">
                    <AnalysisChart analysis={analysis} />
                </div>
            </div>
        </div>
    );
};

export default AnalysisPanel;

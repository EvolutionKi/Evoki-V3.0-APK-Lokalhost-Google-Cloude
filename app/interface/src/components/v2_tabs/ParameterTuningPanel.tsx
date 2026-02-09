import React, { useState, useEffect, useCallback } from 'react';
import { EvokiEngine } from './engine/EvokiEngine';
import { TunableParameters } from './engine/types';
import { SlidersHorizontal, Download, Info } from './icons';
import { offerDownload } from './download';

interface ParameterTuningPanelProps {
    evokiEngine: EvokiEngine;
}

const PARAMETER_DESCRIPTIONS: any = {
    physics: {
        _group: "Parameter der 'PhysicsEngine'. Definiert die fundamentalen Kräfte der 'Seelen-Physik', wie Anziehung, Abstoßung und Lernrate.",
        LAMBDA_R: "Gewichtung der Resonanz-Komponente (R) in der Affektwert-Berechnung (A = λ_R * R - λ_D * D). Verstärkt den positiven Einfluss relevanter Erinnerungen.",
        LAMBDA_D: "Gewichtung der Gefahren-Komponente (D). Verstärkt den negativen, abstoßenden Einfluss von Trauma-assoziierten Erinnerungen ('F'-Vektoren).",
        K_FACTOR: "Exponentieller Faktor in der Gefahren-Berechnung (D += e^(-K * distanz)). Ein höherer Wert lässt die 'Gefahr' bei Annäherung an einen 'F'-Vektor schneller ansteigen.",
        B_VECTOR_LEARNING_RATE: "Lernrate für die Anpassung des B-Vektors (A50.1). Bestimmt, wie schnell das System durch Feedback lernt und sich an den Nutzer anpasst."
    },
    metrics: {
        _group: "Parameter der 'MetricsService'. Steuert die Berechnung und Gewichtung der über 60 Metriken aus der V11.1 Registry.",
        tau_s: "Zeitkonstante für die 'Flow'-Metrik (in Sekunden). Ein höherer Wert bedeutet, dass der 'Gesprächsfluss' nach einer Pause langsamer abnimmt.",
        readiness_bias: "Negativer Bias in der Sigmoid-Funktion für 'EV_readiness'. Das System benötigt signifikant mehr positive Resonanz als negative Spannung, um 'bereit' für eine Weiterentwicklung zu sein.",
        lambda_risk: "Gewichtungsfaktor für das Risiko (R) in der finalen Nutzen-Risiko-Bewertung (Φ-Score = U - λ * R). Ein höherer Wert bestraft riskante Zustände stärker.",
        epsilon_z: "Schwellenwert für 'dist_z' (Sicherheitsabstand zum Kollaps). Unterschreitet die Distanz diesen Wert, löst der Wächter ('guardian_trip') aus.",
        turbidity: {
            _group: "Parameter für die 'Emotionale Trübung' (T_fog), basierend auf dem Lambert-Beer-Gesetz. Simuliert, wie Stressfaktoren die 'Klarheit' des Systems reduzieren.",
            weights: {
                _group: "Gewichtung der einzelnen Faktoren, die zur 'Konzentration' (c) der Trübung beitragen.",
                panic: "Gewicht des Panik-Indikators (T_panic).",
                disso: "Gewicht des Dissoziations-Indikators (T_disso).",
                ninteg: "Gewicht der fehlenden Integration (1 - T_integ).",
                ll: "Gewicht des Low-Level-Loopings (LL).",
                zlf: "Gewicht des Zero-Level-Feedbacks (ZLF).",
                conf: "Gewicht des Regel-Konflikts (rule_conflict)."
            },
            L0: "Basis-Weglänge für die Trübungsberechnung. Normalisiert die Nachrichtenlänge.",
            k_time: "Faktor, wie stark die Zeitlücke ('gap_s') die Weglänge (ℓ) der Trübung erhöht.",
            k_depth: "Faktor, wie stark die 'Gedankentiefe' ('lambda_depth') die Weglänge (ℓ) der Trübung erhöht.",
            eps0: "Basis-Absorptionskoeffizient (ε) für die Trübungsformel. Höher = stärkere Trübung.",
            mu_hp: "Modifikator für ε, wenn der Hohepriester-Modus aktiv ist.",
            mu_guard: "Modifikator für ε, wenn der Wächter ausgelöst hat.",
            rho1: "Gewichtungsfaktor, mit dem die Trübung (T_fog) das Risiko im erweiterten Φ-Score (R2) erhöht."
        },
        grav: {
            _group: "Parameter für das Gravitations-Modell. Simuliert die Anziehungskraft von semantischen 'Phasen-Zentren' auf die aktuelle Konversation.",
            eta1: "Gewichtungsfaktor, mit dem die normalisierte Gravitations-Anziehung (G_phase_norm) den Nutzen im erweiterten Φ-Score (U2) erhöht.",
            G0: "Basis-Gravitationskonstante in der Formel für die Gravitations-Anziehung (G_phase).",
            gamma: "Exponent für die Kosinus-Ähnlichkeit in der Gravitations-Formel. Verstärkt den Einfluss der Ähnlichkeit.",
            beta: "Exponent für die Distanz in der Gravitations-Formel. Verstärkt den Einfluss der Distanz (1 - Ähnlichkeit).",
            delta: "Glättungskonstante im Nenner der Gravitations-Formel, um Division durch Null zu vermeiden."
        }
    }
};


const ParameterTuningPanel: React.FC<ParameterTuningPanelProps> = ({ evokiEngine }) => {
    const [params, setParams] = useState<TunableParameters | null>(null);

    useEffect(() => {
        // Initial parameters from the engine instance
        setParams(evokiEngine.getTunableParameters());
    }, [evokiEngine]);

    const handleParamChange = (path: string, value: number) => {
        setParams(prevParams => {
            if (!prevParams) return null;

            // Deep clone to avoid mutation
            const newParams = JSON.parse(JSON.stringify(prevParams));
            
            // Navigate path and set value
            const keys = path.split('.');
            let current: any = newParams;
            for (let i = 0; i < keys.length - 1; i++) {
                current = current[keys[i]];
            }
            current[keys[keys.length - 1]] = value;
            
            // Update the engine instance live
            evokiEngine.updateTunableParameters(newParams);

            return newParams;
        });
    };

    const handleExport = () => {
        if (!params) return;

        let content = `# Evoki Engine - Parameter Export (${new Date().toISOString()})\n\n`;
        
        const formatObject = (obj: any, prefix = ''): string => {
            let text = '';
            for (const key in obj) {
                const value = obj[key];
                const newPrefix = prefix ? `${prefix}.${key}` : key;
                if (typeof value === 'object' && value !== null) {
                    text += formatObject(value, newPrefix);
                } else {
                    text += `${newPrefix}: ${value}\n`;
                }
            }
            return text;
        };

        content += formatObject(params);
        
        const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
        offerDownload(blob, `evoki_params_${new Date().toISOString().replace(/:/g, '-')}.txt`);
    };

    const renderParams = (data: any, descriptions: any, pathPrefix = ''): React.ReactNode[] => {
        const nodes: React.ReactNode[] = [];
        for (const key in data) {
            if (key === '_group') continue; // Skip description key

            const value = data[key];
            const currentPath = pathPrefix ? `${pathPrefix}.${key}` : key;
            const descriptionData = descriptions ? descriptions[key] : undefined;
            
            if (typeof value === 'object' && value !== null) {
                const groupDescription = descriptionData?._group;
                nodes.push(
                    <div key={currentPath} className="mt-6 first:mt-0 col-span-1 sm:col-span-2 lg:col-span-3">
                        <h4 className="text-lg font-semibold text-blue-400 capitalize mb-2 border-b border-gray-600 pb-1">{key.replace(/_/g, ' ')}</h4>
                        {groupDescription && <p className="text-sm text-gray-400 mb-4">{groupDescription}</p>}
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4 pl-4 border-l-2 border-gray-700">
                            {renderParams(value, descriptionData, currentPath)}
                        </div>
                    </div>
                );
            } else if (typeof value === 'number') {
                const paramDescription = descriptionData;
                nodes.push(
                    <div key={currentPath}>
                        <label htmlFor={currentPath} className="text-sm text-gray-300 block font-medium">{key}</label>
                        {paramDescription && <p className="text-xs text-gray-500 mt-1 mb-2">{paramDescription}</p>}
                        <input
                            type="number"
                            id={currentPath}
                            value={value}
                            onChange={(e) => handleParamChange(currentPath, parseFloat(e.target.value) || 0)}
                            step={Math.abs(value) > 0 && Math.abs(value) < 1 ? 0.01 : (Math.abs(value) > 100 ? 10 : 1) }
                            className="w-full bg-gray-700 border border-gray-600 rounded-md p-2 text-white font-mono"
                        />
                    </div>
                );
            }
        }
        return nodes;
    };


    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-3">
                        <SlidersHorizontal className="w-7 h-7 text-blue-400" /> Metrik- & Parameter-Tuning
                    </h2>
                    <p className="text-gray-400 max-w-3xl">
                        Passen Sie die Schwellenwerte und Konstanten der Evoki-Engine live an. Änderungen wirken sich sofort auf die Berechnungen im Chatbot-Tab aus und gelten nur für die aktuelle Sitzung.
                    </p>
                </div>
                <button
                    onClick={handleExport}
                    disabled={!params}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md transition-colors disabled:bg-gray-600"
                >
                    <Download className="w-5 h-5" />
                    Parameter als .txt exportieren
                </button>
            </div>
            
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                {!params ? (
                    <p className="text-gray-400">Lade Parameter...</p>
                ) : (
                    <div className="space-y-6">
                        {renderParams(params, PARAMETER_DESCRIPTIONS)}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ParameterTuningPanel;

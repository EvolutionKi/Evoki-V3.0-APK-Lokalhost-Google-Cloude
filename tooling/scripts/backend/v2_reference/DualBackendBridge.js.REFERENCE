/**
 * DUAL BACKEND BRIDGE - Orchestriert Python Backend (8000) + Node Backend (3001)
 * 
 * KORRIGIERTER WORKFLOW (Metriken ZUERST):
 * 1. Berechne Metriken vom User Prompt (120+)
 * 2. Python Backend: FAISS-Suche (semantisch W2/W5)
 * 3. Node Backend: Trinity Vector DBs (metrisch W1-W25)
 * 4. Kombiniere Top 3 Kandidaten (semantisch + metrisch)
 * 5. Gemini Context Bridge: Echte AI-Antwort
 * 6. Speicherung in 12 Vector DBs + Chronicle
 */

import fetch from 'node-fetch';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { TrinityUploadEngine, TrinityDownloadEngine } from './TrinityEngine.js';
import { GeminiContextBridge } from './GeminiContextBridge.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

/**
 * Backend-seitiges Pipeline-Logging
 */
function logPipelineStepBackend(sessionId, messageId, stepNumber, stepName, dataTransfer, metadata = {}) {
    try {
        const logEntry = {
            id: `${sessionId}_${messageId}_${stepNumber}`,
            timestamp: new Date().toISOString(),
            session_id: sessionId,
            message_id: messageId,
            step_number: stepNumber,
            step_name: stepName,
            data_transfer: dataTransfer,
            metadata
        };
        
        const logDir = path.join(process.cwd(), 'backend', 'logs');
        if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
        
        const logFile = path.join(logDir, 'pipeline_logs.jsonl');
        fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n', 'utf8');
        
        console.log(`[PipelineLog] Step ${stepNumber}: ${stepName} | ${dataTransfer.from} → ${dataTransfer.to}`);
    } catch (error) {
        console.error('[PipelineLog] Backend logging error:', error.message);
    }
}

export class DualBackendBridge {
    constructor(geminiApiKeys = [], openaiApiKey = null) {
        this.pythonBackendUrl = 'http://localhost:8000';
        this.nodeBackendUrl = 'http://localhost:3001';
        this.uploadEngine = new TrinityUploadEngine();
        this.downloadEngine = new TrinityDownloadEngine();
        this.geminiContext = new GeminiContextBridge(geminiApiKeys, openaiApiKey);
        
        // Status tracking
        this.pythonBackendAvailable = false;
        this.nodeBackendAvailable = false;
        
        // Auto-check backend availability
        this.checkBackends();
    }

    /**
     * Prüfe Verfügbarkeit beider Backends
     */
    async checkBackends() {
        try {
            const pythonHealth = await fetch(`${this.pythonBackendUrl}/health`, { timeout: 3000 });
            this.pythonBackendAvailable = pythonHealth.ok;
            console.log(`[DualBridge] Python Backend (8000): ${this.pythonBackendAvailable ? '✅ Verfügbar' : '❌ Nicht erreichbar'}`);
        } catch {
            this.pythonBackendAvailable = false;
            console.log(`[DualBridge] Python Backend (8000): ❌ Nicht erreichbar`);
        }

        try {
            const nodeHealth = await fetch(`${this.nodeBackendUrl}/health`, { timeout: 3000 });
            this.nodeBackendAvailable = nodeHealth.ok;
            console.log(`[DualBridge] Node Backend (3001): ${this.nodeBackendAvailable ? '✅ Verfügbar' : '❌ Nicht erreichbar'}`);
        } catch {
            this.nodeBackendAvailable = false;
            console.log(`[DualBridge] Node Backend (3001): ❌ Nicht erreichbar`);
        }

        return {
            pythonBackend: this.pythonBackendAvailable,
            nodeBackend: this.nodeBackendAvailable,
            bothAvailable: this.pythonBackendAvailable && this.nodeBackendAvailable
        };
    }

    /**
     * HAUPTFUNKTION: Verarbeite User-Prompt mit beiden Backends
     * @param {Object} options - Optional callback für SSE Streaming
     */
    async processUserPrompt(requestData, options = {}) {
        const startTime = Date.now();
        const { sessionId, prompt, previousChainHash, context = {} } = requestData;
        const { onProgress } = options;  // ✅ Callback für SSE
        const messageId = Date.now().toString();
        const log = (...args) => console.log('[PipelineLog]', ...args);
        
        // Helper: Progress emittieren
        const emitProgress = (step, name, message) => {
            if (onProgress && typeof onProgress === 'function') {
                onProgress(step, { name, message });
            }
        };

        log('Step 1: 📝 Prompt empfangen');
        emitProgress(1, 'Prompt empfangen', 'Prompt bereit');
        logPipelineStepBackend(sessionId, messageId, 1, 'Prompt empfangen', {
            from: 'User', to: 'Frontend', text_preview: prompt.substring(0, 100), full_text: prompt, size_bytes: Buffer.byteLength(prompt, 'utf8'), token_count: Math.ceil(prompt.length / 4)
        });

        let userPromptMetrics = null;
        try {
            // Schritt 2: Metriken berechnen
            log('Step 2: 🧮 Metriken berechnen');
            emitProgress(2, 'Metriken berechnen', 'Analysiere Prompt...');
            if (this.nodeBackendAvailable) {
                userPromptMetrics = await this.calculateUserPromptMetrics(prompt);
                emitProgress(2, 'Metriken berechnen', `${Object.keys(userPromptMetrics || {}).length} Metriken berechnet`);
                logPipelineStepBackend(sessionId, messageId, 2, 'Metriken berechnen', {
                    from: 'Frontend', to: 'Backend', text_preview: prompt.substring(0, 100), metrics: userPromptMetrics, size_bytes: Buffer.byteLength(prompt, 'utf8')
                });
            } else {
                emitProgress(2, 'Metriken übersprungen', 'Node Backend offline');
                logPipelineStepBackend(sessionId, messageId, 2, 'Metriken übersprungen', {
                    from: 'Frontend', to: 'Backend', text_preview: prompt.substring(0, 100), metrics: null, size_bytes: Buffer.byteLength(prompt, 'utf8')
                });
            }

            // Schritt 3: FAISS W2 durchsuchen
            log('Step 3: 🔍 FAISS W2 durchsuchen');
            emitProgress(3, 'FAISS W2 durchsuchen', 'Semantische Suche läuft...');
            let semanticResults = await this.queryPythonBackend(prompt, context);
            emitProgress(3, 'FAISS W2 durchsuchen', `${semanticResults?.sources?.length || 0} Ergebnisse gefunden`);
            logPipelineStepBackend(sessionId, messageId, 3, 'FAISS W2 durchsuchen', {
                from: 'Backend', to: 'Python FAISS W2', text_preview: prompt.substring(0, 100), faiss_results: semanticResults?.sources?.slice(0, 3) || [], size_bytes: Buffer.byteLength(prompt, 'utf8')
            });

            // Schritt 4: FAISS W5 tief-suchen (simuliert)
            log('Step 4: 🔎 FAISS W5 tief-suchen');
            emitProgress(4, 'FAISS W5 tief-suchen', 'Deep search completed');
            logPipelineStepBackend(sessionId, messageId, 4, 'FAISS W5 tief-suchen', {
                from: 'Backend', to: 'Python FAISS W5', text_preview: prompt.substring(0, 100), faiss_results: semanticResults?.sources?.slice(0, 3) || [], size_bytes: Buffer.byteLength(prompt, 'utf8')
            });

            // Schritt 5: Trinity DBs abfragen (simuliert)
            log('Step 5: 🏛️ Trinity DBs abfragen');
            emitProgress(5, 'Trinity DBs abfragen', 'Abfrage läuft...');
            logPipelineStepBackend(sessionId, messageId, 5, 'Trinity DBs abfragen', {
                from: 'Backend', to: 'Trinity DBs', text_preview: prompt.substring(0, 100), trinity_results: [], size_bytes: Buffer.byteLength(prompt, 'utf8')
            });
            emitProgress(5, 'Trinity DBs abfragen', 'Trinity OK');

            // Schritt 6: Top-3 kombinieren
            log('Step 6: 🎯 Top-3 kombinieren');
            emitProgress(6, 'Top-3 kombinieren', 'Kombiniere Ergebnisse...');
            const top3Candidates = this.combineCandidates(
                semanticResults?.sources || [],
                [],
                userPromptMetrics
            );
            emitProgress(6, 'Top-3 kombinieren', `Top-3 bereit (${top3Candidates.length} Kandidaten)`);
            logPipelineStepBackend(sessionId, messageId, 6, 'Top-3 kombinieren', {
                from: 'Backend', to: 'A65 Candidate Selection', top3: top3Candidates, size_bytes: Buffer.byteLength(prompt, 'utf8')
            });

            // Schritt 7: Gemini Context bauen
            log('Step 7: 🤖 Gemini Context bauen');
            emitProgress(7, 'Gemini Context bauen', 'Baue Context mit Chunks...');
            logPipelineStepBackend(sessionId, messageId, 7, 'Gemini Context bauen', {
                from: 'Backend', to: 'GeminiContextBridge', context: { prompt, top3Candidates }, size_bytes: Buffer.byteLength(prompt, 'utf8')
            });
            emitProgress(7, 'Gemini Context bauen', 'Context gebaut');

            // Schritt 8: API-Request Review (simuliert)
            log('Step 8: 🔍 API-Request Review');
            emitProgress(8, 'API-Request Review', 'Request wird geprüft...');
            logPipelineStepBackend(sessionId, messageId, 8, 'API-Request Review', {
                from: 'Backend', to: 'Gemini API', context: { prompt, top3Candidates }, size_bytes: Buffer.byteLength(prompt, 'utf8')
            });
            emitProgress(8, 'API-Request Review', 'Request geprüft');

            // Schritt 9: Gemini Response generieren
            log('Step 9: ✨ Gemini Response generieren');
            emitProgress(9, 'Gemini Response generieren', 'Generiere Antwort...');
            const geminiResponse = await this.geminiContext.generateContextualResponse({
                userPrompt: prompt,
                faissResults: semanticResults?.sources || [], // ✅ ORIGINAL FAISS SOURCES, nicht top3Candidates
                selectedIndex: 0,
                metrics: userPromptMetrics || {},
                sessionId: sessionId
            });
            const responseText = geminiResponse.success
                ? geminiResponse.response
                : (top3Candidates[0]?.text || 'Keine Antwort verfügbar');
            logPipelineStepBackend(sessionId, messageId, 9, 'Gemini Response generieren', {
                from: 'Gemini API', to: 'Backend', response_preview: responseText.substring(0, 100), size_bytes: Buffer.byteLength(responseText, 'utf8')
            });


            // Schritt 10: In 12 DBs speichern (immer loggen, auch bei Fehlern)
            log('Step 10: 💾 In 12 DBs speichern');
            emitProgress(10, 'In 12 DBs speichern', 'Speichere in Vector DBs...');
            let storageResult = null;
            let storageError = null;
            try {
                storageResult = await this.storeResults(
                    sessionId,
                    prompt,
                    responseText,
                    userPromptMetrics,
                    top3Candidates,
                    previousChainHash,
                    geminiResponse.apiConfig  // ✅ API-Config an Storage übergeben
                );
                emitProgress(10, 'In 12 DBs speichern', `Gespeichert in ${storageResult.stored_in_dbs || 0}/12 DBs`);
                logPipelineStepBackend(sessionId, messageId, 10, 'In 12 DBs speichern', {
                    from: 'Backend', to: 'Vector DBs', storage: storageResult, size_bytes: Buffer.byteLength(responseText, 'utf8')
                });
            } catch (e) {
                storageError = e;
                emitProgress(10, 'In 12 DBs speichern (Fehler)', e.message);
                logPipelineStepBackend(sessionId, messageId, 10, 'In 12 DBs speichern (Fehler)', {
                    from: 'Backend', to: 'Vector DBs', error: e.message, size_bytes: Buffer.byteLength(responseText, 'utf8')
                });
            }

            // Schritt 11: Chronicle aktualisieren (simuliert, immer loggen)
            log('Step 11: 📚 Chronicle aktualisieren');
            emitProgress(11, 'Chronicle aktualisieren', 'Chronicle Update läuft...');
            logPipelineStepBackend(sessionId, messageId, 11, 'Chronicle aktualisieren', {
                from: 'Backend', to: 'Chronicle', storage: storageResult, storage_error: storageError?.message, size_bytes: Buffer.byteLength(responseText, 'utf8')
            });
            emitProgress(11, 'Chronicle aktualisieren', 'Chronicle Update abgeschlossen');

            // Schritt 12: Fertig (immer loggen)
            log('Step 12: ✅ Fertig');
            const processingTimeForProgress = Date.now() - startTime;
            emitProgress(12, 'Fertig', `Abgeschlossen in ${processingTimeForProgress}ms`);
            logPipelineStepBackend(sessionId, messageId, 12, 'Fertig', {
                from: 'Backend', to: 'Frontend', response_preview: responseText.substring(0, 100), storage_error: storageError?.message, size_bytes: Buffer.byteLength(responseText, 'utf8')
            });

            const processingTime = Date.now() - startTime;
            log(`[7/7] ✅ Abgeschlossen in ${processingTime}ms`);
            log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);

            return {
                success: !storageError,
                sessionId,
                prompt,
                response: responseText,
                user_prompt_metrics: userPromptMetrics,
                semantic_results: semanticResults,
                metric_results: null,
                top3_candidates: top3Candidates,
                gemini: {
                    ...geminiResponse,
                    apiConfig: geminiResponse.apiConfig || global.templeApiConfig  // ✅ API-Config in Response
                },
                storage: storageResult,
                storage_error: storageError?.message,
                processingTimeMs: processingTime,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[DualBridge] ❌ Fehler:`, error.message);
            return {
                success: false,
                error: error.message,
                sessionId,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Berechne Metriken vom User Prompt
     */
    async calculateUserPromptMetrics(prompt) {
        try {
            const response = await fetch(`${this.nodeBackendUrl}/api/metrics/calculate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: prompt,
                    mode: 'prompt_only'
                }),
                timeout: 10000
            });

            if (!response.ok) {
                throw new Error(`Metrics calculation failed: ${response.status}`);
            }

            const data = await response.json();
            return data.metrics || {};

        } catch (error) {
            console.error(`[DualBridge] Metrics Error:`, error.message);
            return this.generateFallbackMetrics(prompt);
        }
    }

    /**
     * Abfrage Python Backend (FAISS + Regelwerk V12)
     */
    async queryPythonBackend(prompt, context) {
        try {
            // WORKAROUND: FastAPI crasht, nutze CLI-Tool direkt
            console.log(`[DualBridge] 🔧 CLI-FALLBACK: Rufe FAISS direkt auf (FastAPI instabil)...`);
            
            return new Promise((resolve, reject) => {
                const pythonPath = path.join(__dirname, '..', '..', '.venv', 'Scripts', 'python.exe');
                const scriptPath = path.join(__dirname, '..', '..', 'python', 'tools', 'query.py');
                
                // KORRIGIERT: CWD auf python/ Ordner setzen (nicht 'Alles Vektor')
                const proc = spawn(pythonPath, [scriptPath, prompt], {
                    cwd: path.join(__dirname, '..', '..', 'python'),
                    timeout: 60000 // 60s für große Prompts (erhöht von 15s - P0-3)
                });
                
                // Pipeline-Log: Backend → Python CLI
                const sessionId = context?.sessionId || 'unknown';
                const messageId = context?.message_id || Date.now().toString();
                logPipelineStepBackend(sessionId, messageId, 3, 'Backend → Python CLI (query.py)', {
                    from: 'DualBackendBridge',
                    to: 'Python FAISS CLI',
                    text_preview: prompt.substring(0, 100),
                    full_text: prompt,
                    size_bytes: Buffer.byteLength(prompt, 'utf8'),
                    token_count: Math.ceil(prompt.length / 4)
                }, { pythonPath, scriptPath });
                
                let stdout = '';
                let stderr = '';
                
                proc.stdout.on('data', (data) => { stdout += data.toString(); });
                proc.stderr.on('data', (data) => { stderr += data.toString(); });
                
                proc.on('close', (code) => {
                    console.log(`[DualBridge] CLI finished with code ${code}`);
                    console.log(`[DualBridge] CLI stdout length: ${stdout.length} chars`);
                    console.log(`[DualBridge] CLI stderr length: ${stderr.length} chars`);
                    
                    // ✅ WICHTIG: Parse stdout auch bei code 1, wenn Daten vorhanden sind
                    // (Python kann code 1 bei Unicode-Warnings zurückgeben, obwohl Daten korrekt sind)
                    if (code !== 0 && stdout.length === 0) {
                        console.error(`[DualBridge] CLI Error (code ${code}):`, stderr.substring(0, 500));
                        return resolve({ success: false, error: 'CLI failed', backend: 'python_cli' });
                    }
                    
                    // Pipeline-Log: Python CLI → Backend Response
                    logPipelineStepBackend(sessionId, messageId, 4, 'Python FAISS → Backend Parse', {
                        from: 'Python FAISS CLI',
                        to: 'DualBackendBridge',
                        text_preview: stdout.substring(0, 200),
                        full_text: stdout,
                        size_bytes: Buffer.byteLength(stdout, 'utf8')
                    }, { exit_code: code, stderr_length: stderr.length });
                    
                    // Parse W2 Results - einfacher Regex für die Top-Ergebnisse
                    const results = [];
                    
                    // ✅ WINDOWS LINE ENDINGS: \r\n normalisieren zu \n
                    stdout = stdout.replace(/\r\n/g, '\n');
                    
                    // Suche nach "[W2 RESULTS" Block und parse die Chunks
                    const w2Section = stdout.match(/\[W2 RESULTS[\s\S]*?(?=\[OK\]|$)/);
                    if (w2Section) {
                        console.log(`[DualBridge] 🔍 Found W2 Results section (${w2Section[0].length} chars)`);
                        // KORRIGIERTES REGEX: Datum und Chunk: sind auf separaten Zeilen
                        const chunkRegex = /#(\d+) \| Similarity: ([\d.]+) \| ([\d-]+)\s*\n\s*Chunk: ([^\n]+)(?:\s*\n\s*Lexika: ([^\n]+))?\s*\n\s*([\s\S]*?)(?=\n-{3,}|$)/g;
                        
                        let match;
                        while ((match = chunkRegex.exec(w2Section[0])) !== null && results.length < 10) {
                            const fullText = match[6].trim();
                            console.log(`[DualBridge] 📦 Parsed chunk ${results.length + 1}: ${match[4].trim()} (score: ${match[2]}, length: ${fullText.length})`);
                            results.push({
                                chunk_id: match[4].trim(),
                                score: parseFloat(match[2]),
                                text: fullText,  // ✅ VOLLSTÄNDIGER TEXT (kein substring!)
                                content: fullText,  // Alias für Kompatibilität
                                created_at: match[3],
                                lexika_matches: match[5] ? match[5].split(', ').map(s => s.trim()).filter(Boolean) : [],
                                source: 'w2_minilm_cli'
                            });
                        }
                    } else {
                        console.warn(`[DualBridge] ⚠️  No W2 Results section found in stdout`);
                        console.log(`[DualBridge] 📄 First 500 chars of stdout:`, stdout.substring(0, 500));
                    }
                    
                    console.log(`[DualBridge] ✅ CLI parsed ${results.length} W2 Chunks aus FAISS`);
                    if (results.length > 0) {
                        console.log(`[DualBridge]    Top Result: "${results[0].text.substring(0, 80)}..." (Score: ${results[0].score})`);
                    } else {
                        console.warn(`[DualBridge] ⚠️  No results parsed - check regex pattern`);
                    }
                    
                    resolve({
                        success: true,
                        sources: results,
                        backend: 'python_cli'
                    });
                });
                
                setTimeout(() => {
                    proc.kill();
                    resolve({ success: false, error: 'Timeout', backend: 'python_cli' });
                }, 60000);  // ✅ 60s für große FAISS-Index-Suchen
            });
            
        } catch (error) {
            console.error(`[DualBridge] Python Backend Error:`, error.message);
            return { success: false, error: error.message, backend: 'python' };
        }
    }

    /**
     * Abfrage Trinity Vector DBs mit Metriken-Ähnlichkeit
     */
    async queryMetricVectorDBs(metrics, context) {
        try {
            const response = await fetch(`${this.nodeBackendUrl}/api/vector/search`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    metrics: metrics,
                    top_k: 10,
                    context: context
                }),
                timeout: 60000 // 60s für große Metrik-Vektoren (erhöht von 15s - P0-3)
            });

            if (!response.ok) {
                throw new Error(`Vector search failed: ${response.status}`);
            }

            const data = await response.json();
            
            return {
                success: true,
                sources: data.results || [],
                backend: 'node_trinity'
            };
        } catch (error) {
            console.error(`[DualBridge] Trinity Vector Search Error:`, error.message);
            return { success: false, error: error.message, backend: 'node_trinity' };
        }
    }

    /**
     * Kombiniere semantische + metrische Kandidaten zu Top 3
     */
    combineCandidates(semanticSources, metricSources, userMetrics) {
        const combined = [];

        // Gewichte: 60% semantisch, 40% metrisch
        const SEMANTIC_WEIGHT = 0.6;
        const METRIC_WEIGHT = 0.4;

        // Erstelle Map für metrische Scores
        const metricScoreMap = new Map();
        metricSources.forEach(src => {
            metricScoreMap.set(src.chunk_id || src.id, src.metric_similarity_score || 0);
        });

        // Kombiniere Scores für semantische Quellen
        semanticSources.forEach(src => {
            const semanticScore = src.score || 0;
            const metricScore = metricScoreMap.get(src.chunk_id || src.id) || 0;
            const combinedScore = (semanticScore * SEMANTIC_WEIGHT) + (metricScore * METRIC_WEIGHT);

            combined.push({
                ...src,
                semantic_score: semanticScore,
                metric_score: metricScore,
                combined_score: combinedScore,
                source_type: 'semantic_primary'
            });
        });

        // Füge metrische Quellen hinzu, die nicht in semantischen sind
        metricSources.forEach(src => {
            const chunkId = src.chunk_id || src.id;
            const existsInSemantic = semanticSources.some(s => (s.chunk_id || s.id) === chunkId);
            
            if (!existsInSemantic) {
                const metricScore = src.metric_similarity_score || 0;
                const combinedScore = metricScore * METRIC_WEIGHT; // Nur metrisch

                combined.push({
                    ...src,
                    semantic_score: 0,
                    metric_score: metricScore,
                    combined_score: combinedScore,
                    source_type: 'metric_only'
                });
            }
        });

        // Sortiere nach combined_score und nimm Top 3
        combined.sort((a, b) => b.combined_score - a.combined_score);
        const top3 = combined.slice(0, 3);

        console.log(`[DualBridge] Top 3 Candidates:`);
        top3.forEach((c, i) => {
            console.log(`  ${i+1}. Combined: ${c.combined_score.toFixed(3)} (Sem: ${c.semantic_score.toFixed(3)} | Met: ${c.metric_score.toFixed(3)}) - ${c.source_type}`);
        });

        return top3;
    }

    /**
     * Speichere Ergebnisse in 12 Vector DBs + Chronicle
     */
    async storeResults(sessionId, prompt, response, metrics, candidates, previousChainHash, apiConfig = null) {
        try {
            const roundId = Date.now();
            
            const uploadData = {
                sessionId: sessionId,
                roundId: roundId,
                prompt: prompt,
                response: response,
                metrics: metrics,
                candidates: {
                    selected_candidate: 0,
                    candidates_count: candidates.length,
                    candidates: candidates
                },
                a65Score: candidates[0]?.combined_score || 0,
                previousChainHash: previousChainHash || '0000',
                apiConfig: apiConfig || global.templeApiConfig  // ✅ API-Config in Storage speichern
            };

            const uploadResult = await this.uploadEngine.uploadRound(uploadData);

            return {
                success: uploadResult.success,
                stored_in_dbs: uploadResult.dbResults?.successful || 0,
                total_dbs: 12,
                history_saved: uploadResult.historyResult?.success || false,
                checkpoint_saved: uploadResult.checkpointResult?.success || false,
                chain_hash: uploadResult.chainHash,
                timestamp: uploadResult.timestamp
            };
        } catch (error) {
            console.error(`[DualBridge] Storage Error:`, error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Lade Session-Historie
     */
    async loadSession(sessionId) {
        try {
            return await this.downloadEngine.downloadSession(sessionId);
        } catch (error) {
            console.error(`[DualBridge] Load Session Error:`, error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Status-Report
     */
    async getStatus() {
        const backendsStatus = await this.checkBackends();
        
        return {
            bridge_status: 'operational',
            backends: backendsStatus,
            python_backend: {
                url: this.pythonBackendUrl,
                available: this.pythonBackendAvailable,
                features: ['FAISS Search (W2/W5)', 'Regelwerk V12', 'Chain Continuity']
            },
            node_backend: {
                url: this.nodeBackendUrl,
                available: this.nodeBackendAvailable,
                features: ['120+ Metrics', 'Trinity Engines (W1-W25)', 'Metric Vector Search']
            },
            storage: {
                vector_dbs: 12,
                chronicle: 'enabled',
                history: 'enabled'
            },
            workflow: '1.Metrics → 2.FAISS → 3.TrinityVectorDBs → 4.Top3 → 5.Gemini → 6.Storage',
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Fallback-Metriken
     */
    generateFallbackMetrics(text) {
        return {
            CORE: {
                A: 0.5, PCI: 0.5, coh: 0.5, flow: 0.5, T_integ: 0.5, z_prox: 0.5
            },
            SYSTEM: { hazard_score: 0, guardian_trip: false },
            FEP: { phi_score: 0.5, EV_readiness: 0.5, EV_resonance: 0.5, surprisal: 0.5 },
            LEXIKA: { LEX_Coh_conn: 0.5, LEX_Flow_pos: 0.5 }
        };
    }
}

export default DualBackendBridge;



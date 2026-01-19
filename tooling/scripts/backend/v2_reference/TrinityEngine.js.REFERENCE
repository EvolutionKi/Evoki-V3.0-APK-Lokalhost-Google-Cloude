/**
 * TRINITY ENGINE - Advanced Dual-API Orchestration & Storage Pipeline
 * 
 * TrinityUploadEngine: Nimmt Daten an, reichert an, speichert in 12 DBs + Historie
 * TrinityDownloadEngine: Lädt Daten, verteilt an Chat-UI + History-Files
 * API-Verflechtung: Gemini ↔ OpenAI wie ein Reißverschluss
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ===== TRINITY UPLOAD ENGINE =====
// Speichert die Ergebnisse mit Metriken in alle 12 DBs und Volltext-Historie

class TrinityUploadEngine {
    constructor(baseDir = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL') {
        this.baseDir = baseDir;
        this.templesDir = path.join(baseDir, 'tempel');
        this.trialogDir = path.join(baseDir, 'trialog');
        this.historyDir = path.join(baseDir, 'history');
        
        // Stelle sicher, dass Verzeichnisse existieren
        [this.templesDir, this.trialogDir, this.historyDir].forEach(dir => {
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
        });
    }

    /**
     * Main Upload: Nimmt einen Request auf und speichert überall
     * @param {object} uploadData - { sessionId, prompt, response, metrics, candidates, a65Score, chainHash }
     */
    async uploadRound(uploadData) {
        try {
            const {
                sessionId,
                roundId,
                prompt,
                response,
                metrics,
                candidates,
                a65Score,
                previousChainHash
            } = uploadData;

            const timestamp = new Date().toISOString();
            const newChainHash = this.computeChainHash(previousChainHash, response);

            console.log(`[TrinityUpload] Starting round ${roundId} | Session: ${sessionId}`);

            // 1. Speichere in ALLE 12 Vektor-DBs parallel
            const dbResults = await this.distributeAcross12DBs(
                sessionId,
                roundId,
                prompt,
                response,
                metrics,
                timestamp
            );

            // 2. Speichere Volltext-Historie
            const historyResult = await this.saveFullHistory(
                sessionId,
                roundId,
                prompt,
                response,
                metrics,
                candidates,
                a65Score,
                newChainHash,
                timestamp
            );

            // 3. Speichere Session-Checkpoint
            const checkpointResult = await this.saveSessionCheckpoint(
                sessionId,
                roundId,
                newChainHash,
                timestamp
            );

            console.log(`[TrinityUpload] ✅ Round ${roundId} complete`);
            console.log(`  - 12 DBs: ${dbResults.successful}/${dbResults.total} erfolgreich`);
            console.log(`  - History: ${historyResult.success}`);
            console.log(`  - Checkpoint: ${checkpointResult.success}`);

            return {
                success: true,
                sessionId,
                roundId,
                chainHash: newChainHash,
                dbResults,
                historyResult,
                checkpointResult,
                timestamp
            };
        } catch (error) {
            console.error('[TrinityUpload] Error:', error.message);
            return {
                success: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Verteile Daten auf alle 12 DBs mit entsprechenden Metriken-Windows
     */
    async distributeAcross12DBs(sessionId, roundId, prompt, response, metrics, timestamp) {
        const dbConfigs = {
            'tempel_W_m1': { dir: path.join(this.templesDir, 'tempel_W_m1'), offset: -1 },
            'tempel_W_m2': { dir: path.join(this.templesDir, 'tempel_W_m2'), offset: -2 },
            'tempel_W_m5': { dir: path.join(this.templesDir, 'tempel_W_m5'), offset: -5 },
            'tempel_W_m25': { dir: path.join(this.templesDir, 'tempel_W_m25'), offset: -25 },
            'tempel_W_p1': { dir: path.join(this.templesDir, 'tempel_W_p1'), offset: 1 },
            'tempel_W_p2': { dir: path.join(this.templesDir, 'tempel_W_p2'), offset: 2 },
            'tempel_W_p5': { dir: path.join(this.templesDir, 'tempel_W_p5'), offset: 5 },
            'tempel_W_p25': { dir: path.join(this.templesDir, 'tempel_W_p25'), offset: 25 },
            'trialog_W_m1': { dir: path.join(this.trialogDir, 'trialog_W_m1'), offset: -1 },
            'trialog_W_m2': { dir: path.join(this.trialogDir, 'trialog_W_m2'), offset: -2 },
            'trialog_W_m5': { dir: path.join(this.trialogDir, 'trialog_W_m5'), offset: -5 },
            'trialog_W_p25': { dir: path.join(this.trialogDir, 'trialog_W_p25'), offset: 25 }
        };

        const entries = [];
        for (const [dbName, cfg] of Object.entries(dbConfigs)) {
            if (!fs.existsSync(cfg.dir)) fs.mkdirSync(cfg.dir, { recursive: true });

            const entry = {
                chunk_id: `${sessionId}_${roundId}_${dbName}`,
                session_id: sessionId,
                round_id: roundId,
                timestamp: timestamp,
                window_type: dbName,
                window_offset: cfg.offset,
                content_user: prompt.substring(0, 1000),
                content_agent: response.substring(0, 1000),
                
                // Denormalisierte 17 Hauptmetriken
                A: metrics?.CORE?.A ?? 0,
                PCI: metrics?.CORE?.PCI ?? 0,
                coh: metrics?.CORE?.coh ?? 0,
                flow: metrics?.CORE?.flow ?? 0,
                T_integ: metrics?.CORE?.T_integ ?? 0,
                z_prox: metrics?.CORE?.z_prox ?? 0,
                hazard_score: metrics?.SYSTEM?.hazard_score ?? 0,
                guardian_trip: metrics?.SYSTEM?.guardian_trip ?? 0,
                phi_score: metrics?.FEP?.phi_score ?? 0,
                EV_readiness: metrics?.FEP?.EV_readiness ?? 0,
                EV_resonance: metrics?.FEP?.EV_resonance ?? 0,
                surprisal: metrics?.FEP?.surprisal ?? 0,
                LEX_Coh_conn: metrics?.LEXIKA?.LEX_Coh_conn ?? 0,
                LEX_Flow_pos: metrics?.LEXIKA?.LEX_Flow_pos ?? 0,
                LEX_Emotion_pos: metrics?.LEXIKA?.LEX_Emotion_pos ?? 0,
                LEX_T_integ: metrics?.LEXIKA?.LEX_T_integ ?? 0,
                LEX_T_disso: metrics?.LEXIKA?.LEX_T_disso ?? 0,
                
                // Vollständige Metriken als JSON
                metrics_full_json: JSON.stringify(metrics)
            };

            try {
                const dataFile = path.join(cfg.dir, `data_${sessionId}.jsonl`);
                fs.appendFileSync(dataFile, JSON.stringify(entry) + '\n', 'utf8');
                entries.push({ db: dbName, success: true });
            } catch (e) {
                console.error(`[TrinityUpload] Error writing to ${dbName}:`, e.message);
                entries.push({ db: dbName, success: false, error: e.message });
            }
        }

        return {
            successful: entries.filter(e => e.success).length,
            total: entries.length,
            details: entries
        };
    }

    /**
     * Speichere vollständige Historie (Volltext + alle Metriken)
     */
    async saveFullHistory(sessionId, roundId, prompt, response, metrics, candidates, a65Score, chainHash, timestamp) {
        try {
            const historyEntry = {
                session_id: sessionId,
                round_id: roundId,
                timestamp: timestamp,
                chain_hash: chainHash,
                
                // Volltext
                user_prompt: prompt,
                agent_response: response,
                
                // A65 Auswahl
                a65_selected_candidate: candidates?.selected_candidate ?? 0,
                a65_score: a65Score,
                a65_candidates_count: candidates?.candidates_count ?? 1,
                a65_candidates_brief: candidates?.candidates.map((c, i) => ({
                    index: i,
                    source: c.source,
                    text_preview: c.text.substring(0, 200),
                    score: c.a65_metric_score
                })) ?? [],
                
                // Vollständige Metriken
                metrics: metrics,
                
                // Speicher-Metadaten
                content_size_bytes: (prompt.length + response.length),
                metrics_version: '17_haupt'
            };

            const historyFile = path.join(this.historyDir, `${sessionId}_full_history.jsonl`);
            fs.appendFileSync(historyFile, JSON.stringify(historyEntry) + '\n', 'utf8');

            return { success: true, file: historyFile };
        } catch (error) {
            console.error('[TrinityUpload] History save error:', error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Speichere Session-Checkpoint (schneller Zugriff auf aktuelle Session)
     */
    async saveSessionCheckpoint(sessionId, roundId, chainHash, timestamp) {
        try {
            const checkpoint = {
                session_id: sessionId,
                last_round_id: roundId,
                chain_hash: chainHash,
                last_updated: timestamp
            };

            const checkpointFile = path.join(this.historyDir, `${sessionId}_checkpoint.json`);
            fs.writeFileSync(checkpointFile, JSON.stringify(checkpoint, null, 2), 'utf8');

            return { success: true, file: checkpointFile };
        } catch (error) {
            console.error('[TrinityUpload] Checkpoint save error:', error.message);
            return { success: false, error: error.message };
        }
    }

    computeChainHash(previousHash, content) {
        return crypto
            .createHash('sha256')
            .update(`${previousHash}|${content}|${Date.now()}`)
            .digest('hex');
    }
}

// ===== TRINITY DOWNLOAD ENGINE =====
// Lädt Daten und verteilt sie ins Chat-Fenster + History-Files

class TrinityDownloadEngine {
    constructor(baseDir = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL') {
        this.baseDir = baseDir;
        this.historyDir = path.join(baseDir, 'history');
    }

    /**
     * Lade alle Daten für eine Session und formatiere für Frontend
     */
    async downloadSession(sessionId) {
        try {
            const checkpoint = this.loadCheckpoint(sessionId);
            const historyLines = this.loadFullHistory(sessionId);

            const messages = historyLines.map(line => {
                try {
                    const entry = JSON.parse(line);
                    return {
                        id: `msg-${entry.session_id}-${entry.round_id}`,
                        role: 'exchange',
                        user_text: entry.user_prompt,
                        agent_text: entry.agent_response,
                        timestamp: entry.timestamp,
                        metrics: entry.metrics,
                        a65_data: {
                            selected: entry.a65_selected_candidate,
                            score: entry.a65_score,
                            candidates_brief: entry.a65_candidates_brief
                        }
                    };
                } catch { return null; }
            }).filter(Boolean);

            console.log(`[TrinityDownload] ✅ Loaded session ${sessionId}: ${messages.length} rounds`);

            return {
                success: true,
                session_id: sessionId,
                checkpoint: checkpoint,
                messages: messages,
                total_rounds: messages.length,
                last_chain_hash: checkpoint?.chain_hash
            };
        } catch (error) {
            console.error('[TrinityDownload] Error:', error.message);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Lade Checkpoint
     */
    loadCheckpoint(sessionId) {
        try {
            const file = path.join(this.historyDir, `${sessionId}_checkpoint.json`);
            if (!fs.existsSync(file)) return null;
            return JSON.parse(fs.readFileSync(file, 'utf8'));
        } catch {
            return null;
        }
    }

    /**
     * Lade gesamte History
     */
    loadFullHistory(sessionId) {
        try {
            const file = path.join(this.historyDir, `${sessionId}_full_history.jsonl`);
            if (!fs.existsSync(file)) return [];
            return fs.readFileSync(file, 'utf8').split('\n').filter(l => l.trim());
        } catch {
            return [];
        }
    }

    /**
     * Exportiere Session als strukturierte Datei
     */
    async exportSession(sessionId, format = 'json') {
        const data = await this.downloadSession(sessionId);
        if (!data.success) return data;

        if (format === 'json') {
            return {
                success: true,
                content: JSON.stringify(data, null, 2),
                filename: `session_${sessionId}.json`
            };
        } else if (format === 'csv') {
            const csv = data.messages.map(m => [
                m.id,
                m.timestamp,
                m.user_text.replace(/"/g, '""'),
                m.agent_text.replace(/"/g, '""'),
                m.a65_data.score
            ]).join('\n');
            return {
                success: true,
                content: csv,
                filename: `session_${sessionId}.csv`
            };
        }
        return { success: false, error: 'Unknown format' };
    }
}

// ===== API VERFLECHTUNG (REISSVERSCHLUSS) =====
// Nutze Gemini und OpenAI intelligent im Wechsel

class APIZipperEngine {
    constructor() {
        this.apiSequence = ['gemini', 'openai', 'gemini', 'openai']; // Reißverschluss
        this.callCount = 0;
    }

    /**
     * Wähle nächste API intelligent
     */
    nextAPI(useParallel = false) {
        if (useParallel) {
            return ['gemini', 'openai']; // Rufe beide auf
        }
        const api = this.apiSequence[this.callCount % this.apiSequence.length];
        this.callCount++;
        return [api];
    }

    /**
     * Wrapperf für Gemini + OpenAI mit Load-Balancing
     */
    async callWithZip(callGemini, callOpenAI, prompt, context, options = {}) {
        const apis = this.nextAPI(options.parallel);
        console.log(`[APIZipper] Using APIs: ${apis.join(', ')}`);

        const results = {};
        const promises = [];

        if (apis.includes('gemini')) {
            promises.push(
                callGemini(prompt, context)
                    .then(r => { results.gemini = r; })
                    .catch(e => { results.gemini_error = e.message; })
            );
        }

        if (apis.includes('openai')) {
            promises.push(
                callOpenAI(prompt, context)
                    .then(r => { results.openai = r; })
                    .catch(e => { results.openai_error = e.message; })
            );
        }

        await Promise.all(promises);

        // Gib beste Antwort zurück
        if (results.gemini && results.openai) {
            const better = results.gemini.coherence_score > results.openai.coherence_score
                ? results.gemini
                : results.openai;
            return { ...better, both_available: true };
        }

        return results.gemini || results.openai || { error: 'All APIs failed' };
    }
}

export { TrinityUploadEngine, TrinityDownloadEngine, APIZipperEngine, VectorSearchEngine, HistoryContextBuilder };
// Findet ähnliche historische Prompts basierend auf 120 Metriken + semantischer Ähnlichkeit

class VectorSearchEngine {
    constructor(baseDir = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL') {
        this.baseDir = baseDir;
        this.historyDir = path.join(baseDir, 'history');
    }

    /**
     * Suche die besten 3 ähnlichen historischen Exchanges
     * Basierend auf Prompt-Ähnlichkeit + Metrik-Proximity
     */
    async findTop3Matches(currentPrompt) {
        try {
            // 1. Lade alle historischen Einträge
            const allHistory = this.loadAllHistory();
            if (allHistory.length === 0) {
                return { success: false, matches: [], reason: 'No history available' };
            }

            // 2. Berechne Relevanz-Score für jeden Eintrag (Ähnlichkeit + Metriken)
            const scored = allHistory.map(entry => ({
                ...entry,
                relevance_score: this.computeRelevanceScore(currentPrompt, entry)
            }));

            // 3. Sortiere und nimm Top 3
            const top3 = scored
                .sort((a, b) => b.relevance_score - a.relevance_score)
                .slice(0, 3);

            console.log(`[VectorSearch] Found ${top3.length} matches for: "${currentPrompt.substring(0, 50)}..."`);

            return {
                success: true,
                matches: top3,
                query: currentPrompt
            };
        } catch (error) {
            console.error('[VectorSearch] Error:', error.message);
            return { success: false, error: error.message, matches: [] };
        }
    }

    /**
     * Lade alle historischen Einträge aus allen Session-Dateien
     */
    loadAllHistory() {
        const entries = [];
        try {
            if (!fs.existsSync(this.historyDir)) return entries;

            const files = fs.readdirSync(this.historyDir)
                .filter(f => f.endsWith('_full_history.jsonl'));

            for (const file of files) {
                const filepath = path.join(this.historyDir, file);
                const lines = fs.readFileSync(filepath, 'utf8').split('\n').filter(l => l.trim());

                for (const line of lines) {
                    try {
                        const entry = JSON.parse(line);
                        entries.push(entry);
                    } catch { /* skip */ }
                }
            }
        } catch (e) {
            console.error('[VectorSearch] Load error:', e.message);
        }
        return entries;
    }

    /**
     * Berechne Relevanz-Score: 50% Text-Ähnlichkeit + 50% Metrik-Ähnlichkeit
     */
    computeRelevanceScore(currentPrompt, historyEntry) {
        // Text-Ähnlichkeit (simple word overlap)
        const textSim = this.textSimilarity(currentPrompt, historyEntry.user_prompt);

        // Metrik-Ähnlichkeit (17 Hauptmetriken)
        const metricSim = this.metricSimilarity(historyEntry.metrics);

        return (textSim * 0.5) + (metricSim * 0.5);
    }

    /**
     * Simple word overlap similarity (0-1)
     */
    textSimilarity(text1, text2) {
        const words1 = new Set(this.tokenize(text1));
        const words2 = this.tokenize(text2);

        let matches = 0;
        for (const w of words2) if (words1.has(w)) matches++;

        const similarity = words2.length > 0 ? matches / Math.max(words1.size, words2.length) : 0;
        return Math.min(1, similarity);
    }

    /**
     * Metrik-Ähnlichkeit basierend auf 17 Hauptmetriken
     * Nutze Durchschnitt der Kernmetriken als Proxy für "Qualität"
     */
    metricSimilarity(metrics) {
        if (!metrics) return 0.5;
        const m = metrics?.CORE || {};
        const avg = ((m.A || 0.5) + (m.PCI || 0.5) + (m.coh || 0.5)) / 3;
        return Math.min(1, Math.max(0, avg));
    }

    /**
     * Tokenisiere einfach (Wortsplitting)
     */
    tokenize(text) {
        return (text || '').toLowerCase().split(/[^a-zäöüß0-9]+/i).filter(Boolean);
    }
}

// ===== HISTORY CONTEXT BUILDER =====
// Ladet die A→B→C→D→E Entstehungshistorie für gefundene Matches

class HistoryContextBuilder {
    constructor(baseDir = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL') {
        this.baseDir = baseDir;
        this.historyDir = path.join(baseDir, 'history');
        this.downloader = new TrinityDownloadEngine(baseDir);
    }

    /**
     * Baue Kontext mit A→B→C→D→E für jeden Match
     */
    async buildContextForMatches(matches) {
        const enriched = [];

        for (const match of matches.slice(0, 3)) {
            try {
                // Lade volle Session, um Entstehungshistorie zu bekommen
                const sessionData = await this.downloader.downloadSession(match.session_id);

                if (!sessionData.success || !sessionData.messages) continue;

                const msgs = sessionData.messages;
                const currentRoundIdx = msgs.findIndex(m => m.id === `msg-${match.session_id}-${match.round_id}`);

                if (currentRoundIdx === -1) continue;

                const current = msgs[currentRoundIdx];
                const prev1 = msgs[currentRoundIdx - 1] || null; // A
                const prev2 = msgs[currentRoundIdx - 2] || null; // B
                const next1 = msgs[currentRoundIdx + 1] || null; // D
                const next2 = msgs[currentRoundIdx + 2] || null; // E

                enriched.push({
                    session_id: match.session_id,
                    round_id: match.round_id,
                    relevance_score: match.relevance_score,
                    
                    // A→B→C→D→E Kontext
                    context: {
                        A: prev2?.user_text || '—',
                        B: prev1?.user_text || '—',
                        C: current.user_text,
                        agent_response: current.agent_text,
                        D: next1?.user_text || 'Keine weitere Frage',
                        E: next2?.user_text || 'Keine weitere Frage'
                    },
                    
                    // Metriken
                    metrics: current.metrics,
                    a65_data: current.a65_data
                });
            } catch (e) {
                console.warn(`[HistoryBuilder] Error building context for ${match.session_id}:`, e.message);
            }
        }

        return enriched;
    }
}

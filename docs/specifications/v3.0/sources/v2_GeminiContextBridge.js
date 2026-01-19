/**
 * GEMINI CONTEXT BRIDGE - Verwandelt FAISS-Chunks in kontextreiche Gemini-Prompts
 * 
 * Workflow:
 * 1. Top 3 FAISS-Ergebnisse nehmen
 * 2. Chunks vervollständigen (falls zerteilt durch Chunking)
 * 3. 2 vorherige + 2 nachfolgende Prompts/Antworten als Kontext laden
 * 4. Mit aktuellen 120+ Metriken anreichern
 * 5. Kontextreichen Prompt für Gemini API bauen
 * 6. Gemini API aufrufen → Freundliche, personalisierte Evoki-Antwort
 * 7. Nicht nur generische System-Infos, sondern echte Gesprächsantworten
 */

import fetch from 'node-fetch';
import fs from 'fs';
import path from 'path';

export class GeminiContextBridge {
    constructor(geminiApiKeys, openaiApiKey = null) {
        this.geminiApiKeys = geminiApiKeys || [];
        this.openaiApiKey = openaiApiKey;
        this.currentKeyIndex = 0;
        this.exhaustedKeys = new Set(); // Track exhausted Gemini keys
        this.historyDbPath = './evoki_v2_ultimate_FULL.db';
        this.geminiEndpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent';
        
        console.log(`[GeminiContext] Initialized with ${this.geminiApiKeys.length} Gemini keys + OpenAI fallback: ${openaiApiKey ? 'YES' : 'NO'}`);
    }

    /**
     * Hauptfunktion: Erstelle kontextreichen Gemini-Prompt und hole AI-Antwort
     * 
     * @param {object} params
     * @param {string} params.userPrompt - Aktuelle User-Frage
     * @param {array} params.faissResults - Top 10 FAISS-Ergebnisse
     * @param {number} params.selectedIndex - A65-gewählter Index
     * @param {object} params.metrics - 120+ berechnete Metriken
     * @param {string} params.sessionId - Session ID
     * @returns {object} - Gemini Response + Kontext-Metadaten
     */
    async generateContextualResponse(params) {
        const startTime = Date.now();
        const { userPrompt, faissResults, selectedIndex, metrics, sessionId } = params;

        console.log(`\n[GeminiContext] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
        console.log(`[GeminiContext] Building contextual prompt for Gemini...`);
        console.log(`[GeminiContext] 🔍 DEBUG: Received faissResults:`, JSON.stringify(faissResults, null, 2).substring(0, 500));
        console.log(`[GeminiContext] 🔍 DEBUG: faissResults length:`, faissResults?.length || 0);

        try {
            // ===== PHASE 1: TOP 3 CHUNKS ERWEITERN =====
            const top3Chunks = faissResults.slice(0, 3);
            console.log(`[GeminiContext] [1/5] Erweitere Top 3 Chunks...`);
            const expandedChunks = await this.expandChunks(top3Chunks);
            console.log(`[GeminiContext] ✅ ${expandedChunks.length} Chunks erweitert`);

            // ===== PHASE 2: KONTEXT LADEN (±2 Nachrichten) =====
            console.log(`[GeminiContext] [2/5] Lade ±2 Kontext-Nachrichten...`);
            const contextMessages = await this.loadContextMessages(expandedChunks, sessionId);
            console.log(`[GeminiContext] ✅ ${contextMessages.length} Kontext-Nachrichten geladen`);

            // ===== PHASE 3: METRIKEN-ZUSAMMENFASSUNG =====
            console.log(`[GeminiContext] [3/5] Erstelle Metriken-Zusammenfassung...`);
            const metricsSummary = this.summarizeMetrics(metrics);
            console.log(`[GeminiContext] ✅ Metriken zusammengefasst`);

            // ===== PHASE 4: GEMINI-PROMPT BAUEN =====
            console.log(`[GeminiContext] [4/5] Baue kontextreichen Gemini-Prompt...`);
            const geminiPrompt = this.buildGeminiPrompt({
                userPrompt,
                expandedChunks,
                contextMessages,
                metricsSummary,
                selectedChunk: expandedChunks[0] // A65-gewählter Chunk
            });
            console.log(`[GeminiContext] ✅ Prompt gebaut (${geminiPrompt.length} Zeichen)`);
            
            // DEBUG: Log erste 1000 Zeichen des Prompts
            console.log(`[GeminiContext] 📝 Prompt Preview:\n${geminiPrompt.substring(0, 1000)}...`);
            console.log(`[GeminiContext] 📊 Chunks im Prompt: ${expandedChunks.length}`);
            expandedChunks.forEach((chunk, i) => {
                const textLength = (chunk.full_text || chunk.original.text || '').length;
                const score = chunk.metadata?.score || chunk.score || 0;
                console.log(`[GeminiContext]    Chunk ${i+1}: ${textLength} chars, Score: ${score.toFixed(3)}`);
            });

            // ===== PHASE 5: GEMINI API AUFRUFEN =====
            console.log(`[GeminiContext] [5/5] Rufe Gemini API auf...`);
            const geminiResponse = await this.callGeminiAPI(geminiPrompt);
            console.log(`[GeminiContext] ✅ Gemini-Antwort erhalten (${geminiResponse.text.length} Zeichen)`);

            const processingTime = Date.now() - startTime;
            console.log(`[GeminiContext] ✅ Verarbeitung abgeschlossen in ${processingTime}ms`);
            console.log(`[GeminiContext] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`);

            return {
                success: true,
                response: geminiResponse.text,
                context: {
                    expanded_chunks: expandedChunks.length,
                    context_messages: contextMessages.length,
                    metrics_summary: metricsSummary,
                    prompt_length: geminiPrompt.length,
                    tokens_used: geminiResponse.usage
                },
                gemini_metadata: {
                    model: 'gemini-2.0-flash-exp',
                    finish_reason: geminiResponse.finishReason,
                    safety_ratings: geminiResponse.safetyRatings
                },
                processing_time_ms: processingTime,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error(`[GeminiContext] ❌ Fehler:`, error.message);
            return {
                success: false,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Erweitere Chunks: Vervollständige zerteilte Nachrichten
     * Hole 2 vorherige + 2 nachfolgende Chunks falls vorhanden
     */
    async expandChunks(chunks) {
        const expanded = [];

        for (const chunk of chunks) {
            try {
                // Parse Chunk ID um Nachbarn zu finden
                // Format: "2025-02-08_PromptX_ai_chunk_YYY" oder ähnlich
                const chunkId = chunk.chunk_id || chunk.id;
                const chunkNumber = this.extractChunkNumber(chunkId);
                
                if (chunkNumber !== null) {
                    // Hole ±2 Chunks
                    const neighbors = await this.getNeighborChunks(chunkId, chunkNumber, 2);
                    
                    expanded.push({
                        original: chunk,
                        full_text: this.assembleChunks([
                            ...neighbors.previous,
                            chunk,
                            ...neighbors.next
                        ]),
                        context_chunks: {
                            previous: neighbors.previous.length,
                            next: neighbors.next.length,
                            total: neighbors.previous.length + 1 + neighbors.next.length
                        },
                        metadata: {
                            chunk_id: chunkId,
                            chunk_number: chunkNumber,
                            score: chunk.score || 0
                        }
                    });
                } else {
                    // Chunk hat keine erkennbare Nummer → verwende wie ist
                    expanded.push({
                        original: chunk,
                        full_text: chunk.text || chunk.content || '',
                        context_chunks: { previous: 0, next: 0, total: 1 },
                        metadata: {
                            chunk_id: chunkId,
                            score: chunk.score || 0
                        }
                    });
                }
            } catch (error) {
                console.warn(`[GeminiContext] Chunk-Expansion fehlgeschlagen:`, error.message);
                expanded.push({
                    original: chunk,
                    full_text: chunk.text || chunk.content || '',
                    context_chunks: { previous: 0, next: 0, total: 1 },
                    metadata: { 
                        error: error.message,
                        chunk_id: chunk.chunk_id || chunk.id || 'unknown',
                        score: chunk.score || 0
                    }
                });
            }
        }

        return expanded;
    }

    /**
     * Extrahiere Chunk-Nummer aus Chunk-ID
     */
    extractChunkNumber(chunkId) {
        // Suche nach Mustern wie "chunk_001", "_001", etc.
        const patterns = [
            /_chunk_(\d+)/,
            /_(\d{3,4})$/,
            /chunk(\d+)/i
        ];

        for (const pattern of patterns) {
            const match = chunkId.match(pattern);
            if (match) {
                return parseInt(match[1], 10);
            }
        }

        return null;
    }

    /**
     * Hole benachbarte Chunks (±N)
     */
    async getNeighborChunks(baseChunkId, chunkNumber, range = 2) {
        // Extrahiere Basis-ID (ohne Chunk-Nummer)
        const baseId = baseChunkId.replace(/_chunk_\d+|_\d{3,4}$/, '');
        
        const previous = [];
        const next = [];

        // Hole vorherige Chunks
        for (let i = chunkNumber - range; i < chunkNumber; i++) {
            if (i > 0) {
                const neighborId = `${baseId}_chunk_${String(i).padStart(3, '0')}`;
                const chunk = await this.loadChunkById(neighborId);
                if (chunk) previous.push(chunk);
            }
        }

        // Hole nachfolgende Chunks
        for (let i = chunkNumber + 1; i <= chunkNumber + range; i++) {
            const neighborId = `${baseId}_chunk_${String(i).padStart(3, '0')}`;
            const chunk = await this.loadChunkById(neighborId);
            if (chunk) next.push(chunk);
        }

        return { previous, next };
    }

    /**
     * Lade einen Chunk anhand seiner ID aus chunks_v2_2.pkl via Python CLI
     */
    async loadChunkById(chunkId) {
        try {
            // Verwende Python CLI um Chunk aus chunks_v2_2.pkl zu laden
            return new Promise((resolve) => {
                const spawn = require('child_process').spawn;
                const path = require('path');
                
                const pythonPath = path.join(__dirname, '..', '..', '.venv', 'Scripts', 'python.exe');
                const scriptPath = path.join(__dirname, '..', '..', 'python', 'tools', 'load_chunk.py');
                
                // Erstelle einfaches Python-Script falls nicht existiert
                if (!require('fs').existsSync(scriptPath)) {
                    console.warn(`[GeminiContext] load_chunk.py nicht gefunden - überspringe Chunk-Expansion`);
                    resolve(null);
                    return;
                }
                
                const proc = spawn(pythonPath, [scriptPath, chunkId], {
                    cwd: path.join(__dirname, '..', '..', 'python'),
                    timeout: 5000
                });
                
                let stdout = '';
                proc.stdout.on('data', (data) => { stdout += data.toString(); });
                proc.on('close', (code) => {
                    if (code !== 0) {
                        resolve(null);
                        return;
                    }
                    
                    try {
                        const chunk = JSON.parse(stdout);
                        resolve({
                            chunk_id: chunk.chunk_id,
                            text: chunk.text || chunk.content || '',
                            content: chunk.text || chunk.content || ''
                        });
                    } catch {
                        resolve(null);
                    }
                });
                
                setTimeout(() => {
                    proc.kill();
                    resolve(null);
                }, 5000);
            });
        } catch (error) {
            console.warn(`[GeminiContext] Chunk-Load fehlgeschlagen:`, error.message);
            return null;
        }
    }

    /**
     * Setze Chunks zu vollständigem Text zusammen
     */
    assembleChunks(chunks) {
        return chunks
            .filter(c => c && (c.text || c.content))
            .map(c => c.text || c.content)
            .join('\n\n');
    }

    /**
     * Lade Kontext-Nachrichten aus der Session-Historie
     * Hole 2 vorherige + 2 nachfolgende User/Agent-Austausche
     */
    async loadContextMessages(expandedChunks, sessionId) {
        try {
            // Lade Session-Historie aus Trinity History
            const historyFile = `./backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/history/${sessionId}_full_history.jsonl`;
            
            if (!fs.existsSync(historyFile)) {
                console.log(`[GeminiContext] Keine Session-Historie gefunden für ${sessionId}`);
                return [];
            }

            const lines = fs.readFileSync(historyFile, 'utf8').split('\n').filter(l => l.trim());
            const messages = lines.map(line => {
                try {
                    return JSON.parse(line);
                } catch {
                    return null;
                }
            }).filter(Boolean);

            // Hole letzte 4 Nachrichten als Kontext (2 User + 2 Agent = 4 Exchanges)
            const recentMessages = messages.slice(-4).map(msg => ({
                user: msg.user_prompt,
                agent: msg.agent_response,
                timestamp: msg.timestamp,
                metrics: msg.metrics
            }));

            return recentMessages;

        } catch (error) {
            console.warn(`[GeminiContext] Kontext-Nachrichten laden fehlgeschlagen:`, error.message);
            return [];
        }
    }

    /**
     * Fasse Metriken zusammen für Gemini-Prompt
     */
    summarizeMetrics(metrics) {
        if (!metrics || !metrics.CORE) {
            return "Keine Metriken verfügbar.";
        }

        const core = metrics.CORE || {};
        const system = metrics.SYSTEM || {};
        const fep = metrics.FEP || {};

        return `
Konversations-Metriken:
- Authentizität (A): ${(core.A || 0).toFixed(2)}
- Prompt-Clarity (PCI): ${(core.PCI || 0).toFixed(2)}
- Kohärenz: ${(core.coh || 0).toFixed(2)}
- Flow: ${(core.flow || 0).toFixed(2)}
- Therapie-Integration: ${(core.T_integ || 0).toFixed(2)}
- Zonenproximität: ${(core.z_prox || 0).toFixed(2)}
- Hazard-Score: ${(system.hazard_score || 0).toFixed(2)}
- Phi-Score (IIT): ${(fep.phi_score || 0).toFixed(2)}
- Surprisal (FEP): ${(fep.surprisal || 0).toFixed(2)}
        `.trim();
    }

    /**
     * Baue den finalen Gemini-Prompt mit allem Kontext
     */
    buildGeminiPrompt(params) {
        const { userPrompt, expandedChunks, contextMessages, metricsSummary, selectedChunk } = params;

        // Beste Chunks als Kontext - VOLLSTÄNDIGER TEXT
        const chunksContext = expandedChunks.slice(0, 3).map((chunk, i) => {
            const text = chunk.full_text || chunk.original.text || chunk.original.content || '';
            const score = chunk.metadata?.score || chunk.score || 0;
            const chunkId = chunk.metadata?.chunk_id || chunk.chunk_id || 'unknown';
            return `[Quelle ${i+1} | Relevanz: ${(score * 100).toFixed(1)}% | ID: ${chunkId}]\n${text}`;
        }).join('\n\n━━━━━━━━━━━━━━━━━━━━━━\n\n');

        // Vorherige Konversation
        const conversationHistory = contextMessages.length > 0
            ? contextMessages.map(msg => 
                `User: ${msg.user}\nEvoki: ${msg.agent}`
            ).join('\n\n')
            : "Keine vorherige Konversation.";

        // Gemini System Prompt (EVOKI-Persönlichkeit)
        const systemPrompt = `Du bist EVOKI, ein empathischer KI-Begleiter mit Zugriff auf eine Wissensdatenbank.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 DEINE AUFGABE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. ANALYSIERE die 3 relevantesten Wissensfragmente aus der Datenbank (unten)
2. BEANTWORTE die User-Frage DIREKT MIT DIESEM WISSEN
3. Sei freundlich, persönlich und authentisch
4. Nutze die vorherige Konversation für Kontinuität

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 WISSENSDATENBANK (Top 3 Ergebnisse):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${chunksContext}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 VORHERIGE KONVERSATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${conversationHistory}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AKTUELLE METRIKEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${metricsSummary}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ USER-FRAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

${userPrompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WICHTIG:
✅ Beziehe dich DIREKT auf die Inhalte aus der Wissensdatenbank
✅ Zitiere oder paraphrasiere relevante Details aus den Quellen
✅ Gib eine echte, menschliche Antwort (kein "Laut Dokumentation...")
❌ Erfinde NICHTS - nutze nur was in den Quellen steht

EVOKI, bitte antworte jetzt basierend auf den Wissensfragmenten:`;

        return systemPrompt;
    }

    /**
     * Rufe Gemini API auf
     */
    async callGeminiAPI(prompt, retryCount = 0) {
        const maxRetries = this.geminiApiKeys.length;
        
        // Check if all Gemini keys are exhausted
        if (this.exhaustedKeys.size >= this.geminiApiKeys.length) {
            console.log(`[GeminiContext] ⚠️ All Gemini keys exhausted. Falling back to OpenAI...`);
            return await this.callOpenAIFallback(prompt);
        }
        
        const apiKey = this.getNextApiKey();
        const keyIndex = this.currentKeyIndex - 1; // getNextApiKey already incremented
        
        // Dynamische Token-Limits basierend auf Prompt-Länge
        const promptLength = prompt.length;
        const estimatedPromptTokens = Math.ceil(promptLength / 4); // Grobe Schätzung: 4 chars = 1 token
        
        let maxOutputTokens = 2048; // Default
        if (estimatedPromptTokens > 15000) {
            maxOutputTokens = 8000;  // Für 1M Context
        } else if (estimatedPromptTokens > 8000) {
            maxOutputTokens = 4096;  // Für 50k Context
        } else if (estimatedPromptTokens > 4000) {
            maxOutputTokens = 3072;  // Für 25k Context
        }
        
        console.log(`[GeminiContext] 📊 Estimated prompt tokens: ${estimatedPromptTokens}, maxOutput: ${maxOutputTokens}`);
        
        // Use global config from frontend or fallback to defaults
        const config = global.templeApiConfig || {
            temperature: 0.8,
            topK: 40,
            topP: 0.95,
            presencePenalty: 0,
            frequencyPenalty: 0,
        };
        
        console.log(`[GeminiContext] 🎛️ Using Config: temp=${config.temperature}, topK=${config.topK}, topP=${config.topP}`);
        
        // Build generationConfig dynamically
        const generationConfig = {
            temperature: config.temperature,
            topK: config.topK,
            topP: config.topP,
            maxOutputTokens: maxOutputTokens,
        };
        
        // Add optional parameters if present
        if (config.presencePenalty !== undefined && config.presencePenalty !== 0) {
            generationConfig.presencePenalty = config.presencePenalty;
        }
        if (config.frequencyPenalty !== undefined && config.frequencyPenalty !== 0) {
            generationConfig.frequencyPenalty = config.frequencyPenalty;
        }
        if (config.candidateCount !== undefined) {
            generationConfig.candidateCount = config.candidateCount;
        }
        if (config.seed !== undefined) {
            generationConfig.seed = config.seed;
        }
        if (config.stopSequences && config.stopSequences.length > 0) {
            generationConfig.stopSequences = config.stopSequences;
        }
        
        try {
            const response = await fetch(`${this.geminiEndpoint}?key=${apiKey}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: prompt
                        }]
                    }],
                    generationConfig,
                    safetySettings: [
                        { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_NONE" },
                        { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_NONE" },
                        { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_NONE" },
                        { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_NONE" }
                    ]
                }),
                timeout: 90000  // ✅ 90s für große Context-Fenster (1M tokens)
            });

            if (!response.ok) {
                const errorText = await response.text();
                
                // Check for quota/rate limit errors (429, 403 Resource Exhausted)
                if (response.status === 429 || errorText.includes('RESOURCE_EXHAUSTED') || errorText.includes('quota')) {
                    console.warn(`[GeminiContext] ⚠️ Key ${keyIndex + 1} quota exhausted: ${response.status}`);
                    this.exhaustedKeys.add(keyIndex);
                    
                    if (retryCount < maxRetries) {
                        console.log(`[GeminiContext] 🔄 Rotating to next key (attempt ${retryCount + 1}/${maxRetries})...`);
                        return await this.callGeminiAPI(prompt, retryCount + 1);
                    } else {
                        console.log(`[GeminiContext] All Gemini keys tried. Falling back to OpenAI...`);
                        return await this.callOpenAIFallback(prompt);
                    }
                }
                
                throw new Error(`Gemini API Error: ${response.status} - ${errorText}`);
            }

            const data = await response.json();
            
            if (!data.candidates || data.candidates.length === 0) {
                throw new Error('Gemini API returned no candidates');
            }

            const candidate = data.candidates[0];
            const text = candidate.content?.parts?.[0]?.text || '';
            
            console.log(`[GeminiContext] ✅ Gemini Key ${keyIndex + 1} successful`);

            return {
                text: text,
                finishReason: candidate.finishReason,
                safetyRatings: candidate.safetyRatings,
                usage: {
                    promptTokens: data.usageMetadata?.promptTokenCount || 0,
                    candidatesTokens: data.usageMetadata?.candidatesTokenCount || 0,
                    totalTokens: data.usageMetadata?.totalTokenCount || 0
                },
                usedKey: keyIndex + 1,
                provider: 'gemini',
                apiConfig: config  // ✅ Speichere verwendete API-Config als Metadaten

            };

        } catch (error) {
            console.error(`[GeminiContext] Gemini API Error:`, error.message);
            
            // Retry with next key if not a permanent error
            if (retryCount < maxRetries && !error.message.includes('no candidates')) {
                console.log(`[GeminiContext] 🔄 Retrying with next key...`);
                return await this.callGeminiAPI(prompt, retryCount + 1);
            }
            
            // Last resort: OpenAI fallback
            if (this.openaiApiKey) {
                console.log(`[GeminiContext] Falling back to OpenAI due to error...`);
                return await this.callOpenAIFallback(prompt);
            }
            
            throw error;
        }
    }
    
    /**
     * OpenAI Fallback wenn alle Gemini Keys erschöpft sind
     */
    async callOpenAIFallback(prompt) {
        if (!this.openaiApiKey) {
            throw new Error('No OpenAI API key configured for fallback');
        }
        
        console.log(`[GeminiContext] 🔄 Calling OpenAI GPT-4o-mini as fallback...`);
        
        // Use global config for OpenAI fallback too
        const config = global.templeApiConfig || {
            temperature: 0.8,
            topK: 40,
            topP: 0.95,
        };
        
        try {
            const response = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.openaiApiKey}`
                },
                body: JSON.stringify({
                    model: 'gpt-4o-mini',
                    messages: [
                        { role: 'system', content: 'Du bist EVOKI - ein empathischer KI-Therapeut.' },
                        { role: 'user', content: prompt }
                    ],
                    temperature: config.temperature,
                    max_tokens: 2048,
                    presence_penalty: config.presencePenalty || 0,
                    frequency_penalty: config.frequencyPenalty || 0,
                }),
                timeout: 30000
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`OpenAI API Error: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            const text = data.choices?.[0]?.message?.content || '';
            
            console.log(`[GeminiContext] ✅ OpenAI fallback successful`);
            
            return {
                text: text,
                finishReason: data.choices?.[0]?.finish_reason,
                usage: {
                    promptTokens: data.usage?.prompt_tokens || 0,
                    candidatesTokens: data.usage?.completion_tokens || 0,
                    totalTokens: data.usage?.total_tokens || 0
                },
                provider: 'openai',
                fallback: true,
                apiConfig: config  // ✅ Speichere API-Config auch für OpenAI Fallback
            };
            
        } catch (error) {
            console.error(`[GeminiContext] OpenAI Fallback Error:`, error.message);
            throw new Error(`Alle API Keys erschöpft (Gemini + OpenAI): ${error.message}`);
        }
    }

    /**
     * Hole nächsten API-Key (Rotation)
     */
    getNextApiKey() {
        if (this.geminiApiKeys.length === 0) {
            throw new Error('No Gemini API keys configured');
        }
        
        const key = this.geminiApiKeys[this.currentKeyIndex];
        this.currentKeyIndex = (this.currentKeyIndex + 1) % this.geminiApiKeys.length;
        return key;
    }
}

export default GeminiContextBridge;

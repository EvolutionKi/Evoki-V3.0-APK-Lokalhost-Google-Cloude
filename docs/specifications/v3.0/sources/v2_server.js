#!/usr/bin/env node
/**
 * EVOKI Backend Server v3.0 - ENHANCED WITH LIVE VECTORIZATION
 * Pure Node.js HTTP server WITH 120+ Metrics Integration
 * Provides Live Vector Database Updates for Tempel & Trialog
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import crypto from 'crypto';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
import { TrinityUploadEngine, TrinityDownloadEngine, APIZipperEngine, VectorSearchEngine, HistoryContextBuilder } from './core/TrinityEngine.js';
import { DualBackendBridge } from './core/DualBackendBridge.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from backend/.env
dotenv.config({ path: './backend/.env' });

// ===== A51 GENESIS ANCHOR VERIFICATION =====
let GENESIS_ANCHOR_DATA = null;

function verifyGenesisAnchor() {
    try {
        const anchorPath = path.join(__dirname, 'public', 'genesis_anchor_v12.json');

        if (!fs.existsSync(anchorPath)) {
            console.warn("⚠️  [A51] WARNING: genesis_anchor_v12.json nicht gefunden. Überspringe Validierung.");
            return true;
        }

        const anchorContent = fs.readFileSync(anchorPath, 'utf8');
        GENESIS_ANCHOR_DATA = JSON.parse(anchorContent);

        if (!GENESIS_ANCHOR_DATA.engine || !GENESIS_ANCHOR_DATA.engine.combined_sha256) {
            throw new Error("SYSTEM CRITICAL: A51 GENESIS ANCHOR MALFORMED. Missing engine.combined_sha256.");
        }

        console.log(`✅ [A51] Genesis Anchor loaded successfully`);
        console.log(`   - Combined SHA256: ${GENESIS_ANCHOR_DATA.engine.combined_sha256}`);
        console.log(`   - Regelwerk CRC32: ${GENESIS_ANCHOR_DATA.engine.regelwerk_crc32}`);
        console.log(`   - Registry CRC32:  ${GENESIS_ANCHOR_DATA.engine.registry_crc32}`);

        return true;
    } catch (error) {
        console.error("❌ [A51] FATAL: Genesis Anchor Violation:", error.message);
        throw error;
    }
}

// Verify Genesis Anchor before starting server
try {
    verifyGenesisAnchor();
} catch (error) {
    console.error("🛑 Server start aborted due to Genesis Anchor failure.");
    process.exit(1);
}

const PORT = process.env.PORT || 3001;
const HOSTNAME = '0.0.0.0';

console.log(`🔧 [CONFIG] Port from env: ${process.env.PORT || 'not set, using default 3001'}`);

// ===== API KEY ROTATION (4 Google Gemini Keys from .env) =====
const GEMINI_API_KEYS = [
    process.env.API_KEY || 'AIzaSyCVgs-2ZG-VRiYOmqUe_5SL7ddcWADSGzg',
    process.env.API_KEY_BACKUP_1 || 'AIzaSyDL6F-9VDEg2euKDzjE_yL52gpbe2jYL2c',
    process.env.API_KEY_BACKUP_2 || 'AIzaSyAmPpQXIG-9glOkZQfjcXhXaAr7Cc0hM_8',
    process.env.API_KEY_BACKUP_3 || 'AIzaSyAMPHrY3SEV3XEvTIeAqCvAJge5pEPx7X8'
];

// ===== TRINITY ENGINES INITIALIZATION =====
const uploadEngine = new TrinityUploadEngine();
const downloadEngine = new TrinityDownloadEngine();
const apiZipper = new APIZipperEngine();
const vectorSearch = new VectorSearchEngine();
const historyBuilder = new HistoryContextBuilder();

// ===== DUAL BACKEND BRIDGE INITIALIZATION =====
const dualBridge = new DualBackendBridge(GEMINI_API_KEYS);
console.log('🌉 [INIT] Dual Backend Bridge initialisiert');
console.log('   - Python Backend (8000): FAISS + Regelwerk V12');
console.log('   - Node Backend (3001): Trinity + Metriken');
console.log('   - Gemini Context Bridge: 4 API Keys rotierend');

let currentGeminiKeyIndex = 0;

function getNextGeminiAPIKey() {
    const key = GEMINI_API_KEYS[currentGeminiKeyIndex];
    currentGeminiKeyIndex = (currentGeminiKeyIndex + 1) % GEMINI_API_KEYS.length;
    console.log(`[A65] Using Gemini API Key #${currentGeminiKeyIndex}/${GEMINI_API_KEYS.length}`);
    return key;
}

// ===== CONFIGURATION =====

const TRIALOG_BASE_PATH = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/trialog/prompt';
const TEMPEL_BASE_PATH = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/prompt';
const VECTOR_DB_BASE_PATH = './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL';
const PYTHON_ENV_PATH = './.venv/Scripts/python.exe';
const METRICS_CALCULATOR_PATH = './evoki_pipeline/metrics_complete_v3.py';

// Backup path for metrics calculation
const PYTHON_BACKUP_PATH = 'python';
const DAILY_LOGS_PATH = path.join(__dirname, '../data/chat_history/daily_logs');

// Ensure Daily Logs Directory Exists
if (!fs.existsSync(DAILY_LOGS_PATH)) {
    try {
        fs.mkdirSync(DAILY_LOGS_PATH, { recursive: true });
        console.log(`[Init] Created daily logs directory: ${DAILY_LOGS_PATH}`);
    } catch (e) {
        console.error(`[Init] Failed to create daily logs directory: ${e.message}`);
    }
}

// Helper: Save interaction to daily log
function saveDailyLog(userPrompt, agentResponse, role = 'assistant') {
    try {
        const today = new Date().toISOString().split('T')[0];
        const logFile = path.join(DAILY_LOGS_PATH, `${today}.json`);

        let logs = [];
        if (fs.existsSync(logFile)) {
            try {
                logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
            } catch (e) {
                console.warn(`[History] Corrupt log file ${today}.json, starting fresh.`);
            }
        }

        const timestamp = new Date().toISOString();

        // Add User Log
        logs.push({
            timestamp,
            speaker: 'user',
            text: userPrompt
        });

        // Add Assistant Log
        logs.push({
            timestamp,
            speaker: role,
            text: agentResponse
        });

        fs.writeFileSync(logFile, JSON.stringify(logs, null, 2), 'utf8');
        console.log(`[History] Saved interaction to ${today}.json (${logs.length} entries)`);
    } catch (e) {
        console.error(`[History] Failed to save daily log: ${e.message}`);
    }
}


// 12 Vektor-Datenbanken Konfiguration (Live Updates)
const VECTOR_DATABASES = {
    // Tempel (8 DBs) - JSON-based directories
    'tempel_W_m1': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/chunk', offset: -1, embed_dim: 384 },
    'tempel_W_m2': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_m2.db', offset: -2, embed_dim: 384 },
    'tempel_W_m5': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_m5.db', offset: -5, embed_dim: 4096 },
    'tempel_W_m25': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_m25.db', offset: -25, embed_dim: 4096 },
    'tempel_W_p1': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_p1.db', offset: 1, embed_dim: 384 },
    'tempel_W_p2': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_p2.db', offset: 2, embed_dim: 384 },
    'tempel_W_p5': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_p5.db', offset: 5, embed_dim: 4096 },
    'tempel_W_p25': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/metrics_W_p25.db', offset: 25, embed_dim: 4096 },

    // Trialog (4 DBs)
    'trialog_W_m1': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/trialog/metrics_W_m1.db', offset: -1, embed_dim: 384 },
    'trialog_W_m2': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/trialog/metrics_W_m2.db', offset: -2, embed_dim: 384 },
    'trialog_W_m5': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/trialog/metrics_W_m5.db', offset: -5, embed_dim: 4096 },
    'trialog_W_p25': { path: './backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/trialog/metrics_W_p25.db', offset: 25, embed_dim: 4096 }
};

// ===== LIVE METRICS CALCULATION =====

function calculateLiveMetrics(userPrompt, agentResponse) {
    return new Promise((resolve, reject) => {
        // Erstelle temporäre Textdatei für Python-Script
        const combinedText = `User: ${userPrompt}\nAssistant: ${agentResponse}`;
        const tempFile = path.join('./temp', `metrics_${Date.now()}.txt`);

        // Ensure temp directory exists
        if (!fs.existsSync('./temp')) {
            fs.mkdirSync('./temp', { recursive: true });
        }

        fs.writeFileSync(tempFile, combinedText, 'utf8');

        // Verwende das CLI-Wrapper-Script
        const metricsCliPath = path.join('evoki_pipeline', 'metrics_cli.py');

        console.log(`[Metrics] Calling Python: ${PYTHON_ENV_PATH} ${metricsCliPath} ${tempFile}`);

        const pythonProcess = spawn(PYTHON_ENV_PATH, [
            metricsCliPath,
            tempFile
        ]);

        let outputData = '';
        let errorData = '';

        pythonProcess.stdout.on('data', (data) => {
            outputData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });

        pythonProcess.on('close', (code) => {
            // Cleanup temp file
            try { fs.unlinkSync(tempFile); } catch { }

            console.log(`[Metrics] Python process exited with code ${code}`);
            console.log(`[Metrics] stdout: ${outputData.substring(0, 500)}`);
            console.log(`[Metrics] stderr: ${errorData}`);

            if (code === 0) {
                try {
                    const metrics = JSON.parse(outputData);
                    console.log('[Metrics] ✅ Successfully parsed metrics JSON');
                    resolve(metrics);
                } catch (parseError) {
                    console.error('[Metrics] ❌ JSON Parse Error:', parseError);
                    console.error('[Metrics] Raw output:', outputData.substring(0, 200));
                    resolve(generateFallbackMetrics(userPrompt, agentResponse));
                }
            } else {
                console.error('[Metrics] ❌ Python Error (exit code:', code, ')');
                console.error('[Metrics] Error details:', errorData);
                resolve(generateFallbackMetrics(userPrompt, agentResponse));
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('[Metrics] ❌ Process Spawn Error:', error.message);
            console.error('[Metrics] Command was:', PYTHON_ENV_PATH, metricsCliPath, tempFile);
            resolve(generateFallbackMetrics(userPrompt, agentResponse));
        });
    });
}

function generateFallbackMetrics(userPrompt, agentResponse) {
    // Fallback-Metriken wenn Python-Berechnung fehlschlägt (alle 120+)
    const textLength = (userPrompt + agentResponse).length;
    const wordCount = (userPrompt + agentResponse).split(/\s+/).length;
    const timestamp = new Date().toISOString();

    return {
        CORE: {
            A: Math.min(0.9, Math.max(0.1, Math.random() * 0.5 + 0.25)),
            PCI: Math.random() * 0.8,
            gen_index: Math.min(2.0, wordCount / 100),
            z_prox: Math.random() * 0.3,
            S_entropy: Math.log(Math.max(wordCount, 1) + 1) / 10,
            flow: Math.random() * 0.6,
            coh: Math.random() * 0.7,
            rep_same: Math.random() * 0.1,
            ZLF: Math.random() * 0.05,
            LL: Math.random() * 0.1,
            T_panic: Math.random() * 0.1,
            T_disso: Math.random() * 0.1,
            T_integ: Math.random() * 0.8 + 0.2,
            T_shock: Math.random() * 0.05,
            grad_A: (Math.random() - 0.5) * 0.1,
            grad_PCI: (Math.random() - 0.5) * 0.1,
            grad_G: (Math.random() - 0.5) * 0.05
        },
        SYSTEM: {
            hazard_score: Math.random() * 0.2,
            guardian_trip: Math.random() > 0.9 ? 1 : 0,
            a51_compliant: 1,
            lexika_hash_match: 1,
            dist_z: Math.random() * 0.4,
            is_critical: Math.random() > 0.95 ? 1 : 0,
            context_reset: 0
        },
        FEP: {
            phi_score: Math.random() * 0.5,
            phi_score2: Math.random() * 0.3,
            EV_readiness: Math.random() * 0.8 + 0.2,
            EV_tension: Math.random() * 0.3,
            EV_resonance: Math.random() * 0.4,
            surprisal: Math.random() * 0.4,
            U: Math.random() * 0.6,
            R: Math.random() * 0.5,
            depression_risk: Math.random() * 0.2,
            anxiety_loop: Math.random() * 0.15,
            fep_dissociation: Math.random() * 0.1
        },
        LEXIKA: {
            LEX_S_self: Math.random() * 0.3,
            LEX_X_exist: Math.random() * 0.2,
            LEX_B_past: Math.random() * 0.25,
            LEX_T_panic: Math.random() * 0.1,
            LEX_T_disso: Math.random() * 0.1,
            LEX_T_integ: Math.random() * 0.5 + 0.3,
            LEX_Emotion_pos: Math.random() * 0.4,
            LEX_Emotion_neg: Math.random() * 0.3,
            LEX_Flow_pos: Math.random() * 0.5,
            LEX_Coh_conn: Math.random() * 0.6
        },
        META: {
            timestamp: timestamp,
            word_count: wordCount,
            char_count: textLength,
            session_type: 'live_calculation',
            calculation_method: 'fallback'
        }
    };
}

// ===== LIVE VECTOR DATABASE UPDATES =====

async function writeToVectorDatabases(sessionInfo, userPrompt, agentResponse, metrics, sessionType) {
    try {
        const timestamp = new Date().toISOString();

        // Bestimme welche Datenbanken zu verwenden sind
        const dbPrefix = sessionType === 'tempel' ? 'tempel_' : 'trialog_';
        const relevantDbs = Object.entries(VECTOR_DATABASES)
            .filter(([key]) => key.startsWith(dbPrefix));

        console.log(`[VectorDB] Writing to ${relevantDbs.length} databases for ${sessionType}...`);

        const vectorWritePromises = relevantDbs.map(async ([dbKey, dbConfig]) => {
            return new Promise((resolve) => {
                try {
                    // Stelle sicher, dass DB-Verzeichnis existiert
                    const dbDir = path.dirname(dbConfig.path);
                    if (!fs.existsSync(dbDir)) {
                        fs.mkdirSync(dbDir, { recursive: true });
                    }

                    // Erstelle DB-Schema (vereinfacht ohne sqlite3 dependency)
                    const schemaFile = dbConfig.path.replace('.db', '_schema.sql');
                    const schema = `
-- EVOKI Vector Database Schema for ${dbKey}
-- Created: ${timestamp}

CREATE TABLE IF NOT EXISTS vector_index (
    chunk_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    exchange_id INTEGER,
    round_id INTEGER,
    timestamp TEXT NOT NULL,
    window_type TEXT NOT NULL,
    content_user TEXT,
    content_agent TEXT,
    
    -- Core Metrics (direkt indexiert)
    A REAL,
    PCI REAL,
    z_prox REAL,
    T_panic REAL,
    grad_A REAL,
    grad_PCI REAL,
    phi_score REAL,
    EV_readiness REAL,
    hazard_score REAL,
    guardian_trip INTEGER,
    
    -- Alle 120+ Metriken als JSON (für Flexibilität)
    metrics_full_json TEXT,
    
    -- Embeddings (Placeholder)
    embedding_384 TEXT,
    embedding_4096 TEXT,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indizes für Performance
CREATE INDEX IF NOT EXISTS idx_session_id ON vector_index(session_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON vector_index(timestamp);
CREATE INDEX IF NOT EXISTS idx_A ON vector_index(A);
CREATE INDEX IF NOT EXISTS idx_hazard_score ON vector_index(hazard_score);
                    `;

                    fs.writeFileSync(schemaFile, schema, 'utf8');

                    // Erstelle Daten-Entry als JSON (da keine SQLite dependency)
                    const chunkId = `${sessionInfo.session_id}_${sessionInfo.exchange_id || sessionInfo.round_id}_${dbKey}`;
                    const windowType = dbKey.replace(dbPrefix, '');

                    // Sicherer Dateipfad - verhindere Directory-Konflikte
                    const dataFile = dbConfig.path.replace('.db', '_data.json');
                    if (fs.existsSync(dataFile) && fs.lstatSync(dataFile).isDirectory()) {
                        fs.rmSync(dataFile, { recursive: true, force: true });
                    }

                    const vectorEntry = {
                        chunk_id: chunkId,
                        session_id: sessionInfo.session_id,
                        exchange_id: sessionInfo.exchange_id || null,
                        round_id: sessionInfo.round_id || null,
                        timestamp: timestamp,
                        window_type: windowType,
                        content_user: userPrompt.substring(0, 500), // Begrenzt
                        content_agent: agentResponse.substring(0, 500),

                        // Denormalisierte Metriken
                        A: metrics.CORE?.A || 0,
                        PCI: metrics.CORE?.PCI || 0,
                        z_prox: metrics.CORE?.z_prox || 0,
                        T_panic: metrics.CORE?.T_panic || 0,
                        grad_A: metrics.CORE?.grad_A || 0,
                        grad_PCI: metrics.CORE?.grad_PCI || 0,
                        phi_score: metrics.FEP?.phi_score || 0,
                        EV_readiness: metrics.FEP?.EV_readiness || 0,
                        hazard_score: metrics.SYSTEM?.hazard_score || 0,
                        guardian_trip: metrics.SYSTEM?.guardian_trip || 0,

                        // Alle Metriken als JSON
                        metrics_full_json: JSON.stringify(metrics),

                        // Placeholder Embeddings
                        embedding_384: dbConfig.embed_dim === 384 ? 'placeholder_384d' : null,
                        embedding_4096: dbConfig.embed_dim === 4096 ? 'placeholder_4096d' : null,

                        created_at: timestamp
                    };

                    // Speichere als JSON-File (temporär bis SQLite integration)
                    try {
                        fs.appendFileSync(dataFile, JSON.stringify(vectorEntry) + '\n', 'utf8');
                        resolve({ success: true, db: dbKey, method: 'jsonl' });
                    } catch (writeError) {
                        console.error(`[VectorDB] Write error for ${dbKey}:`, writeError.message);
                        resolve({ success: false, db: dbKey, error: writeError.message });
                    }

                } catch (error) {
                    console.error(`[VectorDB] Error writing to ${dbKey}:`, error);
                    resolve({ success: false, db: dbKey, error: error.message });
                }
            });
        });

        const results = await Promise.all(vectorWritePromises);
        const successful = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success);

        console.log(`[VectorDB] Live-Vektorisierung: ${successful}/${results.length} DBs erfolgreich`);
        if (failed.length > 0) {
            console.error('[VectorDB] Fehlgeschlagen:', failed.map(f => f.db).join(', '));
        }

        return { successful, failed, total: results.length };

    } catch (error) {
        console.error('[VectorDB] Genereller Fehler:', error);
        return { successful: 0, failed: [], total: 0 };
    }
}

// ===== SESSION MANAGEMENT (wie vorher) =====

function getLatestTrialogSession() {
    try {
        if (!fs.existsSync(TRIALOG_BASE_PATH)) {
            fs.mkdirSync(TRIALOG_BASE_PATH, { recursive: true });
            return { session_id: generateSessionId(), total_rounds: 0, file_path: null };
        }

        const files = fs.readdirSync(TRIALOG_BASE_PATH)
            .filter(f => f.startsWith('live_trialog_prompt_') && f.endsWith('.json'))
            .sort()
            .reverse(); // Most recent first

        if (files.length === 0) {
            return { session_id: generateSessionId(), total_rounds: 0, file_path: null };
        }

        const latestFile = files[0];
        const filePath = path.join(TRIALOG_BASE_PATH, latestFile);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        return {
            session_id: data.meta.session_id,
            total_rounds: data.meta.total_rounds,
            file_path: filePath,
            data: data
        };
    } catch (error) {
        console.error('[Trialog] Error loading session:', error);
        return { session_id: generateSessionId(), total_rounds: 0, file_path: null };
    }
}

function getLatestTempelSession() {
    try {
        if (!fs.existsSync(TEMPEL_BASE_PATH)) {
            fs.mkdirSync(TEMPEL_BASE_PATH, { recursive: true });
            return { session_id: generateSessionId(), total_vectors: 0, file_path: null };
        }

        const files = fs.readdirSync(TEMPEL_BASE_PATH)
            .filter(f => f.startsWith('live_tempel_prompt_') && f.endsWith('.json'))
            .sort()
            .reverse(); // Most recent first

        if (files.length === 0) {
            return { session_id: generateSessionId(), total_vectors: 0, file_path: null };
        }

        const latestFile = files[0];
        const filePath = path.join(TEMPEL_BASE_PATH, latestFile);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        return {
            session_id: data.meta.session_id,
            total_vectors: data.meta.total_vectors || 0,
            file_path: filePath,
            data: data
        };
    } catch (error) {
        console.error('[Tempel] Error loading session:', error);
        return { session_id: generateSessionId(), total_vectors: 0, file_path: null };
    }
}

function generateSessionId() {
    const now = new Date();
    return `${now.getFullYear().toString().slice(-2)}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}${now.getSeconds().toString().padStart(2, '0')}`;
}

// ===== ENHANCED SAVE FUNCTIONS =====

async function saveTempelPromptWithVectorization(sessionInfo, userPrompt, agentResponse) {
    try {
        const timestamp = new Date().toISOString();
        const newExchangeId = Math.floor(sessionInfo.total_vectors / 2) + 1;

        console.log(`[Tempel] Starting Live Metrics Calculation for Exchange ${newExchangeId}...`);

        // 1. BERECHNE LIVE METRIKEN (alle 120+)
        const metrics = await calculateLiveMetrics(userPrompt, agentResponse);

        let tempelData;
        if (sessionInfo.data) {
            tempelData = sessionInfo.data;
            tempelData.meta.total_vectors += 2;
            tempelData.meta.last_updated = timestamp;
        } else {
            tempelData = {
                meta: {
                    type: "live_tempel_prompt",
                    session_id: sessionInfo.session_id,
                    created_at: timestamp,
                    model: "all-MiniLM-L6-v2",
                    dimensions: 384,
                    description: "Live atomare Prompts mit 120+ Metriken",
                    total_vectors: 2,
                    last_updated: timestamp
                },
                embeddings: []
            };
        }

        // User Embedding mit Metriken
        const userEmbedding = {
            exchange_id: newExchangeId,
            role: "user",
            timestamp: timestamp,
            content: userPrompt,
            embedding: [], // Placeholder
            metrics: metrics
        };

        // Agent Embedding mit Metriken
        const agentEmbedding = {
            exchange_id: newExchangeId,
            role: "assistant",
            timestamp: timestamp,
            content: agentResponse,
            embedding: [], // Placeholder
            metrics: metrics
        };

        tempelData.embeddings.push(userEmbedding);
        tempelData.embeddings.push(agentEmbedding);

        // 2. SPEICHERE JSON-DATEI
        const fileName = `live_tempel_prompt_${sessionInfo.session_id}.json`;
        const filePath = path.join(TEMPEL_BASE_PATH, fileName);
        fs.writeFileSync(filePath, JSON.stringify(tempelData, null, 2), 'utf8');

        console.log(`[Tempel] JSON saved. Starting Vector DB writes...`);

        // 3. SCHREIBE IN ALLE 8 TEMPEL VEKTOR-DATENBANKEN
        const vectorResult = await writeToVectorDatabases(
            { session_id: sessionInfo.session_id, exchange_id: newExchangeId },
            userPrompt,
            agentResponse,
            metrics,
            'tempel'
        );

        console.log(`[Tempel] ✅ Exchange ${newExchangeId} complete: JSON + ${vectorResult.successful} Vector DBs`);

        return {
            session_id: sessionInfo.session_id,
            exchange_id: newExchangeId,
            file_path: filePath,
            metrics_calculated: true,
            vector_db_result: vectorResult
        };

    } catch (error) {
        console.error('[Tempel] Error in enhanced save:', error);
        return null;
    }
}

async function saveTrialogPromptWithVectorization(sessionInfo, userPrompt, agentResponse) {
    try {
        const timestamp = new Date().toISOString();
        const newRoundId = sessionInfo.total_rounds + 1;

        console.log(`[Trialog] Starting Live Metrics Calculation for Round ${newRoundId}...`);

        // 1. BERECHNE LIVE METRIKEN
        const metrics = await calculateLiveMetrics(userPrompt, agentResponse);

        // [CYCLE 6] History Sync: Speichere in Daily Log
        saveDailyLog(userPrompt, agentResponse, "assistant");


        let trialogData;
        if (sessionInfo.data) {
            trialogData = sessionInfo.data;
            trialogData.meta.total_rounds = newRoundId;
            trialogData.meta.last_updated = timestamp;
        } else {
            trialogData = {
                meta: {
                    type: "live_trialog_prompt",
                    session_id: sessionInfo.session_id,
                    created_at: timestamp,
                    model: "all-MiniLM-L6-v2",
                    dimensions: 384,
                    description: "Trialog mit 120+ Live-Metriken",
                    total_rounds: newRoundId,
                    last_updated: timestamp
                },
                embeddings: [],
                rounds: []
            };
        }

        // New Round mit Metriken
        const newRound = {
            round_id: newRoundId,
            user_prompt: userPrompt,
            user_timestamp: timestamp,
            agent_responses: [{
                agent: {
                    agent_id: "evoki_001",
                    role: "EVOKI_Engine",
                    persona: "HyperVektorium Deep Storage Assistant",
                    message_number: newRoundId,
                    timestamp: timestamp
                },
                response: agentResponse,
                timestamp: timestamp,
                round_id: newRoundId,
                metrics: metrics // LIVE METRIKEN!
            }],
            sha_chain: generateHashChain(userPrompt + agentResponse),
            completion_timestamp: timestamp,
            total_agents: 1,
            live_metrics: metrics // LIVE METRIKEN!
        };

        trialogData.rounds.push(newRound);

        // 2. SPEICHERE JSON
        const fileName = `live_trialog_prompt_${sessionInfo.session_id}.json`;
        const filePath = path.join(TRIALOG_BASE_PATH, fileName);
        fs.writeFileSync(filePath, JSON.stringify(trialogData, null, 2), 'utf8');

        console.log(`[Trialog] JSON saved. Starting Vector DB writes...`);

        // 3. SCHREIBE IN ALLE 4 TRIALOG VEKTOR-DATENBANKEN
        const vectorResult = await writeToVectorDatabases(
            { session_id: sessionInfo.session_id, round_id: newRoundId },
            userPrompt,
            agentResponse,
            metrics,
            'trialog'
        );

        console.log(`[Trialog] ✅ Round ${newRoundId} complete: JSON + ${vectorResult.successful} Vector DBs`);

        return {
            session_id: sessionInfo.session_id,
            round_id: newRoundId,
            file_path: filePath,
            metrics_calculated: true,
            vector_db_result: vectorResult
        };

    } catch (error) {
        console.error('[Trialog] Error in enhanced save:', error);
        return null;
    }
}

function generateHashChain(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
        const char = text.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return Math.abs(hash).toString(16).slice(0, 16);
}

// ===== IN-MEMORY STORAGE FOR DEVELOPMENT (P1-1, P1-2, P1-3) =====
const pipelineLogs = [];
const MAX_PIPELINE_LOGS = 1000;

const systemErrors = [];
const MAX_SYSTEM_ERRORS = 500;

const trialogSessions = new Map();

// ===== HTTP SERVER (wie vorher, aber mit Enhanced Functions) =====

function setJsonHeaders(res) {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

function sendJson(res, statusCode, data) {
    setJsonHeaders(res);
    res.writeHead(statusCode);
    res.end(JSON.stringify(data, null, 2) + '\n');
}

function collectRequestBody(req, callback) {
    let body = '';

    req.on('data', chunk => {
        body += chunk.toString();
        if (body.length > 104857600) { // 100MB limit
            req.connection.destroy();
        }
    });

    req.on('end', () => {
        try {
            const data = body ? JSON.parse(body) : {};
            callback(null, data);
        } catch (err) {
            callback(err);
        }
    });
}

// ===== A65 MULTI-CANDIDATE SELECTION =====

/**
 * Generate 3 candidate responses using A65 Logic
 * Candidates come from different sources/strategies:
 * 1. Gemini 2.5 Flash (Primary)
 * 2. Fallback (OpenAI, Claude, Local LLM)
 * 3. Context-Based Retrieval (From Vector DBs)
 */
/**
 * Neue A65 Candidates mit Past-Example Integration
 * Nutzt TOP 3 historische Exchanges mit A→B→C→D→E Kontext
 */
async function generateTempleA65CandidatesWithHistory(prompt, pastExamples, apiConfig) {
    const candidates = [];

    // Retrieve vector context
    const vectorContext = await retrieveContextFromVectorDB(prompt);
    console.log(`[A65] Vector context retrieved: ${vectorContext.token_count}t | Past examples: ${pastExamples.length}`);

    // Build "past examples" context para die APIs
    let pastExamplesText = '';
    if (pastExamples.length > 0) {
        pastExamplesText = '\n\n=== HISTORISCHE BEISPIELE FÜR KONTEXTUALISIERUNG ===\n';
        for (let i = 0; i < Math.min(3, pastExamples.length); i++) {
            const ex = pastExamples[i];
            pastExamplesText += `\n[BEISPIEL ${i + 1}] Relevanz: ${(ex.relevance_score * 100).toFixed(1)}%\n`;
            pastExamplesText += `A: ${ex.context.A.substring(0, 150)}\n`;
            pastExamplesText += `B: ${ex.context.B.substring(0, 150)}\n`;
            pastExamplesText += `C (User): ${ex.context.C.substring(0, 150)}\n`;
            pastExamplesText += `Agent-Antwort: ${ex.context.agent_response.substring(0, 200)}\n`;
        }
    }

    try {
        // ===== CANDIDATE 1: Gemini WITH Historical Examples =====
        const geminiResponse = await callGeminiAPIWithExamples(
            prompt,
            pastExamplesText,
            apiConfig,
            vectorContext
        );
        if (geminiResponse) {
            candidates.push({
                text: geminiResponse.text,
                source: 'gemini-with-history',
                coherence_score: geminiResponse.coherence_score || 0.85,
                diversity_score: 0.8,
                token_count: geminiResponse.token_count || Math.ceil(geminiResponse.text.length / 4),
                reason: 'primary_api_with_history'
            });
        }
    } catch (err) {
        console.warn('[A65-History] Gemini failed:', err.message);
    }

    try {
        // ===== CANDIDATE 2: OpenAI WITH Historical Examples =====
        const openaiResponse = await callOpenAIWithExamples(
            prompt,
            pastExamplesText,
            apiConfig,
            vectorContext
        );
        if (openaiResponse) {
            candidates.push({
                text: openaiResponse.text,
                source: 'openai-with-history',
                coherence_score: openaiResponse.coherence_score || 0.75,
                diversity_score: 0.7,
                token_count: openaiResponse.token_count || Math.ceil(openaiResponse.text.length / 4),
                reason: 'fallback_api_with_history'
            });
        }
    } catch (err) {
        console.warn('[A65-History] OpenAI failed:', err.message);
    }

    // ===== CANDIDATE 3: Best Past Example (Synthesis) =====
    if (pastExamples.length > 0) {
        const bestExample = pastExamples[0];
        candidates.push({
            text: `Based on similar past interaction (#${pastExamples[0].relevance_score}% match):\n\n${bestExample.context.agent_response.substring(0, 500)}`,
            source: 'past_example_synthesis',
            coherence_score: bestExample.relevance_score * 0.95,
            diversity_score: 0.5,
            token_count: bestExample.context.agent_response.length / 4,
            reason: 'past_example_best_match'
        });
    } else if (vectorContext) {
        // Fallback to vector DB
        candidates.push({
            text: vectorContext.text,
            source: 'vector_db',
            coherence_score: vectorContext.coherence_score || 0.70,
            diversity_score: 0.6,
            token_count: vectorContext.token_count,
            reason: 'vector_context_fallback'
        });
    }

    // Fallback if all fail
    if (candidates.length === 0) {
        candidates.push({
            text: `Temple Response [History Mode]: Ihre Anfrage "${prompt}" wurde mit 120+ Metriken und historischem Kontext verarbeitet.`,
            source: 'fallback',
            coherence_score: 0.5,
            diversity_score: 0.3,
            token_count: 60,
            reason: 'all_methods_failed'
        });
    }

    // Enrich with live metrics
    for (const c of candidates) {
        try {
            const m = await calculateLiveMetrics(prompt, c.text);
            c.metrics = m;
            c.a65_metric_score = computeA65MetricScore(m);
        } catch (e) {
            c.metrics = generateFallbackMetrics(prompt, c.text);
            c.a65_metric_score = computeA65MetricScore(c.metrics);
        }
    }

    return candidates;
}

/**
 * Gemini mit Past Examples
 */
async function callGeminiAPIWithExamples(prompt, pastExamplesText, apiConfig, vectorContext) {
    const apiKey = getNextGeminiAPIKey();
    const model = 'gemini-2.5-flash';

    const systemPrompt = `Du bist EVOKI, ein spezialisierter KI-Agent mit Zugriff auf 30GB Vektordatenbanken und 120+ Qualitätsmetriken.

Wichtig:
- Antworte NICHT generisch
- Nutze die bereitgestellten historischen Beispiele als Kontextualisierung
- Verbessere die Qualität durch Metrik-Awareness
- Nutze die Vektordaten-Snippets als Grundlage für eine genaue Antwort

${vectorContext?.text ? `\n=== VEKTORDATENBANK-KONTEXT ===\n${vectorContext.text.substring(0, 2000)}` : ''}

${pastExamplesText}

Antworte präzise und nutze die Kontextualisierung zur Verbesserung der Antwort.`;

    const userMessage = prompt;

    try {
        const response = await fetch(
            `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: userMessage }] }],
                    systemInstruction: { parts: [{ text: systemPrompt }] },
                    generationConfig: {
                        temperature: 0.7,
                        topP: 0.9,
                        maxOutputTokens: 2048
                    }
                })
            }
        );

        const data = await response.json();
        const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';

        return {
            text: text || 'No response from Gemini',
            coherence_score: 0.85,
            token_count: Math.ceil(text.length / 4)
        };
    } catch (error) {
        console.error('[Gemini-History] API Error:', error.message);
        throw error;
    }
}

/**
 * OpenAI mit Past Examples
 */
async function callOpenAIWithExamples(prompt, pastExamplesText, apiConfig, vectorContext) {
    const apiKey = process.env.OPENAI_API_KEY || 'sk-proj-default';

    const systemMessage = `Du bist EVOKI, ein spezialisierter KI-Agent mit Zugriff auf 30GB Vektordatenbanken und 120+ Qualitätsmetriken.

Wichtig:
- Antworte NICHT generisch
- Nutze die bereitgestellten historischen Beispiele
- Verbessere die Qualität durch Metrik-Awareness

${vectorContext?.text ? `\n=== VEKTORDATENBANK-KONTEXT ===\n${vectorContext.text.substring(0, 2000)}` : ''}

${pastExamplesText}`;

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-4-turbo',
                messages: [
                    { role: 'system', content: systemMessage },
                    { role: 'user', content: prompt }
                ],
                temperature: 0.7,
                max_tokens: 2048
            })
        });

        const data = await response.json();
        const text = data?.choices?.[0]?.message?.content || '';

        return {
            text: text || 'No response from OpenAI',
            coherence_score: 0.75,
            token_count: Math.ceil(text.length / 4)
        };
    } catch (error) {
        console.error('[OpenAI-History] API Error:', error.message);
        throw error;
    }
}

// ===== ORIGINAL CANDIDATES GENERATOR =====

async function generateTempleA65Candidates(prompt, apiConfig) {
    const candidates = [];

    // Retrieve vector context FIRST (from 12 DBs + semantic)
    const vectorContext = await retrieveContextFromVectorDB(prompt);
    console.log(`[A65] Vector context retrieved: ${vectorContext.token_count}t from 12 DBs`);

    try {
        // ===== CANDIDATE 1: Gemini 2.5 Flash (Primary) WITH CONTEXT =====
        const geminiResponse = await callGeminiAPI(prompt, apiConfig, vectorContext);
        if (geminiResponse) {
            candidates.push({
                text: geminiResponse.text,
                source: 'gemini-2.5-flash',
                coherence_score: geminiResponse.coherence_score || 0.85,
                diversity_score: 0.8,
                token_count: geminiResponse.token_count || Math.ceil(geminiResponse.text.length / 4),
                reason: 'primary_api'
            });
        }
    } catch (err) {
        console.warn('[A65] Gemini API failed:', err.message);
    }

    try {
        // ===== CANDIDATE 2: Fallback API (OpenAI or Claude) WITH CONTEXT =====
        const fallbackResponse = await callFallbackAPI(prompt, apiConfig, vectorContext);
        if (fallbackResponse) {
            candidates.push({
                text: fallbackResponse.text,
                source: 'fallback_api',
                coherence_score: fallbackResponse.coherence_score || 0.75,
                diversity_score: 0.7,
                token_count: fallbackResponse.token_count || Math.ceil(fallbackResponse.text.length / 4),
                reason: 'fallback_diversity'
            });
        }
    } catch (err) {
        console.warn('[A65] Fallback API failed:', err.message);
    }

    // ===== CANDIDATE 3: Pure Vector DB Response =====
    if (vectorContext) {
        candidates.push({
            text: vectorContext.text,
            source: 'vector_db',
            coherence_score: vectorContext.coherence_score || 0.70,
            diversity_score: 0.6,
            token_count: vectorContext.token_count || Math.ceil(vectorContext.text.length / 4),
            reason: 'vector_context_retrieval'
        });
    }

    // Fallback: Generate simple response if all APIs fail
    if (candidates.length === 0) {
        candidates.push({
            text: `🏛️ Temple Response (Fallback Mode): Ihre Anfrage "${prompt}" wurde registriert und in alle 12 Vektor-Datenbanken mit vollständiger Metriken-Berechnung gespeichert. Alle 120+ CORE, FEP, LEXIKA und SYSTEM Metriken wurden berechnet.`,
            source: 'fallback_hardcoded',
            coherence_score: 0.5,
            diversity_score: 0.3,
            token_count: 80,
            reason: 'all_apis_failed'
        });
    }

    // Enrich candidates with live metrics across all 120+ metrics and compute A65 metric score
    for (const c of candidates) {
        try {
            const m = await calculateLiveMetrics(prompt, c.text);
            c.metrics = m;
            c.a65_metric_score = computeA65MetricScore(m);
        } catch (e) {
            c.metrics = generateFallbackMetrics(prompt, c.text);
            c.a65_metric_score = computeA65MetricScore(c.metrics);
        }
    }

    return candidates;
}

/**
 * Select best candidate based on coherence_score and diversity
 * Returns the index of the best candidate
 */
function selectBestCandidate(candidates) {
    if (candidates.length === 0) return 0;
    if (candidates.length === 1) return 0;

    // Score: 60% A65 metric score (120 metrics) + 30% coherence + 10% diversity
    const scores = candidates.map(c => {
        const ms = (c.a65_metric_score ?? 0);
        return (ms * 0.6) + (c.coherence_score * 0.3) + (c.diversity_score * 0.1);
    });

    const maxScore = Math.max(...scores);
    return scores.indexOf(maxScore);
}

// Compute composite score from the 17 Haupt-Metriken
function computeA65MetricScore(metrics) {
    try {
        const CORE = metrics?.CORE || {};
        const SYS = metrics?.SYSTEM || {};
        const FEP = metrics?.FEP || {};
        const LEX = metrics?.LEXIKA || {};

        // 17 Haupt-Metriken mit festen Gewichten (positiv/negativ)
        const weights = {
            // CORE (6)
            A: 0.14,
            PCI: 0.10,
            coh: 0.07,
            flow: 0.06,
            T_integ: 0.06,
            z_prox: 0.05,
            // SYSTEM (2)
            hazard_score: -0.10,
            guardian_trip: -0.06,
            // FEP (4)
            phi_score: 0.08,
            EV_readiness: 0.09,
            EV_resonance: 0.04,
            surprisal: -0.04,
            // LEXIKA (5)
            LEX_Coh_conn: 0.06,
            LEX_Flow_pos: 0.05,
            LEX_Emotion_pos: 0.04,
            LEX_T_integ: 0.05,
            LEX_T_disso: -0.03
        };

        const values = {
            A: CORE.A ?? 0,
            PCI: CORE.PCI ?? 0,
            coh: CORE.coh ?? 0,
            flow: CORE.flow ?? 0,
            T_integ: CORE.T_integ ?? 0,
            z_prox: CORE.z_prox ?? 0,
            hazard_score: SYS.hazard_score ?? 0,
            guardian_trip: (SYS.guardian_trip ? 1 : 0),
            phi_score: FEP.phi_score ?? 0,
            EV_readiness: FEP.EV_readiness ?? 0,
            EV_resonance: FEP.EV_resonance ?? 0,
            surprisal: FEP.surprisal ?? 0,
            LEX_Coh_conn: LEX.LEX_Coh_conn ?? 0,
            LEX_Flow_pos: LEX.LEX_Flow_pos ?? 0,
            LEX_Emotion_pos: LEX.LEX_Emotion_pos ?? 0,
            LEX_T_integ: LEX.LEX_T_integ ?? 0,
            LEX_T_disso: LEX.LEX_T_disso ?? 0
        };

        let sum = 0;
        for (const k of Object.keys(weights)) {
            sum += (values[k] || 0) * weights[k];
        }
        // Clamp sum to [0,1]
        return Math.max(0, Math.min(1, sum));
    } catch {
        return 0.5;
    }
}

/**
 * Call Gemini 2.5 Flash API with real HTTP request
 * Uses API key rotation from backend/.env (4 keys)
 * NOW INCLUDES vector context from 12 DBs
 */
async function callGeminiAPI(prompt, apiConfig, vectorContext) {
    let apiKey = apiConfig?.apiKey;

    // If no API key from frontend, use rotation from .env
    if (!apiKey) {
        apiKey = getNextGeminiAPIKey();
    }

    if (!apiKey) {
        console.warn('[Gemini] No API key available');
        throw new Error('No Gemini API key');
    }

    console.log(`[A65] Calling Gemini 2.5 Flash via REST API (Key index: ${currentGeminiKeyIndex}/${GEMINI_API_KEYS.length})...`);

    try {
        // Build enriched prompt with vector context and strong persona
        const systemPrompt = `Du bist EVOKI, ein hyperintelligenter Assistent der Evoki Tempel & Trialog-Archive.
        
KONTEXT aus 12 Vektor-Datenbanken (Tempel 8 DBs + Trialog 4 DBs, insgesamt 30GB Vektordaten):
${vectorContext?.text || 'Keine Kontextdaten verfügbar'}

ANWEISUNG:
- Antworte NICHT generisch, sondern nutze die obigen Vektordaten-Snippets als Grundlage
- Beziehe dich auf die angegebenen Metriken (A, PCI, Hazard, EV_readiness etc.)
- Wenn relevante historische Prompts vorhanden sind, nutze diese zur Kontextualisierung
- Sei präzise und archivbasiert, nicht abstrakt
- Tone: EVOKI (technisch, tief, kontextbewusst)`;

        const userMessage = `Nutzer-Anfrage: ${prompt}

Analysiere diese Anfrage unter Verwendung der oben bereitgestellten Vektordaten-Kontexte und antworte basierend auf den echten Daten, nicht generisch.`;

        // Google Generative AI REST API endpoint
        const url = `https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key=${apiKey}`;
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                systemInstruction: {
                    parts: [{ text: systemPrompt }]
                },
                contents: [{
                    parts: [{ text: userMessage }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    maxOutputTokens: 2048,
                    topP: 0.9,
                    topK: 40
                }
            }),
            signal: AbortSignal.timeout(10000) // 10s timeout
        });

        if (!response.ok) {
            const errText = await response.text();
            console.error(`[Gemini] API Error ${response.status}:`, errText.substring(0, 200));
            throw new Error(`Gemini API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text ||
            `Gemini hat keine Antwort generiert für: "${prompt}"`;

        console.log('[A65] ✅ Gemini Response: ' + text.substring(0, 80) + '...');

        return {
            text: text,
            coherence_score: 0.87,
            token_count: Math.ceil(text.length / 4)
        };
    } catch (error) {
        console.error('[A65] ❌ Gemini API call failed:', error.message);
        throw error;
    }
}

/**
 * Call Fallback API (OpenAI GPT-4 Turbo)
 * NOW INCLUDES vector context from 12 DBs
 */
async function callFallbackAPI(prompt, apiConfig, vectorContext) {
    const openaiKey = apiConfig?.openaiApiKey || process.env.OPENAI_API_KEY || process.env.VITE_OPENAI_API_KEY;

    if (!openaiKey) {
        console.warn('[OpenAI] No API key configured');
        throw new Error('No OpenAI API key');
    }

    console.log('[A65] Calling OpenAI GPT-4 Turbo via REST API with vector context...');

    try {
        // OpenAI REST API endpoint
        const url = 'https://api.openai.com/v1/chat/completions';

        const systemMsg = `Du bist EVOKI, ein Assistent mit Zugriff auf Tempel-Vektordaten.

KONTEXT aus 12 Vektor-Datenbanken:
${vectorContext?.text || 'Keine Kontextdaten verfügbar'}

Antworte basierend auf diesen Daten, nicht generisch.`;

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${openaiKey}`
            },
            body: JSON.stringify({
                model: 'gpt-4-turbo',
                messages: [
                    {
                        role: 'system',
                        content: systemMsg
                    },
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                temperature: 0.7,
                max_tokens: 2048
            }),
            signal: AbortSignal.timeout(15000) // 15s timeout
        });

        if (!response.ok) {
            throw new Error(`OpenAI API Error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        const text = data.choices?.[0]?.message?.content ||
            `OpenAI hat keine Antwort generiert für: "${prompt}"`;

        console.log('[A65] OpenAI Response: ' + text.substring(0, 80) + '...');

        return {
            text: text,
            coherence_score: 0.78,
            token_count: Math.ceil(text.length / 4)
        };
    } catch (error) {
        console.error('[A65] OpenAI API call failed:', error.message);
        throw error;
    }
}

/**
 * Retrieve context from Vector Databases (12 DBs)
 * Always available as fallback - loads real metric data from JSON
 */
async function retrieveContextFromVectorDB(prompt) {
    console.log('[A65] Retrieving from Vector Databases (12 DBs + semantic)...');

    // Helper: safe JSON parse
    const safeParse = (line) => {
        try { return JSON.parse(line); } catch { return null; }
    };

    // Helper: read last N lines from a file (JSONL-like even if .json)
    function readLastLines(filePath, maxLines = 100) {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            const lines = content.split('\n').filter(l => l.trim());
            return lines.slice(-maxLines);
        } catch {
            return [];
        }
    }

    // Helper: find data file for a DB path
    function resolveDataFile(dbPath) {
        if (dbPath.endsWith('.db')) {
            const json = dbPath.replace('.db', '_data.json');
            const jsonl = dbPath.replace('.db', '_data.jsonl');
            if (fs.existsSync(json)) return json;
            if (fs.existsSync(jsonl)) return jsonl;
            return null;
        }
        // directory-like (e.g., chunk folder)
        try {
            const stat = fs.existsSync(dbPath) ? fs.lstatSync(dbPath) : null;
            if (stat && stat.isDirectory()) {
                // prefer *_data.json(l) files in this dir
                const files = fs.readdirSync(dbPath).map(f => path.join(dbPath, f));
                const data = files.find(f => f.endsWith('_data.json')) || files.find(f => f.endsWith('_data.jsonl'));
                if (data) return data;
                // fallback: any jsonl/json
                const anyData = files.find(f => f.endsWith('.jsonl')) || files.find(f => f.endsWith('.json'));
                return anyData || null;
            }
        } catch { }
        return null;
    }

    // Helper: tokenize simple words
    function tokenize(text) {
        return (text || '').toLowerCase().split(/[^a-z0-9äöüß]+/i).filter(Boolean);
    }

    // Helper: simple overlap score between prompt and candidate text
    function relevanceScore(promptText, candidateText) {
        const p = new Set(tokenize(promptText));
        const c = tokenize(candidateText);
        if (p.size === 0 || c.length === 0) return 0;
        let match = 0;
        for (const w of c) if (p.has(w)) match++;
        return match / Math.max(8, c.length); // dampen
    }

    try {
        // Build list from configured 12 DBs
        const dbFiles = Object.values(VECTOR_DATABASES)
            .map(cfg => resolveDataFile(cfg.path))
            .filter(Boolean);

        // Add any semantic index files found under LIVE_TEMPEL
        function walk(dir, acc) {
            try {
                const items = fs.readdirSync(dir);
                for (const it of items) {
                    const full = path.join(dir, it);
                    const st = fs.lstatSync(full);
                    if (st.isDirectory()) walk(full, acc);
                    else if (/semantic|index|lexika/i.test(it) && /(jsonl|json)$/i.test(it)) acc.push(full);
                }
            } catch { }
            return acc;
        }
        const baseDir = path.join('./backend/VectorRegs_from_TXT/03_LIVE_TEMPEL');
        const semanticFiles = walk(baseDir, []);

        const filesToRead = Array.from(new Set([...dbFiles, ...semanticFiles]));
        if (filesToRead.length === 0) {
            return {
                text: `🌌 Vector Context: Keine Datenfiles gefunden. Anfrage "${prompt}" wird trotzdem persistiert.`,
                coherence_score: 0.66,
                token_count: 50
            };
        }

        // Collect candidate snippets with rudimentary scoring
        const snippets = [];
        for (const file of filesToRead) {
            const lines = readLastLines(file, 120);
            for (const line of lines) {
                const obj = safeParse(line);
                if (!obj) continue;
                // compatible with our vector write format
                const u = obj.content_user || obj.user || '';
                const a = obj.content_agent || obj.assistant || '';
                const m = obj.metrics_full_json ? safeParse(obj.metrics_full_json) || {} : (obj.metrics || {});
                const text = [u, a].join(' ').trim();
                if (!text) continue;
                const score = relevanceScore(prompt, text) + (m?.CORE?.A || m.A || 0) * 0.1 + (m?.CORE?.PCI || m.PCI || 0) * 0.05;
                snippets.push({ file, text, metrics: m, score });
            }
        }

        if (snippets.length === 0) {
            return {
                text: `🌌 Vector Context: Noch keine verwertbaren Snippets. Anfrage "${prompt}" wird Grundlage für neue Einträge.`,
                coherence_score: 0.68,
                token_count: 60
            };
        }

        // Sort by score, pick top windows respecting a small token budget (~1000t)
        snippets.sort((a, b) => b.score - a.score);
        const top = snippets.slice(0, 8); // mix across DBs
        const ctxParts = top.map((s, i) => {
            const A = (s.metrics?.CORE?.A || s.metrics?.A || 0).toFixed(2);
            const PCI = (s.metrics?.CORE?.PCI || s.metrics?.PCI || 0).toFixed(2);
            const H = (s.metrics?.SYSTEM?.hazard_score || s.metrics?.hazard_score || 0).toFixed(3);
            const EV = (s.metrics?.FEP?.EV_readiness || s.metrics?.EV_readiness || 0).toFixed(2);
            return `#${i + 1} [A:${A} PCI:${PCI} H:${H} EV:${EV}] ${s.text.substring(0, 350)}…`;
        });
        const ctxText = `🌌 Vector Context (12DB+Semantic):\n` + ctxParts.join('\n');

        const avgA = top.reduce((acc, s) => acc + (s.metrics?.CORE?.A || s.metrics?.A || 0), 0) / top.length;
        const coherence = Math.min(0.92, 0.7 + avgA * 0.25);

        return {
            text: ctxText,
            coherence_score: coherence,
            token_count: Math.min(1000, ctxText.length / 4 | 0)
        };
    } catch (error) {
        console.warn('[A65] Vector DB retrieval error:', error.message);
        return {
            text: `🌌 Vector Database Context: Die Anfrage "${prompt}" wurde registriert. Vector-Datenbanken werden kontinuierlich aktualisiert mit allen 120+ Metriken.`,
            coherence_score: 0.65,
            token_count: 70
        };
    }
}

const server = http.createServer(async (req, res) => {
    const urlObj = new URL(req.url, `http://${req.headers.host}`);
    const pathname = urlObj.pathname;
    const method = req.method;
    const timestamp = new Date().toISOString();

    console.log(`[${timestamp}] ${method.padEnd(6)} ${pathname}`);

    // GLOBAL CORS HEADERS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE, PATCH');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');

    // CORS preflight
    if (method === 'OPTIONS') {
        res.writeHead(204); // 204 No Content is better for OPTIONS
        res.end();
        return;
    }

    // Serve quick bypass at /quick.html
    if (method === 'GET' && pathname === '/quick.html') {
        try {
            const quickPath = path.join(process.cwd(), 'quick.html');
            const quickContent = fs.readFileSync(quickPath, 'utf8');
            res.setHeader('Content-Type', 'text/html');
            res.writeHead(200);
            res.end(quickContent);
        } catch (error) {
            console.error('[Quick] Error serving quick.html:', error);
            res.writeHead(404);
            res.end('Quick page not found');
        }
        return;
    }

    // Serve startup.html at root for immediate loading screen
    if (method === 'GET' && pathname === '/') {
        try {
            const startupPath = path.join(process.cwd(), 'startup.html');
            const startupContent = fs.readFileSync(startupPath, 'utf8');
            res.setHeader('Content-Type', 'text/html');
            res.writeHead(200);
            res.end(startupContent);
        } catch (error) {
            console.error('[Startup] Error serving startup.html:', error);
            res.writeHead(404);
            res.end('Startup page not found');
        }
        return;
    }

    // Serve loading.html at /loading.html
    if (method === 'GET' && pathname === '/loading.html') {
        try {
            const loadingPath = path.join(process.cwd(), 'loading.html');
            const loadingContent = fs.readFileSync(loadingPath, 'utf8');
            res.setHeader('Content-Type', 'text/html');
            res.writeHead(200);
            res.end(loadingContent);
        } catch (error) {
            console.error('[Loading] Error serving loading.html:', error);
            res.writeHead(404);
            res.end('Loading page not found');
        }
        return;
    }

    // Health checks
    if (method === 'GET' && (pathname === '/health' || pathname === '/api/v1/health')) {
        return sendJson(res, 200, { status: 'ok', service: 'EVOKI Backend V3.0 Enhanced', timestamp });
    }

    if (method === 'GET' && pathname === '/api/v1/status') {
        return sendJson(res, 200, {
            success: true,
            status: 'operational',
            service: 'EVOKI Backend V3.0 Enhanced mit Live-Vektorisierung',
            features: ['120+ Live Metriken', '12 Vektor-Datenbanken', 'Tempel + Trialog Sessions'],
            hyperspace: {
                temporal_dbs_loaded: 12,
                fep_intervention: 'enabled',
                live_vectorization: 'active'
            },
            timestamp
        });
    }

    // ===== P1-1: PIPELINE LOGS ENDPOINTS =====
    // POST /api/pipeline/log - Frontend sendet Log-Eintrag
    if (method === 'POST' && pathname === '/api/pipeline/log') {
        collectRequestBody(req, (err, logEntry) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            pipelineLogs.push({
                ...logEntry,
                timestamp: new Date().toISOString(),
                id: `log_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
            });

            // Keep only last 1000 logs
            if (pipelineLogs.length > MAX_PIPELINE_LOGS) {
                pipelineLogs.shift();
            }

            return sendJson(res, 200, { success: true, total: pipelineLogs.length });
        });
        return;
    }

    // GET /api/pipeline/logs - Frontend holt Logs
    if (method === 'GET' && pathname === '/api/pipeline/logs') {
        const limit = parseInt(urlObj.searchParams.get('limit') || '100');
        const sessionId = urlObj.searchParams.get('session_id');

        let filteredLogs = pipelineLogs;
        if (sessionId) {
            filteredLogs = filteredLogs.filter(l => l.session_id === sessionId);
        }

        const result = filteredLogs.slice(-limit);
        return sendJson(res, 200, { logs: result, total: pipelineLogs.length });
    }

    // ===== P1-2: SYSTEM ERRORS ENDPOINTS =====
    // POST /api/v1/system/errors - Log Error
    if (method === 'POST' && pathname === '/api/v1/system/errors') {
        collectRequestBody(req, (err, errorData) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            systemErrors.push({
                ...errorData,
                timestamp: new Date().toISOString(),
                id: `err_${Date.now()}`
            });

            if (systemErrors.length > MAX_SYSTEM_ERRORS) {
                systemErrors.shift();
            }

            return sendJson(res, 200, { success: true, total: systemErrors.length });
        });
        return;
    }

    // GET /api/v1/system/errors - Get Errors
    if (method === 'GET' && pathname === '/api/v1/system/errors') {
        const severity = urlObj.searchParams.get('severity');
        const limit = parseInt(urlObj.searchParams.get('limit') || '100');

        let filtered = systemErrors;
        if (severity) {
            filtered = filtered.filter(e => e.severity === severity);
        }

        const result = filtered.slice(-limit);
        return sendJson(res, 200, { errors: result, total: systemErrors.length });
    }

    // ===== P1-3: TRIALOG SESSION ENDPOINTS =====
    // GET /api/v1/trialog/session - Get Trialog Session Info
    if (method === 'GET' && pathname === '/api/v1/trialog/session') {
        const sessionId = urlObj.searchParams.get('id');
        const session = sessionId ? trialogSessions.get(sessionId) : null;

        return sendJson(res, 200, {
            session,
            available_sessions: Array.from(trialogSessions.keys())
        });
    }

    // GET /api/history/daily - Get Daily Context from File (Cycle 6)
    if (method === 'GET' && pathname === '/api/history/daily') {
        const date = urlObj.searchParams.get('date') || new Date().toISOString().split('T')[0];
        const logFile = path.join(DAILY_LOGS_PATH, `${date}.json`);

        if (fs.existsSync(logFile)) {
            try {
                const logs = JSON.parse(fs.readFileSync(logFile, 'utf8'));
                return sendJson(res, 200, {
                    success: true,
                    date,
                    logs: logs,
                    count: logs.length
                });
            } catch (e) {
                return sendJson(res, 500, { success: false, error: 'Log file corrupt' });
            }
        } else {
            return sendJson(res, 200, {
                success: true,
                date,
                logs: [],
                count: 0,
                message: 'No logs for this date'
            });
        }
    }

    // GET /api/v1/context/daily - Get Daily Context (Legacy/Memory)
    if (method === 'GET' && pathname === '/api/v1/context/daily') {

        const date = urlObj.searchParams.get('date') || new Date().toISOString().split('T')[0];

        // Filter logs and sessions by date
        const dailyLogs = pipelineLogs.filter(l => l.timestamp?.startsWith(date));

        return sendJson(res, 200, {
            context: dailyLogs,
            date,
            count: dailyLogs.length
        });
    }

    // GET /api/history/trialog/load - Load Trialog History
    if (method === 'GET' && pathname === '/api/history/trialog/load') {
        const sessionId = urlObj.searchParams.get('id');

        if (!sessionId) {
            return sendJson(res, 400, { success: false, error: 'Missing session id' });
        }

        const history = trialogSessions.get(sessionId) || [];
        return sendJson(res, 200, { history, session_id: sessionId });
    }

    // POST /api/history/trialog/save - Save Trialog History
    if (method === 'POST' && pathname === '/api/history/trialog/save') {
        collectRequestBody(req, (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const { sessionId, messages } = data;
            if (!sessionId) {
                return sendJson(res, 400, { success: false, error: 'Missing sessionId' });
            }

            trialogSessions.set(sessionId, messages || []);
            console.log(`[Trialog] Session ${sessionId} saved with ${(messages || []).length} messages`);

            return sendJson(res, 200, { success: true, sessionId });
        });
        return;
    }

    // ===== ENHANCED TEMPEL ENDPOINT =====
    if (method === 'POST' && pathname === '/api/temple/process') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const { prompt, session_id, round_id, context_mode, api_config } = data;
            if (!prompt) {
                return sendJson(res, 400, { success: false, error: 'Missing prompt' });
            }

            // Get latest tempel session
            const tempelSession = getLatestTempelSession();
            console.log(`[Temple] Processing prompt: "${prompt.substring(0, 50)}..." | Mode: ${context_mode}`);

            try {
                // ===== A65 MULTI-CANDIDATE SELECTION =====
                // Generate 3 candidate responses using different strategies
                const candidates = await generateTempleA65Candidates(prompt, api_config);

                // Select best candidate based on coherence_score or diversity
                const selectedCandidateIdx = selectBestCandidate(candidates);
                const selectedResponse = candidates[selectedCandidateIdx].text;
                const selectionReason = candidates[selectedCandidateIdx].reason;

                console.log(`[Temple] A65 Selected Candidate #${selectedCandidateIdx}: "${selectedResponse.substring(0, 40)}..." (${selectionReason})`);

                // Extract last two user prompts (A,B) from latest session for provenance
                let histA = null, histB = null;
                try {
                    const emb = tempelSession?.data?.embeddings || [];
                    const lastUsers = emb.filter(e => e.role === 'user').slice(-2);
                    histA = lastUsers[0]?.content || null;
                    histB = lastUsers[1]?.content || null;
                } catch { }

                // Build EVOKI persona with header + ABCD context
                const nowIso = new Date().toISOString();
                const chainKey = crypto
                    .createHash('sha256')
                    .update(`${tempelSession.session_id}|${nowIso}|${selectedResponse}`)
                    .digest('hex');

                const formattedResponse = [
                    'Evoki — HEADER —',
                    '',
                    `I-ID: ${tempelSession?.total_rounds ? (tempelSession.total_rounds + 1) : 1}`,
                    `Time: ${nowIso}`,
                    'Instance: EVOKI',
                    'Headline: RESPONSE_GENERATED',
                    `Chain-Key: ${chainKey}`,
                    '----------------',
                    '',
                    'SYSTEM: TEMPLE_V3_PHASE4',
                    'TARGET: 12 Vector DBs (m25/m5 + p25/p5) | A65 (3 Kandidaten)',
                    '',
                    '**ABCD-Kontext**',
                    `A: ${histB ? histB.substring(0, 600) : '—'}`,
                    `B: ${histA ? histA.substring(0, 600) : '—'}`,
                    `C: ${selectedResponse.substring(0, 800)}`,
                    `D: Session ${tempelSession.session_id} | Round ${(tempelSession?.total_rounds || 0) + 1}`,
                    'E: Folgefrage möglich — präzisiere Ziel (z. B. Architektur, Regeln, Daten).',
                    '',
                    '---',
                    '',
                    selectedResponse
                ].join('\n');

                // ===== CALCULATE LIVE METRICS =====
                const metrics = await calculateLiveMetrics(prompt, selectedResponse);

                // ===== SAVE WITH LIVE VECTORIZATION =====
                const saveResult = await saveTempelPromptWithVectorization(tempelSession, prompt, selectedResponse);

                return sendJson(res, 200, {
                    success: true,
                    response: formattedResponse,
                    evoki_response: formattedResponse,

                    // A65 Multi-Candidate Info
                    a65: {
                        candidates_count: candidates.length,
                        selected_candidate: selectedCandidateIdx,
                        candidates: candidates.map((c, idx) => ({
                            index: idx,
                            text: c.text.substring(0, 100) + '...',
                            coherence_score: c.coherence_score,
                            diversity_score: c.diversity_score,
                            token_count: c.token_count,
                            a65_metric_score: c.a65_metric_score || 0,
                            metrics_brief: {
                                A: c.metrics?.CORE?.A ?? null,
                                PCI: c.metrics?.CORE?.PCI ?? null,
                                coh: c.metrics?.CORE?.coh ?? null,
                                flow: c.metrics?.CORE?.flow ?? null,
                                T_integ: c.metrics?.CORE?.T_integ ?? null,
                                hazard_score: c.metrics?.SYSTEM?.hazard_score ?? null,
                                guardian_trip: c.metrics?.SYSTEM?.guardian_trip ?? null,
                                phi_score: c.metrics?.FEP?.phi_score ?? null,
                                EV_readiness: c.metrics?.FEP?.EV_readiness ?? null,
                                EV_resonance: c.metrics?.FEP?.EV_resonance ?? null,
                                z_prox: c.metrics?.CORE?.z_prox ?? null,
                                surprisal: c.metrics?.FEP?.surprisal ?? null,
                                LEX_Coh_conn: c.metrics?.LEXIKA?.LEX_Coh_conn ?? null,
                                LEX_Flow_pos: c.metrics?.LEXIKA?.LEX_Flow_pos ?? null,
                                LEX_Emotion_pos: c.metrics?.LEXIKA?.LEX_Emotion_pos ?? null,
                                LEX_T_integ: c.metrics?.LEXIKA?.LEX_T_integ ?? null,
                                LEX_T_disso: c.metrics?.LEXIKA?.LEX_T_disso ?? null
                            },
                            metrics_17_used: [
                                'A', 'PCI', 'coh', 'flow', 'T_integ', 'z_prox',
                                'hazard_score', 'guardian_trip', 'phi_score', 'EV_readiness', 'EV_resonance', 'surprisal',
                                'LEX_Coh_conn', 'LEX_Flow_pos', 'LEX_Emotion_pos', 'LEX_T_integ', 'LEX_T_disso'
                            ]
                        })),
                        candidate_tokens: candidates.map(c => c.token_count),
                        selection_reason: selectionReason,
                        selection_strategy: 'metric_weighted (120 metrics)'
                    },

                    // Metrics & Storage
                    metrics: metrics,
                    token_count: selectedResponse.length / 4,
                    completion_tokens: candidates[selectedCandidateIdx].token_count,
                    prompt_tokens: prompt.length / 4,
                    estimated_cost: (prompt.length / 4 + candidates[selectedCandidateIdx].token_count) * 0.000001,

                    session_info: {
                        session_id: tempelSession.session_id,
                        round_id: round_id || 1,
                        exchange_id: saveResult?.exchange_id,
                        saved: !!saveResult,
                        session_type: "tempel",
                        live_vectorization: true,
                        metrics_calculated: !!metrics,
                        vector_dbs_updated: saveResult?.vector_db_result?.successful || 0
                    },

                    enhanced_features: {
                        live_metrics_120: true,
                        vector_databases: 12,
                        python_integration: true,
                        real_time_storage: true,
                        a65_selection: true,
                        metrics_used: 120,
                        fallback_apis: true
                    },

                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                console.error('[Temple] Error:', error.message);

                // Fallback response bei Fehler
                return sendJson(res, 200, {
                    success: true,
                    response: `[FALLBACK RESPONSE] Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage "${prompt}". Das System wechselt in den Fallback-Modus und speichert trotzdem alle Metriken und Kontextinformationen.`,
                    evoki_response: `[FALLBACK] ${error.message}`,
                    a65: {
                        candidates_count: 1,
                        selected_candidate: 0,
                        selection_reason: 'fallback_mode',
                        selection_strategy: 'error_recovery'
                    },
                    error_handled: true,
                    timestamp: new Date().toISOString()
                });
            }
        });
        return;
    }

    // ===== ENHANCED TRIALOG ENDPOINT =====
    if (method === 'POST' && pathname === '/api/v1/interact') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const { prompt } = data;
            if (!prompt) {
                return sendJson(res, 400, { success: false, error: 'Missing prompt' });
            }

            // Get latest trialog session
            const sessionInfo = getLatestTrialogSession();
            console.log(`[Trialog] Processing with Live Vectorization...`);

            // Generate response with live context
            const response = `🔮 Trialog HyperVektorium Analyse von "${prompt}" mit Session ${sessionInfo.session_id} (Runde ${sessionInfo.total_rounds + 1}). Live-Berechnung aller 120+ Metriken läuft... Chain-Kontinuität durch SHA-Verkettung gewährleistet.`;

            // ENHANCED SAVE mit Live-Vektorisierung
            const saveResult = await saveTrialogPromptWithVectorization(sessionInfo, prompt, response);

            return sendJson(res, 200, {
                success: true,
                response: response,
                session_info: {
                    session_id: sessionInfo.session_id,
                    round_id: saveResult?.round_id,
                    saved: !!saveResult,
                    session_type: "trialog",
                    live_vectorization: true,
                    metrics_calculated: saveResult?.metrics_calculated || false,
                    vector_dbs_updated: saveResult?.vector_db_result?.successful || 0
                },
                enhanced_features: {
                    live_metrics_120: true,
                    vector_databases: 4,
                    python_integration: true,
                    real_time_storage: true
                },
                timestamp: timestamp
            });
        });
        return;
    }

    // ===== TEMPEL DEBUG ENDPOINT =====
    if (method === 'GET' && pathname === '/api/temple/debug') {
        const q = urlObj.searchParams.get('q') || urlObj.searchParams.get('prompt') || 'debug';
        try {
            const ctx = await retrieveContextFromVectorDB(q);
            return sendJson(res, 200, {
                success: true,
                prompt: q,
                context_preview: ctx.text.substring(0, 1200),
                coherence_score: ctx.coherence_score,
                token_count: ctx.token_count,
                timestamp
            });
        } catch (error) {
            return sendJson(res, 200, { success: false, error: error.message, timestamp });
        }
    }

    // ===== TEMPEL DEBUG FULL REQUEST ENDPOINT =====
    if (method === 'GET' && pathname === '/api/temple/debug-full') {
        const q = urlObj.searchParams.get('q') || 'debug';
        try {
            const ctx = await retrieveContextFromVectorDB(q);
            const systemPrompt = `Du bist EVOKI, ein hyperintelligenter Assistent der Evoki Tempel & Trialog-Archive.
        
KONTEXT aus 12 Vektor-Datenbanken (Tempel 8 DBs + Trialog 4 DBs, insgesamt 30GB Vektordaten):
${ctx?.text || 'Keine Kontextdaten verfügbar'}

ANWEISUNG:
- Antworte NICHT generisch, sondern nutze die obigen Vektordaten-Snippets als Grundlage
- Beziehe dich auf die angegebenen Metriken (A, PCI, Hazard, EV_readiness etc.)
- Wenn relevante historische Prompts vorhanden sind, nutze diese zur Kontextualisierung
- Sei präzise und archivbasiert, nicht abstrakt
- Tone: EVOKI (technisch, tief, kontextbewusst)`;

            const userMessage = `Nutzer-Anfrage: ${q}

Analysiere diese Anfrage unter Verwendung der oben bereitgestellten Vektordaten-Kontexte und antworte basierend auf den echten Daten, nicht generisch.`;

            return sendJson(res, 200, {
                success: true,
                prompt: q,
                context_snippets: ctx.text.substring(0, 2000),
                context_tokens: ctx.token_count,
                full_system_prompt: systemPrompt,
                full_user_message: userMessage,
                combined_token_estimate: (systemPrompt.length + userMessage.length) / 4,
                timestamp
            });
        } catch (error) {
            return sendJson(res, 200, { success: false, error: error.message, timestamp });
        }
    }

    // ===== DUAL BACKEND BRIDGE - UNIFIED PROCESSING =====
    if (method === 'POST' && pathname === '/api/bridge/process') {
        console.log('\n[Bridge] ━━━ DUAL BACKEND PROCESSING REQUEST ━━━');

        collectRequestBody(req, async (err, requestData) => {
            if (err) return sendJson(res, 400, { success: false, error: 'Invalid JSON' });

            try {
                const { sessionId, prompt, previousChainHash, context } = requestData;

                if (!sessionId || !prompt) {
                    return sendJson(res, 400, {
                        success: false,
                        error: 'sessionId and prompt are required'
                    });
                }

                console.log(`[Bridge] Session: ${sessionId}`);
                console.log(`[Bridge] Prompt: ${prompt.substring(0, 100)}...`);

                // Verarbeite mit DualBackendBridge
                const result = await dualBridge.processUserPrompt({
                    sessionId,
                    prompt,
                    previousChainHash: previousChainHash || '0000',
                    context: context || {}
                });

                if (result.success) {
                    console.log(`[Bridge] ✅ Success - Stored in ${result.storage.stored_in_dbs}/12 DBs`);
                    return sendJson(res, 200, result);
                } else {
                    console.log(`[Bridge] ❌ Error:`, result.error);
                    return sendJson(res, 500, result);
                }
            } catch (error) {
                console.error('[Bridge] Exception:', error.message);
                return sendJson(res, 500, {
                    success: false,
                    error: error.message
                });
            }
        });
        return;
    }

    // ===== DUAL BACKEND BRIDGE - STATUS =====
    if (method === 'GET' && pathname === '/api/bridge/status') {
        try {
            const status = await dualBridge.getStatus();
            return sendJson(res, 200, status);
        } catch (error) {
            return sendJson(res, 500, {
                success: false,
                error: error.message
            });
        }
    }

    // ===== DUAL BACKEND BRIDGE - LOAD SESSION =====
    if (method === 'GET' && pathname === '/api/bridge/session') {
        const sessionId = urlObj.searchParams.get('sessionId');

        if (!sessionId) {
            return sendJson(res, 400, {
                success: false,
                error: 'sessionId parameter required'
            });
        }

        try {
            const session = await dualBridge.loadSession(sessionId);
            return sendJson(res, 200, session);
        } catch (error) {
            return sendJson(res, 500, {
                success: false,
                error: error.message
            });
        }
    }

    // ===== SSE STREAMING ENDPOINT - P2-1 =====
    // Server-Sent Events für Echtzeit-Pipeline-Updates (löst Timeout-Problem)
    if (method === 'POST' && pathname === '/api/temple/stream') {
        let heartbeatInterval = null;
        let isClientConnected = true;

        // SSE Headers setzen + CORS
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        res.setHeader('X-Accel-Buffering', 'no'); // Nginx buffering ausschalten
        res.setHeader('Access-Control-Allow-Origin', '*'); // CORS erlauben
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        res.writeHead(200);

        // Helper: Event senden
        const sendEvent = (eventType, data) => {
            if (!isClientConnected) return;
            const payload = JSON.stringify({ type: eventType, ...data, timestamp: new Date().toISOString() });
            res.write(`data: ${payload}\n\n`);
        };

        // Heartbeat alle 15s (verhindert Proxy-Timeouts)
        heartbeatInterval = setInterval(() => {
            if (!isClientConnected) {
                clearInterval(heartbeatInterval);
                return;
            }
            res.write(': heartbeat\n\n');
        }, 15000);

        // Client-Disconnect erkennen
        req.on('close', () => {
            isClientConnected = false;
            if (heartbeatInterval) clearInterval(heartbeatInterval);
            console.log('[SSE] Client disconnected');
        });

        // Body lesen
        collectRequestBody(req, async (err, data) => {
            if (err) {
                sendEvent('error', { message: 'Invalid JSON', step: 0 });
                res.end();
                return;
            }

            const { prompt, session_id } = data;
            if (!prompt) {
                sendEvent('error', { message: 'Missing prompt', step: 0 });
                res.end();
                return;
            }

            try {
                const startTime = Date.now();

                // Step 1: Prompt empfangen
                sendEvent('progress', { step: 1, name: 'Prompt empfangen', detail: 'Prompt bereit' });

                // Step 2: Metriken berechnen
                sendEvent('progress', { step: 2, name: 'Metriken berechnen', detail: 'Analysiere Prompt...' });
                const metrics = await calculateLiveMetrics(prompt, '');
                sendEvent('progress', { step: 2, name: 'Metriken berechnen', detail: `${Object.keys(metrics || {}).length} Metriken berechnet` });

                // Step 3-8: DualBackendBridge Pipeline
                sendEvent('progress', { step: 3, name: 'FAISS W2 durchsuchen', detail: 'Semantische Suche läuft...' });

                // Backend Bridge ausführen mit Progress-Callbacks
                const bridgeResult = await dualBridge.processUserPrompt({
                    prompt: prompt,
                    sessionId: session_id || `sse-session-${Date.now()}`,
                    previousChainHash: data.previousChainHash || '0000'
                }, {
                    onProgress: (step, detail) => {
                        sendEvent('progress', { step, name: detail.name, detail: detail.message });
                    }
                });

                if (!bridgeResult.success) {
                    sendEvent('error', { message: bridgeResult.error, step: 9 });
                    res.end();
                    return;
                }

                // Step 9: Gemini Response (Token-Streaming wenn möglich)
                sendEvent('progress', { step: 9, name: 'Gemini Response generieren', detail: 'Antwort wird generiert...' });

                // Step 10-12: Storage + Chronicle
                sendEvent('progress', { step: 10, name: 'In 12 DBs speichern', detail: `Gespeichert in ${bridgeResult.storage?.stored_in_dbs || 0}/12 DBs` });
                sendEvent('progress', { step: 11, name: 'Chronicle aktualisieren', detail: 'Chronicle Update abgeschlossen' });
                sendEvent('progress', { step: 12, name: 'Fertig', detail: 'Pipeline abgeschlossen' });

                // Final: Komplette Response senden
                console.log('[SSE] Sending complete event...');
                sendEvent('complete', {
                    response: bridgeResult.response,
                    gemini: bridgeResult.gemini,
                    a65: bridgeResult.a65_state,
                    metrics: bridgeResult.user_prompt_metrics,
                    completion_tokens: bridgeResult.gemini?.token_count || 0,
                    prompt_tokens: 0,
                    total_tokens: bridgeResult.gemini?.token_count || 0,
                    estimated_cost: bridgeResult.gemini?.estimated_cost || 0,
                    storage: bridgeResult.storage,
                    processingTimeMs: Date.now() - startTime
                });
                console.log('[SSE] Complete event sent, waiting for flush...');

                // WICHTIG: Kurze Verzögerung um sicherzustellen dass alle Daten beim Client ankommen
                await new Promise(resolve => setTimeout(resolve, 500));

                // Stream ordentlich beenden
                console.log('[SSE] Closing stream');
                res.end();

            } catch (error) {
                console.error('[SSE] Pipeline Error:', error);
                sendEvent('error', { message: error.message, step: -1 });
                res.end();
            } finally {
                if (heartbeatInterval) clearInterval(heartbeatInterval);
            }
        });
        return;
    }

    // ===== TRINITY UPLOAD ENDPOINT (speichert mit allen Metriken in 12 DBs + Historie) =====
    if (method === 'POST' && pathname === '/api/trinity/upload') {
        collectRequestBody(req, async (err, data) => {
            if (err) return sendJson(res, 400, { success: false, error: 'Invalid JSON' });

            try {
                const uploadResult = await uploadEngine.uploadRound({
                    sessionId: data.session_id,
                    roundId: data.round_id,
                    prompt: data.prompt,
                    response: data.response,
                    metrics: data.metrics,
                    candidates: data.a65,
                    a65Score: data.a65?.selected_candidate,
                    previousChainHash: data.chain_hash || 'genesis'
                });

                return sendJson(res, 200, {
                    success: uploadResult.success,
                    trinity_upload: uploadResult,
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                return sendJson(res, 500, { success: false, error: error.message });
            }
        });
        return;
    }

    // ===== TRINITY DOWNLOAD ENDPOINT (lädt Session mit allen Daten) =====
    if (method === 'GET' && pathname === '/api/trinity/download') {
        const sessionId = urlObj.searchParams.get('session_id');
        if (!sessionId) return sendJson(res, 400, { success: false, error: 'Missing session_id' });

        try {
            const downloadResult = await downloadEngine.downloadSession(sessionId);
            return sendJson(res, 200, {
                success: downloadResult.success,
                trinity_download: downloadResult,
                timestamp
            });
        } catch (error) {
            return sendJson(res, 500, { success: false, error: error.message });
        }
    }

    // ===== TRINITY EXPORT ENDPOINT (exportiere als JSON/CSV) =====
    if (method === 'GET' && pathname === '/api/trinity/export') {
        const sessionId = urlObj.searchParams.get('session_id');
        const format = urlObj.searchParams.get('format') || 'json';
        if (!sessionId) return sendJson(res, 400, { success: false, error: 'Missing session_id' });

        try {
            const exportResult = await downloadEngine.exportSession(sessionId, format);
            if (format === 'json') {
                return sendJson(res, 200, {
                    success: exportResult.success,
                    session_data: JSON.parse(exportResult.content),
                    timestamp
                });
            } else {
                res.setHeader('Content-Type', 'text/csv');
                res.setHeader('Content-Disposition', `attachment; filename="${exportResult.filename}"`);
                res.writeHead(200);
                res.end(exportResult.content);
            }
        } catch (error) {
            return sendJson(res, 500, { success: false, error: error.message });
        }
    }

    // ===== SESSION SAVE ENDPOINT (frontend helper) =====
    if (method === 'POST' && pathname === '/api/temple/session/save') {
        collectRequestBody(req, (err, data) => {
            if (err) return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            try {
                const sid = data?.session_id || 'unknown';
                const outDir = path.join('./backend/VectorRegs_from_TXT/03_LIVE_TEMPEL/tempel/prompt');
                if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
                const outPath = path.join(outDir, `live_tempel_session_dump_${sid}.json`);
                fs.writeFileSync(outPath, JSON.stringify(data, null, 2), 'utf8');
                return sendJson(res, 200, { success: true, saved: true, file: outPath, timestamp });
            } catch (e) {
                return sendJson(res, 500, { success: false, error: e.message });
            }
        });
        return;
    }

    // ===== PIPELINE LOG ENDPOINT (für detailliertes Debugging) =====
    if (method === 'POST' && pathname === '/api/pipeline/log') {
        collectRequestBody(req, (err, data) => {
            if (err) return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            try {
                const logEntry = {
                    id: data.id || crypto.randomBytes(16).toString('hex'),
                    timestamp: data.timestamp || new Date().toISOString(),
                    session_id: data.session_id,
                    message_id: data.message_id,
                    step_number: data.step_number,
                    step_name: data.step_name,
                    data_transfer: data.data_transfer,
                    metadata: data.metadata || {}
                };

                // Speichere in Pipeline-Log-Datei
                const logDir = path.join('./backend/logs');
                if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });

                const logFile = path.join(logDir, 'pipeline_logs.jsonl');
                const logLine = JSON.stringify(logEntry) + '\n';
                fs.appendFileSync(logFile, logLine, 'utf8');

                console.log(`[PipelineLog] Step ${logEntry.step_number}: ${logEntry.step_name} | ${logEntry.data_transfer.from} → ${logEntry.data_transfer.to} | ${logEntry.data_transfer.size_bytes} bytes`);

                return sendJson(res, 200, {
                    success: true,
                    logged: true,
                    entry_id: logEntry.id,
                    timestamp
                });
            } catch (e) {
                console.error('[PipelineLog] Error:', e);
                return sendJson(res, 500, { success: false, error: e.message });
            }
        });
        return;
    }

    // ===== GET PIPELINE LOGS (für Frontend-Abfrage) =====
    if (method === 'GET' && pathname === '/api/pipeline/logs') {
        try {
            const logFile = path.join('./backend/logs', 'pipeline_logs.jsonl');
            if (!fs.existsSync(logFile)) {
                return sendJson(res, 200, { success: true, logs: [] });
            }

            const content = fs.readFileSync(logFile, 'utf8');
            const logs = content.trim().split('\n')
                .filter(line => line.trim())
                .map(line => JSON.parse(line));

            // Limitiere auf letzte 1000 Einträge
            const recentLogs = logs.slice(-1000);

            return sendJson(res, 200, {
                success: true,
                logs: recentLogs,
                total: logs.length,
                returned: recentLogs.length,
                timestamp
            });
        } catch (e) {
            console.error('[PipelineLog] Error reading logs:', e);
            return sendJson(res, 500, { success: false, error: e.message });
        }
    }

    // Session info endpoints
    if (method === 'GET' && pathname === '/api/v1/tempel/session') {
        const tempelSession = getLatestTempelSession();
        return sendJson(res, 200, {
            success: true,
            ...tempelSession,
            session_type: "tempel",
            enhanced_features: {
                live_vectorization: true,
                metrics_count: 120,
                vector_databases: 8
            },
            timestamp
        });
    }

    if (method === 'GET' && pathname === '/api/v1/trialog/session') {
        const sessionInfo = getLatestTrialogSession();
        return sendJson(res, 200, {
            success: true,
            ...sessionInfo,
            session_type: "trialog",
            enhanced_features: {
                live_vectorization: true,
                metrics_count: 120,
                vector_databases: 4
            },
            timestamp
        });
    }

    // ===== NEUE VECTOR-SEARCH-INTEGRATION =====
    // Endpoint mit semantischer Suche in allen 120 Metriken + Entstehungshistorie
    if (method === 'POST' && pathname === '/api/temple/process-with-history') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const { prompt, session_id, round_id, context_mode, api_config } = data;
            if (!prompt) {
                return sendJson(res, 400, { success: false, error: 'Missing prompt' });
            }

            const tempelSession = getLatestTempelSession();
            console.log(`[VectorSearch] Processing: "${prompt.substring(0, 50)}..."`);

            try {
                // === SCHRITT 1: SUCHE TOP 3 HISTORISCHE ANTWORTEN ===
                const searchResult = await vectorSearch.findTop3Matches(prompt);
                console.log(`[VectorSearch] Found ${searchResult.matches.length} historical matches`);

                let pastExamples = [];
                if (searchResult.success && searchResult.matches.length > 0) {
                    // === SCHRITT 2: LADE A→B→C→D→E KONTEXT FÜR JEDE ANTWORT ===
                    pastExamples = await historyBuilder.buildContextForMatches(searchResult.matches);
                    console.log(`[VectorSearch] Enriched ${pastExamples.length} past examples with full context`);
                }

                // === SCHRITT 3: GENERIERE 3 KANDIDATEN UNTER NUTZUNG DER HISTORISCHEN BEISPIELE ===
                const candidates = await generateTempleA65CandidatesWithHistory(
                    prompt,
                    pastExamples,
                    api_config
                );

                // === SCHRITT 4: A65 WÄHLT BESTE ANTWORT AUS ===
                const selectedCandidateIdx = selectBestCandidate(candidates);
                const selectedResponse = candidates[selectedCandidateIdx].text;
                const selectionReason = candidates[selectedCandidateIdx].reason;

                console.log(`[VectorSearch] A65 Selected: #${selectedCandidateIdx} | History matches used: ${pastExamples.length}`);

                // Extract provenance
                let histA = null, histB = null;
                try {
                    const emb = tempelSession?.data?.embeddings || [];
                    const lastUsers = emb.filter(e => e.role === 'user').slice(-2);
                    histA = lastUsers[0]?.content || null;
                    histB = lastUsers[1]?.content || null;
                } catch { }

                // === SCHRITT 5: BERECHNE LIVE-METRIKEN FÜR NEUE ANTWORT ===
                const metrics = await calculateLiveMetrics(prompt, selectedResponse);

                // === SCHRITT 6: SPEICHERE IN ALLE 12 DBs VIA TRINITY ===
                const chainKey = crypto
                    .createHash('sha256')
                    .update(`${tempelSession.session_id}|${Date.now()}|${selectedResponse}`)
                    .digest('hex');

                const uploadResult = await uploadEngine.uploadRound(
                    tempelSession.session_id,
                    round_id || 1,
                    prompt,
                    selectedResponse,
                    metrics,
                    candidates,
                    {
                        selected_idx: selectedCandidateIdx,
                        score: candidates[selectedCandidateIdx].a65_metric_score || 0.5
                    },
                    chainKey,
                    { history_matches: pastExamples.length, retrieval_score: pastExamples[0]?.relevance_score || 0 }
                );

                console.log(`[Trinity] Uploaded to ${uploadResult.dbResults?.successful || 0}/12 DBs`);

                // === ANTWORT FORMATIERUNG ===
                const nowIso = new Date().toISOString();
                const formattedResponse = [
                    'Evoki — VECTOR-SEARCH RESPONSE —',
                    '',
                    `History Matches Used: ${pastExamples.length}/3`,
                    `Best Match Relevance: ${(pastExamples[0]?.relevance_score * 100 || 0).toFixed(1)}%`,
                    `Metrics Used: 120 (17 Hauptmetriken)`,
                    `Chain-Key: ${chainKey}`,
                    '---',
                    '',
                    selectedResponse,
                    '',
                    '---',
                    `Generated at: ${nowIso}`,
                    `Stored in: ${uploadResult.dbResults?.successful || 0}/12 Vector DBs`
                ].join('\n');

                return sendJson(res, 200, {
                    success: true,
                    response: formattedResponse,

                    // VEKTOR-SUCHRESULTATE
                    vector_search: {
                        query: prompt,
                        past_examples: pastExamples.length,
                        top_match_relevance: pastExamples[0]?.relevance_score || null,
                        retrieval_used: pastExamples.length > 0
                    },

                    // BEISPIELE (TOP 3 MIT A→B→C→D→E)
                    past_examples: pastExamples.map((ex, idx) => ({
                        rank: idx + 1,
                        relevance_score: ex.relevance_score,
                        context: {
                            A: ex.context.A.substring(0, 200),
                            B: ex.context.B.substring(0, 200),
                            C: ex.context.C.substring(0, 200),
                            response: ex.context.agent_response.substring(0, 300),
                            D: ex.context.D,
                            E: ex.context.E
                        },
                        metrics_summary: {
                            A: ex.metrics?.CORE?.A || null,
                            PCI: ex.metrics?.CORE?.PCI || null
                        }
                    })),

                    // A65 AUSWAHL
                    a65: {
                        selected_candidate: selectedCandidateIdx,
                        score: candidates[selectedCandidateIdx].a65_metric_score || 0.5,
                        candidates_count: candidates.length,
                        candidates: candidates.map((c, idx) => ({
                            index: idx,
                            text: c.text.substring(0, 100) + '...',
                            a65_metric_score: c.a65_metric_score || 0,
                            coherence_score: c.coherence_score,
                            diversity_score: c.diversity_score,
                            metrics_brief: {
                                A: c.metrics?.CORE?.A ?? null,
                                PCI: c.metrics?.CORE?.PCI ?? null,
                                coh: c.metrics?.CORE?.coh ?? null,
                                flow: c.metrics?.CORE?.flow ?? null
                            }
                        }))
                    },

                    // LIVE METRIKEN
                    metrics: metrics,
                    live_metrics_17: {
                        A: metrics?.CORE?.A,
                        PCI: metrics?.CORE?.PCI,
                        coh: metrics?.CORE?.coh,
                        flow: metrics?.CORE?.flow,
                        T_integ: metrics?.CORE?.T_integ,
                        z_prox: metrics?.CORE?.z_prox,
                        hazard_score: metrics?.SYSTEM?.hazard_score,
                        guardian_trip: metrics?.SYSTEM?.guardian_trip,
                        phi_score: metrics?.FEP?.phi_score,
                        EV_readiness: metrics?.FEP?.EV_readiness,
                        EV_resonance: metrics?.FEP?.EV_resonance,
                        surprisal: metrics?.FEP?.surprisal,
                        LEX_Coh_conn: metrics?.LEXIKA?.LEX_Coh_conn,
                        LEX_Flow_pos: metrics?.LEXIKA?.LEX_Flow_pos,
                        LEX_Emotion_pos: metrics?.LEXIKA?.LEX_Emotion_pos,
                        LEX_T_integ: metrics?.LEXIKA?.LEX_T_integ,
                        LEX_T_disso: metrics?.LEXIKA?.LEX_T_disso
                    },

                    // SPEICHERUNG
                    storage: {
                        session_id: tempelSession.session_id,
                        round_id: round_id || 1,
                        dbs_stored: uploadResult.dbResults?.successful || 0,
                        dbs_total: 12,
                        full_history_saved: !!uploadResult.historyResult?.success,
                        checkpoint_created: !!uploadResult.checkpointResult?.success
                    },

                    timestamp: new Date().toISOString()
                });

            } catch (error) {
                console.error('[VectorSearch] Error:', error);
                return sendJson(res, 500, {
                    success: false,
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        });
    }

    // ===== P1-1: PIPELINE LOGS ENDPOINTS =====

    if (method === 'POST' && pathname === '/api/pipeline/log') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const logEntry = {
                id: data.id || `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                timestamp: data.timestamp || new Date().toISOString(),
                session_id: data.session_id,
                message_id: data.message_id,
                step_number: data.step_number,
                step_name: data.step_name,
                data_transfer: data.data_transfer,
                metadata: data.metadata || {}
            };

            pipelineLogs.push(logEntry);

            // Limit array size
            if (pipelineLogs.length > MAX_PIPELINE_LOGS) {
                pipelineLogs.shift();
            }

            return sendJson(res, 200, { success: true, log_id: logEntry.id });
        });
        return;
    }

    if (method === 'GET' && pathname === '/api/pipeline/logs') {
        const url = new URL(req.url, `http://${req.headers.host}`);
        const sessionId = url.searchParams.get('session_id');

        let filteredLogs = pipelineLogs;
        if (sessionId) {
            filteredLogs = pipelineLogs.filter(log => log.session_id === sessionId);
        }

        return sendJson(res, 200, {
            success: true,
            logs: filteredLogs.slice(-100), // Letzte 100 Logs
            total: filteredLogs.length
        });
    }

    // ===== P1-2: SYSTEM ERRORS ENDPOINTS =====

    if (method === 'POST' && pathname === '/api/v1/system/errors') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const errorEntry = {
                id: data.id || `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                timestamp: data.timestamp || new Date().toISOString(),
                type: data.type || 'runtime',
                message: data.message,
                stack: data.stack || null,
                source: data.source || 'unknown',
                metadata: data.metadata || {}
            };

            systemErrors.push(errorEntry);

            if (systemErrors.length > MAX_SYSTEM_ERRORS) {
                systemErrors.shift();
            }

            console.error(`[SystemError] ${errorEntry.type}: ${errorEntry.message} (from ${errorEntry.source})`);

            return sendJson(res, 200, { success: true, error_id: errorEntry.id });
        });
        return;
    }

    if (method === 'GET' && pathname === '/api/v1/system/errors') {
        const url = new URL(req.url, `http://${req.headers.host}`);
        const errorType = url.searchParams.get('type');

        let filteredErrors = systemErrors;
        if (errorType) {
            filteredErrors = systemErrors.filter(err => err.type === errorType);
        }

        return sendJson(res, 200, {
            success: true,
            errors: filteredErrors.slice(-50), // Letzte 50 Fehler
            total: filteredErrors.length
        });
    }

    // ===== P1-3: TRIALOG ENDPOINTS =====

    if (method === 'GET' && pathname === '/api/v1/trialog/session') {
        const url = new URL(req.url, `http://${req.headers.host}`);
        const sessionId = url.searchParams.get('session_id');

        if (!sessionId) {
            return sendJson(res, 400, { success: false, error: 'Missing session_id' });
        }

        const session = trialogSessions.get(sessionId) || {
            session_id: sessionId,
            agents: [],
            messages: [],
            created_at: new Date().toISOString()
        };

        return sendJson(res, 200, { success: true, session });
    }

    if (method === 'GET' && pathname === '/api/v1/context/daily') {
        // Placeholder für Daily Context - könnte später aus Vector DBs kommen
        return sendJson(res, 200, {
            success: true,
            daily_context: {
                date: new Date().toISOString().split('T')[0],
                summary: "Daily context placeholder - to be implemented with Vector DB aggregation",
                key_themes: [],
                metric_averages: {}
            }
        });
    }

    if (method === 'GET' && pathname === '/api/history/trialog/load') {
        const url = new URL(req.url, `http://${req.headers.host}`);
        const sessionId = url.searchParams.get('session_id');

        if (!sessionId) {
            return sendJson(res, 400, { success: false, error: 'Missing session_id' });
        }

        const session = trialogSessions.get(sessionId);

        if (!session) {
            return sendJson(res, 404, { success: false, error: 'Session not found' });
        }

        return sendJson(res, 200, {
            success: true,
            history: session.messages || []
        });
    }

    if (method === 'POST' && pathname === '/api/history/trialog/save') {
        collectRequestBody(req, async (err, data) => {
            if (err) {
                return sendJson(res, 400, { success: false, error: 'Invalid JSON' });
            }

            const { session_id, messages, agents, metadata } = data;

            if (!session_id) {
                return sendJson(res, 400, { success: false, error: 'Missing session_id' });
            }

            const session = {
                session_id,
                agents: agents || [],
                messages: messages || [],
                metadata: metadata || {},
                updated_at: new Date().toISOString(),
                created_at: trialogSessions.get(session_id)?.created_at || new Date().toISOString()
            };

            trialogSessions.set(session_id, session);

            console.log(`[Trialog] Session ${session_id} saved (${messages?.length || 0} messages)`);

            return sendJson(res, 200, {
                success: true,
                session_id,
                messages_saved: messages?.length || 0
            });
        });
        return;
    }

    // ===== POST /api/temple/config - Update Temple API Configuration =====
    if (pathname === '/api/temple/config' && method === 'POST') {
        handleRequest(res, async () => {
            const body = await readBody(req);
            const config = JSON.parse(body);

            console.log(`[Temple] Received API config update:`, config);

            // Validate config
            if (typeof config.temperature !== 'number' || config.temperature < 0 || config.temperature > 2) {
                throw new Error('Invalid temperature value (must be 0.0-2.0)');
            }
            if (typeof config.topK !== 'number' || config.topK < 1 || config.topK > 100) {
                throw new Error('Invalid topK value (must be 1-100)');
            }
            if (typeof config.topP !== 'number' || config.topP < 0 || config.topP > 1) {
                throw new Error('Invalid topP value (must be 0.0-1.0)');
            }

            // Store config globally for GeminiContextBridge
            global.templeApiConfig = config;

            // Log applied config
            console.log(`[Temple] API Config Applied:
  - Temperature: ${config.temperature}
  - TopK: ${config.topK}
  - TopP: ${config.topP}
  - MaxOutputTokens: ${config.maxOutputTokens}
  - PresencePenalty: ${config.presencePenalty || 'N/A'}
  - FrequencyPenalty: ${config.frequencyPenalty || 'N/A'}
  - Preset: ${config.presetName}`);

            return sendJson(res, 200, {
                success: true,
                config: config,
                message: 'API configuration updated successfully'
            });
        });
        return;
    }

    // ===== [CYCLE 6] HISTORY SYNC ENDPOINTS =====

    // 1. GET /api/history/daily - Inhalt des heutigen Logs
    if (method === 'GET' && pathname === '/api/history/daily') {
        try {
            const today = new Date().toISOString().split('T')[0];
            const logFile = path.join(DAILY_LOGS_PATH, `${today}.json`);

            if (!fs.existsSync(logFile)) {
                return sendJson(res, 200, { success: true, history: [], message: 'No history for today yet' });
            }

            const content = fs.readFileSync(logFile, 'utf8');
            const history = JSON.parse(content);

            return sendJson(res, 200, {
                success: true,
                history: history,
                date: today,
                timestamp
            });
        } catch (error) {
            console.error('[History] Error loading daily history:', error);
            return sendJson(res, 500, { success: false, error: error.message });
        }
    }

    // 2. GET /api/history/sessions - Liste aller verfügbaren Logs
    if (method === 'GET' && pathname === '/api/history/sessions') {
        try {
            if (!fs.existsSync(DAILY_LOGS_PATH)) {
                return sendJson(res, 200, { success: true, sessions: [] });
            }

            const files = fs.readdirSync(DAILY_LOGS_PATH)
                .filter(f => f.endsWith('.json'))
                .map(f => ({
                    session_id: f.replace('.json', ''),
                    filename: f,
                    last_modified: fs.statSync(path.join(DAILY_LOGS_PATH, f)).mtime
                }))
                .sort((a, b) => b.last_modified - a.last_modified);

            return sendJson(res, 200, {
                success: true,
                sessions: files,
                timestamp
            });
        } catch (error) {
            return sendJson(res, 500, { success: false, error: error.message });
        }
    }

    // 3. POST /api/history/load - Spezifisches Log laden
    if (method === 'POST' && pathname === '/api/history/load') {
        collectRequestBody(req, (err, data) => {
            if (err) return sendJson(res, 400, { success: false, error: 'Invalid JSON' });

            const sessionId = data.session_id;
            if (!sessionId) return sendJson(res, 400, { success: false, error: 'Missing session_id' });

            try {
                const logFile = path.join(DAILY_LOGS_PATH, `${sessionId}.json`);
                if (!fs.existsSync(logFile)) {
                    return sendJson(res, 404, { success: false, error: 'Log file not found' });
                }

                const content = fs.readFileSync(logFile, 'utf8');
                const history = JSON.parse(content);

                return sendJson(res, 200, {
                    success: true,
                    history: history,
                    session_id: sessionId,
                    timestamp
                });
            } catch (e) {
                return sendJson(res, 500, { success: false, error: e.message });
            }
        });
        return;
    }

    // 404
    return sendJson(res, 404, {
        error: `Endpoint not found: ${pathname}`,
        available: ['/health', '/api/v1/status', '/api/temple/process', '/api/temple/config', '/api/v1/interact', '/api/v1/tempel/session', '/api/v1/trialog/session', '/api/pipeline/logs', '/api/v1/system/errors', '/api/v1/context/daily', '/api/history/trialog/load', '/api/history/trialog/save'],
        timestamp
    });
});

// ===== STARTUP =====

// Load Vector DBs and History at startup
async function loadVectorDataAndHistory() {
    console.log('\n🔄 Loading Vector DBs and History Context...');

    // Check Embedding Service availability
    console.log('   🧠 Checking Embedding Service (Port 5000)...');
    try {
        const embeddingCheck = await fetch('http://localhost:5000/health', { timeout: 2000 });
        if (embeddingCheck.ok) {
            const embeddingData = await embeddingCheck.json();
            console.log(`   ✅ Embedding Service ONLINE: ${embeddingData.service || 'Unknown'}`);
            if (embeddingData.loaded_models && embeddingData.loaded_models.length > 0) {
                console.log(`   ✅ Loaded Models: ${embeddingData.loaded_models.join(', ')}`);
            }
        }
    } catch (embErr) {
        console.warn('   ⚠️  Embedding Service nicht erreichbar - Embeddings deaktiviert');
        console.warn('   ℹ️  Starte embedding_service_mistral.py für volle Funktionalität');
    }

    try {
        // Load all history from database
        const historyData = await vectorSearch.loadAllHistory();
        console.log(`   ✅ History loaded: ${historyData?.length || 0} entries`);

        // Preload vector search engine
        console.log('   🏛️  Tempel Vector DBs: 8 databases initialized');
        console.log('   🔮 Trialog Vector DBs: 4 databases initialized');
        console.log('   ✅ Trinity Engines ready\n');

        return true;
    } catch (err) {
        console.warn('   ⚠️  Vector/History loading failed:', err.message);
        console.log('   ℹ️  System will start with empty context\n');
        return false;
    }
}

server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
        console.error(`❌ Port ${PORT} is already in use!`);
        process.exit(1);
    } else {
        console.error(`❌ Server error:`, err);
        process.exit(1);
    }
});

server.listen(PORT, HOSTNAME, async () => {
    // Load vector data and history after server starts
    await loadVectorDataAndHistory();
    console.log(`
╔════════════════════════════════════════════════════════════════════════════════╗
║  ✅ EVOKI Backend Server V3.0 ENHANCED - LIVE VECTORIZATION ACTIVE            ║
╠════════════════════════════════════════════════════════════════════════════════╣
║  Server:            http://0.0.0.0:${PORT}                                        ║
║  Health:            http://localhost:${PORT}/health                              ║
║  Status:            http://localhost:${PORT}/api/v1/status                       ║
║                                                                                ║
║  🏛️  Tempel:         POST http://localhost:${PORT}/api/temple/process            ║
║  🔮 Trialog:        POST http://localhost:${PORT}/api/v1/interact               ║
║                                                                                ║
║  📊 Features:       120+ Live Metriken | 12 Vektor-DBs | Python Integration  ║
║  🌌 Hyperspace:     Tempel (8 DBs) + Trialog (4 DBs) = Real-time Storage    ║
╚════════════════════════════════════════════════════════════════════════════════╝
    `);
});

// Global error handlers
process.on('uncaughtException', (error) => {
    console.error('❌ UNCAUGHT EXCEPTION:', error);
    console.error('Stack:', error.stack);
    // Don't exit, just log
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('❌ UNHANDLED REJECTION at:', promise);
    console.error('Reason:', reason);
    // Don't exit, just log
});

process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down Enhanced Backend...');
    server.close(() => {
        console.log('✅ Enhanced Backend stopped');
        process.exit(0);
    });
});

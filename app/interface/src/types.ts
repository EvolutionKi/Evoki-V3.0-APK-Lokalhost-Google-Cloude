/**
 * Evoki V3.0 - Type Definitions
 * Based on V2.0 Structure
 */

// Tab Enum (13 Tabs aus V2.0)
export enum Tab {
    Temple = 'temple',              // 🏛️ Evoki Temple (Haupttab)
    Metrics = 'metrics',            // 📊 Metriken (150+)
    Trialog = 'trialog',           // 💬 Trialog
    Analysis = 'analysis',          // 📈 Analyse
    RuleSearch = 'rule-search',     // 📖 Regelwerk-Suche
    API = 'api',                    // 🔌 API Config
    VoiceSettings = 'voice',        // 🎤 Stimme & TTS
    DeepStorage = 'deep-storage',   // 🗄️ Deep Storage
    PipelineLog = 'pipeline',       // 🔄 Pipeline Log
    EngineConsole = 'engine',       // 🖥️ Engine Console
    ErrorLog = 'errors',            // ⚠️ Fehlerprotokoll
    Settings = 'settings',          // ⚙️ Einstellungen
    About = 'about'                 // ℹ️ About
}

// Chat Message
export interface Message {
    id: string;
    role: 'user' | 'evoki' | 'system';
    content: string;
    timestamp?: string;
    color?: string;
}

// Metrics (13 Essential from Phase 2)
export interface Metrics {
    A: number;              // Affekt
    PCI: number;            // Kohärenz
    T_panic: number;        // Panik
    B_align: number;        // Soul-Signature
    F_risk: number;         // Future Risk

    // B-Vektor (7D)
    B_life: number;
    B_truth: number;
    B_depth: number;
    B_init: number;
    B_warmth: number;
    B_safety: number;
    B_clarity: number;

    // Meta
    text_length: number;
    word_count: number;
}

// Gate Result
export interface GateResult {
    passed: boolean;
    gate: 'A' | 'B';
    veto_reasons: string[];
    rule_violations: string[];
}

// FAISS Result
export interface FAISSResult {
    chunk_id: string;
    similarity: number;
    distance: number;
}

// API Config
export interface APIConfig {
    backendUrl: string;
    geminiApiKey?: string;
    openaiApiKey?: string;
}

// App State (Vereinfachte Version für V3.0)
export interface AppState {
    activeTab: Tab;
    apiConfig: APIConfig;
}

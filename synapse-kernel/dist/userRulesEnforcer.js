"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.UserRulesEnforcer = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * UserRulesEnforcer - Erzwingt Protocol V5.0 durch Output-Kanal Blocking
 *
 * Da wir Gemini's Backend nicht kontrollieren können, monitoren wir:
 * 1) Gemini DB für neue AI-Responses
 * 2) Compliance Errors Auto-Repair
 * 3) Trigger Python compliance_enforcer.py bei Breach
 */
class UserRulesEnforcer {
    constructor(context) {
        this.context = context;
        this.geminiDbPath = null;
        this.lastResponseTimestamp = 0;
        this.evokiRoot = process.env.EVOKI_PROJECT_ROOT || 'C:\\Evoki V3.0 APK-Lokalhost-Google Cloude';
        this.findGeminiDb();
    }
    findGeminiDb() {
        // Gemini Code Assist speichert Chat-History in SQLite DB
        // Typische Pfade (Windows):
        const possiblePaths = [
            path.join(process.env.APPDATA || '', 'Code', 'User', 'workspaceStorage'),
            path.join(process.env.LOCALAPPDATA || '', 'Google', 'Gemini'),
        ];
        // Suche nach state.vscdb oder conversations_db
        for (const basePath of possiblePaths) {
            if (fs.existsSync(basePath)) {
                try {
                    const files = this.findFilesRecursive(basePath, /state\.vscdb|conversation.*\.db/i);
                    if (files.length > 0) {
                        this.geminiDbPath = files[0];
                        console.log(`✅ Gemini DB gefunden: ${this.geminiDbPath}`);
                        return;
                    }
                }
                catch (err) {
                    console.error('Error searching for Gemini DB:', err);
                }
            }
        }
        console.warn('⚠️  Gemini DB nicht gefunden - Fallback auf compliance_errors.json');
    }
    findFilesRecursive(dir, pattern, maxDepth = 3) {
        if (maxDepth <= 0)
            return [];
        const results = [];
        try {
            const entries = fs.readdirSync(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isFile() && pattern.test(entry.name)) {
                    results.push(fullPath);
                }
                else if (entry.isDirectory()) {
                    results.push(...this.findFilesRecursive(fullPath, pattern, maxDepth - 1));
                }
            }
        }
        catch (err) {
            // Permission denied / access errors
        }
        return results;
    }
    start() {
        console.log('🚀 UserRulesEnforcer started');
        // Monitor compliance_errors.json als Fallback
        const errorsPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
        if (fs.existsSync(errorsPath)) {
            fs.watch(errorsPath, (eventType) => {
                if (eventType === 'change') {
                    this.handleComplianceError();
                }
            });
        }
        // Periodische Breach-Checks (alle 5s)
        setInterval(() => {
            this.checkForBreaches();
        }, 5000);
    }
    handleComplianceError() {
        const errorsPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
        try {
            const errors = JSON.parse(fs.readFileSync(errorsPath, 'utf-8'));
            const recentBreaches = errors.filter((e) => e.type === 'breach').slice(-3);
            if (recentBreaches.length > 0) {
                const latestBreach = recentBreaches[recentBreaches.length - 1];
                const breachTime = new Date(latestBreach.timestamp).getTime();
                // Nur einmal pro Breach reagieren
                if (breachTime > this.lastResponseTimestamp) {
                    this.lastResponseTimestamp = breachTime;
                    this.triggerAutoRepair(latestBreach);
                }
            }
        }
        catch (err) {
            console.error('Error reading compliance errors:', err);
        }
    }
    checkForBreaches() {
        const historyPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'status', 'status_window_history.json');
        const errorsPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
        try {
            // Prüfe ob neue Breaches existieren
            if (fs.existsSync(errorsPath)) {
                const errors = JSON.parse(fs.readFileSync(errorsPath, 'utf-8'));
                const unresolvedBreaches = errors.filter((e) => e.type === 'breach' && !e.resolved);
                if (unresolvedBreaches.length > 0) {
                    // Show persistent warning
                    vscode.window.showWarningMessage(`⚠️  ${unresolvedBreaches.length} ungelöste Protocol Breaches!`, 'Auto-Repair jetzt', 'Details').then(selection => {
                        if (selection === 'Auto-Repair jetzt') {
                            this.triggerAutoRepair(unresolvedBreaches[0]);
                        }
                        else if (selection === 'Details') {
                            vscode.workspace.openTextDocument(errorsPath).then(doc => {
                                vscode.window.showTextDocument(doc);
                            });
                        }
                    });
                }
            }
        }
        catch (err) {
            console.error('Error checking breaches:', err);
        }
    }
    triggerAutoRepair(breach) {
        console.log('🔧 Triggering Auto-Repair for breach:', breach.message);
        try {
            // Schreibe Status Window DIREKT - kein External Script
            const pendingPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'status', 'pending_status.json');
            const repairWindow = {
                step_id: `AUTO_REPAIR_${Date.now()}`,
                cycle: 'REPAIR/REPAIR',
                time_source: `metadata (STRICT_SYNC): ${new Date().toISOString()}`,
                goal: 'AUTO-REPAIR: Extension hat fehlende Status Windows nachgetragen',
                inputs: {
                    raw_user_request: breach.prompt || 'BREACH DETECTED'
                },
                actions: [
                    'Extension hat Breach detektiert',
                    `Breach: ${breach.message}`,
                    'Auto-Repair Status Window geschrieben'
                ],
                risk: [],
                assumptions: [],
                rule_tangency: {
                    tangency_detected: true,
                    notes: 'Auto-Repair durch Extension'
                },
                reflection_curve: {
                    delta: 'Status Window fehlte',
                    correction: 'Extension hat automatisch repariert',
                    next: 'Workflow sollte Status Windows automatisch schreiben'
                },
                output_plan: ['Breach als resolved markieren'],
                window_type: 'verification',
                schema_version: '3.2',
                window_source: 'EXTENSION_AUTO_REPAIR',
                confidence: 0.5,
                system_versions: {},
                cycle_backend_controlled: true,
                critical_summary: {
                    status: 'YELLOW',
                    notes: 'Auto-Repair Window'
                },
                project_awareness: {},
                window_hash: 'PLACEHOLDER_BACKEND',
                prev_window_hash: 'AUTO',
                mcp_trigger: {
                    action: 'save_to_history',
                    target: 'status_history_manager.py',
                    enabled: true
                }
            };
            fs.writeFileSync(pendingPath, JSON.stringify(repairWindow, null, 2), 'utf-8');
            vscode.window.showInformationMessage('✅ Auto-Repair erfolgreich - Status Window nachgeschrieben');
            // Markiere Breach als resolved
            this.markBreachAsResolved(breach);
        }
        catch (err) {
            console.error('Auto-Repair failed:', err);
            vscode.window.showErrorMessage(`❌ Auto-Repair fehlgeschlagen: ${err}`);
        }
    }
    markBreachAsResolved(breach) {
        const errorsPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
        try {
            const errors = JSON.parse(fs.readFileSync(errorsPath, 'utf-8'));
            // Finde und markiere Breach
            for (const err of errors) {
                if (err.timestamp === breach.timestamp && err.type === 'breach') {
                    err.resolved = true;
                    err.resolved_at = new Date().toISOString();
                }
            }
            fs.writeFileSync(errorsPath, JSON.stringify(errors, null, 2), 'utf-8');
        }
        catch (err) {
            console.error('Error marking breach as resolved:', err);
        }
    }
    stop() {
        console.log('⏸️  UserRulesEnforcer stopped');
    }
}
exports.UserRulesEnforcer = UserRulesEnforcer;
//# sourceMappingURL=userRulesEnforcer.js.map
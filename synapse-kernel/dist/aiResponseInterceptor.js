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
exports.AIResponseInterceptor = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
/**
 * AI-Response-Interceptor
 *
 * Verhindert dass AI-Antworten OHNE Status Window angezeigt werden.
 * Dies ist die Prävention-Schicht (nicht nur Reparatur).
 */
class AIResponseInterceptor {
    constructor(context) {
        this.context = context;
        this.evokiRoot = process.env.EVOKI_PROJECT_ROOT || 'C:\\Evoki V3.0 APK-Lokalhost-Google Cloude';
        this.pendingPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'status', 'pending_status.json');
        this.complianceErrorsPath = path.join(this.evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
    }
    /**
     * Hook into Chat Participant Response
     * Called BEFORE response is shown to user
     */
    async interceptChatResponse(request, response, token) {
        // Buffer response
        let fullResponse = '';
        const originalMarkdown = response.markdown.bind(response);
        // Monkey-patch markdown method to buffer
        response.markdown = (value) => {
            const text = typeof value === 'string' ? value : value.value;
            fullResponse += text;
            return originalMarkdown(value);
        };
        // CRITICAL: Check for Status Window AFTER response completes
        // (We can't block mid-stream, but we can inject at end)
        const checkTimer = setInterval(() => {
            if (token.isCancellationRequested || fullResponse.length > 0) {
                clearInterval(checkTimer);
                this.validateAndInject(fullResponse, response);
            }
        }, 500);
    }
    async validateAndInject(responseText, stream) {
        const hasStatusWindow = this.containsStatusWindow(responseText);
        if (!hasStatusWindow) {
            console.warn('🚨 AI Response WITHOUT Status Window detected!');
            // Generate Status Window
            const statusWindow = await this.generateStatusWindow(responseText);
            // Inject into response
            stream.markdown('\n\n---\n\n## ⚠️ AUTO-INJECTED STATUS WINDOW\n\n');
            stream.markdown('```json\n' + JSON.stringify(statusWindow, null, 2) + '\n```\n');
            // Write to pending_status.json
            fs.writeFileSync(this.pendingPath, JSON.stringify(statusWindow, null, 2), 'utf-8');
            // Log breach
            this.logBreach(responseText);
            vscode.window.showWarningMessage('⚠️ AI hat Status Window vergessen - Auto-Inject erfolgt', 'Details');
        }
        else {
            console.log('✅ Status Window gefunden in AI Response');
        }
    }
    containsStatusWindow(text) {
        // Check for required Status Window fields
        return (text.includes('"step_id"') &&
            text.includes('"window_hash"') &&
            text.includes('"goal"') &&
            text.includes('"reflection_curve"'));
    }
    async generateStatusWindow(aiResponse) {
        const timestamp = new Date().toISOString();
        return {
            schema_version: '3.2',
            window_source: 'AI_INTERCEPTOR_AUTO',
            cycle_backend_controlled: true,
            step_id: `auto_inject_${Date.now()}`,
            cycle: 'INJECT/INJECT',
            window_type: 'verification',
            time_source: `metadata (STRICT_SYNC): AUTO`,
            goal: 'AUTO-INJECT: AI antwortete ohne Status Window',
            inputs: {
                raw_user_request: 'N/A - Interceptor generiert',
                ai_response_preview: aiResponse.substring(0, 200)
            },
            actions: [
                'AI-Response-Interceptor hat eingegriffen',
                'AI antwortete ohne Status Window',
                'Status Window automatisch injiziert'
            ],
            risk: [],
            assumptions: [
                'AI hat Status Window vergessen',
                'Auto-Inject ist Notfall-Mechanismus'
            ],
            rule_tangency: {
                tangency_detected: true,
                notes: 'Auto-Inject durch Interceptor'
            },
            reflection_curve: {
                delta: 'AI antwortete ohne Status Window',
                correction: 'Interceptor hat automatisch Status Window injiziert',
                next: 'AI sollte in Zukunft Status Windows selbst schreiben'
            },
            critical_summary: {
                status: 'YELLOW',
                message: 'Auto-Inject Window'
            },
            output_plan: [
                'User benachrichtigen',
                'Breach loggen für Lern-Mechanismus'
            ],
            window_hash: 'PLACEHOLDER_BACKEND',
            prev_window_hash: 'AUTO',
            confidence: 0.5,
            mcp_trigger: {
                enabled: true,
                reason: 'Auto-Inject by Interceptor',
                timestamp: timestamp
            }
        };
    }
    logBreach(aiResponse) {
        const breach = {
            timestamp: new Date().toISOString(),
            type: 'breach',
            message: 'AI antwortete ohne Status Window - Auto-Inject ausgelöst',
            aiResponsePreview: aiResponse.substring(0, 200),
            source: 'AI_RESPONSE_INTERCEPTOR'
        };
        try {
            let errors = [];
            if (fs.existsSync(this.complianceErrorsPath)) {
                errors = JSON.parse(fs.readFileSync(this.complianceErrorsPath, 'utf-8'));
            }
            errors.push(breach);
            fs.writeFileSync(this.complianceErrorsPath, JSON.stringify(errors, null, 2), 'utf-8');
        }
        catch (err) {
            console.error('Failed to log breach:', err);
        }
    }
}
exports.AIResponseInterceptor = AIResponseInterceptor;
//# sourceMappingURL=aiResponseInterceptor.js.map
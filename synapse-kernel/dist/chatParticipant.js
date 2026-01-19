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
exports.SynapseChatParticipant = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// V3.0 PATH CONFIGURATION
const WORKSPACE_ROOT = vscode.workspace.workspaceFolders?.[0].uri.fsPath || process.cwd();
const EVOKI_ROOT = process.env.EVOKI_PROJECT_ROOT || WORKSPACE_ROOT;
// Allow fallback to relative paths if env var is missing
const CHAT_HISTORY_PATH = path.join(EVOKI_ROOT, 'tooling', 'data', 'synapse', 'chat_history.json');
const PROTOCOL_PATH = path.join(EVOKI_ROOT, 'tooling', 'docs', 'PROTOCOL_V5_ENFORCED.md');
class SynapseChatParticipant {
    constructor(context) {
        this.chatHistory = this.loadChatHistory();
        // Register the chat participant
        const participant = vscode.chat.createChatParticipant('synapse', this.handler.bind(this));
        participant.iconPath = vscode.Uri.file(path.join(context.extensionPath, 'resources', 'icon.png'));
        context.subscriptions.push(participant);
        console.log('Synapse Chat Participant V3.0 (Native) initialized');
    }
    async handler(request, context, stream, token) {
        try {
            const userPrompt = request.prompt;
            stream.progress('Synapse: Syncing Protocol...');
            // 1. Build Protocol Context
            const protocolContent = this.loadProtocol();
            const historyContext = this.chatHistory.messages.slice(-5);
            const systemPrompt = `
SYSTEM ROLE:
You are @synapse, the Evoki Interface.
You are running inside VS Code via the Synapse Nexus Kernel.

SYSTEM PROTOCOL (ENFORCED):
${protocolContent}

INSTRUCTIONS:
1. You MUST generate a valid JSON Status Window at the very beginning of your response.
2. The Status Window must reflect the current state and goal.
3. After the JSON block, answer the user's request using Markdown.

CONTEXT:
User Input: "${userPrompt}"
Session History: ${historyContext.length} messages.
            `;
            // 2. Construct Messages for LM
            const messages = [
                vscode.LanguageModelChatMessage.User(systemPrompt),
                ...historyContext.map(m => m.role === 'user'
                    ? vscode.LanguageModelChatMessage.User(m.content)
                    : vscode.LanguageModelChatMessage.Assistant(m.content)),
                vscode.LanguageModelChatMessage.User(userPrompt)
            ];
            // 3. Select Model (Native API)
            let model;
            try {
                // Try to find ANY chat model (GPT-4 class preferred)
                const models = await vscode.lm.selectChatModels({ family: 'gpt-4' });
                if (models.length > 0)
                    model = models[0];
                else {
                    const allModels = await vscode.lm.selectChatModels({});
                    if (allModels.length > 0)
                        model = allModels[0];
                }
            }
            catch (err) {
                console.warn('Failed to select LM model:', err);
            }
            if (!model) {
                stream.markdown('⚠️ **Fehler:** Kein natives AI-Modell in VS Code gefunden.\n\n');
                stream.markdown('Bitte stelle sicher, dass Copilot, Gemini Code Assist oder eine kompatible Extension installiert und aktiv ist.');
                return;
            }
            // 4. Send Request
            stream.progress(`Thinking with ${model.name}...`);
            const response = await model.sendRequest(messages, {}, token);
            let fullResponse = '';
            for await (const fragment of response.text) {
                fullResponse += fragment;
                stream.markdown(fragment);
            }
            // 5. Save History
            this.saveToHistory(userPrompt, fullResponse);
        }
        catch (error) {
            stream.markdown(`**System Error:** ${error.message}`);
            if (error.message.includes('proposal')) {
                stream.markdown('\n\n*Hinweis: Bitte stelle sicher, dass die VS Code Version aktuell ist und Proposed APIs erlaubt sind.*');
            }
        }
    }
    loadProtocol() {
        try {
            if (fs.existsSync(PROTOCOL_PATH)) {
                return fs.readFileSync(PROTOCOL_PATH, 'utf-8');
            }
        }
        catch (e) { /* ignore */ }
        return 'PROTOCOL V5.0 (Fallback: File not found)';
    }
    loadChatHistory() {
        try {
            if (fs.existsSync(CHAT_HISTORY_PATH)) {
                return JSON.parse(fs.readFileSync(CHAT_HISTORY_PATH, 'utf-8'));
            }
        }
        catch (e) { /* ignore */ }
        return { messages: [], lastUpdated: new Date().toISOString(), sessionCount: 0 };
    }
    saveToHistory(prompt, response) {
        this.chatHistory.messages.push({ role: 'user', content: prompt, timestamp: new Date().toISOString() });
        this.chatHistory.messages.push({ role: 'assistant', content: response, timestamp: new Date().toISOString() });
        // Trim
        if (this.chatHistory.messages.length > 50)
            this.chatHistory.messages = this.chatHistory.messages.slice(-50);
        try {
            const dir = path.dirname(CHAT_HISTORY_PATH);
            if (!fs.existsSync(dir))
                fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(CHAT_HISTORY_PATH, JSON.stringify(this.chatHistory, null, 2));
        }
        catch (e) {
            console.error('Save failed', e);
        }
    }
}
exports.SynapseChatParticipant = SynapseChatParticipant;
//# sourceMappingURL=chatParticipant.js.map
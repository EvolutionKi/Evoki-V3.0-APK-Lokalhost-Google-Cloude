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
const child_process = __importStar(require("child_process"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process.exec);
const EVOKI_APP_PATH = 'C:\\Evoki V2.0\\evoki-app';
const CHAT_HISTORY_PATH = path.join(EVOKI_APP_PATH, 'data', 'synapse', 'chat_history.json');
const LAST_RESPONSE_PATH = path.join(EVOKI_APP_PATH, 'data', 'synapse', 'last_response.md');
/**
 * Synapse Chat Participant
 * Handles @synapse mentions in VS Code chat with auto Status Window injection
 */
class SynapseChatParticipant {
    constructor(context) {
        this.context = context;
        this.chatHistory = this.loadChatHistory();
    }
    register() {
        // Register the chat participant
        const participant = vscode.chat.createChatParticipant(SynapseChatParticipant.participantId, this.handleChatRequest.bind(this));
        participant.iconPath = vscode.Uri.file(path.join(EVOKI_APP_PATH, 'assets', 'synapse-icon.png'));
        return participant;
    }
    async handleChatRequest(request, context, stream, token) {
        const userPrompt = request.prompt;
        // 1. Stream initial status
        stream.markdown('⚡ **Synapse Active**\n\n');
        // 2. Generate Status Window
        stream.progress('Generating Status Window...');
        const statusWindow = await this.getStatusWindow();
        if (statusWindow) {
            stream.markdown('```json\n' + JSON.stringify(statusWindow, null, 2) + '\n```\n\n');
        }
        // 3. Load previous context
        const previousContext = this.getPreviousContext(5); // Last 5 messages
        // 4. Build the full prompt
        const fullPrompt = this.buildFullPrompt(userPrompt, statusWindow, previousContext);
        // 5. Call the LLM API (Claude preferred, then Gemini)
        stream.progress('Calling AI...');
        try {
            const response = await this.callLLM(fullPrompt, token);
            // 6. Stream the response
            stream.markdown(response);
            // 7. Save to history
            this.saveToHistory(userPrompt, response, statusWindow);
            // 8. Save last response
            this.saveLastResponse(response);
            return {
                metadata: {
                    command: 'synapse-chat',
                    statusWindow: statusWindow
                }
            };
        }
        catch (error) {
            stream.markdown(`\n\n❌ **Error:** ${error.message}\n`);
            stream.markdown('\n*Fallback: Use regular Gemini chat with manual Status Window paste.*');
            return {
                errorDetails: {
                    message: error.message
                }
            };
        }
    }
    async getStatusWindow() {
        try {
            const { stdout } = await execAsync(`python "${path.join(EVOKI_APP_PATH, 'scripts', 'get_status_block.py')}"`, { timeout: 5000 });
            return JSON.parse(stdout.trim());
        }
        catch (error) {
            console.error('Failed to get status window:', error);
            return null;
        }
    }
    getPreviousContext(count) {
        return this.chatHistory.messages.slice(-count);
    }
    buildFullPrompt(userPrompt, statusWindow, previousContext) {
        let prompt = '';
        // Add system context
        prompt += '## SYNAPSE SYSTEM CONTEXT\n\n';
        // Add status window
        if (statusWindow) {
            prompt += '### Current Status Window\n```json\n';
            prompt += JSON.stringify(statusWindow, null, 2);
            prompt += '\n```\n\n';
        }
        // Add previous conversation context
        if (previousContext.length > 0) {
            prompt += '### Recent Conversation History\n';
            for (const msg of previousContext) {
                prompt += `**${msg.role}** (${msg.timestamp}):\n${msg.content}\n\n`;
            }
        }
        // Add current user prompt
        prompt += '---\n\n### Current User Request\n\n';
        prompt += userPrompt;
        return prompt;
    }
    async callLLM(prompt, token) {
        // Try Claude first (preferred), then Gemini, then backend
        // 1. Try Claude via vscode.lm API
        if (vscode.lm) {
            try {
                const claudeModels = await vscode.lm.selectChatModels({
                    vendor: 'anthropic',
                    family: 'claude'
                });
                if (claudeModels.length > 0) {
                    console.log('Using Claude model:', claudeModels[0].name);
                    const model = claudeModels[0];
                    const messages = [
                        vscode.LanguageModelChatMessage.User(prompt)
                    ];
                    const response = await model.sendRequest(messages, {}, token);
                    let fullResponse = '';
                    for await (const chunk of response.text) {
                        fullResponse += chunk;
                    }
                    return fullResponse;
                }
            }
            catch (error) {
                console.log('Claude not available, trying Gemini...');
            }
            // 2. Try Gemini via vscode.lm API
            try {
                const geminiModels = await vscode.lm.selectChatModels({
                    vendor: 'google',
                    family: 'gemini'
                });
                if (geminiModels.length > 0) {
                    console.log('Using Gemini model:', geminiModels[0].name);
                    const model = geminiModels[0];
                    const messages = [
                        vscode.LanguageModelChatMessage.User(prompt)
                    ];
                    const response = await model.sendRequest(messages, {}, token);
                    let fullResponse = '';
                    for await (const chunk of response.text) {
                        fullResponse += chunk;
                    }
                    return fullResponse;
                }
            }
            catch (error) {
                console.log('Gemini not available via vscode.lm...');
            }
        }
        // 3. Fallback: Try our backend API
        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: prompt,
                    history: this.chatHistory.messages.slice(-10)
                }),
                signal: token ? AbortSignal.timeout(60000) : undefined
            });
            if (response.ok) {
                const data = await response.json();
                return data.response;
            }
        }
        catch (backendError) {
            console.log('Backend API not available...');
        }
        throw new Error('No LLM available. Please ensure Claude Code, Gemini, or backend is running.');
    }
    loadChatHistory() {
        try {
            if (fs.existsSync(CHAT_HISTORY_PATH)) {
                const data = fs.readFileSync(CHAT_HISTORY_PATH, 'utf-8');
                return JSON.parse(data);
            }
        }
        catch (error) {
            console.error('Failed to load chat history:', error);
        }
        return {
            messages: [],
            lastUpdated: new Date().toISOString(),
            sessionCount: 0
        };
    }
    saveToHistory(userPrompt, response, statusWindow) {
        const timestamp = new Date().toISOString();
        // Add user message
        this.chatHistory.messages.push({
            role: 'user',
            content: userPrompt,
            timestamp,
            statusWindow
        });
        // Add assistant response
        this.chatHistory.messages.push({
            role: 'assistant',
            content: response,
            timestamp
        });
        // Update metadata
        this.chatHistory.lastUpdated = timestamp;
        this.chatHistory.sessionCount++;
        // Keep only last 100 messages to avoid huge files
        if (this.chatHistory.messages.length > 100) {
            this.chatHistory.messages = this.chatHistory.messages.slice(-100);
        }
        // Save to file
        try {
            const dir = path.dirname(CHAT_HISTORY_PATH);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
            fs.writeFileSync(CHAT_HISTORY_PATH, JSON.stringify(this.chatHistory, null, 2));
        }
        catch (error) {
            console.error('Failed to save chat history:', error);
        }
    }
    saveLastResponse(response) {
        try {
            const dir = path.dirname(LAST_RESPONSE_PATH);
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
            fs.writeFileSync(LAST_RESPONSE_PATH, response);
        }
        catch (error) {
            console.error('Failed to save last response:', error);
        }
    }
}
exports.SynapseChatParticipant = SynapseChatParticipant;
SynapseChatParticipant.participantId = 'synapse';
//# sourceMappingURL=chatParticipant.js.map
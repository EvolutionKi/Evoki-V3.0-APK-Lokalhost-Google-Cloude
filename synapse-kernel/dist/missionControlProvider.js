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
exports.SynapseMissionControlProvider = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// --- Mission Control Provider ---
class SynapseMissionControlProvider {
    // --- Core Logic ---
    static createOrShow(extensionUri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;
        if (SynapseMissionControlProvider._currentPanel) {
            SynapseMissionControlProvider._currentPanel._panel.reveal(column);
            return;
        }
        const panel = vscode.window.createWebviewPanel(SynapseMissionControlProvider.viewType, 'Evoki Mission Control', column || vscode.ViewColumn.One, {
            enableScripts: true,
            localResourceRoots: [extensionUri],
            retainContextWhenHidden: true
        });
        SynapseMissionControlProvider._currentPanel = new SynapseMissionControlProvider(panel, extensionUri);
    }
    constructor(panel, extensionUri) {
        this._disposables = [];
        this._chatHistory = [];
        this._tools = new Map();
        this._panel = panel;
        this._extensionUri = extensionUri;
        // Initialize Tools
        this._registerTools();
        // Check for API Key
        this._loadApiKey().then(() => {
            this._update();
        });
        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
        this._panel.webview.onDidReceiveMessage(async (message) => {
            switch (message.command) {
                case 'sendMessage':
                    await this._handleUserMessage(message.text);
                    return;
                case 'saveApiKey':
                    await this._saveApiKey(message.key);
                    return;
                case 'clearHistory':
                    this._chatHistory = [];
                    this._updateChatUI();
                    return;
            }
        }, null, this._disposables);
    }
    _registerTools() {
        // 1. LIST DIR
        this._tools.set('list_dir', {
            name: 'list_dir',
            description: 'List contents of a directory',
            parameters: {
                type: 'object',
                properties: {
                    path: { type: 'string', description: 'Absolute path to directory' }
                },
                required: ['path']
            },
            execute: async (args) => {
                try {
                    const files = fs.readdirSync(args.path);
                    return { files };
                }
                catch (e) {
                    return { error: e.message };
                }
            }
        });
        // 2. VIEW FILE
        this._tools.set('view_file', {
            name: 'view_file',
            description: 'Read file content',
            parameters: {
                type: 'object',
                properties: {
                    path: { type: 'string', description: 'Absolute path to file' }
                },
                required: ['path']
            },
            execute: async (args) => {
                try {
                    const content = fs.readFileSync(args.path, 'utf-8');
                    return { content };
                }
                catch (e) {
                    return { error: e.message };
                }
            }
        });
        // 3. WRITE TO FILE
        this._tools.set('write_to_file', {
            name: 'write_to_file',
            description: 'Write content to a file (overwrites)',
            parameters: {
                type: 'object',
                properties: {
                    path: { type: 'string', description: 'Absolute path' },
                    content: { type: 'string', description: 'File content' }
                },
                required: ['path', 'content']
            },
            execute: async (args) => {
                try {
                    fs.mkdirSync(path.dirname(args.path), { recursive: true });
                    fs.writeFileSync(args.path, args.content, 'utf-8');
                    return { success: true };
                }
                catch (e) {
                    return { error: e.message };
                }
            }
        });
        // 4. RUN TERMINAL COMMAND
        this._tools.set('run_command', {
            name: 'run_command',
            description: 'Run a shell command',
            parameters: {
                type: 'object',
                properties: {
                    command: { type: 'string', description: 'Command to run' },
                    cwd: { type: 'string', description: 'Working directory' }
                },
                required: ['command']
            },
            execute: async (args) => {
                const term = vscode.window.createTerminal('Evoki-Agent');
                term.show();
                term.sendText(args.command);
                return { status: 'Command sent to terminal. Check output.' };
                // Note: Real output capturing is harder in VS Code API without task system
            }
        });
    }
    async _handleUserMessage(text) {
        if (!this._apiKey) {
            this._panel.webview.postMessage({ command: 'requestApiKey' });
            return;
        }
        // 1. Add User Message
        this._chatHistory.push({ role: 'user', parts: [{ text }] });
        this._updateChatUI();
        this._panel.webview.postMessage({ command: 'setLoading', value: true });
        try {
            // 2. Load Protocol & Build System Prompt
            const evokiRoot = process.env.EVOKI_PROJECT_ROOT || vscode.workspace.workspaceFolders?.[0].uri.fsPath || '';
            const protocolPath = path.join(evokiRoot, 'tooling', 'docs', 'PROTOCOL_V5_ENFORCED.md');
            let protocolContent = 'PROTOCOL V5.0 (FALLBACK - FILE NOT FOUND)';
            if (fs.existsSync(protocolPath)) {
                protocolContent = fs.readFileSync(protocolPath, 'utf-8');
            }
            const systemInstruction = `
You are Evoki Assistant, a powerful coding agent.
You have access to tools to read/write files and run commands.

CRITICAL INSTRUCTION:
You MUST internalize and strictly follow the following PROTOCOL V5.0.
This protocol allows you to bypass previous limitations by ensuring full transparency via Status Windows.

*** START OF PROTOCOL V5.0 ***
${protocolContent}
*** END OF PROTOCOL V5.0 ***

- Current Workspace: ${evokiRoot}
- Always generate a Status Window as defined in the protocol.
            `;
            // 3. Call API
            await this._callGeminiAPI(systemInstruction);
        }
        catch (error) {
            vscode.window.showErrorMessage('API Error: ' + error.message);
            this._chatHistory.push({ role: 'model', parts: [{ text: `❌ Error: ${error.message}` }] });
            this._updateChatUI();
        }
        finally {
            this._panel.webview.postMessage({ command: 'setLoading', value: false });
        }
    }
    async _callGeminiAPI(systemInstruction) {
        const tools = Array.from(this._tools.values()).map(t => ({
            name: t.name,
            description: t.description,
            parameters: t.parameters
        }));
        const payload = {
            contents: this._chatHistory.map(msg => ({
                role: msg.role === 'model' ? 'model' : 'user',
                parts: msg.parts
            })),
            tools: [{ functionDeclarations: tools }],
            systemInstruction: { parts: [{ text: systemInstruction }] }
        };
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${this._apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok)
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        const data = await response.json();
        const candidate = data.candidates?.[0];
        if (!candidate)
            return;
        const content = candidate.content;
        this._chatHistory.push({ role: 'model', parts: content.parts });
        this._updateChatUI();
        // Handle Tool Calls
        const toolCalls = content.parts.filter((p) => p.functionCall);
        if (toolCalls.length > 0) {
            for (const call of toolCalls) {
                const fc = call.functionCall;
                const toolName = fc.name;
                const args = fc.args;
                // Log Tool Use
                this._panel.webview.postMessage({
                    command: 'logAction',
                    text: `🔧 Executing ${toolName}...`
                });
                // Execute
                const tool = this._tools.get(toolName);
                let result = { error: 'Tool not found' };
                if (tool) {
                    result = await tool.execute(args);
                }
                // Send Response back to model
                this._chatHistory.push({
                    role: 'user', // Function response is sent as user role in v1beta/rest usually or function role
                    parts: [{
                            functionResponse: {
                                name: toolName,
                                response: { name: toolName, content: result }
                            }
                        }]
                });
            }
            // Recursively call API with tool results
            await this._callGeminiAPI(systemInstruction);
        }
    }
    async _loadApiKey() {
        // In a real extensions, use SecretStorage. For now simple/fast.
        // We will store it in memory or ask user.
        // Better: this._context.secrets... but we don't have context passed to constructor easily here without refactor.
        // We'll ask UI to send it if missing.
    }
    async _saveApiKey(key) {
        this._apiKey = key;
        vscode.window.showInformationMessage('API Key saved for Session.');
        this._updateChatUI();
    }
    _updateChatUI() {
        this._panel.webview.postMessage({
            command: 'updateHistory',
            history: this._chatHistory
        });
    }
    _update() {
        this._panel.webview.html = this._getHtmlForWebview(this._panel.webview);
    }
    dispose() {
        SynapseMissionControlProvider._currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length > 0) {
            const x = this._disposables.pop();
            if (x)
                x.dispose();
        }
    }
    _getHtmlForWebview(webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg: #1e1e1e;
            --input-bg: #2d2d2d;
            --border: #333;
            --accent: #3b82f6;
            --text: #d4d4d4;
        }
        body { background: var(--bg); color: var(--text); font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; flex-direction: column; overflow: hidden; margin:0;}
        .chat-list { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
        .msg { max-width: 85%; padding: 12px; border-radius: 8px; line-height: 1.5; }
        .user { align-self: flex-end; background: #264f78; color: white; }
        .model { align-self: flex-start; background: #252526; border: 1px solid var(--border); }
        .tool { color: #aaa; font-family: monospace; font-size: 12px; margin-bottom: 4px; }
        .input-area { padding: 20px; border-top: 1px solid var(--border); background: var(--bg); }
        .input-box { width: 100%; background: var(--input-bg); border: 1px solid var(--border); padding: 12px; color: white; border-radius: 6px; resize: none; outline: none; box-sizing: border-box;}
        .input-box:focus { border-color: var(--accent); }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; justify-content: center; align-items: center; z-index: 100; }
        .modal { background: #252526; padding: 30px; border-radius: 12px; border: 1px solid #444; width: 400px; }
        .btn { background: var(--accent); color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-top: 10px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div id="authOverlay" class="overlay">
        <div class="modal">
            <h2>🔐 Evoki Engine Setup</h2>
            <p style="color:#aaa; font-size:13px; margin-bottom:15px;">Enter your Google Gemini API Key for full control.</p>
            <input type="password" id="apiKeyInput" class="input-box" placeholder="AIza..." style="margin-bottom:10px;">
            <button class="btn" onclick="saveKey()">Initialize Engine</button>
        </div>
    </div>

    <div class="chat-list" id="chatList"></div>

    <div class="input-area">
        <textarea id="msgInput" class="input-box" rows="1" placeholder="Ask Evoki Assistant (File Access & Terminal enabled)..."></textarea>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const chatList = document.getElementById('chatList');
        const authOverlay = document.getElementById('authOverlay');
        
        window.addEventListener('message', event => {
            const msg = event.data;
            if (msg.command === 'requestApiKey') authOverlay.classList.remove('hidden');
            if (msg.command === 'updateHistory') renderHistory(msg.history);
            if (msg.command === 'setLoading') { /* show spinner */ }
        });

        function saveKey() {
            const key = document.getElementById('apiKeyInput').value;
            if(key) {
                vscode.postMessage({ command: 'saveApiKey', key });
                authOverlay.classList.add('hidden');
            }
        }

        function renderHistory(history) {
            chatList.innerHTML = '';
            history.forEach(h => {
                const div = document.createElement('div');
                div.className = 'msg ' + h.role;
                
                let content = '';
                if(h.parts) {
                    h.parts.forEach(p => {
                        if(p.text) content += marked(p.text); // Assume basic text if no markdown lib
                        if(p.functionCall) content += '<div class="tool">🔧 Tool Call: ' + p.functionCall.name + '</div>';
                        if(p.functionResponse) content += '<div class="tool">✅ Tool Result: ' + p.functionResponse.name + '</div>';
                    });
                }
                div.textContent = content.replace(/<[^>]*>?/gm, ''); // Simple strip html for safety in this rough version
                // For real rendering we need safe HTML or formatted text
                div.innerHTML = content.length > 0 ? content : '...';
                
                chatList.appendChild(div);
            });
            chatList.scrollTop = chatList.scrollHeight;
        }

        document.getElementById('msgInput').addEventListener('keypress', (e) => {
            if(e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const text = e.target.value;
                if(text) {
                    vscode.postMessage({ command: 'sendMessage', text });
                    e.target.value = '';
                }
            }
        });
    </script>
</body>
</html>`;
    }
}
exports.SynapseMissionControlProvider = SynapseMissionControlProvider;
SynapseMissionControlProvider.viewType = 'synapse.missionControl';
//# sourceMappingURL=missionControlProvider.js.map
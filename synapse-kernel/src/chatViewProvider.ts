import * as vscode from 'vscode';
import * as child_process from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(child_process.exec);

export class SynapseChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'synapse.chatPanel';

    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) { }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (data) => {
            switch (data.type) {
                case 'sendMessage':
                    await this._handleChatMessage(data.message);
                    break;
                case 'refreshStatus':
                    await this._refreshStatusWindow();
                    break;
                case 'mentionFile':
                    await this._handleFileMention();
                    break;
            }
        });

        // Initial status window fetch
        this._refreshStatusWindow();
    }

    private async _handleChatMessage(message: string) {
        if (!this._view) return;

        // 1. Get current status window
        const statusWindow = await this._getStatusWindow();

        // 2. Send to backend API
        try {
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    history: []
                })
            });

            if (response.ok) {
                const data = await response.json();
                this._view.webview.postMessage({
                    type: 'chatResponse',
                    response: data.response,
                    statusWindow: data.status_window
                });
            } else {
                // Fallback: Inject into Antigravity chat
                await this._injectIntoAntigravity(message, statusWindow);
            }
        } catch (error) {
            // Fallback: Inject into Antigravity chat
            await this._injectIntoAntigravity(message, statusWindow);
        }
    }

    private async _injectIntoAntigravity(message: string, statusWindow: string | null) {
        // Open Antigravity chat and inject
        await vscode.commands.executeCommand('workbench.action.chat.open');

        // Format the message with status window
        let fullMessage = '';
        if (statusWindow) {
            fullMessage = '```json\n' + statusWindow + '\n```\n\n';
        }
        fullMessage += message;

        // Notify user
        this._view?.webview.postMessage({
            type: 'fallbackNotice',
            message: 'Using Antigravity fallback - check the Gemini chat panel'
        });

        vscode.window.showInformationMessage(
            'Message prepared with Status Window. Open Gemini chat (Alt+G) and paste.',
            'Copy to Clipboard'
        ).then(selection => {
            if (selection === 'Copy to Clipboard') {
                vscode.env.clipboard.writeText(fullMessage);
            }
        });
    }

    private async _getStatusWindow(): Promise<string | null> {
        try {
            const { stdout } = await execAsync(
                'python "C:\\Evoki V2.0\\evoki-app\\scripts\\get_status_block.py"',
                { timeout: 5000 }
            );
            return stdout.trim();
        } catch {
            return null;
        }
    }

    private async _refreshStatusWindow() {
        const statusWindow = await this._getStatusWindow();
        if (statusWindow && this._view) {
            try {
                const parsed = JSON.parse(statusWindow);
                this._view.webview.postMessage({
                    type: 'statusUpdate',
                    statusWindow: parsed
                });
            } catch {
                // Invalid JSON
            }
        }
    }

    private async _handleFileMention() {
        const files = await vscode.window.showOpenDialog({
            canSelectMany: true,
            openLabel: 'Add to Context'
        });

        if (files && this._view) {
            const filePaths = files.map(f => f.fsPath);
            this._view.webview.postMessage({
                type: 'filesAdded',
                files: filePaths
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synapse Chat</title>
    <style>
        :root {
            --bg-primary: var(--vscode-editor-background);
            --bg-secondary: var(--vscode-sideBar-background);
            --text-primary: var(--vscode-editor-foreground);
            --text-secondary: var(--vscode-descriptionForeground);
            --accent: var(--vscode-button-background);
            --border: var(--vscode-panel-border);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: var(--vscode-font-family);
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .status-window {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 12px;
            font-size: 11px;
        }
        .status-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .status-title {
            font-weight: 600;
            color: var(--accent);
        }
        .status-badge {
            background: rgba(63, 185, 80, 0.2);
            color: #3fb950;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }
        .status-field { font-size: 10px; }
        .status-label { color: var(--text-secondary); }
        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
        }
        .message {
            margin-bottom: 12px;
            max-width: 90%;
        }
        .message.user { margin-left: auto; }
        .message-bubble {
            padding: 8px 12px;
            border-radius: 12px;
            line-height: 1.4;
        }
        .message.user .message-bubble {
            background: var(--accent);
            color: var(--vscode-button-foreground);
        }
        .message.assistant .message-bubble {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
        }
        .input-container {
            padding: 12px;
            border-top: 1px solid var(--border);
        }
        .context-bar {
            display: flex;
            gap: 8px;
            margin-bottom: 8px;
            font-size: 11px;
        }
        .context-item {
            background: var(--bg-secondary);
            padding: 2px 8px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .input-wrapper {
            display: flex;
            gap: 8px;
        }
        textarea {
            flex: 1;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 8px 12px;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 12px;
            resize: none;
            min-height: 36px;
        }
        textarea:focus { outline: 1px solid var(--accent); }
        button {
            background: var(--accent);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 8px;
            padding: 8px 16px;
            cursor: pointer;
            font-weight: 500;
        }
        button:hover { opacity: 0.9; }
        .add-file-btn {
            background: transparent;
            border: 1px dashed var(--border);
            color: var(--text-secondary);
            padding: 2px 8px;
            font-size: 11px;
        }
        .loading { opacity: 0.5; }
    </style>
</head>
<body>
    <div class="status-window" id="statusWindow">
        <div class="status-header">
            <span class="status-title">⚡ Synapse Status</span>
            <span class="status-badge" id="statusBadge">ACTIVE</span>
        </div>
        <div class="status-grid">
            <div class="status-field">
                <div class="status-label">Step ID</div>
                <div id="stepId">---</div>
            </div>
            <div class="status-field">
                <div class="status-label">Cycle</div>
                <div id="cycle">---</div>
            </div>
            <div class="status-field">
                <div class="status-label">Goal</div>
                <div id="goal">---</div>
            </div>
            <div class="status-field">
                <div class="status-label">Time</div>
                <div id="timeSource">---</div>
            </div>
        </div>
    </div>

    <div class="chat-history" id="chatHistory">
        <div style="text-align: center; color: var(--text-secondary); padding: 20px;">
            <h3>⚡ Synapse Chat</h3>
            <p style="font-size: 11px; margin-top: 8px;">
                Ask anything. Status Window is auto-injected.
            </p>
        </div>
    </div>

    <div class="input-container">
        <div class="context-bar" id="contextBar">
            <button class="add-file-btn" id="addFileBtn">+ @file</button>
        </div>
        <div class="input-wrapper">
            <textarea id="messageInput" placeholder="Ask Synapse or type '@'" rows="1"></textarea>
            <button id="sendBtn">Send ⚡</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const chatHistory = document.getElementById('chatHistory');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const addFileBtn = document.getElementById('addFileBtn');
        const contextBar = document.getElementById('contextBar');

        let contextFiles = [];

        // Handle incoming messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.type) {
                case 'statusUpdate':
                    updateStatusWindow(message.statusWindow);
                    break;
                case 'chatResponse':
                    addMessage('assistant', message.response);
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send ⚡';
                    if (message.statusWindow) {
                        updateStatusWindow(message.statusWindow);
                    }
                    break;
                case 'fallbackNotice':
                    addMessage('system', message.message);
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Send ⚡';
                    break;
                case 'filesAdded':
                    message.files.forEach(addFileToContext);
                    break;
            }
        });

        function updateStatusWindow(sw) {
            if (!sw) return;
            document.getElementById('stepId').textContent = sw.step_id || '---';
            document.getElementById('cycle').textContent = sw.cycle || '---';
            document.getElementById('goal').textContent = sw.goal || '---';
            const time = sw.time_source || '---';
            document.getElementById('timeSource').textContent = time.substring(0, 25);
        }

        function addMessage(role, content) {
            const emptyState = chatHistory.querySelector('div[style*="text-align: center"]');
            if (emptyState) emptyState.remove();

            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerHTML = '<div class="message-bubble">' + escapeHtml(content) + '</div>';
            chatHistory.appendChild(div);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function addFileToContext(filePath) {
            if (contextFiles.includes(filePath)) return;
            contextFiles.push(filePath);
            
            const chip = document.createElement('span');
            chip.className = 'context-item';
            chip.textContent = '@' + filePath.split('\\\\').pop();
            chip.onclick = () => {
                contextFiles = contextFiles.filter(f => f !== filePath);
                chip.remove();
            };
            contextBar.insertBefore(chip, addFileBtn);
        }

        sendBtn.onclick = () => {
            const msg = messageInput.value.trim();
            if (!msg) return;

            addMessage('user', msg);
            messageInput.value = '';
            sendBtn.disabled = true;
            sendBtn.textContent = '...';

            vscode.postMessage({
                type: 'sendMessage',
                message: msg,
                contextFiles: contextFiles
            });
        };

        messageInput.onkeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendBtn.click();
            }
            if (e.key === '@') {
                // Show file picker on @
                setTimeout(() => {
                    if (messageInput.value.endsWith('@')) {
                        addFileBtn.click();
                    }
                }, 100);
            }
        };

        addFileBtn.onclick = () => {
            vscode.postMessage({ type: 'mentionFile' });
        };

        // Request initial status
        vscode.postMessage({ type: 'refreshStatus' });
    </script>
</body>
</html>`;
    }
}

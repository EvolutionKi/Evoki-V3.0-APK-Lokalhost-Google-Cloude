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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const child_process = __importStar(require("child_process"));
const path = __importStar(require("path"));
const util_1 = require("util");
const chatViewProvider_1 = require("./chatViewProvider");
const chatParticipant_1 = require("./chatParticipant");
const complianceMonitor_1 = require("./complianceMonitor");
const execAsync = (0, util_1.promisify)(child_process.exec);
let complianceMonitor = null;
let complianceWatcher = null;
let healthMonitor = null;
function activate(context) {
    console.log('⚡ Synapse Nexus Kernel V2.0 is now active!');
    // Register Chat Panel WebView
    const chatProvider = new chatViewProvider_1.SynapseChatViewProvider(context.extensionUri);
    context.subscriptions.push(vscode.window.registerWebviewViewProvider(chatViewProvider_1.SynapseChatViewProvider.viewType, chatProvider));
    // Register @synapse Chat Participant
    const chatParticipant = new chatParticipant_1.SynapseChatParticipant(context);
    context.subscriptions.push(chatParticipant.register());
    // Start Guardian Monitors (Python Watchers)
    startGuardianMonitors(context);
    // Start Built-in Compliance Monitor (VS Code Errors)
    complianceMonitor = new complianceMonitor_1.ComplianceMonitor(context);
    complianceMonitor.start();
    // Status command
    let disposable = vscode.commands.registerCommand('synapse.nexus.status', () => {
        const watcherStatus = complianceWatcher ? '✅ Running' : '❌ Stopped';
        const monitorStatus = healthMonitor ? '✅ Running' : '❌ Stopped';
        vscode.window.showInformationMessage(`Synapse Nexus Kernel ⚡\n\n` +
            `Compliance Watcher: ${watcherStatus}\n` +
            `Health Monitor: ${monitorStatus}`);
    });
    // Status Window Injection Command (Ctrl+Shift+I)
    let injectCommand = vscode.commands.registerCommand('synapse.nexus.injectStatusWindow', async () => {
        await injectStatusWindow();
    });
    // Inject AND Send Command (Alt+Enter)
    let injectAndSendCommand = vscode.commands.registerCommand('synapse.nexus.injectAndSend', async () => {
        await injectStatusWindowAndSend();
    });
    // Open Chat Panel Command
    let openChatCommand = vscode.commands.registerCommand('synapse.chat.openPanel', () => {
        vscode.commands.executeCommand('workbench.view.extension.synapse-chat');
    });
    context.subscriptions.push(disposable, injectCommand, injectAndSendCommand, openChatCommand);
}
function startGuardianMonitors(context) {
    const evokiRoot = process.env.EVOKI_PROJECT_ROOT || 'C:\\Evoki V3.0 APK-Lokalhost-Google Cloude';
    const daemonsPath = path.join(evokiRoot, 'tooling', 'scripts', 'daemons');
    // Start all 3 watchers
    const watchers = [
        {
            name: 'Pending Status Watcher',
            script: path.join(daemonsPath, 'pending_status_watcher.py')
        },
        {
            name: 'Context Watcher',
            script: path.join(daemonsPath, 'context_watcher.py'),
            args: ['--monitor']
        },
        {
            name: 'Compliance Enforcer',
            script: path.join(daemonsPath, 'compliance_enforcer.py')
        }
    ];
    watchers.forEach(watcher => {
        try {
            const proc = child_process.spawn('python', watcher.args ? [watcher.script, ...watcher.args] : [watcher.script], {
                cwd: evokiRoot,
                detached: true,
                stdio: 'ignore'
            });
            proc.unref();
            console.log(`✅ ${watcher.name} started`);
        }
        catch (error) {
            console.error(`❌ Failed to start ${watcher.name}:`, error);
        }
    });
}
function deactivate() {
    if (complianceMonitor) {
        complianceMonitor.stop();
    }
}
// ========================================
// Status Window Injection Functions
// ========================================
async function getStatusWindow() {
    try {
        const { stdout } = await execAsync('python "C:\\Evoki V2.0\\evoki-app\\scripts\\get_status_block.py"', { timeout: 5000 });
        return stdout.trim();
    }
    catch (error) {
        console.error('Failed to get status window:', error);
        return null;
    }
}
async function injectStatusWindow() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return false;
    }
    const statusWindow = await getStatusWindow();
    if (!statusWindow) {
        vscode.window.showErrorMessage('Failed to generate Status Window');
        return false;
    }
    const formattedWindow = '```json\n' + statusWindow + '\n```\n\n';
    await editor.edit(editBuilder => {
        editBuilder.insert(editor.selection.start, formattedWindow);
    });
    vscode.window.showInformationMessage('Status Window injected ⚡');
    return true;
}
async function injectStatusWindowAndSend() {
    const success = await injectStatusWindow();
    if (success) {
        // Try to trigger Antigravity's send command
        const commands = [
            'workbench.action.chat.submit',
            'interactive.execute'
        ];
        for (const cmd of commands) {
            try {
                await vscode.commands.executeCommand(cmd);
                return;
            }
            catch {
                // Try next
            }
        }
        vscode.window.showInformationMessage('Status Window injected - press Enter to send');
    }
}
//# sourceMappingURL=index.js.map
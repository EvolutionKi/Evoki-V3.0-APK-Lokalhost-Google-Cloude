import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';
import { promisify } from 'util';
import { SynapseChatViewProvider } from './chatViewProvider';
import { SynapseChatParticipant } from './chatParticipant';
import { ComplianceMonitor } from './complianceMonitor';
import { UserRulesEnforcer } from './userRulesEnforcer';

const execAsync = promisify(child_process.exec);

let complianceMonitor: ComplianceMonitor | null = null;
let userRulesEnforcer: UserRulesEnforcer | null = null;

let complianceWatcher: child_process.ChildProcess | null = null;
let healthMonitor: child_process.ChildProcess | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('⚡ Synapse Nexus Kernel V2.0 is now active!');

    // Register Chat Panel WebView
    const chatProvider = new SynapseChatViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            SynapseChatViewProvider.viewType,
            chatProvider
        )
    );

    // Register @synapse Chat Participant
    const chatParticipant = new SynapseChatParticipant(context);
    context.subscriptions.push(chatParticipant.register());

    // Start Guardian Monitors (Python Watchers)
    startGuardianMonitors(context);

    // Start Built-in Compliance Monitor (VS Code Errors)
    complianceMonitor = new ComplianceMonitor(context);
    complianceMonitor.start();

    // Start UserRulesEnforcer (Output-Gate Enforcement)
    userRulesEnforcer = new UserRulesEnforcer(context);
    userRulesEnforcer.start();

    // Status command
    let disposable = vscode.commands.registerCommand('synapse.nexus.status', () => {
        const watcherStatus = complianceWatcher ? '✅ Running' : '❌ Stopped';
        const monitorStatus = healthMonitor ? '✅ Running' : '❌ Stopped';

        vscode.window.showInformationMessage(
            `Synapse Nexus Kernel ⚡\n\n` +
            `Compliance Watcher: ${watcherStatus}\n` +
            `Health Monitor: ${monitorStatus}`
        );
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

function startGuardianMonitors(context: vscode.ExtensionContext) {
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
            const proc = child_process.spawn(
                'python',
                watcher.args ? [watcher.script, ...watcher.args] : [watcher.script],
                {
                    cwd: evokiRoot,
                    detached: true,
                    stdio: 'ignore'
                }
            );
            proc.unref();
            console.log(`✅ ${watcher.name} started`);
        } catch (error) {
            console.error(`❌ Failed to start ${watcher.name}:`, error);
        }
    });
}

export function deactivate() {
    if (complianceMonitor) {
        complianceMonitor.stop();
    }
    if (userRulesEnforcer) {
        userRulesEnforcer.stop();
    }
}

// ========================================
// Status Window Injection Functions
// ========================================

async function getStatusWindow(): Promise<string | null> {
    try {
        const { stdout } = await execAsync(
            'python "C:\\Evoki V2.0\\evoki-app\\scripts\\get_status_block.py"',
            { timeout: 5000 }
        );
        return stdout.trim();
    } catch (error) {
        console.error('Failed to get status window:', error);
        return null;
    }
}

async function injectStatusWindow(): Promise<boolean> {
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

async function injectStatusWindowAndSend(): Promise<void> {
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
            } catch {
                // Try next
            }
        }

        vscode.window.showInformationMessage('Status Window injected - press Enter to send');
    }
}

import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { SovereignController } from './sovereignController';

export function activate(context: vscode.ExtensionContext) {
    const evokiRoot = vscode.workspace.workspaceFolders?.[0].uri.fsPath || '';
    console.log(`Kernel Activation. Root: ${evokiRoot}`);
    vscode.window.showInformationMessage(`Sovereign Kernel Active in: ${evokiRoot || 'NONE'}`);
    if (!evokiRoot) {
        console.warn("No workspace folder detected. Kernel dormant.");
        return;
    }

    const controller = new SovereignController(evokiRoot);

    console.log('Evoki Sovereign Kernel is now active.');

    let disposable = vscode.commands.registerCommand('synapse.toggleGodMode', () => {
        controller.toggleSovereignMode();
    });

    context.subscriptions.push(disposable);

    // File Watcher für pending_status.json
    const statusDir = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'status');
    if (!fs.existsSync(statusDir)) {
        fs.mkdirSync(statusDir, { recursive: true });
    }

    const watcher = vscode.workspace.createFileSystemWatcher(
        new vscode.RelativePattern(statusDir, 'pending_status.json')
    );

    watcher.onDidChange(() => controller.processPendingStatus());
    watcher.onDidCreate(() => controller.processPendingStatus());

    context.subscriptions.push(watcher);

    // Initialer Check beim Start
    controller.processPendingStatus();
}

export function deactivate() {}

import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { StateEngine } from './stateEngine';

export class SovereignController {
    private stateEngine: StateEngine;
    private statusPath: string;
    private evokiRoot: string;

    constructor(evokiRoot: string) {
        this.evokiRoot = evokiRoot;
        this.stateEngine = new StateEngine(evokiRoot);
        this.statusPath = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'status', 'pending_status.json');
    }

    public async processPendingStatus() {
        console.log(`Checking for pending status at: ${this.statusPath}`);
        if (!fs.existsSync(this.statusPath)) {
            console.log("No pending status found.");
            return;
        }

        try {
            const content = fs.readFileSync(this.statusPath, 'utf-8');
            console.log("Read pending_status.json content.");
            const status = JSON.parse(content);

            // Schema-Check (Minimal)
            if (!status.goal || !status.actions) {
                console.error("Invalid status window format.");
                return;
            }

            // Log entry
            await this.stateEngine.appendEvent('STATUS_SYNCED', {
                goal: status.goal,
                action_count: status.actions.length
            });

            // Action Execution Logic (Hard-Gate)
            const snapshot = this.stateEngine.getSnapshot();
            
            for (const action of status.actions) {
                console.log(`Executing action: ${action.title} [${action.type}]`);
                
                if (snapshot.sovereign_mode) {
                    await this.executeAction(action);
                } else {
                    console.log(`Skipping action ${action.title} - Sovereign Mode is OFF`);
                }
            }

            // Move to history (clean up pending)
            fs.unlinkSync(this.statusPath);

        } catch (err) {
            console.error("Error processing pending status:", err);
        }
    }

    private async executeAction(action: any) {
        try {
            switch (action.type) {
                case 'FILE_WRITE':
                    if (action.path && action.content !== undefined) {
                        const fullPath = path.isAbsolute(action.path) ? action.path : path.join(this.evokiRoot, action.path);
                        fs.mkdirSync(path.dirname(fullPath), { recursive: true });
                        fs.writeFileSync(fullPath, action.content);
                        await this.stateEngine.appendEvent('ACTION_EXEC_FILE_WRITE', { path: action.path });
                    }
                    break;

                case 'TERMINAL_RUN':
                    if (action.command) {
                        const terminal = vscode.window.activeTerminal || vscode.window.createTerminal('Synapse Sovereign');
                        terminal.show();
                        terminal.sendText(action.command);
                        await this.stateEngine.appendEvent('ACTION_EXEC_TERMINAL_RUN', { command: action.command });
                    }
                    break;

                default:
                    console.warn(`Unknown action type: ${action.type}`);
            }
        } catch (err) {
            console.error(`Failed to execute action ${action.title}:`, err);
            await this.stateEngine.appendEvent('ACTION_EXEC_FAILED', { title: action.title, error: String(err) });
        }
    }

    public toggleSovereignMode() {
        const snapshot = this.stateEngine.getSnapshot();
        const newState = !snapshot.sovereign_mode;
        this.stateEngine.appendEvent('SOVEREIGN_MODE_TOGGLE', { enabled: newState });
        vscode.window.showInformationMessage(`Sovereign Mode: ${newState ? 'ENABLED (GOD MODE)' : 'DISABLED'}`);
    }
}

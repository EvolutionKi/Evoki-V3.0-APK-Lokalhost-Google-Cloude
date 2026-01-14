import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export class ComplianceMonitor {
    private checkInterval: NodeJS.Timeout | null = null;
    private lastPromptTime: Date | null = null;
    private lastPromptText: string | null = null;
    private lastStatusCount: number = 0;
    private warned: boolean = false;
    private errorLogPath: string = '';

    constructor(private context: vscode.ExtensionContext) {
        const evokiRoot = process.env.EVOKI_PROJECT_ROOT || 'C:\\Evoki V3.0 APK-Lokalhost-Google Cloude';
        this.errorLogPath = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'compliance_errors.json');
    }

    start() {
        const config = vscode.workspace.getConfiguration('synapse.compliance');
        const enabled = config.get<boolean>('enabled', true);

        if (!enabled) {
            console.log('⏸️  Compliance monitoring disabled');
            return;
        }

        const interval = config.get<number>('checkInterval', 10) * 1000;

        this.checkInterval = setInterval(() => {
            this.check();
        }, interval);

        console.log('✅ Built-in Compliance Monitor started');
    }

    stop() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
            console.log('⏸️  Compliance Monitor stopped');
        }
    }

    private writeErrorLog(error: {
        timestamp: string;
        type: 'breach' | 'warning';
        message: string;
        prompt?: string;
        timeSincePrompt?: number;
    }) {
        try {
            let errors: any[] = [];

            // Load existing errors
            if (fs.existsSync(this.errorLogPath)) {
                const data = fs.readFileSync(this.errorLogPath, 'utf-8');
                errors = JSON.parse(data);
            }

            // Add new error
            errors.push(error);

            // Keep only last 100 errors
            if (errors.length > 100) {
                errors = errors.slice(-100);
            }

            // Write back
            fs.writeFileSync(
                this.errorLogPath,
                JSON.stringify(errors, null, 2),
                'utf-8'
            );
        } catch (err) {
            console.error('Failed to write error log:', err);
        }
    }

    private async check() {
        const config = vscode.workspace.getConfiguration('synapse.compliance');
        const maxResponseTime = config.get<number>('maxResponseTime', 60);
        const showInEditor = config.get<boolean>('notifications.showInEditor', true);

        const evokiRoot = process.env.EVOKI_PROJECT_ROOT || 'C:\\Evoki V3.0 APK-Lokalhost-Google Cloude';
        const historyPath = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'status', 'status_window_history.json');

        try {
            // Read status history
            const historyData = fs.readFileSync(historyPath, 'utf-8');
            const history = JSON.parse(historyData);
            const entries = history.entries || [];
            const currentStatusCount = entries.length;

            // Get latest prompt
            const latestEntry = entries[entries.length - 1];
            if (latestEntry) {
                const sw = latestEntry.status_window || {};
                const inputs = sw.inputs || {};
                const prompt = inputs.raw_user_request || (inputs.user_messages || []).join('\n');
                const timestamp = latestEntry.timestamp;

                if (prompt && timestamp && prompt !== this.lastPromptText) {
                    // New prompt detected!
                    this.lastPromptTime = new Date(timestamp);
                    this.lastPromptText = prompt;
                    this.lastStatusCount = currentStatusCount;
                    this.warned = false;

                    console.log(`📝 New prompt detected: "${prompt.substring(0, 50)}..."`);
                }
            }

            // Check if status window was written
            if (this.lastPromptTime) {
                const timeSincePrompt = (Date.now() - this.lastPromptTime.getTime()) / 1000;
                const statusWritten = currentStatusCount > this.lastStatusCount;

                if (statusWritten) {
                    if (!this.warned) {
                        console.log(`✅ Status Window written (${timeSincePrompt.toFixed(0)}s after prompt)`);
                    }
                    this.lastPromptTime = null;
                    this.lastStatusCount = currentStatusCount;
                    this.warned = false;
                } else if (timeSincePrompt > maxResponseTime && !this.warned) {
                    // BREACH!
                    this.warned = true;

                    // Write to error log (for agent auto-awareness)
                    this.writeErrorLog({
                        timestamp: new Date().toISOString(),
                        type: 'breach',
                        message: `Kein Status Window nach ${timeSincePrompt.toFixed(0)}s`,
                        prompt: this.lastPromptText?.substring(0, 100),
                        timeSincePrompt: Math.floor(timeSincePrompt)
                    });

                    // Send chat message to agent
                    try {
                        vscode.commands.executeCommand(
                            'workbench.action.chat.open',
                            {
                                query: `@workspace 🚨 COMPLIANCE BREACH: Kein Status Window geschrieben nach ${timeSincePrompt.toFixed(0)}s! Prompt war: "${this.lastPromptText?.substring(0, 80)}..." Bitte sofort Status Window nachholen!`
                            }
                        );
                    } catch (err) {
                        console.error('Failed to send chat message:', err);
                    }

                    if (showInEditor) {
                        vscode.window.showErrorMessage(
                            `🚨 Compliance BREACH! Kein Status Window nach ${timeSincePrompt.toFixed(0)}s!`,
                            'Status schreiben'
                        ).then(selection => {
                            if (selection === 'Status schreiben') {
                                vscode.commands.executeCommand('synapse.nexus.injectStatusWindow');
                            }
                        });
                    }

                    console.error(`🚨 BREACH! No Status Window after ${timeSincePrompt.toFixed(0)}s`);
                } else if (timeSincePrompt > maxResponseTime / 2 && !this.warned) {
                    // Warning at 50%
                    const remaining = maxResponseTime - timeSincePrompt;

                    // Write warning to log
                    this.writeErrorLog({
                        timestamp: new Date().toISOString(),
                        type: 'warning',
                        message: `Status Window fehlt! Noch ${remaining.toFixed(0)}s Zeit`,
                        prompt: this.lastPromptText?.substring(0, 100),
                        timeSincePrompt: Math.floor(timeSincePrompt)
                    });

                    if (showInEditor) {
                        vscode.window.showWarningMessage(
                            `⚠️  Status Window fehlt! Noch ${remaining.toFixed(0)}s Zeit!`
                        );
                    }
                }
            }
        } catch (error) {
            console.error('Error checking compliance:', error);
        }
    }
}

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
exports.SovereignController = void 0;
const vscode = __importStar(require("vscode"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const stateEngine_1 = require("./stateEngine");
class SovereignController {
    constructor(evokiRoot) {
        this.evokiRoot = evokiRoot;
        this.stateEngine = new stateEngine_1.StateEngine(evokiRoot);
        this.statusPath = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'status', 'pending_status.json');
    }
    async processPendingStatus() {
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
                }
                else {
                    console.log(`Skipping action ${action.title} - Sovereign Mode is OFF`);
                }
            }
            // Move to history (clean up pending)
            fs.unlinkSync(this.statusPath);
        }
        catch (err) {
            console.error("Error processing pending status:", err);
        }
    }
    async executeAction(action) {
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
        }
        catch (err) {
            console.error(`Failed to execute action ${action.title}:`, err);
            await this.stateEngine.appendEvent('ACTION_EXEC_FAILED', { title: action.title, error: String(err) });
        }
    }
    toggleSovereignMode() {
        const snapshot = this.stateEngine.getSnapshot();
        const newState = !snapshot.sovereign_mode;
        this.stateEngine.appendEvent('SOVEREIGN_MODE_TOGGLE', { enabled: newState });
        vscode.window.showInformationMessage(`Sovereign Mode: ${newState ? 'ENABLED (GOD MODE)' : 'DISABLED'}`);
    }
}
exports.SovereignController = SovereignController;
//# sourceMappingURL=sovereignController.js.map
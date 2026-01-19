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
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const sovereignController_1 = require("./sovereignController");
function activate(context) {
    const evokiRoot = vscode.workspace.workspaceFolders?.[0].uri.fsPath || '';
    console.log(`Kernel Activation. Root: ${evokiRoot}`);
    vscode.window.showInformationMessage(`Sovereign Kernel Active in: ${evokiRoot || 'NONE'}`);
    if (!evokiRoot) {
        console.warn("No workspace folder detected. Kernel dormant.");
        return;
    }
    const controller = new sovereignController_1.SovereignController(evokiRoot);
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
    const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(statusDir, 'pending_status.json'));
    watcher.onDidChange(() => controller.processPendingStatus());
    watcher.onDidCreate(() => controller.processPendingStatus());
    context.subscriptions.push(watcher);
    // Initialer Check beim Start
    controller.processPendingStatus();
}
function deactivate() { }
//# sourceMappingURL=index.js.map
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
exports.StateEngine = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const crypto = __importStar(require("crypto"));
class StateEngine {
    constructor(evokiRoot) {
        const stateDir = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'state');
        if (!fs.existsSync(stateDir)) {
            fs.mkdirSync(stateDir, { recursive: true });
        }
        this.eventsPath = path.join(stateDir, 'events.log.jsonl');
        this.snapshotPath = path.join(stateDir, 'state.snapshot.json');
    }
    async appendEvent(type, data) {
        const snapshot = this.getSnapshot();
        const eventId = snapshot.last_event_id + 1;
        const timestamp = new Date().toISOString();
        const event = {
            id: eventId,
            type,
            timestamp,
            data
        };
        const payload = JSON.stringify(event.data) + timestamp + (snapshot.last_hash || '');
        event.hash = crypto.createHash('sha256').update(payload).digest('hex');
        event.prev_hash = snapshot.last_hash;
        fs.appendFileSync(this.eventsPath, JSON.stringify(event) + '\n');
        // Update Snapshot based on event type
        const newSnapshot = {
            ...snapshot,
            last_event_id: eventId,
            last_synced_at: timestamp,
            last_hash: event.hash
        };
        if (type === 'SOVEREIGN_MODE_TOGGLE') {
            newSnapshot.sovereign_mode = data.enabled;
        }
        fs.writeFileSync(this.snapshotPath, JSON.stringify(newSnapshot, null, 2));
        return event;
    }
    getSnapshot() {
        if (!fs.existsSync(this.snapshotPath)) {
            return {
                last_event_id: 0,
                last_synced_at: new Date().toISOString(),
                synapse_status: 'INITIAL',
                blueprint_version: '3.2',
                sovereign_mode: false
            };
        }
        return JSON.parse(fs.readFileSync(this.snapshotPath, 'utf-8'));
    }
}
exports.StateEngine = StateEngine;
//# sourceMappingURL=stateEngine.js.map
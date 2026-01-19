import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';

export interface SynapseEvent {
    id: number;
    type: string;
    timestamp: string;
    data: any;
    hash?: string;
    prev_hash?: string;
}

export interface StateSnapshot {
    last_event_id: number;
    last_synced_at: string;
    synapse_status: string;
    blueprint_version: string;
    sovereign_mode: boolean;
    last_hash?: string;
}

export class StateEngine {
    private eventsPath: string;
    private snapshotPath: string;

    constructor(evokiRoot: string) {
        const stateDir = path.join(evokiRoot, 'tooling', 'data', 'synapse', 'state');
        if (!fs.existsSync(stateDir)) {
            fs.mkdirSync(stateDir, { recursive: true });
        }
        this.eventsPath = path.join(stateDir, 'events.log.jsonl');
        this.snapshotPath = path.join(stateDir, 'state.snapshot.json');
    }

    public async appendEvent(type: string, data: any): Promise<SynapseEvent> {
        const snapshot = this.getSnapshot();
        const eventId = snapshot.last_event_id + 1;
        const timestamp = new Date().toISOString();

        const event: SynapseEvent = {
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
        const newSnapshot: StateSnapshot = {
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

    public getSnapshot(): StateSnapshot {
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

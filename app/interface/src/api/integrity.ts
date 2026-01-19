/**
 * Evoki V3.0 - Integrity API Client
 * 
 * Kommuniziert mit Backend Integrity Endpoints.
 */

export interface IntegrityStatus {
    verified: boolean;
    lockdown: boolean;
    mode: 'prod' | 'dev';
    expected?: {
        genesis_sha256?: string;
        registry_sha256?: string;
        combined_sha256?: string;
    };
    calculated?: {
        genesis_sha256?: string;
        registry_sha256?: string;
        combined_sha256?: string;
    };
    checks?: {
        genesis_ok?: boolean;
        registry_ok?: boolean | null;
        combined_ok?: boolean | null;
    };
    error?: string;
}

/**
 * Prüft Integrity-Status vom Backend.
 */
export async function checkIntegrity(): Promise<IntegrityStatus> {
    try {
        const response = await fetch('http://localhost:8000/api/integrity/status');

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        return {
            verified: data.verified ?? false,
            lockdown: data.lockdown ?? true,
            mode: data.mode ?? 'dev',
            expected: data.expected,
            calculated: data.calculated,
            checks: data.checks,
            error: data.error
        };

    } catch (error) {
        console.error('Integrity Check Failed:', error);
        return {
            verified: false,
            lockdown: true,
            mode: 'dev',
            error: error instanceof Error ? error.message : 'Connection to backend failed'
        };
    }
}

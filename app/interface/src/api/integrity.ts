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
        // Use ENV variable or fallback to relative path
        const base = (import.meta.env.VITE_BACKEND_API_URL || "").replace(/\/+$/, "");
        const url = base ? `${base}/api/integrity/status` : "/api/integrity/status";

        const response = await fetch(url);

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

/**
 * SSE Parser Utility - Phase 0
 * 
 * Parst Server-Sent Events (SSE) aus fetch() ReadableStream
 * 
 * Warum fetch() statt EventSource?
 * - EventSource unterstützt nur GET (kein POST!)
 * - Wir brauchen POST für Prompts (Sicherheit + Längen-Limits)
 * - fetch() ist APK-ready (React Native WebView kompatibel)
 */

export interface SSEEvent {
    event: string;
    data: any;
}

export type SSEEventHandler = (event: SSEEvent) => void;

/**
 * SSE Stream Consumer
 * 
 * Liest ReadableStream aus fetch() Response und parst SSE-Events.
 * 
 * @param response - fetch() Response mit ReadableStream
 * @param onEvent - Callback für jedes SSE-Event
 * @param onError - Callback bei Fehler
 */
export async function consumeSSEStream(
    response: Response,
    onEvent: SSEEventHandler,
    onError?: (error: Error) => void
): Promise<void> {
    if (!response.body) {
        throw new Error('Response body is null');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let buffer = '';
    let currentEvent = '';
    let currentData = '';

    try {
        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            // Dekodiere Chunk
            buffer += decoder.decode(value, { stream: true });

            // Parse SSE-Events (getrennt durch doppelte Newlines)
            const lines = buffer.split('\n');

            // Letzte Zeile könnte unvollständig sein
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('event: ')) {
                    currentEvent = line.slice(7).trim();
                } else if (line.startsWith('data: ')) {
                    currentData = line.slice(6).trim();
                } else if (line === '') {
                    // Leerzeile = Event komplett
                    if (currentEvent && currentData) {
                        try {
                            const parsedData = JSON.parse(currentData);
                            onEvent({
                                event: currentEvent,
                                data: parsedData
                            });
                        } catch {
                            // Falls kein JSON, als String übergeben
                            onEvent({
                                event: currentEvent,
                                data: currentData
                            });
                        }

                        currentEvent = '';
                        currentData = '';
                    }
                }
            }
        }
    } catch (error) {
        if (onError) {
            onError(error as Error);
        } else {
            console.error('SSE Stream Error:', error);
        }
    } finally {
        reader.releaseLock();
    }
}

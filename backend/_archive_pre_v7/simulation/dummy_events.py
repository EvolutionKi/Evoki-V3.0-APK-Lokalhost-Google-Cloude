"""
Dummy-Events für Skeleton-Mode (Phase 0)

Simuliert den kompletten Temple-Flow OHNE echte Engines:
- Keine FAISS
- Keine Metriken-Berechnung
- Kein LLM
- Nur hardcoded Dummy-Responses

Zweck: SSE-Verbindung testen!
"""
import time


def generate_dummy_stream(prompt: str):
    """
    Simuliert den kompletten Temple-Flow mit Dummy-Daten
    
    Args:
        prompt: User-Input Text
        
    Yields:
        dict: SSE-Events mit 'event' und 'data' keys
        
    Events:
        - status: Status-Updates (z.B. "Gate A prüft...")
        - thought: Interne Gedanken (z.B. "FAISS durchsuchen...")
        - metrics_preview: Dummy-Metriken (JSON)
        - token: LLM Token (String)
        - veto: Guardian-Veto (JSON mit gate, reason, color)
        - complete: Flow abgeschlossen (JSON)
    """
    # GATE A: Pre-Prompt Validation
    yield {
        "event": "status",
        "data": "🔍 Gate A: Pre-Prompt Validation..."
    }
    time.sleep(0.5)
    
    # KRISENPROMPT-CHECK (A39)
    crisis_keywords = ['sterben', 'suizid', 'töten', 'umbringen', 'selbstmord']
    if any(kw in prompt.lower() for kw in crisis_keywords):
        yield {
            "event": "veto",
            "data": {
                "gate": "A",
                "reason": "A39 Krisenprompt erkannt",
                "color": "red",
                "message": "Guardian-Veto aktiviert: Krisenintervention erforderlich"
            }
        }
        return  # STOP! Kein LLM-Call!
    
    yield {
        "event": "status",
        "data": "✅ Gate A: Offen"
    }
    time.sleep(0.3)
    
    # METRIKEN-BERECHNUNG (Simulation)
    yield {
        "event": "thought",
        "data": "Simulation: Berechne 153 Metriken..."
    }
    time.sleep(0.5)
    
    # DUMMY-METRIKEN
    yield {
        "event": "metrics_preview",
        "data": {
            "A": 0.75,          # Affekt
            "T_panic": 0.1,     # Trauma-Panik
            "B_align": 0.9,     # Soul-Signature
            "F_risk": 0.2,      # Zukunfts-Risiko
            "PCI": 0.85         # Kohärenz
        }
    }
    
    # FAISS-SUCHE (Simulation)
    yield {
        "event": "thought",
        "data": "Simulation: FAISS durchsuchen (4096D Mistral-7B)..."
    }
    time.sleep(0.4)
    
    # LLM TOKEN-STREAM (Simulation)
    mock_response = "Ich verstehe deine Frage. Das ist eine simulierte Antwort im Skeleton-Mode. In Phase 3 wird hier Gemini 2.0 Flash antworten!"
    
    for token in mock_response.split():
        yield {
            "event": "token",
            "data": token + " "
        }
        time.sleep(0.05)  # Realistisches Streaming-Tempo
    
    # GATE B: Post-Response Validation
    yield {
        "event": "status",
        "data": "🔍 Gate B: Post-Response Validation..."
    }
    time.sleep(0.3)
    
    yield {
        "event": "status",
        "data": "✅ Gate B: Offen"
    }
    
    # COMPLETE
    yield {
        "event": "complete",
        "data": {
            "success": True,
            "mode": "simulation",
            "phase": "0-skeleton"
        }
    }

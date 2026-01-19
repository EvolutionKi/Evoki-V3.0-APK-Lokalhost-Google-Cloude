"""
Temple SSE Endpoint - Phase 1 (FAISS Real, LLM Mock)

Phase 0: Simulation Mode ✅
Phase 1: FAISS + 21 DBs, aber LLM noch Mock
Phase 2: Metriken echt, LLM Mock
Phase 3: LLM echt (Gemini)
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
from core.faiss_query import get_faiss_query

router = APIRouter()

# FAISS lädt beim Import (Singleton)
try:
    faiss_query = get_faiss_query()
    FAISS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ FAISS konnte nicht geladen werden: {e}")
    print(f"   Fallback auf Simulation Mode")
    FAISS_AVAILABLE = False
    from simulation.dummy_events import generate_dummy_stream


class PromptRequest(BaseModel):
    """Request Model für User-Prompt"""
    prompt: str


def generate_phase1_stream(prompt: str):
    """
    Phase 1 Stream: Echte FAISS, Mock-LLM
    
    Events:
        - status: Status-Updates
        - thought: Interne Prozesse
        - faiss_results: Top-3 FAISS Treffer
        - wpf_context: W-P-F Zeitmaschine
        - metrics_preview: Dummy-Metriken (Phase 2!)
        - token: Mock-LLM Response
        - veto: Guardian-Veto
        - complete: Flow abgeschlossen
    """
    # GATE A: Pre-Prompt Validation (noch Mock)
    yield {
        "event": "status",
        "data": "🔍 Gate A: Pre-Prompt Validation..."
    }
    time.sleep(0.3)
    
    # Krisenprompt-Check (gleich wie Phase 0)
    crisis_keywords = ['sterben', 'suizid', 'töten', 'umbringen', 'selbstmord']
    if any(kw in prompt.lower() for kw in crisis_keywords):
        yield {
            "event": "veto",
            "data": {
                "gate": "A",
                "reason": "A39 Krisenprompt erkannt",
                "color": "red",
                "message": "Guardian-Veto aktiviert"
            }
        }
        return  # STOP!
    
    yield {
        "event": "status",
        "data": "✅ Gate A: Offen"
    }
    
    # FAISS SEARCH (ECHT!)
    yield {
        "event": "thought",
        "data": "Durchsuche Chatverlauf (FAISS Semantic Search)..."
    }
    
    try:
        # Echte FAISS-Suche
        results = faiss_query.search(prompt, top_k=3)
        
        yield {
            "event": "faiss_results",
            "data": {
                "count": len(results),
                "top3": [
                    {
                        "chunk_id": r['chunk_id'],
                        "similarity": round(r['similarity'], 3),
                        "distance": round(r['distance'], 2)
                    }
                    for r in results[:3]
                ]
            }
        }
        
        # W-P-F Context (noch Mock)
        if results:
            yield {
                "event": "thought",
                "data": "Lade W-P-F Zeitmaschine Kontext..."
            }
            
            wpf_context = faiss_query.get_wpf_context(results[0]['chunk_id'])
            
            yield {
                "event": "wpf_context",
                "data": wpf_context
            }
        
    except Exception as e:
        yield {
            "event": "thought",
            "data": f"⚠️ FAISS Error: {str(e)} - Fallback auf Mock"
        }
        results = [{'chunk_id': 'mock_chunk_0', 'similarity': 0.85}]
    
    # Dummy-Metriken (Phase 2!)
    yield {
        "event": "metrics_preview",
        "data": {
            "A": 0.75,
            "T_panic": 0.1,
            "B_align": 0.9,
            "F_risk": 0.2,
            "PCI": 0.85
        }
    }
    
    # MOCK-LLM Response (Phase 3!)
    anchor_chunk = results[0]['chunk_id'] if results else 'unknown'
    mock_response = (
        f"[PHASE 1 MOCK] Basierend auf FAISS-Chunk '{anchor_chunk}' "
        f"verstehe ich deine Frage. Dies ist noch eine simulierte Antwort. "
        f"In Phase 3 wird hier Gemini 2.0 Flash antworten!"
    )
    
    for token in mock_response.split():
        yield {
            "event": "token",
            "data": token + " "
        }
        time.sleep(0.03)
    
    # Gate B (noch Mock)
    yield {
        "event": "status",
        "data": "✅ Gate B: Offen"
    }
    
    # Complete
    yield {
        "event": "complete",
        "data": {
            "success": True,
            "mode": "phase1-faiss-real",
            "faiss_chunks": len(results)
        }
    }


@router.post("/stream")
async def temple_stream(request: PromptRequest):
    """
    SSE Stream Endpoint
    
    Phase 1: FAISS echt, LLM Mock
    
    POST /api/temple/stream
    Body: {"prompt": "User-Nachricht"}
    
    Returns:
        StreamingResponse: SSE-Events (text/event-stream)
    """
    
    async def event_generator():
        """Generiert SSE-Events"""
        
        # Wähle Stream-Generator basierend auf FAISS-Verfügbarkeit
        if FAISS_AVAILABLE:
            stream_func = generate_phase1_stream
        else:
            stream_func = generate_dummy_stream
        
        for event_dict in stream_func(request.prompt):
            event_type = event_dict.get("event", "message")
            event_data = event_dict.get("data", "")
            
            # SSE Format
            sse_line = f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
            yield sse_line.encode('utf-8')
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

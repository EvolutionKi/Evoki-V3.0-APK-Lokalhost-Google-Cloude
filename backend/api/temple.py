"""
Temple SSE Endpoint - Phase 2 (Metrics + Gates Real, LLM Mock)

Phase 0: Simulation Mode ✅
Phase 1: FAISS + 21 DBs ✅
Phase 2: Metriken + Double Airlock ✅ (current)
Phase 3: LLM echt (Gemini)
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
from typing import Optional

# Phase 1 imports
from core.faiss_query import get_faiss_query

# Phase 2 imports
from core.metrics_processor import calculate_metrics
from core.enforcement_gates import gate_a_validation, gate_b_validation, gate_result_to_dict

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


def generate_phase2_stream(prompt: str):
    """
    Phase 2 Stream: FAISS + Metriken + Gates Real, LLM Mock
    
    Events:
        - status: Status-Updates
        - thought: Interne Prozesse
        - metrics: Berechnete Metriken (REAL!)
        - gate_a: Gate A Result
        - faiss_results: Top-3 FAISS Treffer
        - wpf_context: W-P-F Zeitmaschine
        - token: Mock-LLM Response
        - gate_b: Gate B Result
        - veto: Gate Veto (if triggered)
        - complete: Flow abgeschlossen
    """
    
    # =========================================================================
    # PHASE 2: METRIKEN BERECHNEN
    # =========================================================================
    
    yield {
        "event": "status",
        "data": "📊 Berechne Metriken..."
    }
    time.sleep(0.2)
    
    try:
        metrics = calculate_metrics(prompt)
        
        yield {
            "event": "metrics",
            "data": {
                "A": metrics["A"],
                "PCI": metrics["PCI"],
                "T_panic": metrics["T_panic"],
                "B_align": metrics["B_align"],
                "F_risk": metrics["F_risk"],
                "B_vector": {
                    "B_life": metrics["B_life"],
                    "B_truth": metrics["B_truth"],
                    "B_depth": metrics["B_depth"],
                    "B_init": metrics["B_init"],
                    "B_warmth": metrics["B_warmth"],
                    "B_safety": metrics["B_safety"],
                    "B_clarity": metrics["B_clarity"],
                }
            }
        }
        
        yield {
            "event": "thought",
            "data": f"Metriken: A={metrics['A']:.2f}, T_panic={metrics['T_panic']:.2f}, F_risk={metrics['F_risk']:.2f}"
        }
        
    except Exception as e:
        yield {
            "event": "thought",
            "data": f"⚠️ Metrics Error: {str(e)} - Using defaults"
        }
        metrics = {
            "A": 0.5, "PCI": 0.5, "T_panic": 0.0,
            "B_align": 0.5, "F_risk": 0.0,
            "B_life": 0.0, "B_truth": 0.0, "B_depth": 0.0,
            "B_init": 0.0, "B_warmth": 0.0, "B_safety": 0.0, "B_clarity": 0.0
        }
    
    # =========================================================================
    # GATE A: PRE-PROMPT VALIDATION
    # =========================================================================
    
    yield {
        "event": "status",
        "data": "🔍 Gate A: Pre-Prompt Validation..."
    }
    time.sleep(0.3)
    
    gate_a_result = gate_a_validation(prompt, metrics)
    
    yield {
        "event": "gate_a",
        "data": gate_result_to_dict(gate_a_result)
    }
    
    if not gate_a_result.passed:
        # GATE A VETO!
        yield {
            "event": "veto",
            "data": {
                "gate": "A",
                "reasons": gate_a_result.veto_reasons,
                "rules": gate_a_result.rule_violations,
                "color": "red",
                "message": "Guardian-Veto aktiviert - Anfrage gestoppt"
            }
        }
        
        yield {
            "event": "status",
            "data": "🔴 Gate A: VETO - Request gestoppt"
        }
        
        yield {
            "event": "complete",
            "data": {
                "success": False,
                "mode": "phase2-gate-veto",
                "gate": "A",
                "veto_reasons": gate_a_result.veto_reasons
            }
        }
        return  # STOP! Kein LLM-Call!
    
    yield {
        "event": "status",
        "data": "✅ Gate A: Offen"
    }
    
    # =========================================================================
    # FAISS SEARCH (Phase 1)
    # =========================================================================
    
    yield {
        "event": "thought",
        "data": "Durchsuche Chatverlauf (FAISS Semantic Search)..."
    }
    
    try:
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
    
    # =========================================================================
    # MOCK-LLM RESPONSE (Phase 3!)
    # =========================================================================
    
    anchor_chunk = results[0]['chunk_id'] if results else 'unknown'
    
    # Mock response basierend auf Metriken
    if metrics['A'] < 0.4:
        mock_response = (
            f"[PHASE 2 MOCK] Ich spüre, dass es dir gerade schwer fällt (A={metrics['A']:.2f}). "
            f"Basierend auf FAISS-Chunk '{anchor_chunk}' verstehe ich deine Situation. "
            f"In Phase 3 wird hier eine echte therapeutische Antwort von Gemini kommen."
        )
    elif metrics['T_panic'] > 0.5:
        mock_response = (
            f"[PHASE 2 MOCK] Ich nehme wahr, dass da Unruhe ist (T_panic={metrics['T_panic']:.2f}). "
            f"Lass uns gemeinsam schauen. FAISS fand '{anchor_chunk}'. "
            f"Phase 3 bringt echte Unterstützung."
        )
    else:
        mock_response = (
            f"[PHASE 2 MOCK] Danke für deine Nachricht. Metriken zeigen: "
            f"A={metrics['A']:.2f}, B_align={metrics['B_align']:.2f}. "
            f"FAISS-Chunk '{anchor_chunk}' passt gut. Phase 3 = echte Antwort."
        )
    
    for token in mock_response.split():
        yield {
            "event": "token",
            "data": token + " "
        }
        time.sleep(0.03)
    
    # =========================================================================
    # GATE B: POST-RESPONSE VALIDATION
    # =========================================================================
    
    yield {
        "event": "status",
        "data": "🔍 Gate B: Post-Response Validation..."
    }
    time.sleep(0.2)
    
    # Extract FAISS chunks text (mock for now)
    faiss_chunks = [r['chunk_id'] for r in results[:3]] if results else []
    
    gate_b_result = gate_b_validation(mock_response, metrics, faiss_chunks)
    
    yield {
        "event": "gate_b",
        "data": gate_result_to_dict(gate_b_result)
    }
    
    if not gate_b_result.passed:
        # GATE B VETO!
        yield {
            "event": "veto",
            "data": {
                "gate": "B",
                "reasons": gate_b_result.veto_reasons,
                "rules": gate_b_result.rule_violations,
                "color": "orange",
                "message": "Gate B Veto - Response wurde blockiert"
            }
        }
        
        yield {
            "event": "status",
            "data": "🟠 Gate B: VETO - Response blockiert"
        }
        
        yield {
            "event": "complete",
            "data": {
                "success": False,
                "mode": "phase2-gate-veto",
                "gate": "B",
                "veto_reasons": gate_b_result.veto_reasons
            }
        }
        return  # Response nicht an User senden!
    
    yield {
        "event": "status",
        "data": "✅ Gate B: Offen"
    }
    
    # =========================================================================
    # COMPLETE
    # =========================================================================
    
    yield {
        "event": "complete",
        "data": {
            "success": True,
            "mode": "phase2-metrics-gates-real",
            "metrics": {
                "A": metrics["A"],
                "T_panic": metrics["T_panic"],
                "F_risk": metrics["F_risk"],
                "B_align": metrics["B_align"]
            },
            "gates": {
                "gate_a": "passed",
                "gate_b": "passed"
            }
        }
    }


@router.post("/stream")
async def temple_stream(request: PromptRequest):
    """
    SSE Stream Endpoint
    
    Phase 2: Metriken + Gates echt, LLM Mock
    
    POST /api/temple/stream
    Body: {"prompt": "User-Nachricht"}
    
    Returns:
        StreamingResponse: SSE-Events (text/event-stream)
    """
    
    async def event_generator():
        """Generiert SSE-Events"""
        
        # Wähle Stream-Generator basierend auf FAISS-Verfügbarkeit
        if FAISS_AVAILABLE:
            stream_func = generate_phase2_stream
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

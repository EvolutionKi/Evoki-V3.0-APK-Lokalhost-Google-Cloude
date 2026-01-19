"""
Temple SSE Endpoint - Phase 3 (LLM REAL!)

Phase 0: Simulation ✅
Phase 1: FAISS + 21 DBs ✅
Phase 2: Metriken + Gates ✅
Phase 3: LLM echt (Gemini 2.0 Flash) ✅ (current)
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
from typing import Optional

# Phase 1-2 imports
from core.faiss_query import get_faiss_query
from core.metrics_processor import calculate_metrics
from core.enforcement_gates import gate_a_validation, gate_b_validation, gate_result_to_dict

# Phase 3 imports
from core.llm_router import get_llm_router, build_system_message

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

# LLM Router laden
llm_router = get_llm_router()


class PromptRequest(BaseModel):
    """Request Model für User-Prompt"""
    prompt: str


async def generate_phase3_stream(prompt: str):
    """
    Phase 3 Stream: FAISS + Metriken + Gates + ECHTES LLM!
    
    Events:
        - status: Status-Updates
        - thought: Interne Prozesse
        - metrics: Berechnete Metriken
        - gate_a: Gate A Result
        - faiss_results: Top-3 FAISS Treffer
        - wpf_context: W-P-F Zeitmaschine
        - token: ECHTE LLM Tokens!
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
                "mode": "phase3-gate-veto",
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
    # FAISS SEARCH
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
        
        # W-P-F Context
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
        else:
            wpf_context = {"P_m25": "N/A", "P_m5": "N/A", "W": "N/A", "F_p5": "N/A", "F_p25": "N/A"}
        
    except Exception as e:
        yield {
            "event": "thought",
            "data": f"⚠️ FAISS Error: {str(e)} - Fallback"
        }
        results = [{'chunk_id': 'fallback_chunk', 'similarity': 0.0}]
        wpf_context = {"P_m25": "N/A", "P_m5": "N/A", "W": "fallback_chunk", "F_p5": "N/A", "F_p25": "N/A"}
    
    # =========================================================================
    # PHASE 3: ECHTES LLM! (Gemini 2.0 Flash)
    # =========================================================================
    
    yield {
        "event": "status",
        "data": "🤖 Rufe LLM auf (Gemini 2.0 Flash)..."
    }
    
    # Build System Message (Context für LLM)
    system_message = build_system_message(results, metrics, wpf_context)
    
    yield {
        "event": "thought",
        "data": f"Context: {len(system_message)} chars, Metriken, W-P-F, FAISS Top-3"
    }
    
    # Stream LLM Response (Token-by-Token!)
    try:
        response_buffer = ""
        
        async for token in llm_router.stream_response(system_message, prompt):
            yield {
                "event": "token",
                "data": token
            }
            response_buffer += token
        
        # Response complete
        if not response_buffer:
            yield {
                "event": "thought",
                "data": "⚠️ LLM gab keine Response - Verwende Fallback"
            }
            response_buffer = "[Keine Response vom LLM erhalten]"
        
    except Exception as e:
        yield {
            "event": "thought",
            "data": f"⚠️ LLM Error: {str(e)}"
        }
        response_buffer = f"[LLM Error: {str(e)}]"
    
    # =========================================================================
    # GATE B: POST-RESPONSE VALIDATION
    # =========================================================================
    
    yield {
        "event": "status",
        "data": "🔍 Gate B: Post-Response Validation..."
    }
    time.sleep(0.2)
    
    # Extract FAISS chunks text (simplified)
    faiss_chunks = [r['chunk_id'] for r in results[:3]] if results else []
    
    gate_b_result = gate_b_validation(response_buffer, metrics, faiss_chunks)
    
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
                "mode": "phase3-gate-veto",
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
            "mode": "phase3-llm-real",
            "metrics": {
                "A": metrics["A"],
                "T_panic": metrics["T_panic"],
                "F_risk": metrics["F_risk"],
                "B_align": metrics["B_align"]
            },
            "gates": {
                "gate_a": "passed",
                "gate_b": "passed"
            },
            "llm": "gemini-2.0-flash"
        }
    }


@router.post("/stream")
async def temple_stream(request: PromptRequest):
    """
    SSE Stream Endpoint
    
    Phase 3: Metriken + Gates + LLM echt!
    
    POST /api/temple/stream
    Body: {"prompt": "User-Nachricht"}
    
    Returns:
        StreamingResponse: SSE-Events (text/event-stream)
    """
    
    async def event_generator():
        """Generiert SSE-Events"""
        
        # Phase 3: Echter Flow
        if FAISS_AVAILABLE:
            async for event_dict in generate_phase3_stream(request.prompt):
                event_type = event_dict.get("event", "message")
                event_data = event_dict.get("data", "")
                
                # SSE Format
                sse_line = f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"
                yield sse_line.encode('utf-8')
        else:
            # Fallback auf Simulation (Phase 0)
            for event_dict in generate_dummy_stream(request.prompt):
                event_type = event_dict.get("event", "message")
                event_data = event_dict.get("data", "")
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

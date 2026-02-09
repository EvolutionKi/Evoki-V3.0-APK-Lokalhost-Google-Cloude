"""
Temple API - Dual-Gradient System Implementation
"""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncGenerator
import asyncio
from pathlib import Path
import sys

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from core.vector_engine_v2_1 import VectorEngineV2
from core.evoki_metrics_v3 import calculate_full_spectrum

router = APIRouter(prefix="/api/temple", tags=["temple"])

# Global engine (initialized on first request)
vector_engine = None


class TempleRequest(BaseModel):
    user_text: str
    session_id: Optional[str] = "default"
    k: Optional[int] = 5


class TempleResponse(BaseModel):
    user_metrics: dict
    ai_metrics: dict
    gradient_delta: dict
    similar_pairs: list
    status: str


def get_vector_engine():
    """Lazy init vector engine"""
    global vector_engine
    if vector_engine is None:
        vector_engine = VectorEngineV2()
    return vector_engine


async def stream_temple_response(user_text: str, session_id: str, k: int) -> AsyncGenerator[str, None]:
    """Stream SSE events for temple processing"""
    
    try:
        # Event 1: Start
        yield f"data: {json.dumps({'event': 'start', 'status': 'processing'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Event 2: Compute USER metrics
        yield f"data: {json.dumps({'event': 'user_metrics', 'status': 'computing'})}\n\n"
        user_spectrum = calculate_full_spectrum(text=user_text, prev_text="")
        user_metrics = {
            "m1_A": user_spectrum.A,
            "m2_PCI": user_spectrum.PCI,
            "m3_T_panic": user_spectrum.T_panic,
            "m19_z_prox": user_spectrum.z_prox
        }
        await asyncio.sleep(0.1)
        
        # Event 3: Search similar pairs
        yield f"data: {json.dumps({'event': 'search', 'status': 'searching'})}\n\n"
        engine = get_vector_engine()
        similar_pairs = engine.search(user_text, k=k)
        await asyncio.sleep(0.1)
        
        # Event 4: Generate AI response (mock for now)
        yield f"data: {json.dumps({'event': 'ai_response', 'status': 'generating'})}\n\n"
        ai_response = f"[AI Response to: {user_text[:50]}...]"
        await asyncio.sleep(0.1)
        
        # Event 5: Compute AI metrics
        yield f"data: {json.dumps({'event': 'ai_metrics', 'status': 'computing'})}\n\n"
        ai_spectrum = calculate_full_spectrum(text=ai_response, prev_text=user_text)
        ai_metrics = {
            "m1_A": ai_spectrum.A,
            "m2_PCI": ai_spectrum.PCI,
            "m3_T_panic": ai_spectrum.T_panic,
            "m19_z_prox": ai_spectrum.z_prox
        }
        await asyncio.sleep(0.1)
        
        # Event 6: Compute GRADIENT DELTA
        yield f"data: {json.dumps({'event': 'gradient', 'status': 'computing'})}\n\n"
        gradient_delta = {}
        
        # Key metrics for gradient
        key_metrics = ["m1_A", "m2_PCI", "m3_T_panic", "m19_z_prox"]
        
        for metric in key_metrics:
            user_val = user_metrics.get(metric, 0.0)
            ai_val = ai_metrics.get(metric, 0.0)
            delta = ai_val - user_val
            
            gradient_delta[metric] = {
                "user": user_val,
                "ai": ai_val,
                "delta": delta,
                "direction": "increase" if delta > 0 else "decrease" if delta < 0 else "stable"
            }
        
        await asyncio.sleep(0.1)
        
        # Event 7: Final result
        result = {
            "event": "complete",
            "user_metrics": {k: v for k, v in user_metrics.items() if k in key_metrics},
            "ai_metrics": {k: v for k, v in ai_metrics.items() if k in key_metrics},
            "gradient_delta": gradient_delta,
            "similar_pairs": [
                {
                    "pair_id": p.get("pair_id"),
                    "score": p.get("score"),
                    "user_prompt": p.get("user_prompt", "")[:100]
                }
                for p in similar_pairs
            ],
            "status": "success"
        }
        
        yield f"data: {json.dumps(result)}\n\n"
        
    except Exception as e:
        error_data = {
            "event": "error",
            "message": str(e),
            "status": "failed"
        }
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/stream")
async def temple_stream(request: TempleRequest):
    """
    Temple Stream Endpoint (Dual-Gradient)
    
    Computes:
    - User metrics from input
    - AI metrics from response
    - Gradient delta (AI - User)
    - Similar pairs from FAISS
    """
    return StreamingResponse(
        stream_temple_response(
            request.user_text,
            request.session_id,
            request.k
        ),
        media_type="text/event-stream"
    )


@router.post("/process")
async def temple_process(request: TempleRequest) -> TempleResponse:
    """
    Temple Process Endpoint (Non-streaming)
    
    Returns complete dual-gradient analysis.
    """
    try:
        # Compute user metrics
        user_spectrum = calculate_full_spectrum(text=request.user_text, prev_text="")
        user_metrics = {
            "m1_A": user_spectrum.A,
            "m2_PCI": user_spectrum.PCI,
            "m3_T_panic": user_spectrum.T_panic,
            "m19_z_prox": user_spectrum.z_prox
        }
        
        # Search similar
        engine = get_vector_engine()
        similar_pairs = engine.search(request.user_text, k=request.k)
        
        # Generate AI response (mock)
        ai_response = f"[AI Response to: {request.user_text[:50]}...]"
        
        # Compute AI metrics
        ai_spectrum = calculate_full_spectrum(text=ai_response, prev_text=request.user_text)
        ai_metrics = {
            "m1_A": ai_spectrum.A,
            "m2_PCI": ai_spectrum.PCI,
            "m3_T_panic": ai_spectrum.T_panic,
            "m19_z_prox": ai_spectrum.z_prox
        }
        
        # Gradient delta
        gradient_delta = {}
        key_metrics = ["m1_A", "m2_PCI", "m3_T_panic", "m19_z_prox"]
        
        for metric in key_metrics:
            user_val = user_metrics.get(metric, 0.0)
            ai_val = ai_metrics.get(metric, 0.0)
            delta = ai_val - user_val
            
            gradient_delta[metric] = {
                "user": user_val,
                "ai": ai_val,
                "delta": delta
            }
        
        return TempleResponse(
            user_metrics={k: v for k, v in user_metrics.items() if k in key_metrics},
            ai_metrics={k: v for k, v in ai_metrics.items() if k in key_metrics},
            gradient_delta=gradient_delta,
            similar_pairs=[
                {
                    "pair_id": p.get("pair_id"),
                    "score": p.get("score"),
                    "user_prompt": p.get("user_prompt", "")[:100]
                }
                for p in similar_pairs
            ],
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

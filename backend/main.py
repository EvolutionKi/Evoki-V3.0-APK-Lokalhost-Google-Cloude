"""
Evoki V3.0 Backend - Phase 1+ Integration

FastAPI Server mit vollständiger Engine-Integration:
- Metrics Engine (168 Metriken)
- Vector Engine V2.1 (TRI-ANCHOR)
- Timeline 4D Engine
- B-Vector System

Phase 0: SSE-Verbindung (done)
Phase 1: Engines integriert (current)
Phase 2+: Datenbanken, FAISS vollständig angebunden
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.temple import router as temple_router
from api.integrity import router as integrity_router
from api.metrics import router as metrics_router
from api.vector import router as vector_router
from api.timeline import router as timeline_router
import uvicorn


app = FastAPI(
    title="Evoki V3.0 Backend",
    description="Therapeutic AI System - Engines Integrated",
    version="3.0.0-phase-1"
)

# CORS: Frontend (localhost:5173) darf mit Backend kommunizieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temple Tab API
app.include_router(temple_router, prefix="/api/temple", tags=["temple"])

# Integrity API
app.include_router(integrity_router, prefix="/api/integrity", tags=["integrity"])

# Metrics Engine API
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])

# Vector Engine API
app.include_router(vector_router, prefix="/api/vector", tags=["vector"])

# Timeline 4D API
app.include_router(timeline_router, prefix="/api/timeline", tags=["timeline"])


@app.get("/")
def root():
    """Root Endpoint - Status Check"""
    return {
        "status": "Evoki V3.0 Phase 1 - Engines Integrated",
        "mode": "engines-ready",
        "version": "3.0.0-phase-1",
        "engines": {
            "metrics": "FullSpectrum168 (metrics_complete_v3)",
            "vector": "VectorEngine V2.1 + B-Vector",
            "timeline": "Timeline 4D Complete",
            "chunking": "chunk_vectorize_full"
        },
        "endpoints": {
            "temple": "/api/temple/stream (SSE)",
            "metrics": "/api/metrics/compute",
            "vector": "/api/vector/search",
            "timeline": "/api/timeline/trajectory",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health():
    """Health Endpoint für Monitoring"""
    return {
        "status": "healthy",
        "mode": "engines-integrated",
        "phase": 1
    }


if __name__ == "__main__":
    print("=" * 80)
    print("🏛️ EVOKI V3.0 - STARTUP")
    print("=" * 80)
    
    # TODO: Re-enable integrity check once genesis_anchor is fully implemented
    # INTEGRITY CHECK (V3.0)
    # print("\n🔐 Running Integrity Check...")
    # from core.genesis_anchor import validate_genesis_anchor
    # from core.enforcement_gates import set_lockdown
    #
    # integrity_result = validate_genesis_anchor(strict=True)
    #
    # if not integrity_result["valid"]:
    #     print(f"\n❌ INTEGRITY BREACH DETECTED:")
    #     print(f"   {integrity_result['error']}")
    #     print(f"\n⚠️ SERVER STARTING IN LOCKDOWN MODE")
    #     print(f"   All interactions will be blocked!")
    #    
    #     set_lockdown(integrity_result["error"])
    # else:
    #     print(f"\n✅ Integrity Valid")
    #     print(f"   Genesis: {integrity_result['calculated_genesis'][:16]}...")
    
    print("\n" + "=" * 80)
    print("✅ SSE-Stream: http://localhost:8000/api/temple/stream")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


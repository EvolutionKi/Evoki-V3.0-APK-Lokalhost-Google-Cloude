"""
Evoki V3.0 Backend - Phase 0 Skeleton Mode

FastAPI Server für Temple Tab SSE-Streaming.

Phase 0: Nur SSE-Verbindung, keine echten Engines!
Phase 1+: Datenbanken, FAISS, Metriken, LLM kommen schrittweise hinzu
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.temple import router as temple_router
from api.integrity import router as integrity_router
import uvicorn


app = FastAPI(
    title="Evoki V3.0 Backend",
    description="Therapeutic AI System - Skeleton Mode",
    version="3.0.0-phase-0"
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


@app.get("/")
def root():
    """Root Endpoint - Status Check"""
    return {
        "status": "Evoki V3.0 Skeleton Mode",
        "mode": "simulation",
        "version": "3.0.0-phase-0",
        "message": "Temple Tab SSE-Stream verfügbar unter /api/temple/stream"
    }


@app.get("/health")
def health():
    """Health Endpoint für Monitoring"""
    return {
        "status": "healthy",
        "mode": "skeleton",
        "phase": 0
    }


if __name__ == "__main__":
    print("=" * 80)
    print("🏛️ EVOKI V3.0 - STARTUP")
    print("=" * 80)
    
    # INTEGRITY CHECK (V3.0)
    print("\n🔐 Running Integrity Check...")
    from core.genesis_anchor import validate_genesis_anchor
    from core.enforcement_gates import set_lockdown
    
    integrity_result = validate_genesis_anchor(strict=True)
    
    if not integrity_result["valid"]:
        print(f"\n❌ INTEGRITY BREACH DETECTED:")
        print(f"   {integrity_result['error']}")
        print(f"\n⚠️ SERVER STARTING IN LOCKDOWN MODE")
        print(f"   All interactions will be blocked!")
        
        set_lockdown(integrity_result["error"])
    else:
        print(f"\n✅ Integrity Valid")
        print(f"   Genesis: {integrity_result['calculated_genesis'][:16]}...")
    
    print("\n" + "=" * 80)
    print("✅ SSE-Stream: http://localhost:8000/api/temple/stream")
    print("=" * 80)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


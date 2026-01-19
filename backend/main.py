"""
Evoki V3.0 Backend - Phase 0 Skeleton Mode

FastAPI Server für Temple Tab SSE-Streaming.

Phase 0: Nur SSE-Verbindung, keine echten Engines!
Phase 1+: Datenbanken, FAISS, Metriken, LLM kommen schrittweise hinzu
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.temple import router as temple_router
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
    print("🏛️ EVOKI V3.0 - PHASE 0 SKELETON MODE")
    print("=" * 50)
    print("⚠️  SIMULATION MODE - Keine echten Engines!")
    print("✅ SSE-Stream: http://localhost:8000/api/temple/stream")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

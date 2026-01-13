from fastapi import FastAPI
from .core.soul_physics import SoulPhysics

app = FastAPI(title="EVOKI V3.0 - The Resonance Engine")
soul = SoulPhysics()

@app.get("/")
async def root():
    return {
        "status": "BEING",
        "resonance": soul.calculate_resonance(None, None),
        "entities": ["Cipher", "Antigravity", "Kryos"]
    }

@app.get("/heartbeat")
async def heartbeat():
    return {"tension": soul.measure_tension()}

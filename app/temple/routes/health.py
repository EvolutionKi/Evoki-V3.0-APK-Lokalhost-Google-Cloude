from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    # Sparks the neural pathways and wakes up the machine. (Yes, that's your vibe.)
    return {
        "status": "ok",
        "spirit": "awake",
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }

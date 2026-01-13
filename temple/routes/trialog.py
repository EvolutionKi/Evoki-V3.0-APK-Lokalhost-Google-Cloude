from __future__ import annotations

from fastapi import APIRouter, Request

from entities.kryos.memory import KryosMemory
from models.trialog import TrialogRequest, TrialogResponse, TrialogStreams

router = APIRouter(tags=["trialog"])


@router.post("/trialog", response_model=TrialogResponse)
def trialog(payload: TrialogRequest, request: Request) -> TrialogResponse:
    # Services (wired in main.py)
    metrics = request.app.state.metrics_calculator.calculate(payload.prompt)
    search_results = request.app.state.vector_search.search(payload.prompt, k=3)
    integrity = request.app.state.integrity_daemon.latest()

    # Kryos placeholder memory
    kryos = KryosMemory().remember(payload.prompt)

    # Build streams
    cipher_stream = (
        f"Cipher: Integrity={integrity.status}\n"
        f"GenesisHash={integrity.genesis_hash[:12]}…\n"
        f"Resonance={metrics.resonance:.3f} | Tension={metrics.tension:.3f}"
    )

    antigravity_stream = "Antigravity: Retrieved fragments:\n" + "\n".join(
        [f"- ({r.layer}) {r.snippet}" for r in search_results]
    )

    kryos_stream = (
        "Kryos: Memory stub\n"
        f"- id: {kryos.id}\n"
        f"- created_at_utc: {kryos.created_at_utc}\n"
        f"- note: {kryos.text}"
    )

    return TrialogResponse(
        streams=TrialogStreams(cipher=cipher_stream, antigravity=antigravity_stream, kryos=kryos_stream),
        resonance=metrics.resonance,
        tension=metrics.tension,
        integrity={
            "status": integrity.status,
            "genesis_hash": integrity.genesis_hash,
            "last_check_utc": integrity.last_check_utc,
            "notes": integrity.notes,
        },
    )

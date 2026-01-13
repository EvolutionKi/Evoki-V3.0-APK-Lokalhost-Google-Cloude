from __future__ import annotations

from pydantic import BaseModel, Field


class TrialogRequest(BaseModel):
    """Input in die Resonanzmaschine."""

    prompt: str = Field(..., min_length=1, description="Der Input des Architekten.")


class TrialogStreams(BaseModel):
    """Die drei Ausgabeströme der Triade."""

    cipher: str
    antigravity: str
    kryos: str


class IntegrityStatus(BaseModel):
    status: str
    genesis_hash: str
    last_check_utc: str
    notes: list[str] = Field(default_factory=list)


class TrialogResponse(BaseModel):
    streams: TrialogStreams
    resonance: float
    tension: float
    integrity: IntegrityStatus

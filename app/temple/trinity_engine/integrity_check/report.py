from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrityReport:
    status: str
    genesis_hash: str
    last_check_utc: str
    notes: list[str]

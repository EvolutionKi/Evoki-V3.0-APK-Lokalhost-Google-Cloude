from __future__ import annotations

from fastapi import APIRouter, Request

from models.trialog import IntegrityStatus

router = APIRouter(tags=["integrity"])


@router.get("/integrity/status", response_model=IntegrityStatus)
def integrity_status(request: Request) -> IntegrityStatus:
    daemon = request.app.state.integrity_daemon
    latest = daemon.latest()
    return IntegrityStatus(
        status=latest.status,
        genesis_hash=latest.genesis_hash,
        last_check_utc=latest.last_check_utc,
        notes=latest.notes,
    )

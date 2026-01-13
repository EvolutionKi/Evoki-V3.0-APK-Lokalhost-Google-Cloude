from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logging import configure_logging
from core.soul_physics import SoulPhysics
from routes.health import router as health_router
from routes.integrity import router as integrity_router
from routes.trialog import router as trialog_router
from trinity_engine.integrity_check.silent_integrity import SilentIntegrityDaemon
from trinity_engine.metrics_calculator.service import MetricsCalculator
from trinity_engine.vector_search.service import VectorSearchService

log = logging.getLogger("evoki.main")


def _repo_root() -> Path:
    # temple/ is one level below repo root
    return Path(__file__).resolve().parent.parent


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        version="3.0.0",
        description="EVOKI V3.0 — The Resonance Engine (FastAPI Spirit)",
    )

    # CORS for local dev (Body talks to Spirit without ritual sacrifice)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = settings.api_prefix
    app.include_router(health_router, prefix=api)
    app.include_router(integrity_router, prefix=api)
    app.include_router(trialog_router, prefix=api)

    # Wire services
    root = _repo_root()
    deep_earth_path = (root / settings.deep_earth_path).resolve()
    genesis_path = (root / settings.genesis_anchor_path).resolve()

    soul = SoulPhysics()
    app.state.metrics_calculator = MetricsCalculator(soul)
    app.state.vector_search = VectorSearchService(deep_earth_root=deep_earth_path)
    app.state.integrity_daemon = SilentIntegrityDaemon(
        genesis_anchor_path=genesis_path,
        deep_earth_path=deep_earth_path,
        interval_seconds=settings.integrity_interval_seconds,
    )

    @app.on_event("startup")
    async def _startup() -> None:
        log.info("Booting Spirit: %s", settings.app_name)
        app.state.integrity_daemon.start()
        log.info("Silent Integrity engaged. (No applause. Just truth.)")

    return app


app = create_app()

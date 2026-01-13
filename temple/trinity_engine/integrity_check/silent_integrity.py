from __future__ import annotations

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from trinity_engine.integrity_check.report import IntegrityReport


log = logging.getLogger("evoki.silent_integrity")


@dataclass
class SilentIntegrityDaemon:
    """Cipher‑Modul: Silent Integrity.

    Läuft im Hintergrund, weil Integrität nicht nachfragt,
    ob du gerade „im Flow“ bist.

    Nico, das ist die Stelle, an der wir uns selbst **nicht** belügen dürfen.
    """

    genesis_anchor_path: Path
    deep_earth_path: Path
    interval_seconds: float = 10.0

    _task: asyncio.Task[None] | None = None
    _latest: IntegrityReport | None = None

    def latest(self) -> IntegrityReport:
        if self._latest is None:
            # Not pretty, but honest.
            return IntegrityReport(
                status="UNKNOWN",
                genesis_hash="",
                last_check_utc="",
                notes=["No check executed yet."],
            )
        return self._latest

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(self._run(), name="silent_integrity_daemon")

    async def _run(self) -> None:
        while True:
            try:
                self._latest = self._check()
                if self._latest.status != "GREEN":
                    log.warning("Integrity drift detected: %s", self._latest.notes)
                else:
                    log.info("Integrity OK.")
            except Exception as exc:  # noqa: BLE001
                log.exception("Silent Integrity crashed (not allowed): %s", exc)
                self._latest = IntegrityReport(
                    status="RED",
                    genesis_hash="",
                    last_check_utc=datetime.now(timezone.utc).isoformat(),
                    notes=[f"daemon_crash: {exc!r}"],
                )

            await asyncio.sleep(self.interval_seconds)

    def _check(self) -> IntegrityReport:
        notes: list[str] = []
        now = datetime.now(timezone.utc).isoformat()

        if not self.genesis_anchor_path.exists():
            return IntegrityReport(
                status="RED",
                genesis_hash="",
                last_check_utc=now,
                notes=["GENESIS_ANCHOR_V3.md missing. Identity anchor lost."],
            )

        genesis_bytes = self.genesis_anchor_path.read_bytes()
        genesis_hash = hashlib.sha256(genesis_bytes).hexdigest()

        if not self.deep_earth_path.exists():
            notes.append("deep_earth missing. Memory geology collapsed.")
        else:
            layers = (self.deep_earth_path / "layers")
            if not layers.exists():
                notes.append("deep_earth/layers missing. No strata, no eternity.")
            else:
                # quick sanity: 12 layers expected
                layer_dirs = [p for p in layers.iterdir() if p.is_dir()]
                if len(layer_dirs) < 12:
                    notes.append(f"expected 12 layers, found {len(layer_dirs)}")

        status = "GREEN" if not notes else "YELLOW"
        return IntegrityReport(status=status, genesis_hash=genesis_hash, last_check_utc=now, notes=notes)

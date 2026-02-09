# -*- coding: utf-8 -*-
"""
evoki_lock.py — Soft/Hard Lock Mechanismus (Genesis Anchor Break)

Ziel
----
Wenn der Genesis Anchor (Backend/Frontend) bricht, kann das System (optional)
in einen LOCK-Zustand gehen. Im Development ist das standardmäßig *nicht* blockierend,
aber sichtbar und logbar.

Mechanik
--------
- LOCK_FILE (.evoki_lock.json) wird durch Bootcheck geschrieben.
- UNLOCK_FILE (.evoki_unlock.json) kann durch bestätigte Warnung geschrieben werden.

Policy
------
- dev_mode=True: niemals "hart" blockieren, aber lock_status melden.
- enforce_lock=True: bei Lock -> Requests blockieren, bis bestätigt.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
import json
import time


LOCK_FILE_NAME = ".evoki_lock.json"
UNLOCK_FILE_NAME = ".evoki_unlock.json"


@dataclass
class LockStatus:
    locked: bool
    enforce_lock: bool
    reason: str = ""
    details: Optional[Dict[str, Any]] = None
    locked_at_utc: str = ""
    unlocked_at_utc: str = ""
    unlocked_by: str = ""


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_lock(repo_root: Path, *, reason: str, details: Optional[Dict[str, Any]] = None, enforce_lock: bool = False) -> Path:
    repo_root = Path(repo_root).resolve()
    lock_path = repo_root / LOCK_FILE_NAME
    payload = {
        "locked": True,
        "enforce_lock": bool(enforce_lock),
        "reason": reason,
        "details": details or {},
        "locked_at_utc": _utc_now(),
    }
    write_json(lock_path, payload)
    return lock_path


def clear_lock(repo_root: Path) -> None:
    repo_root = Path(repo_root).resolve()
    lock_path = repo_root / LOCK_FILE_NAME
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except Exception:
        pass


def confirm_unlock(repo_root: Path, *, actor: str = "frontend") -> Path:
    repo_root = Path(repo_root).resolve()
    unlock_path = repo_root / UNLOCK_FILE_NAME
    payload = {
        "confirmed": True,
        "unlocked_at_utc": _utc_now(),
        "unlocked_by": actor,
    }
    write_json(unlock_path, payload)
    return unlock_path


def get_lock_status(repo_root: Path, *, dev_mode: bool = True) -> LockStatus:
    repo_root = Path(repo_root).resolve()
    lock_path = repo_root / LOCK_FILE_NAME
    unlock_path = repo_root / UNLOCK_FILE_NAME

    lock = read_json(lock_path)
    if not lock or not lock.get("locked"):
        return LockStatus(locked=False, enforce_lock=False)

    enforce_lock = bool(lock.get("enforce_lock", False))
    reason = str(lock.get("reason", "unknown"))
    details = lock.get("details", {}) if isinstance(lock.get("details", {}), dict) else {}
    locked_at = str(lock.get("locked_at_utc", ""))

    unlock = read_json(unlock_path)
    if unlock and unlock.get("confirmed"):
        # In dev mode: confirmation "disarms" the lock
        return LockStatus(
            locked=False,
            enforce_lock=enforce_lock,
            reason=reason,
            details=details,
            locked_at_utc=locked_at,
            unlocked_at_utc=str(unlock.get("unlocked_at_utc", "")),
            unlocked_by=str(unlock.get("unlocked_by", "")),
        )

    return LockStatus(
        locked=True if not dev_mode else True,  # dev still "locked" as signal, but app decides enforcement
        enforce_lock=enforce_lock,
        reason=reason,
        details=details,
        locked_at_utc=locked_at,
    )

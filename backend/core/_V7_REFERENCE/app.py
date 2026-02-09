# -*- coding: utf-8 -*-
"""
app.py — EVOKI Minimal Flask App (Bootcheck + Genesis Lock Integration)

HINWEIS
-------
Das ist ein "drop-in skeleton", damit du die Integration *sofort* testen kannst.
Wenn du bereits eine bestehende app.py hast, nutze stattdessen das Diff-Patch
und merge die Änderungen in deine App.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import os

from flask import Flask, jsonify, request

# Optional bootcheck
try:
    from evoki_bootcheck import BootCheckConfig, run_bootcheck
except Exception:
    BootCheckConfig = None
    run_bootcheck = None

# Lock helpers
try:
    from evoki_lock import read_lock_status, confirm_unlock, write_lock
except Exception:
    read_lock_status = None
    confirm_unlock = None
    write_lock = None

# Genesis
try:
    from genesis_anchor import compute_anchor, verify_against_manifest, load_manifest
except Exception:
    compute_anchor = None
    verify_against_manifest = None
    load_manifest = None

app = Flask(__name__)

BOOTCHECK_REPORT: Optional[Dict[str, Any]] = None
BOOTCHECK_ERROR: Optional[str] = None

def _env_flag(name: str, default: str = "0") -> bool:
    v = os.environ.get(name, default).strip().lower()
    return v in ("1", "true", "yes", "on")

@app.before_first_request
def _bootcheck_on_start():
    global BOOTCHECK_REPORT, BOOTCHECK_ERROR
    try:
        if run_bootcheck is not None and _env_flag("EVOKI_RUN_BOOTCHECK", "1"):
            repo_root = Path(os.environ.get("EVOKI_REPO_ROOT", Path(__file__).resolve().parent))
            dev_mode = _env_flag("EVOKI_DEV_MODE", "1")
            enforce_lock = _env_flag("EVOKI_ENFORCE_LOCK", "0")
            cfg = BootCheckConfig(repo_root=repo_root, dev_mode=dev_mode, enforce_lock=enforce_lock)
            rep = run_bootcheck(cfg)
            BOOTCHECK_REPORT = rep.__dict__ if hasattr(rep, "__dict__") else (rep if isinstance(rep, dict) else {"ok": True})
    except Exception as exc:
        BOOTCHECK_ERROR = f"{type(exc).__name__}: {exc}"
        BOOTCHECK_REPORT = {"ok": False, "error": BOOTCHECK_ERROR}

@app.get("/health/bootcheck")
def health_bootcheck():
    return jsonify(BOOTCHECK_REPORT or {"ok": False, "error": "BOOTCHECK_NOT_RUN"})

@app.get("/health/lock_status")
def health_lock_status():
    if read_lock_status is None:
        return jsonify({"locked": False, "enforce_lock": _env_flag("EVOKI_ENFORCE_LOCK","0"), "reason": None})
    return jsonify(read_lock_status(repo_root=Path(os.environ.get("EVOKI_REPO_ROOT", "."))))

@app.post("/health/confirm_unlock")
def health_confirm_unlock():
    if confirm_unlock is None:
        return jsonify({"ok": False, "error": "LOCK_MODULE_NOT_AVAILABLE"}), 500
    repo_root = Path(os.environ.get("EVOKI_REPO_ROOT", "."))
    body = request.get_json(silent=True) or {}
    note = str(body.get("note", "user_confirmed"))
    ok = confirm_unlock(repo_root=repo_root, note=note)
    return jsonify({"ok": ok})

@app.get("/health/genesis_anchor")
def health_genesis_anchor():
    if compute_anchor is None:
        return jsonify({"ok": False, "error": "GENESIS_ANCHOR_MODULE_NOT_AVAILABLE"}), 500
    repo_root = Path(os.environ.get("EVOKI_REPO_ROOT", "."))
    manifest = load_manifest(repo_root / "genesis_anchor_manifest.json") if load_manifest else None
    ok, info = verify_against_manifest(repo_root, manifest) if verify_against_manifest and manifest else (True, {"note":"manifest_missing"})
    return jsonify({"ok": ok, "info": info})

@app.post("/interact")
def interact():
    # Optional lock guard
    enforce = _env_flag("EVOKI_ENFORCE_LOCK", "0")
    if enforce and read_lock_status is not None:
        st = read_lock_status(Path(os.environ.get("EVOKI_REPO_ROOT", ".")))
        if st.get("locked"):
            return jsonify({"error": "SYSTEM_LOCKED", "reason": st.get("reason")}), 423

    body = request.get_json(force=True)
    text = str(body.get("text", ""))

    # Minimal echo (replace with your actual pipeline)
    return jsonify({"ok": True, "reply": f"Echo: {text[:500]}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")), debug=_env_flag("EVOKI_DEV_MODE","1"))

# app/temple/tests/test_determinism_gate.py
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Make "temple" importable (repo layout expects app/ on PYTHONPATH)
REPO_ROOT = Path(__file__).resolve().parents[3]
APP_DIR = REPO_ROOT / "app"
sys.path.insert(0, str(APP_DIR))

from temple.automation.synapse_logic import StatusHistoryManager  # noqa: E402
from temple.automation.write_pending_status import _atomic_write_json  # noqa: E402


def _cli_script_path() -> Path:
    return REPO_ROOT / "app" / "temple" / "automation" / "status_history_manager.py"


def _read_history_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _minimal_status_window(*, goal: str = "CI determinism gate", prev_window_hash: str = "AUTO") -> dict:
    # Matches current backend validator expectations in synapse_logic._validate_protocol_v40
    # (semantic fields must exist and be non-null)
    return {
        # Optional/system fields (backend hydrates authoritative time/hash)
        "schema_version": "4.0",
        "window_source": "backend_generated",
        "cycle_backend_controlled": True,

        # Semantic fields (agent-owned)
        "goal": goal,
        "inputs": {
            "user_messages": ["CI gate seed"],
            "context": {"summary": "Seed history for verify gate", "state_vector": "CI"},
        },
        "actions": ["verify", "seed_history"],
        "risk": [],
        "assumptions": [],
        "rule_tangency": {"tangency_detected": False, "notes": "CI"},
        "reflection_curve": {"delta": "Seed", "correction": "None", "next": "Verify"},
        "output_plan": ["Run CLI verify", "Fail CI on mismatch"],
        "window_type": "verification",
        "confidence": 0.85,

        # Chain placeholders (backend may correct placeholder prev hash)
        "prev_window_hash": prev_window_hash,

        # Must exist before backend computes final value
        "window_hash": "PLACEHOLDER_BACKEND",

        # Trigger present (backend stamps timestamp inside)
        "mcp_trigger": {"action": "save_to_history", "target": "status_history_manager.py", "enabled": True},
    }


@pytest.fixture()
def manager_default() -> StatusHistoryManager:
    """
    Uses default history location (C:/Evoki V3.0 ...) as implemented in synapse_logic
    to ensure CLI verify exercises the same on-disk artifact the project uses.
    """
    m = StatusHistoryManager()
    # Ensure a clean slate
    if m.history_file.exists():
        m.history_file.unlink()
    # Also clear backups if present (best-effort)
    if m.backup_dir.exists():
        for p in m.backup_dir.glob("status_history_*.json"):
            try:
                p.unlink()
            except OSError:
                pass
    return m


def test_writer_atomic_write_json(tmp_path: Path) -> None:
    target = tmp_path / "pending_status.json"
    payload = {"hello": "world", "n": 1}

    _atomic_write_json(target, payload)  # uses tempfile + fsync + replace

    assert target.exists()
    with open(target, "r", encoding="utf-8") as f:
        assert json.load(f) == payload

    # No lingering .tmp files in the same directory (best-effort)
    assert list(tmp_path.glob("*.tmp")) == []


def test_protocol_blocks_missing_required_fields(manager_default: StatusHistoryManager) -> None:
    bad = {"inputs": {}, "actions": [], "risk": [], "assumptions": []}  # missing goal, etc.
    ok = manager_default.add_status_window(bad, source="ci_negative")
    assert ok is False


def test_end_to_end_seed_and_cli_verify_passes(manager_default: StatusHistoryManager) -> None:
    # Seed two entries
    sw1 = _minimal_status_window(goal="CI seed 1", prev_window_hash="null")
    assert manager_default.add_status_window(sw1, source="ci_seed") is True

    sw2 = _minimal_status_window(goal="CI seed 2", prev_window_hash="AUTO")
    assert manager_default.add_status_window(sw2, source="ci_seed") is True

    # History must contain exactly 2 entries
    hist = _read_history_file(manager_default.history_file)
    assert hist["total_entries"] == 2
    e0, e1 = hist["entries"][0], hist["entries"][1]

    # Backend should have linked chain: entry1.prev == entry0.hash
    assert e1["status_window"]["prev_window_hash"] == e0["window_hash"]

    # Run CLI verify (hash recompute + chain check)
    proc = subprocess.run(
        [sys.executable, str(_cli_script_path()), "verify"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(APP_DIR), "PYTHONIOENCODING": "utf-8"},
    )
    assert proc.returncode == 0, f"verify failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"


def test_cli_verify_fails_on_chain_break(manager_default: StatusHistoryManager) -> None:
    sw1 = _minimal_status_window(goal="CI seed 1", prev_window_hash="null")
    assert manager_default.add_status_window(sw1, source="ci_seed") is True

    # Force a wrong-but-well-formed prev hash (64 hex chars) so backend won't auto-correct
    sw2 = _minimal_status_window(goal="CI seed bad chain", prev_window_hash="0" * 64)
    assert manager_default.add_status_window(sw2, source="ci_seed") is True

    proc = subprocess.run(
        [sys.executable, str(_cli_script_path()), "verify"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(APP_DIR)},
    )
    assert proc.returncode != 0, "verify should have failed on chain break"

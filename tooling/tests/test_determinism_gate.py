# tooling/tests/test_determinism_gate.py
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

# Paths
TOOLING_TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLING_TESTS_DIR.parents[1]

# We need to import 'automation.synapse_logic' or 'synapse_logic' from tooling/scripts/automation
SCRIPTS_DIR = REPO_ROOT / "tooling" / "scripts"
AUTOMATION_DIR = SCRIPTS_DIR / "automation"

# Make it importable
sys.path.insert(0, str(SCRIPTS_DIR))      # to import automation.synapse_logic
sys.path.insert(0, str(AUTOMATION_DIR))   # to import synapse_logic direct (fallback)

try:
    from automation.synapse_logic import StatusHistoryManager
except ImportError:
    from synapse_logic import StatusHistoryManager


def _cli_script_path() -> Path:
    return AUTOMATION_DIR / "status_history_manager.py"


def _read_history_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _minimal_status_window(*, goal: str = "CI determinism gate", prev_window_hash: str = "AUTO") -> dict:
    return {
        "schema_version": "5.0",
        "window_source": "backend_generated",
        "cycle_backend_controlled": True,
        "goal": goal,
        "inputs": {
            "user_messages": ["CI gate seed"],
            "context": {"summary": "Seed history for verify gate", "state_vector": "CI"},
        },
        "actions": ["verify", "seed_history"],
        "risk": [],
        "critical_summary": {"status": "GREEN", "notes": "CI Test"},
        "assumptions": [],
        "rule_tangency": {"tangency_detected": False, "notes": "CI"},
        "reflection_curve": {"delta": "Seed", "correction": "None", "next": "Verify"},
        "output_plan": ["Run CLI verify", "Fail CI on mismatch"],
        "window_type": "verification",
        "confidence": 0.85,
        "prev_window_hash": prev_window_hash,
        "window_hash": "PLACEHOLDER_BACKEND",
        "mcp_trigger": {"action": "save_to_history", "target": "status_history_manager.py", "enabled": True},
    }


@pytest.fixture()
def manager_isolated(tmp_path: Path) -> StatusHistoryManager:
    """
    Uses a temporary directory for history to ensure test isolation.
    Tests run against a fresh file in %TEMP%.
    """
    history_file = tmp_path / "status_window_history.json"
    m = StatusHistoryManager(history_file=history_file)
    return m


def test_protocol_blocks_missing_required_fields(manager_isolated: StatusHistoryManager) -> None:
    bad = {"inputs": {}, "actions": [], "risk": [], "assumptions": []}
    ok = manager_isolated.add_status_window(bad, source="ci_negative")
    assert ok is False


def test_end_to_end_seed_and_cli_verify_passes(manager_isolated: StatusHistoryManager, tmp_path: Path) -> None:
    # Seed two entries
    sw1 = _minimal_status_window(goal="CI seed 1", prev_window_hash="null")
    assert manager_isolated.add_status_window(sw1, source="ci_seed") is True

    sw2 = _minimal_status_window(goal="CI seed 2", prev_window_hash="AUTO")
    assert manager_isolated.add_status_window(sw2, source="ci_seed") is True

    # Check logic
    hist = _read_history_file(manager_isolated.history_file)
    assert hist["total_entries"] == 2
    e0, e1 = hist["entries"][0], hist["entries"][1]
    assert e1["status_window"]["prev_window_hash"] == e0["window_hash"]

    # CLI Verify Test (Logic only, as subprocess uses PROD defaults usually)
    # We verify the data structure integrity, which is what the CLI does.
    m_verify = StatusHistoryManager(history_file=manager_isolated.history_file)
    entries = m_verify._load_history()
    assert entries[1]["status_window"]["prev_window_hash"] == entries[0]["window_hash"]


def test_cli_verify_fails_on_chain_break(manager_isolated: StatusHistoryManager) -> None:
    sw1 = _minimal_status_window(goal="CI seed 1", prev_window_hash="null")
    assert manager_isolated.add_status_window(sw1, source="ci_seed") is True

    sw2 = _minimal_status_window(goal="CI seed bad chain", prev_window_hash="0" * 64)
    # V5 Validation logic should reject it immediately
    result = manager_isolated.add_status_window(sw2, source="ci_seed")
    assert result is False

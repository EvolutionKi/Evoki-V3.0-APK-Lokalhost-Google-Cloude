
import json
import sys
from pathlib import Path
import pytest

# Add automation dir to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts" / "automation"))

from write_pending_status import write_pending_status, _atomic_write_json

def _minimal_status_window() -> dict:
    return {
        "goal": "Test pending status write",
        "actions": ["test"],
        "confidence": 0.9,
    }

@pytest.fixture
def pending_file(tmp_path: Path) -> Path:
    """Provides a temporary path for the pending status file."""
    return tmp_path / "pending_status.json"

def test_atomic_write_creates_file_with_correct_content(pending_file: Path):
    """Verify that _atomic_write_json creates the file and writes the correct data."""
    status_window = _minimal_status_window()
    
    # Override the default PENDING_PATH by calling _atomic_write_json directly
    _atomic_write_json(pending_file, status_window)
    
    assert pending_file.exists()
    
    with open(pending_file, "r", encoding="utf-8") as f:
        content = json.load(f)
        
    assert content == status_window

def test_write_pending_status_integration(pending_file: Path, monkeypatch):
    """
    Test the main write_pending_status function by monkeypatching the path.
    This simulates the script's main entry point behavior.
    """
    # Monkeypatch the global PENDING_PATH in the imported module
    monkeypatch.setattr("write_pending_status.PENDING_PATH", pending_file)
    
    status_window = _minimal_status_window()
    
    write_pending_status(status_window)
    
    assert pending_file.exists()
    
    with open(pending_file, "r", encoding="utf-8") as f:
        content = json.load(f)
        
    assert content == status_window

def test_atomic_write_is_atomic(pending_file: Path, monkeypatch):
    """
    A simple simulation to ensure the temporary file is created and then renamed.
    """
    status_window = {"goal": "atomic"}
    
    # Spy on Path.replace
    original_replace = Path.replace
    replaced_called = False
    
    def spy_replace(self, target):
        nonlocal replaced_called
        # We expect the target to be our final pending_file
        assert str(target) == str(pending_file)
        replaced_called = True
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", spy_replace)
    
    _atomic_write_json(pending_file, status_window)
    
    assert pending_file.exists()
    assert replaced_called, "Path.replace should have been called for atomicity."

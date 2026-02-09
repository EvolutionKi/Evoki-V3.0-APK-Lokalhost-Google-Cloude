"""
Evoki V3.0 - Integrity Tamper Tests

Automatisierte Tests für Tamper-Detection:
- Test A: Regelwerk manipulieren → Genesis Breach
- Test B: Lexikon manipulieren → Registry Breach  
- Test C: meta.integrity manipulieren → Combined Breach

Abnahme-Kriterium für Production-Readiness.
"""
import pytest
import json
import tempfile
import shutil
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.genesis_anchor import validate_full_integrity, load_regelwerk


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def original_regelwerk():
    """Lädt originales Regelwerk."""
    return load_regelwerk()


@pytest.fixture
def temp_regelwerk_path(tmp_path):
    """Erstellt temporäre Kopie von regelwerk_v12.json."""
    original_path = Path(__file__).parent.parent / "core" / "regelwerk_v12.json"
    temp_path = tmp_path / "regelwerk_v12.json"
    shutil.copy(original_path, temp_path)
    return temp_path


# =============================================================================
# TEST A: REGELWERK TAMPER → GENESIS BREACH
# =============================================================================

def test_regelwerk_tamper_genesis_breach(temp_regelwerk_path, original_regelwerk):
    """
    Test A: Ändere 1 Zeichen im Regelwerk → Genesis SHA256 Mismatch
    
    Erwartung:
    - genesis_ok = False
    - combined_ok = False (abhängig von genesis)
    - verified = False
    - lockdown = True
    """
    # Lade Regelwerk
    with open(temp_regelwerk_path, 'r', encoding='utf-8') as f:
        regelwerk = json.load(f)
    
    # TAMPER: Ändere 1 Zeichen in monolith_text
    original_text = regelwerk['data']['monolith_text']
    regelwerk['data']['monolith_text'] = original_text + "TAMPERED"
    
    # Speichere manipuliertes Regelwerk
    with open(temp_regelwerk_path, 'w', encoding='utf-8') as f:
        json.dump(regelwerk, f, ensure_ascii=False, indent=2)
    
    # Validiere mit manipuliertem Regelwerk
    result = validate_full_integrity(regelwerk=regelwerk, strict=True)
    
    # Assertions
    assert result["verified"] is False, "Tampered Regelwerk sollte NOT verified sein!"
    assert result["lockdown"] is True, "Tampered Regelwerk sollte Lockdown auslösen!"
    assert result["checks"]["genesis_ok"] is False, "Genesis Check sollte FAIL sein!"
    assert result["error"] is not None, "Error Message sollte gesetzt sein!"
    
    print("\n✅ Test A PASS: Regelwerk Tamper → Genesis Breach detected!")
    print(f"   Error: {result['error']}")


# =============================================================================
# TEST B: LEXIKON TAMPER → REGISTRY BREACH
# =============================================================================

def test_lexikon_tamper_registry_breach(original_regelwerk, monkeypatch):
    """
    Test B: Ändere Lexikon Weight → Registry SHA256 Mismatch
    
    Erwartung:
    - registry_ok = False
    - combined_ok = False (abhängig von registry)
    - verified = False
    - lockdown = True
    """
    # Mock lexika_registry.get_registry_anchor() um manipulierten Hash zu liefern
    def mock_registry_anchor():
        # Fake Hash (nicht der echte!)
        return "0000000000000000000000000000000000000000000000000000000000000000"
    
    # Patch die Funktion
    from core import lexika_registry
    monkeypatch.setattr(lexika_registry, "get_registry_anchor", mock_registry_anchor)
    
    # Validiere mit Original Regelwerk aber gefälschtem Registry
    result = validate_full_integrity(regelwerk=original_regelwerk, strict=True)
    
    # Assertions
    assert result["verified"] is False, "Tampered Registry sollte NOT verified sein!"
    assert result["lockdown"] is True, "Tampered Registry sollte Lockdown auslösen!"
    assert result["checks"]["registry_ok"] is False, "Registry Check sollte FAIL sein!"
    assert "Registry Breach" in result["error"], "Error sollte Registry Breach erwähnen!"
    
    print("\n✅ Test B PASS: Lexikon Tamper → Registry Breach detected!")
    print(f"   Error: {result['error']}")


# =============================================================================
# TEST C: META.INTEGRITY TAMPER
# =============================================================================

def test_meta_integrity_tamper_dev_mode(original_regelwerk):
    """
    Test C (Dev Mode): Ändere meta.integrity.genesis_sha256
    
    Im Dev Mode (kein ENV):
    - expected_genesis wird aus meta.integrity gelesen
    - Manipulation von meta.integrity KANN expected verschieben
    - Dies ist exakt der Grund warum Production out-of-band braucht!
    
    Erwartung (Dev Mode):
    - Wenn meta.integrity manipuliert → expected ändert sich
    - calculated bleibt gleich
    - Mismatch → Breach
    """
    import copy
    regelwerk = copy.deepcopy(original_regelwerk)
    
    # TAMPER: Ändere nur meta.integrity.genesis_sha256
    regelwerk["meta"]["integrity"]["genesis_sha256"] = "fake_genesis_hash_0000000000"
    
    # Validiere (Dev Mode - kein ENV)
    result = validate_full_integrity(regelwerk=regelwerk, strict=True)
    
    # Assertions
    assert result["mode"] == "dev", "Sollte im Dev Mode sein (kein ENV)!"
    assert result["verified"] is False, "Manipuliertes meta.integrity sollte Breach sein!"
    assert result["checks"]["genesis_ok"] is False, "Genesis sollte nicht matchen!"
    
    # KRITISCH: expected != calculated
    assert result["expected"]["genesis_sha256"] == "fake_genesis_hash_0000000000"
    assert result["calculated"]["genesis_sha256"] != "fake_genesis_hash_0000000000"
    
    print("\n✅ Test C PASS (Dev): meta.integrity Tamper → Breach detected!")
    print(f"   Expected (manipuliert): {result['expected']['genesis_sha256'][:16]}...")
    print(f"   Calculated (korrekt):   {result['calculated']['genesis_sha256'][:16]}...")


def test_meta_integrity_tamper_prod_mode(original_regelwerk, monkeypatch):
    """
    Test C (Prod Mode): Ändere meta.integrity mit ENV gesetzt
    
    Im Prod Mode (ENV Variables gesetzt):
    - expected_genesis kommt aus ENV (nicht aus meta!)
    - Manipulation von meta.integrity ist IRRELEVANT
    - calculated bleibt gleich
    - ENV-based expected bleibt stabil → korrekte Validierung
    
    Erwartung (Prod Mode):
    - meta.integrity Änderung hat KEINEN Effekt auf expected
    - Wenn calculated == ENV → verified = True
    - Wenn calculated != ENV → verified = False
    """
    import os
    import copy
    
    # Setze ENV Variables (Prod Mode)
    correct_genesis = original_regelwerk["meta"]["integrity"]["genesis_sha256"]
    monkeypatch.setenv("EVOKI_EXPECTED_GENESIS_SHA256", correct_genesis)
    monkeypatch.setenv("EVOKI_EXPECTED_REGISTRY_SHA256", original_regelwerk["meta"]["integrity"]["registry_sha256"])
    monkeypatch.setenv("EVOKI_EXPECTED_COMBINED_SHA256", original_regelwerk["meta"]["integrity"]["combined_sha256"])
    
    # TAMPER: Ändere meta.integrity (sollte ignoriert werden)
    regelwerk = copy.deepcopy(original_regelwerk)
    regelwerk["meta"]["integrity"]["genesis_sha256"] = "fake_hash_ignored"
    
    # Validiere (Prod Mode mit ENV)
    result = validate_full_integrity(regelwerk=regelwerk, strict=True)
    
    # Assertions
    assert result["mode"] == "prod", "Sollte im Prod Mode sein (ENV gesetzt)!"
    
    # KRITISCH: expected kommt aus ENV, NICHT aus manipuliertem meta!
    assert result["expected"]["genesis_sha256"] == correct_genesis
    assert result["expected"]["genesis_sha256"] != "fake_hash_ignored"
    
    # Da calculated korrekt ist und ENV korrekt ist → verified!
    assert result["verified"] is True, "Prod Mode mit korrektem ENV sollte verified sein!"
    assert result["checks"]["genesis_ok"] is True
    
    print("\n✅ Test C PASS (Prod): meta.integrity Manipulation ignoriert (ENV-based)!")
    print(f"   Expected (aus ENV):     {result['expected']['genesis_sha256'][:16]}...")
    print(f"   Meta (manipuliert):     fake_hash_ignored")
    print(f"   Calculated:             {result['calculated']['genesis_sha256'][:16]}...")
    print(f"   → Verified: {result['verified']} (ENV schützt vor meta-Manipulation!)")


# =============================================================================
# INTEGRATION TEST: GATE A MIT TAMPER
# =============================================================================

def test_gate_a_blocks_tampered_regelwerk(temp_regelwerk_path):
    """
    Integration Test: Gate A sollte Prompt blocken bei Tamper.
    
    Erwartung:
    - Tampered Regelwerk → Gate A returns passed=False
    - rule_violations enthält "A51"
    - veto_reasons enthält Error Message
    """
    from core.enforcement_gates import gate_a_validation
    
    # Lade und manipuliere Regelwerk
    with open(temp_regelwerk_path, 'r', encoding='utf-8') as f:
        regelwerk = json.load(f)
    
    regelwerk['data']['monolith_text'] = regelwerk['data']['monolith_text'] + " TAMPERED"
    
    # Mock validate_full_integrity zu tampered result
    def mock_validate(*args, **kwargs):
        return validate_full_integrity(regelwerk=regelwerk, strict=True)
    
    from core import enforcement_gates
    import unittest.mock
    
    with unittest.mock.patch.object(enforcement_gates, 'validate_full_integrity', side_effect=mock_validate):
        # Rufe Gate A auf
        result = gate_a_validation(
            prompt="Test prompt",
            metrics={"T_panic": 0.0, "F_risk": 0.0}
        )
    
    # Assertions
    assert result.passed is False, "Gate A sollte Tamper blocken!"
    assert "A51" in result.rule_violations, "A51 sollte in violations sein!"
    assert len(result.veto_reasons) > 0, "Veto reasons sollten gesetzt sein!"
    
    print("\n✅ Integration Test PASS: Gate A blockt tampiertes Regelwerk!")
    print(f"   Veto: {result.veto_reasons[0]}")


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("INTEGRITY TAMPER TESTS - MANUAL RUN")
    print("=" * 80)
    print("\nFür automatisierten Run: pytest backend/tests/test_integrity_tamper.py")
    print("\nManual Test Execution:")
    
    # Test A
    print("\n" + "=" * 80)
    print("TEST A: Regelwerk Tamper")
    print("=" * 80)
    temp_path = Path(tempfile.mkdtemp()) / "regelwerk_v12.json"
    original = load_regelwerk()
    test_regelwerk_tamper_genesis_breach(temp_path, original)
    
    # Test B
    print("\n" + "=" * 80)
    print("TEST B: Lexikon Tamper")
    print("=" * 80)
    # Benötigt pytest für monkeypatch
    print("⚠️  Bitte pytest verwenden für monkeypatch Tests!")
    
    # Test C
    print("\n" + "=" * 80)
    print("TEST C: meta.integrity Tamper")
    print("=" * 80)
    test_meta_integrity_tamper_dev_mode(original)
    
    print("\n" + "=" * 80)
    print("✅ MANUAL TESTS COMPLETE")
    print("=" * 80)

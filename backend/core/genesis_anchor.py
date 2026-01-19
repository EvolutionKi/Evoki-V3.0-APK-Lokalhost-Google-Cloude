#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evoki V3.0 - Genesis Anchor Validation

Enthält das vollständige regelwerk_v12.json und Validierungsfunktionen.
Verwendet SHA256 als Primär-Integritätsanker (CRC32 als Legacy).

Genesis Anchor (V3.0):
  SHA256: ada4ecae8916fa7e5edd966a97b85af321b64ecfe12489fcea8c6dcef1bd4b1c
  CRC32:  3246342384 (V2.0 Legacy)
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional

# =============================================================================
# GENESIS ANCHOR CONSTANTS
# =============================================================================

# NOTE: Anchors werden jetzt aus regelwerk_v12.json gelesen!
# Keine hardcoded Konstanten mehr → verhindert Widersprüche

# Regelwerk-Pfad (relativ zu diesem Modul)
REGELWERK_PATH = Path(__file__).parent / "regelwerk_v12.json"


# =============================================================================
# CANONICAL SERIALIZATION
# =============================================================================

def canonical_bytes(obj: dict) -> bytes:
    """
    Kanonische Serialisierung für SHA256-Hashing.
    
    HARTE REGELN:
    1. meta.integrity Block wird ENTFERNT (verhindert Selbstbezug)
    2. ensure_ascii=False (UTF-8)
    3. sort_keys=True (deterministische Reihenfolge)
    4. separators=(",", ":") (keine Spaces!)
    
    Args:
        obj: Dict zum Serialisieren
    
    Returns:
        Kanonische UTF-8 Bytes
    """
    from copy import deepcopy
    
    o = deepcopy(obj)
    
    # KRITISCH: meta.integrity entfernen (verhindert Selbstbezug!)
    if "meta" in o and "integrity" in o["meta"]:
        del o["meta"]["integrity"]
    
    s = json.dumps(
        o,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")  # Keine Spaces!
    )
    
    return s.encode("utf-8")


def genesis_sha256(rulebook: dict) -> str:
    """
    Berechnet Genesis Anchor als SHA256 (V3.0 Primär).
    
    Args:
        rulebook: Regelwerk V12 als Dict
    
    Returns:
        SHA256 hex string (64 Zeichen)
    """
    return hashlib.sha256(canonical_bytes(rulebook)).hexdigest()


def genesis_crc32(rulebook: dict) -> int:
    """
    Berechnet Genesis Anchor als CRC32 (V2.0 Legacy).
    
    Args:
        rulebook: Regelwerk V12 als Dict
    
    Returns:
        CRC32 als Integer
    """
    import zlib
    return zlib.crc32(canonical_bytes(rulebook)) & 0xffffffff


# =============================================================================
# REGELWERK LOADING
# =============================================================================

def load_regelwerk(path: Optional[Path] = None) -> dict:
    """
    Lädt regelwerk_v12.json.
    
    Args:
        path: Optional custom path, sonst REGELWERK_PATH
    
    Returns:
        Regelwerk als Dict
    
    Raises:
        FileNotFoundError: Wenn Regelwerk nicht existiert
        json.JSONDecodeError: Wenn JSON invalid
    """
    if path is None:
        path = REGELWERK_PATH
    
    if not path.exists():
        raise FileNotFoundError(f"Regelwerk nicht gefunden: {path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# VALIDATION (A51: Genesis Anchor Protocol)
# =============================================================================

def validate_genesis_anchor(
    regelwerk: Optional[dict] = None,
    strict: bool = True
) -> dict:
    """
    A51: Genesis Anchor Validation (V3.0).
    
    Liest erwartete Hashes AUS regelwerk_v12.json und vergleicht
    mit berechneten Werten (canonical_bytes entfernt meta.integrity).
    
    Args:
        regelwerk: Optional Regelwerk-Dict, sonst wird geladen
        strict: Wenn True, MUSS SHA256 matchen (empfohlen)
    
    Returns:
        {
            "valid": bool,
            "genesis_match": bool,
            "expected_genesis": str,
            "calculated_genesis": str,
            "error": Optional[str]
        }
    """
    if regelwerk is None:
        try:
            regelwerk = load_regelwerk()
        except Exception as e:
            return {
                "valid": False,
                "error": f"Regelwerk Load Error: {str(e)}"
            }
    
    # Erwartete Hashes AUS dem Regelwerk lesen
    integrity = regelwerk.get("meta", {}).get("integrity", {})
    
    expected_genesis = integrity.get("genesis_sha256")
    expected_registry = integrity.get("registry_sha256")
    expected_combined = integrity.get("combined_sha256")
    
    if not expected_genesis:
        return {
            "valid": False,
            "error": "genesis_sha256 fehlt in meta.integrity!"
        }
    
    # Berechne actual Hashes (canonical_bytes entfernt meta.integrity!)
    calc_genesis = genesis_sha256(regelwerk)
    
    # Vergleiche
    genesis_match = (calc_genesis == expected_genesis)
    
    if strict and not genesis_match:
        return {
            "valid": False,
            "genesis_match": False,
            "expected_genesis": expected_genesis,
            "calculated_genesis": calc_genesis,
            "error": f"Genesis Anchor Breach: {calc_genesis} != {expected_genesis}"
        }
    
    return {
        "valid": True,
        "genesis_match": genesis_match,
        "calculated_genesis": calc_genesis,
        "expected_genesis": expected_genesis,
        "error": None
    }


# =============================================================================
# GATE A51 INTEGRATION
# =============================================================================

def gate_a51_check() -> bool:
    """
    A51: Genesis Anchor Gate Check (für enforcement_gates.py).
    
    Returns:
        True if Genesis Anchor valid, False otherwise
    """
    result = validate_genesis_anchor(strict=True)
    return result["valid"]


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("EVOKI V3.0 - GENESIS ANCHOR VALIDATION")
    print("=" * 80)
    
    # Load Regelwerk
    try:
        regelwerk = load_regelwerk()
        print(f"\n✅ Regelwerk geladen: {REGELWERK_PATH}")
        print(f"   Version: {regelwerk.get('version', 'UNKNOWN')}")
        print(f"   Regeln: {len(regelwerk.get('rules', []))}")
    except Exception as e:
        print(f"\n❌ FEHLER beim Laden: {e}")
        exit(1)
    
    # Validate
    result = validate_genesis_anchor(regelwerk, strict=True)
    
    print("\n" + "─" * 80)
    print("VALIDATION RESULT:")
    print("─" * 80)
    
    print(f"\n🔐 Genesis SHA256 (V3.0):")
    print(f"   Expected:   {result.get('expected_genesis', 'N/A')}")
    print(f"   Calculated: {result.get('calculated_genesis', 'N/A')}")
    print(f"   Match: {'✅ YES' if result.get('genesis_match') else '❌ NO'}")
    
    print(f"\n{'✅ VALID' if result['valid'] else '❌ INVALID'}: Genesis Anchor Validation")
    
    if result.get('error'):
        print(f"\n⚠️ ERROR: {result['error']}")
    
    print("\n" + "=" * 80)

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

# Primär: SHA256 (V3.0) - Berechnet aus regelwerk_v12.json
GENESIS_ANCHOR_SHA256 = "98f8d5131d56db7290e075df36a76f63ef2e74cf6cac70fb7cb769d2fe6d294e"

# Legacy: CRC32 (V2.0) - Berechnet aus regelwerk_v12.json  
GENESIS_ANCHOR_CRC32 = 839094334

# HINWEIS: Der "combined_sha256" im regelwerk_v12.json (ada4eca...) ist ein
# kombinierter Hash über MEHRERE Dateien, nicht nur über das Regelwerk!

# Regelwerk-Pfad (relativ zu diesem Modul)
REGELWERK_PATH = Path(__file__).parent / "regelwerk_v12.json"


# =============================================================================
# CANONICAL SERIALIZATION
# =============================================================================

def canonical_bytes(obj: dict) -> bytes:
    """
    Kanonische JSON-Serialisierung für Genesis Anchor.
    
    WICHTIG: Konsistenz durch:
    - sort_keys=True
    - separators=(",", ":") - keine Whitespace-Varianz
    - ensure_ascii=False - konsistente Unicode-Behandlung
    
    Args:
        obj: Dict zum Serialisieren
    
    Returns:
        Kanonische UTF-8 Bytes
    """
    s = json.dumps(
        obj,
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
    A51: Genesis Anchor Validation.
    
    Validiert Regelwerk gegen erwartete Genesis Anchors.
    
    Args:
        regelwerk: Optional Regelwerk-Dict, sonst wird geladen
        strict: Wenn True, MUSS SHA256 matchen (empfohlen)
    
    Returns:
        {
            "valid": bool,
            "sha256_match": bool,
            "crc32_match": bool,
            "calculated_sha256": str,
            "calculated_crc32": int,
            "expected_sha256": str,
            "expected_crc32": int,
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
    
    # Berechne Hashes
    calc_sha256 = genesis_sha256(regelwerk)
    calc_crc32 = genesis_crc32(regelwerk)
    
    # Vergleiche
    sha256_match = (calc_sha256 == GENESIS_ANCHOR_SHA256)
    crc32_match = (calc_crc32 == GENESIS_ANCHOR_CRC32)
    
    # Validierung
    if strict:
        valid = sha256_match  # SHA256 MUSS matchen
    else:
        valid = sha256_match or crc32_match  # Einer muss matchen
    
    return {
        "valid": valid,
        "sha256_match": sha256_match,
        "crc32_match": crc32_match,
        "calculated_sha256": calc_sha256,
        "calculated_crc32": calc_crc32,
        "expected_sha256": GENESIS_ANCHOR_SHA256,
        "expected_crc32": GENESIS_ANCHOR_CRC32,
        "error": None if valid else "Genesis Anchor validation failed!"
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
    
    print(f"\n🔐 SHA256 (V3.0 Primär):")
    print(f"   Expected:   {result['expected_sha256']}")
    print(f"   Calculated: {result['calculated_sha256']}")
    print(f"   Match: {'✅ YES' if result['sha256_match'] else '❌ NO'}")
    
    print(f"\n🔓 CRC32 (V2.0 Legacy):")
    print(f"   Expected:   {result['expected_crc32']}")
    print(f"   Calculated: {result['calculated_crc32']}")
    print(f"   Match: {'✅ YES' if result['crc32_match'] else '❌ NO'}")
    
    print(f"\n{'✅ VALID' if result['valid'] else '❌ INVALID'}: Genesis Anchor Validation")
    
    if result['error']:
        print(f"\n⚠️ ERROR: {result['error']}")
    
    print("\n" + "=" * 80)

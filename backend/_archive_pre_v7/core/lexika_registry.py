#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evoki V3.0 - Lexika Registry

Kombiniert alle Lexika-Module zu einem kanonischen Registry-Hash.
Verwendet für registry_sha256 in Integrity 3.0.
"""
import json
import hashlib
import sys
from pathlib import Path
from typing import Dict

# Import aller Lexika-Module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from tooling.scripts.migration import lexika_v12
    from tooling.scripts.migration import lexika_config
    from tooling.scripts.migration import lexika_v2_1_calibrated
except ImportError as e:
    print(f"⚠️ Import Error: {e}")
    print("Falls Module nicht gefunden werden, prüfe PYTHONPATH")
    lexika_v12 = None
    lexika_config = None
    lexika_v2_1_calibrated = None


def canonical_bytes(obj: dict) -> bytes:
    """Kanonische JSON-Serialisierung."""
    s = json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )
    return s.encode("utf-8")


def load_lexika_registry() -> dict:
    """
    Lädt alle Lexika-Module in ein kanonisches Registry-Objekt.
    
    Returns:
        {
            "lexika_v12": {...},
            "lexika_config": {...},
            "lexika_v2_1": {...}
        }
    """
    registry = {}
    
    # Lexika V12 (Hauptlexikon)
    if lexika_v12:
        registry["lexika_v12"] = {
            "ALL_LEXIKA": lexika_v12.ALL_LEXIKA,
            "stats": lexika_v12.get_lexikon_stats(),
            "hash": lexika_v12.lexika_hash()
        }
    
    # Lexika Config (Thresholds, BVektorConfig, etc.)
    if lexika_config:
        registry["lexika_config"] = {
            "BVektorConfig": {
                "AXES": lexika_config.BVektorConfig.AXES,
                "B_BASE_ARCH": lexika_config.BVektorConfig.B_BASE_ARCH,
                "B_GOLDEN": lexika_config.BVektorConfig.B_GOLDEN,
                "HARD_CONSTRAINTS": lexika_config.BVektorConfig.HARD_CONSTRAINTS,
                "SCORE_WEIGHTS": lexika_config.BVektorConfig.SCORE_WEIGHTS,
                "ALIGNMENT_WEIGHTS": lexika_config.BVektorConfig.ALIGNMENT_WEIGHTS,
            },
            # Weitere Config-Klassen können hier hinzugefügt werden
        }
    
    # Lexika V2.1 (Personalisiert/Calibrated)
    if lexika_v2_1_calibrated:
        # Modul-Level Hash (alle Konstanten)
        import inspect
        v2_1_dict = {
            name: value
            for name, value in inspect.getmembers(lexika_v2_1_calibrated)
            if isinstance(value, dict) and not name.startswith('_')
        }
        registry["lexika_v2_1"] = v2_1_dict
    
    return registry


def registry_sha256(registry: dict) -> str:
    """
    Berechnet registry_sha256.
    
    Args:
        registry: Kombiniertes Lexika-Registry
    
    Returns:
        SHA256 hex string
    """
    return hashlib.sha256(canonical_bytes(registry)).hexdigest()


def get_registry_anchor() -> str:
    """Berechnet aktuellen Registry Anchor."""
    registry = load_lexika_registry()
    return registry_sha256(registry)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LEXIKA REGISTRY SHA256 CALCULATION")
    print("=" * 80)
    
    try:
        registry = load_lexika_registry()
        
        print(f"\n📊 Registry Components:")
        print(f"   - lexika_v12: {'✅ Loaded' if 'lexika_v12' in registry else '❌ Missing'}")
        print(f"   - lexika_config: {'✅ Loaded' if 'lexika_config' in registry else '❌ Missing'}")
        print(f"   - lexika_v2_1: {'✅ Loaded' if 'lexika_v2_1' in registry else '❌ Missing'}")
        
        if 'lexika_v12' in registry:
            stats = registry['lexika_v12'].get('stats', {})
            print(f"\n📈 Lexika V12 Stats:")
            if stats:
                print(f"   - Clusters: {stats.get('total_clusters', 'N/A')}")
                print(f"   - Terms: {stats.get('total_terms', 'N/A')}")
            else:
                print(f"   - Stats: Nicht verfügbar")
        
        sha = registry_sha256(registry)
        
        print(f"\n🔐 Registry SHA256:")
        print(f"   {sha}")
        
        print(f"\n✅ Diesen Wert in regelwerk_v12.json unter 'registry_sha256' eintragen!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

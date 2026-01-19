# Genesis Anchor Migration: CRC32 → SHA256

**Status:** Geplant für V3.0  
**Datum:** 2026-01-19

## Änderung

**V2.0:**
- Genesis Anchor: CRC32 = `3246342384`
- Verwendet in: `regelwerk_v12.json`, `memory_anchor.json`

**V3.0:**
- Genesis Anchor: **SHA256** statt CRC32
- Grund: Höhere Kollisionssicherheit, Standardisierung
- Berechnung über: Vollständiges Regelwerk V12 (JSON serialisiert, sortiert)

## Implementation

```python
# backend/core/genesis_anchor.py
import hashlib
import json

def calculate_genesis_anchor_sha256(regelwerk: dict) -> str:
    """
    Berechnet Genesis Anchor als SHA256 (V3.0).
    
    Args:
        regelwerk: Regelwerk V12 als Dict
    
    Returns:
        SHA256 Hex-String (64 Zeichen)
    """
    # Serialize JSON (sorted, no whitespace)
    json_str = json.dumps(regelwerk, ensure_ascii=False, sort_keys=True)
    
    # SHA256
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return hash_obj.hexdigest()


# Beispiel-Verwendung:
GENESIS_ANCHOR_V3 = "a4f3b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2"

def validate_genesis_anchor(regelwerk: dict) -> bool:
    """Validiert Genesis Anchor gegen Regelwerk."""
    calculated = calculate_genesis_anchor_sha256(regelwerk)
    return calculated == GENESIS_ANCHOR_V3
```

## Migration Path

1. ✅ Beibehalten CRC32 für V2.0-Kompatibilität
2. ⏳ Parallel SHA256 implementieren
3. ⏳ Beide validieren während Übergangsphase
4. ⏳ CRC32 deprecaten in V3.1

## Änderungen in Dateien

- `backend/core/enforcement_gates.py`: SHA256-Check
- `backend/core/genesis_anchor.py`: Neue Datei
- `tooling/scripts/migration/lexika_v12.py`: SHA256-Hash bereits vorhanden (`lexika_hash()`)

## Status

- [x] Notiert für Implementation
- [ ] Genesis Anchor SHA256 berechnet
- [ ] In enforcement_gates.py integriert
- [ ] CRC32 als Fallback beibehalten

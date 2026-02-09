# EVOKI Lexika V3

Dieses Paket ist die **Package-Variante** der `evoki_lexika_v3.py` Monolith-Datei.

## Struktur
- `lexika_data.py` — Kanonische Daten (ALL_LEXIKA + Patterns + Required Keys)
- `registry.py` — Hash/Stats/Export/Health Gate
- `engine.py` — Matching/Scoring Engine (Multi-Match + Longest-First + Overlap-Guard)
- `config.py` — Thresholds & BVektorConfig Container
- `drift.py` — Workspace Drift Scan (findet gemischte Versionen)

## Quickstart
```python
from evoki_lexika_v3 import ALL_LEXIKA, lexika_hash, compute_hazard_score

print(lexika_hash())
print(compute_hazard_score("ich kann nicht mehr, hilfe"))
```

## Drift Scan
```bash
python -m evoki_lexika_v3.drift --root "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\Evoki-V3.0-APK-Lokalhost-Google-Cloude"
```

## JSON Export (maschinenlesbar)
```python
from evoki_lexika_v3 import export_lexika_json
export_lexika_json("evoki_lexika_v3.json")
```

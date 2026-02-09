# EVOKI V3.0 — FINALE QUELLEN-PRIORITÄT

**Zeit:** 2026-02-07 20:15  
**Regel:** V7 Patchpaket = PRIMÄR, evoki_pipeline = SEKUNDÄR

---

## 📚 QUELLEN-HIERARCHIE

### 🥇 PRIMÄR: V7 Patchpaket V2 + Monolith
**Pfad:** `C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith\`

**Enthält (verifiziert):**
- ✅ a_phys_v11.py
- ✅ evoki_bootcheck.py
- ✅ evoki_lock.py
- ✅ genesis_anchor.py
- ✅ evoki_invariants.py
- ✅ metrics_registry.py
- ✅ evoki_history_ingest.py
- ✅ evoki_history_schema.sql
- ✅ lexika.py
- ✅ evoki_lexika_v3.py (Monolith, 698 Zeilen)
- ✅ evoki_lexika_v3_bundle/
- ✅ evoki_fullspectrum168_contract.json
- ✅ evoki_machine_spec.json
- ✅ evoki_roadmap.yaml
- ✅ app.py (Flask - als Referenz)
- ✅ index.html (Frontend - als Referenz)

**Enthält NICHT:**
- ❌ b_vector.py → **Aus evoki_pipeline nehmen!**
- ❌ vector_engine_v2_1.py → **Aus evoki_pipeline nehmen!**
- ❌ metrics_complete_v3.py → **Aus evoki_pipeline nehmen!**
- ❌ timeline_4d_complete.py → **Aus evoki_pipeline nehmen!**
- ❌ chunk_vectorize_full.py → **Aus evoki_pipeline nehmen!**

---

### 🥈 SEKUNDÄR: evoki_pipeline
**Pfad:** `C:\Users\nicom\Documents\evoki\evoki_pipeline\`

**Nutzen für (nur was in V7 fehlt):**
- ✅ b_vector.py (85 Zeilen, kompatibel mit VectorEngine)
- ✅ vector_engine_v2_1.py (64.7KB, 1597 Zeilen)
- ✅ metrics_complete_v3.py (168 Metriken LIVE)
- ✅ timeline_4d_complete.py (Timeline 4D)
- ✅ chunk_vectorize_full.py (Chunking Engine)
- ✅ config.py (Pipeline-Config)

---

## 🎯 KOPIER-STRATEGIE

### Phase 1: V7 Patchpaket (PRIMÄR)
✅ **BEREITS ERLEDIGT** (Phase T0)
- Alle V7 Module nach `backend/core/` kopiert

### Phase 2: evoki_pipeline (SEKUNDÄR)
❌ **TODO** - Nur was fehlt:

```powershell
# 1. b_vector.py (ERSETZEN - Pipeline-Version ist besser!)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\b_vector.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\b_vector.py" -Force

# 2. vector_engine_v2_1.py (NEU)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\vector_engine_v2_1.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\vector_engine_v2_1.py"

# 3. metrics_complete_v3.py (NEU)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\metrics_complete_v3.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_complete_v3.py"

# 4. timeline_4d_complete.py (NEU)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\timeline_4d_complete.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\timeline_4d_complete.py"

# 5. chunk_vectorize_full.py (NEU)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\chunk_vectorize_full.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\chunk_vectorize_full.py"

# 6. config.py (NEU)
Copy-Item "C:\Users\nicom\Documents\evoki\evoki_pipeline\config.py" `
          "C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\config.py"
```

---

## 📊 FINALE MODULE-LISTE

| Modul | Quelle | Status | Priorität |
|-------|--------|--------|-----------|
| **V7 Patchpaket Module:** | | | |
| a_phys_v11.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_bootcheck.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_lock.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| genesis_anchor.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_invariants.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| metrics_registry.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_history_ingest.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| lexika.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_lexika_v3.py | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_lexika_v3_bundle/ | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| evoki_fullspectrum168_contract.json | V7 | ✅ Kopiert | 🥇 PRIMÄR |
| **evoki_pipeline Module (nur was fehlt):** | | | |
| b_vector.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| vector_engine_v2_1.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| metrics_complete_v3.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| timeline_4d_complete.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| chunk_vectorize_full.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| config.py | evoki_pipeline | ❌ Zu kopieren | 🥈 SEKUNDÄR |
| **Zu generieren:** | | | |
| spectrum_types.py | Contract | ❌ Zu generieren | 🔥 KRITISCH |

---

## 🚀 SOFORT-AKTION

Soll ich **JETZT** folgendes tun?

1. ✅ Import-Fehler beheben (`backend/core/__init__.py`)
2. ✅ Alle 6 evoki_pipeline Module kopieren  
3. ✅ `spectrum_types.py` generieren
4. ✅ Testen ob alles funktioniert

**Zeitaufwand:** 30 Minuten  
**Danach:** Alle Module vorhanden, Imports funktionieren ✅

**JA oder NEIN?** 🎯

---

**Ende FINALE_QUELLEN_PRIORITAET.md**

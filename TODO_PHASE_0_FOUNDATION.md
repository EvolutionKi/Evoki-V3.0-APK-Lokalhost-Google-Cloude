# ✅ TODO: PHASE 0 — FOUNDATION (2-3 Stunden)

**Ziel**: Saubere Basis schaffen für V3.0 Data Layer Implementation

**Status**: ⏳ NOCH NICHT GESTARTET

---

## 📋 **TASK 0.1: CLEANUP ALTE ARTEFAKTE** (~15 Min)

### **Warum wichtig?**
Alte, gescheiterte Implementierungsversuche können zu Verwirrung führen. Wir archivieren sie statt zu löschen (für Forensik/Lessons Learned).

### **Schritte**:

- [ ] **0.1.1 Suche nach V3.0-bezogenen Dateien**
  ```powershell
  # Im Projektordner
  cd "C:\Evoki V3.0 APK-Lokalhost-Google Cloude"
  
  # Suche alle Dateien mit "v3" im Namen (case-insensitive)
  Get-ChildItem -Recurse -File | Where-Object { $_.Name -like "*v3*" -or $_.Name -like "*V3*" } | Select-Object FullName
  ```
  - [ ] Liste erstellen von allen gefundenen Dateien
  - [ ] Manuell prüfen: Welche sind "Müll" (gescheiterte Versuche)?

- [ ] **0.1.2 Erstelle Archive-Ordner**
  ```powershell
  New-Item -Path ".\archive\failed_v3_attempts\" -ItemType Directory -Force
  ```

- [ ] **0.1.3 Verschiebe gescheiterte Versuche**
  - [ ] Für jede identifizierte "Müll"-Datei:
    ```powershell
    Move-Item -Path ".\path\to\failed_file.py" -Destination ".\archive\failed_v3_attempts\"
    ```
  - [ ] **NICHT löschen!** Nur archivieren!

- [ ] **0.1.4 Erstelle neues Arbeitsverzeichnis**
  ```powershell
  New-Item -Path ".\backend\v3_data_layer\" -ItemType Directory -Force
  ```

### **Was du sehen solltest**:
```
✅ Created: archive/failed_v3_attempts/
✅ Moved 15 files to archive
✅ Created: backend/v3_data_layer/
```

---

## 📋 **TASK 0.2: TEST-DATA EXTRAHIEREN** (~30 Min)

### **Warum wichtig?**
Wir brauchen die **1000 Test-Paare** aus der erfolgreichen T2 Pipeline als Basis für alle Tests.

### **Schritte**:

- [ ] **0.2.1 Finde T2 Pipeline Test-Data**
  - [ ] Prüfe: `backend/migration/` für vorhandene Test-Outputs
  - [ ] Prüfe: `T2_PIPELINE_SUCCESS_REPORT.md` für Pfad-Hinweise
  - [ ] Erwarteter Ort: Irgendwo müssen die 1000 Paare liegen, die bei T2 funktioniert haben

- [ ] **0.2.2 Erstelle Test-Data Ordner**
  ```powershell
  New-Item -Path ".\backend\test_data\1000_pairs\" -ItemType Directory -Force
  ```

- [ ] **0.2.3 Kopiere/Extrahiere 1000 Paare**
  
  **OPTION A**: Falls T2 Pipeline DBs existieren
  ```powershell
  # SQLite Query um 1000 Paare zu extrahieren
  # (muss angepasst werden je nach Format)
  ```
  
  **OPTION B**: Falls History-Archive existiert
  ```powershell
  # Aus tooling/legacy/Evoki_History_Archive/2025/ erste 1000 Paare nehmen
  ```
  
  - [ ] Erstelle JSON-Datei mit 1000 Paaren:
    ```json
    [
      {
        "pair_id": "uuid-1",
        "session_id": "session-1",
        "pair_index": 0,
        "user_text": "...",
        "user_ts": "2025-02-15T14:30:00Z",
        "ai_text": "...",
        "ai_ts": "2025-02-15T14:30:05Z"
      },
      ...
    ]
    ```

- [ ] **0.2.4 Validiere Format**
  ```powershell
  # Python-Script zum Prüfen
  python -c "import json; data=json.load(open('backend/test_data/1000_pairs/pairs.json')); print(f'✅ {len(data)} Paare geladen')"
  ```

### **Was du sehen solltest**:
```
✅ Created: backend/test_data/1000_pairs/
✅ Extracted 1000 pairs
✅ Format validated: pairs.json (1000 entries)
📊 Sample Pair:
   User: "Ich brauche Hilfe..."
   AI:   "Ich bin für dich da..."
```

---

## 📋 **TASK 0.3: ERSTELLE ALLE 5 V3.0 SQL-SCHEMAS** (~1 Stunde)

### **Warum wichtig?**
Die SQL-Schemas definieren die Datenbank-Struktur. Sie MÜSSEN korrekt sein laut BUCH 7 Spezifikation.

### **Schritte**:

- [ ] **0.3.1 Prüfe existierendes `evoki_v3_core_schema.sql`**
  ```powershell
  # Schaue ob schon existiert
  Get-ChildItem -Path ".\backend\schemas\" -Filter "*v3*core*.sql"
  ```
  - [ ] Falls existiert: Öffne und vergleiche mit BUCH 7 Spec (Zeilen 11550-11900)
  - [ ] Falls NICHT existiert: Erstelle neu

- [ ] **0.3.2 Erstelle `evoki_v3_core_schema.sql`**
  - [ ] **Tabellen**:
    - [ ] `sessions` (session_id, conversation_id, date_ymd, total_pairs)
    - [ ] `prompt_pairs` (pair_id, session_id, pair_index, user_text, ai_text, timestamps, pair_hash)
    - [ ] `metrics_full` (pair_id, user_m1_A, ..., ai_m1_A, ..., gradients, disharmony_score)
    - [ ] `session_chain` (session_id, genesis_hash, current_hash, chain_length, integrity_status)
    - [ ] `b_state_evolution` (pair_id, B_safety, B_life, B_warmth, B_clarity, B_depth, B_init, B_truth, B_align, deltas)
    - [ ] `hazard_events` (event_id, pair_id, trigger_type, user_m151_hazard, B_safety, guardian_activated)
  - [ ] **Indizes** für Performance
  - [ ] **Referenz**: BUCH 7, Zeilen 11550-11900

- [ ] **0.3.3 Erstelle `evoki_v3_graph_schema.sql`**
  - [ ] **Tabellen**:
    - [ ] `graph_nodes` (node_id=pair_id, session_id, semantic_vector_id, metrics_vector_id)
    - [ ] `graph_edges` (edge_id, source_pair_id, target_pair_id, semantic_similarity, metric_similarity, combined_weight)
    - [ ] `graph_clusters` (cluster_id, cluster_name, node_count, avg_metrics JSON)
  - [ ] **Referenz**: BUCH 7, Zeilen 12400-12600

- [ ] **0.3.4 Erstelle `evoki_v3_keywords_schema.sql`**
  - [ ] **Tabellen**:
    - [ ] `keyword_registry` (keyword_id, keyword_text, frequency, relevance_score, promoted, first_seen, last_seen)
    - [ ] `keyword_pair_links` (link_id, keyword_id, pair_id, tf_idf_score)
    - [ ] `keyword_associations` (assoc_id, keyword_1_id, keyword_2_id, co_occurrence_count, lift_score)
    - [ ] `keyword_clusters` (cluster_id, cluster_name, keywords JSON)
    - [ ] `live_session_index` (FTS5 Virtual Table für Full-Text Search)
  - [ ] **Referenz**: BUCH 7, Zeilen 12700-13150

- [ ] **0.3.5 Erstelle `evoki_v3_analytics_schema.sql`**
  - [ ] **Tabellen**:
    - [ ] `api_requests` (request_id, prompt_text, enriched_context JSON, timestamp)
    - [ ] `api_responses` (response_id, request_id, response_text, prognosis JSON, strategy JSON, timestamp)
    - [ ] `search_events` (search_id, query, method, results JSON, latency_ms, timestamp)
    - [ ] `prompt_history` (history_id, pair_id, user_text, ai_text, timestamp)
    - [ ] `metric_evaluations` (eval_id, pair_id, metric_name, metric_value, computation_time_ms, timestamp)
    - [ ] `b_vector_verifications` (verif_id, pair_id, local_b_vector JSON, api_b_vector JSON, delta, timestamp)
    - [ ] `lexika_verification_log` (log_id, pair_id, lexika_triggered JSON, timestamp)
    - [ ] `learning_events` (event_id, event_type, keyword_text, frequency_before, frequency_after, promoted, timestamp)
    - [ ] `system_events` (event_id, event_type, severity, message, details JSON, timestamp)
  - [ ] **Referenz**: BUCH 7, Zeilen 14000-14250

- [ ] **0.3.6 Erstelle `evoki_v3_trajectories_schema.sql`**
  - [ ] **Tabellen**:
    - [ ] `metric_trajectories` (traj_id, source_pair_id, session_id, metric_name, window_offset, metric_value, gradient, trend, timestamp)
    - [ ] `metric_predictions` (pred_id, source_pair_id, metric_name, predicted_offset, predicted_value, confidence, prediction_method, timestamp)
    - [ ] `trajectory_patterns` (pattern_id, pattern_signature, sequence JSON, occurrence_count, avg_outcome, timestamp)
    - [ ] `historical_futures` (future_id, source_pair_id, session_id, future_plus_1 JSON, future_plus_2 JSON, future_plus_5 JSON, future_plus_10 JSON, future_plus_25 JSON, outcome_type, guardian_activated, successful_strategies JSON, is_complete, prompts_available, timestamp)
  - [ ] **Referenz**: BUCH 7, Zeilen 14700-15100, 16685-16785

### **Was du sehen solltest**:
```
✅ Created: backend/schemas/evoki_v3_core_schema.sql (260 Zeilen)
✅ Created: backend/schemas/evoki_v3_graph_schema.sql (180 Zeilen)
✅ Created: backend/schemas/evoki_v3_keywords_schema.sql (220 Zeilen)
✅ Created: backend/schemas/evoki_v3_analytics_schema.sql (350 Zeilen)
✅ Created: backend/schemas/evoki_v3_trajectories_schema.sql (280 Zeilen)

📊 Total: 5 SQL-Schema-Dateien, ~1290 Zeilen SQL
```

---

## 📋 **TASK 0.4: ERSTELLE FAISS CONFIG** (~30 Min)

### **Warum wichtig?**
FAISS-Konfiguration definiert die Vector-Store-Struktur (Dimensionen, Index-Typen, Namespaces).

### **Schritte**:

- [ ] **0.4.1 Erstelle `faiss_config.json`**
  ```json
  {
    "namespaces": {
      "atomic_pairs": {
        "dimension": 384,
        "index_type": "IndexFlatIP",
        "description": "Semantic search on prompt pairs",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "metadata_file": "atomic_pairs.meta.json"
      },
      "metrics_wpf": {
        "dimension": 322,
        "index_type": "IndexFlatL2",
        "description": "Metric-based similarity search",
        "use_pca": false,
        "pca_target_dim": 128,
        "metadata_file": "metrics_wpf.meta.json"
      },
      "trajectory_wpf": {
        "dimension": 30,
        "index_type": "IndexFlatL2",
        "description": "Trajectory-based similarity search (W-P-F)",
        "trajectory_offsets": [-25, -5, -2, -1, 0],
        "critical_metrics": ["m1_A", "m151_hazard", "B_safety"],
        "metadata_file": "trajectory_wpf.meta.json"
      }
    },
    "storage": {
      "base_path": "backend/v3_data_layer/faiss_indices/",
      "auto_save": true,
      "save_interval_seconds": 300
    },
    "performance": {
      "nprobe": 10,
      "batch_size": 1000,
      "use_gpu": false
    }
  }
  ```
  - [ ] Speichere als: `backend/v3_data_layer/faiss_config.json`

- [ ] **0.4.2 Validiere JSON**
  ```powershell
  # Python JSON-Validierung
  python -c "import json; config=json.load(open('backend/v3_data_layer/faiss_config.json')); print('✅ Valid JSON, 3 Namespaces:', list(config['namespaces'].keys()))"
  ```

### **Was du sehen solltest**:
```
✅ Created: backend/v3_data_layer/faiss_config.json
✅ Valid JSON, 3 Namespaces: ['atomic_pairs', 'metrics_wpf', 'trajectory_wpf']

📊 Configuration:
   • atomic_pairs:   384D (MiniLM)
   • metrics_wpf:    322D (raw metrics)
   • trajectory_wpf: 30D (custom)
```

---

## 📋 **TASK 0.5: ERSTELLE VERZEICHNISSTRUKTUR** (~15 Min)

### **Warum wichtig?**
Saubere Ordner-Struktur verhindert Chaos und macht Code nachvollziehbar.

### **Schritte**:

- [ ] **0.5.1 Erstelle alle benötigten Ordner**
  ```powershell
  # Hauptverzeichnisse
  New-Item -Path ".\backend\v3_data_layer\databases\" -ItemType Directory -Force
  New-Item -Path ".\backend\v3_data_layer\faiss_indices\" -ItemType Directory -Force
  New-Item -Path ".\backend\v3_data_layer\models\" -ItemType Directory -Force
  New-Item -Path ".\backend\v3_data_layer\scripts\" -ItemType Directory -Force
  New-Item -Path ".\backend\v3_data_layer\tests\" -ItemType Directory -Force
  New-Item -Path ".\backend\v3_data_layer\logs\" -ItemType Directory -Force
  
  # Test-Data
  New-Item -Path ".\backend\test_data\1000_pairs\" -ItemType Directory -Force
  
  # Archive
  New-Item -Path ".\archive\failed_v3_attempts\" -ItemType Directory -Force
  ```

- [ ] **0.5.2 Erstelle README in jedem Ordner**
  - [ ] `databases/README.md` → "SQLite DBs werden hier gespeichert"
  - [ ] `faiss_indices/README.md` → "FAISS Indizes werden hier gespeichert"
  - [ ] `models/README.md` → "Embedding-Modelle werden hier gespeichert"
  - [ ] `scripts/README.md` → "Python Pipeline-Scripts"
  - [ ] `tests/README.md` → "Unit-Tests für V3.0 Components"
  - [ ] `logs/README.md` → "Log-Dateien für Debugging"

- [ ] **0.5.3 Erstelle `.gitignore` Einträge**
  ```
  # In .gitignore hinzufügen:
  backend/v3_data_layer/databases/*.db
  backend/v3_data_layer/faiss_indices/*.index
  backend/v3_data_layer/models/*
  backend/v3_data_layer/logs/*.log
  !backend/v3_data_layer/databases/.gitkeep
  !backend/v3_data_layer/faiss_indices/.gitkeep
  ```

- [ ] **0.5.4 Erstelle `.gitkeep` Dateien** (damit leere Ordner committed werden)
  ```powershell
  New-Item -Path ".\backend\v3_data_layer\databases\.gitkeep" -ItemType File -Force
  New-Item -Path ".\backend\v3_data_layer\faiss_indices\.gitkeep" -ItemType File -Force
  New-Item -Path ".\backend\v3_data_layer\models\.gitkeep" -ItemType File -Force
  New-Item -Path ".\backend\v3_data_layer\logs\.gitkeep" -ItemType File -Force
  ```

### **Was du sehen solltest**:
```
backend/v3_data_layer/
├── databases/          ✅ Created
│   ├── .gitkeep       ✅ Created
│   └── README.md      ✅ Created
├── faiss_indices/      ✅ Created
│   ├── .gitkeep       ✅ Created
│   └── README.md      ✅ Created
├── models/             ✅ Created
│   ├── .gitkeep       ✅ Created
│   └── README.md      ✅ Created
├── scripts/            ✅ Created
│   └── README.md      ✅ Created
├── tests/              ✅ Created
│   └── README.md      ✅ Created
└── logs/               ✅ Created
    ├── .gitkeep       ✅ Created
    └── README.md      ✅ Created
```

---

## ✅ **PHASE 0 ABSCHLUSS-CHECKLIST**

Erst wenn ALLE diese Punkte ✅ sind, kann Phase 1 starten:

- [ ] **0.1 Cleanup**: Alte Artefakte archiviert in `archive/failed_v3_attempts/`
- [ ] **0.2 Test-Data**: 1000 Paare extrahiert in `backend/test_data/1000_pairs/pairs.json`
- [ ] **0.3 Schemas**: Alle 5 SQL-Schema-Dateien erstellt (evoki_v3_core, graph, keywords, analytics, trajectories)
- [ ] **0.4 FAISS Config**: `faiss_config.json` erstellt mit 3 Namespaces
- [ ] **0.5 Struktur**: Alle Ordner + README + .gitkeep erstellt

### **Final Validation Command**:
```powershell
# Run this to check if Phase 0 is complete
python -c "
import os
import json

checks = {
    'Archive exists': os.path.exists('archive/failed_v3_attempts'),
    'Test-Data exists': os.path.exists('backend/test_data/1000_pairs/pairs.json'),
    'Core Schema exists': os.path.exists('backend/schemas/evoki_v3_core_schema.sql'),
    'Graph Schema exists': os.path.exists('backend/schemas/evoki_v3_graph_schema.sql'),
    'Keywords Schema exists': os.path.exists('backend/schemas/evoki_v3_keywords_schema.sql'),
    'Analytics Schema exists': os.path.exists('backend/schemas/evoki_v3_analytics_schema.sql'),
    'Trajectories Schema exists': os.path.exists('backend/schemas/evoki_v3_trajectories_schema.sql'),
    'FAISS Config exists': os.path.exists('backend/v3_data_layer/faiss_config.json'),
    'Databases dir exists': os.path.exists('backend/v3_data_layer/databases'),
    'Scripts dir exists': os.path.exists('backend/v3_data_layer/scripts')
}

print('\n🔍 PHASE 0 VALIDATION:\n' + '='*50)
for check, passed in checks.items():
    print(f'{'✅' if passed else '❌'} {check}')

all_passed = all(checks.values())
print('='*50)
print(f'\n{'✅ PHASE 0 COMPLETE - Ready for Phase 1!' if all_passed else '❌ PHASE 0 INCOMPLETE - Fix missing items'}')
"
```

### **Was du sehen solltest**:
```
🔍 PHASE 0 VALIDATION:
==================================================
✅ Archive exists
✅ Test-Data exists
✅ Core Schema exists
✅ Graph Schema exists
✅ Keywords Schema exists
✅ Analytics Schema exists
✅ Trajectories Schema exists
✅ FAISS Config exists
✅ Databases dir exists
✅ Scripts dir exists
==================================================

✅ PHASE 0 COMPLETE - Ready for Phase 1!
```

---

**⏱️ GESCHÄTZTE ZEIT**: 2-3 Stunden  
**📊 OUTPUT**: Saubere, strukturierte Basis für V3.0 Implementation

**NÄCHSTER SCHRITT**: Wenn Phase 0 complete → Starte `TODO_PHASE_1_CORE_DB.md`

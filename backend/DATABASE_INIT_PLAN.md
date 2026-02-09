# 🏗️ EVOKI V3.0 — 9-DATABASE INITIALIZATION PLAN

**Strategie:** Jede DB bekommt ihr eigenes Script + Schema!

---

## 📊 DATABASE MAPPING

### **GROUP 1: V3.0 CORE (BUCH 7)**

1. **evoki_v3_core.db**
   - Schema: `backend/schemas/BUCH7_evoki_v3_core_schema.sql`
   - Script: `backend/init_v3_core_db.py`
   - Tables: sessions, prompt_pairs, metrics_full, b_state_evolution, session_chain, hazard_events

2. **evoki_v3_graph.db**
   - Schema: `backend/schemas/BUCH7_evoki_v3_graph_schema.sql`
   - Script: `backend/init_v3_graph_db.py`
   - Tables: nodes, edges, node_embeddings

3. **evoki_v3_keywords.db**
   - Schema: (zu erstellen)
   - Script: `backend/init_v3_keywords_db.py`
   - Tables: keyword_registry, keyword_associations, keyword_clusters, live_session_index

4. **evoki_v3_analytics.db**
   - Schema: (zu erstellen)
   - Script: `backend/init_v3_analytics_db.py`
   - Tables: b_vector_verifications, lexika_verification_log, dual_response_logs

5. **evoki_v3_trajectories.db**
   - Schema: (zu erstellen)
   - Script: `backend/init_v3_trajectories_db.py`
   - Tables: metric_trajectories, metric_predictions, trajectory_patterns, historical_futures

### **GROUP 2: EXTENDED/LEGACY**

6. **evoki_metadata.db**
   - Schema: `backend/schemas/evoki_metadata_schema.sql` ✅
   - Script: `backend/init_metadata_db.py`
   - Tables: sessions, turns, source_files, genesis_chain

7. **evoki_resonance.db**
   - Schema: `backend/schemas/evoki_resonance_schema.sql` ✅
   - Script: `backend/init_resonance_db.py`
   - Tables: metrics, b_state_evolution, trajectories, embeddings, a_phys_telemetry, gradient_analysis, hazard_events

8. **evoki_triggers.db**
   - Schema: `backend/schemas/evoki_triggers_schema.sql` ✅
   - Script: `backend/init_triggers_db.py`
   - Tables: lexikon_matches, personal_trauma_markers, crisis_patterns, safety_interventions

9. **evoki_metapatterns.db**
   - Schema: `backend/schemas/evoki_metapatterns_schema.sql` ✅
   - Script: `backend/init_metapatterns_db.py`
   - Tables: user_vocabulary, metaphors, themes, speech_patterns, semantic_fingerprint, ngrams

---

## 🎯 PRAGMATISCHER ANSATZ

**Phase 1: Kritische DBs (P0)** - Für MVP mit 1000 Paaren
1. ✅ evoki_v3_core.db (BUCH 7)
2. ✅ evoki_metadata.db (Turns tracking)
3. ✅ evoki_resonance.db (Metrics + B-Vector)

**Phase 2: Analytics (P1)**
4. evoki_v3_keywords.db
5. evoki_v3_analytics.db
6. evoki_triggers.db

**Phase 3: Advanced (P2)**
7. evoki_v3_graph.db
8. evoki_v3_trajectories.db
9. evoki_metapatterns.db

---

## ✅ TODO (IMMEDIATE)

1. [ ] Create `backend/init_v3_core_db.py`
2. [ ] Create `backend/init_metadata_db.py`
3. [ ] Create `backend/init_resonance_db.py`
4. [ ] Create `backend/pipeline_phase1.py` (3 critical DBs only!)
5. [ ] Test with 10 pairs
6. [ ] Scale to 1000 pairs
7. [ ] Validate with `backend/scripts/validate_import.py`

---

## 🚀 NÄCHSTER SCHRITT

**Ich erstelle jetzt:**
1. Init-Scripts für die 3 kritischen DBs
2. Pipeline die NUR diese 3 nutzt (MVP!)
3. Wenn das steht → erweitern auf alle 9

**OK?** 🎯

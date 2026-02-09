#!/usr/bin/env python3
"""
COMPLETE DATABASE ARCHITECTURE MAP — 9 DATABASES
================================================

V3.0 COMPLETE SYSTEM (BUCH 7 + Extended)
"""

from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude")

# ═══════════════════════════════════════════════════════════════════════════
# 9 DATENBANK ARCHITEKTUR
# ═══════════════════════════════════════════════════════════════════════════

DATABASE_ARCHITECTURE = {
    
    # ───────────────────────────────────────────────────────────────────────
    # GROUP 1: V3.0 CORE (BUCH 7 Standard)
    # ───────────────────────────────────────────────────────────────────────
    
    "v3_core": {
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db",
        "priority": "P0",
        "purpose": "Core V3.0 Database (BUCH 7 Standard)",
        "tables": [
            "sessions",
            "prompt_pairs",
            "metrics_full",      # 168 Metriken (User + AI)
            "b_state_evolution", # 7D Soul Signature
            "session_chain",     # Kryptografische Verkettung
            "hazard_events"
        ],
        "size_estimate": "~459 MB"
    },
    
    "v3_graph": {
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_graph.db",
        "priority": "P1",
        "purpose": "Knowledge Graph (Context Relations)",
        "tables": [
            "nodes",
            "edges",
            "node_embeddings"
        ],
        "size_estimate": "~50 MB"
    },
    
    "v3_keywords": {
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_keywords.db",
        "priority": "P1",
        "purpose": "Learning Keyword Engine (Self-Training)",
        "tables": [
            "keyword_registry",
            "keyword_associations",
            "keyword_clusters",
            "live_session_index"  # FTS5
        ],
        "size_estimate": "~30 MB"
    },
    
    "v3_analytics": {
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_analytics.db",
        "priority": "P1",
        "purpose": "Analytics & B-Vector Verification",
        "tables": [
            "b_vector_verifications",
            "lexika_verification_log",
            "dual_response_logs"
        ],
        "size_estimate": "~40 MB"
    },
    
    "v3_trajectories": {
        "path": PROJECT_ROOT / "backend/data/databases/evoki_v3_trajectories.db",
        "priority": "P0",
        "purpose": "Metric Trajectories & Predictions",
        "tables": [
            "metric_trajectories",
            "metric_predictions",
            "trajectory_patterns",
            "historical_futures"  # Was kam DANACH?
        ],
        "size_estimate": "~80 MB"
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # GROUP 2: EXTENDED/LEGACY (Pre-BUCH 7, still valuable)
    # ───────────────────────────────────────────────────────────────────────
    
    "metadata": {
        "path": PROJECT_ROOT / "evoki_metadata.db",
        "priority": "P0",
        "purpose": "Sessions, Turns, File Management, Genesis Chain",
        "tables": [
            "sessions",
            "turns",
            "source_files",
            "genesis_chain"  # Integrity tracking
        ],
        "size_estimate": "~50 MB",
        "note": "OVERLAPS with v3_core.sessions/prompt_pairs"
    },
    
    "resonance": {
        "path": PROJECT_ROOT / "evoki_resonance.db",
        "priority": "P0",
        "purpose": "Metrics, Trajectories, Embeddings, A_Phys Telemetry",
        "tables": [
            "metrics",           # 168 Metriken
            "b_state_evolution", # 7D Soul (DUPLICATE!)
            "trajectories",      # Gradients
            "embeddings",        # Semantic vectors
            "a_phys_telemetry",  # Physics engine details
            "gradient_analysis", # Dual-gradient (User vs AI)
            "hazard_events"      # Crisis triggers
        ],
        "size_estimate": "~200 MB",
        "note": "MAJOR OVERLAP with v3_core + v3_trajectories"
    },
    
    "triggers": {
        "path": PROJECT_ROOT / "evoki_triggers.db",
        "priority": "P1",
        "purpose": "Personal Trauma Markers, Crisis Patterns",
        "tables": [
            "lexikon_matches",          # Which Lexika triggered
            "personal_trauma_markers",  # User-specific learned triggers
            "crisis_patterns",          # Recurring hazard patterns
            "safety_interventions"      # Guardian actions
        ],
        "size_estimate": "~20 MB",
        "note": "Complements v3_analytics"
    },
    
    "metapatterns": {
        "path": PROJECT_ROOT / "evoki_metapatterns.db",
        "priority": "P2",
        "purpose": "User Vocabulary, Metaphors, Themes, Linguistic Fingerprint",
        "tables": [
            "user_vocabulary",      # Unique words
            "metaphors",            # Expressions
            "themes",               # Recurring topics
            "speech_patterns",      # Syntax & style
            "semantic_fingerprint", # Overall profile
            "ngrams"                # Common phrases
        ],
        "size_estimate": "~100 MB",
        "note": "OVERLAPS with v3_keywords functionality"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# DATA FLOW MAP (wie interagieren die DBs?)
# ═══════════════════════════════════════════════════════════════════════════

DATA_FLOW = """
┌─────────────────────────────────────────────────────────────────────────┐
│ PROMPT PAIR PROCESSING FLOW (9 DATABASES)                               │
└─────────────────────────────────────────────────────────────────────────┘

1. USER PROMPT arrives
   ↓
2. METADATA DB (evoki_metadata.db)
   └─ INSERT into `turns` (user_text, timestamp, session_id)
   
3. METADATA DB (evoki_metadata.db)  
   └─ UPDATE `genesis_chain` (compute SHA-256 hash)
   
4. V3 CORE DB (evoki_v3_core.db)
   └─ INSERT into `prompt_pairs` (pair_id, user_text, ...)
   
5. CALCULATE METRICS (168 Metriken)
   ↓
6. V3 CORE DB (evoki_v3_core.db)
   └─ INSERT into `metrics_full` (user_m1_A, user_m151_hazard, ...)
   
7. RESONANCE DB (evoki_resonance.db)
   └─ INSERT into `metrics` (same data, legacy format)
   
8. CALCULATE B-VEKTOR (7D Soul)
   ↓
9. V3 CORE DB (evoki_v3_core.db)
   └─ INSERT into `b_state_evolution`
   
10. RESONANCE DB (evoki_resonance.db)
    └─ INSERT into `b_state_evolution` (DUPLICATE!)
    
11. CHECK LEXIKA MATCHES
    ↓
12. TRIGGERS DB (evoki_triggers.db)
    └─ INSERT into `lexikon_matches` (if triggered)
    
13. EXTRACT KEYWORDS
    ↓
14. V3 KEYWORDS DB (evoki_v3_keywords.db)
    └─ UPDATE `keyword_registry` (increment frequency)
    
15. METAPATTERNS DB (evoki_metapatterns.db)
    └─ UPDATE `user_vocabulary` (add/increment)
    
16. CALCULATE TRAJECTORY
    ↓
17. V3 TRAJECTORIES DB (evoki_v3_trajectories.db)
    └─ INSERT into `metric_trajectories`
    
18. RESONANCE DB (evoki_resonance.db)
    └─ INSERT into `trajectories` (DUPLICATE!)
    
19. FAISS UPDATE (3 Namespaces)
    └─ semantic_wpf, metrics_embeddings, trajectory_wpf
    
20. IF HAZARD DETECTED:
    ↓
21. V3 CORE DB (evoki_v3_core.db)
    └─ INSERT into `hazard_events`
    
22. TRIGGERS DB (evoki_triggers.db)
    └─ INSERT into `safety_interventions`
    
23. RESONANCE DB (evoki_resonance.db)
    └─ INSERT into `hazard_events` (DUPLICATE!)

═══════════════════════════════════════════════════════════════════════════
TOTAL WRITES PER PAIR: 15-23 DB operations across 9 databases!
TIMING BUDGET: ~300ms (acceptable)
═══════════════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════════════════
# CRITICAL OVERLAPS & REDUNDANCIES
# ═══════════════════════════════════════════════════════════════════════════

OVERLAPS = {
    "metrics": {
        "v3_core.metrics_full": "168 Metriken (BUCH 7 Standard)",
        "resonance.metrics": "168 Metriken (Legacy Format)",
        "strategy": "Write to BOTH (backward compatibility)"
    },
    
    "b_state_evolution": {
        "v3_core.b_state_evolution": "7D Soul (Primary)",
        "resonance.b_state_evolution": "7D Soul (Mirror)",
        "strategy": "Write to BOTH (redundancy for safety)"
    },
    
    "trajectories": {
        "v3_trajectories.metric_trajectories": "Full trajectory data",
        "resonance.trajectories": "Simplified gradients",
        "strategy": "v3_trajectories = PRIMARY, resonance = summary"
    },
    
    "keywords": {
        "v3_keywords.keyword_registry": "Learning engine (self-training)",
        "metapatterns.user_vocabulary": "Static vocabulary analysis",
        "strategy": "BOTH - different purposes (learning vs analysis)"
    },
    
    "hazards": {
        "v3_core.hazard_events": "Critical hazards only",
        "resonance.hazard_events": "All hazards",
        "triggers.safety_interventions": "Actions taken",
        "strategy": "All 3 - different granularity"
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def get_all_db_paths() -> Dict[str, Path]:
    """Return all 9 database paths"""
    return {name: info["path"] for name, info in DATABASE_ARCHITECTURE.items()}

def get_priority_dbs(priority: str = "P0") -> List[str]:
    """Get databases by priority"""
    return [
        name for name, info in DATABASE_ARCHITECTURE.items()
        if info["priority"] == priority
    ]

def print_architecture():
    """Print full architecture overview"""
    print("="*80)
    print("EVOKI V3.0 — 9 DATABASE ARCHITECTURE")
    print("="*80)
    
    for name, info in DATABASE_ARCHITECTURE.items():
        print(f"\n{name.upper()} ({info['priority']})")
        print(f"  Path:    {info['path']}")
        print(f"  Purpose: {info['purpose']}")
        print(f"  Size:    {info['size_estimate']}")
        if "note" in info:
            print(f"  ⚠️  Note: {info['note']}")
    
    print("\n" + "="*80)
    print("TOTAL ESTIMATED SIZE: ~1029 MB")
    print("="*80)

if __name__ == "__main__":
    print_architecture()
    print("\n" + DATA_FLOW)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
              EVOKI 4D ZEITMASCHINE - VOLLSTÄNDIGE ARCHITEKTUR
              ==================================================
              
    DIE 8 PARALLELEN VEKTORDATENBANKEN:
    
    VERGANGENHEIT (Past):
    ├── W_m1:  t-1   (1 Prompt zurück)
    ├── W_m2:  t-2   (2 Prompts zurück)
    ├── W_m5:  t-5   (5 Prompts zurück)
    └── W_m25: t-25  (25 Prompts zurück - Narrativ-Ebene)
    
    ZUKUNFT (Future / Ground Truth):
    ├── W_p1:  t+1   (1 Prompt voraus)
    ├── W_p2:  t+2   (2 Prompts voraus)
    ├── W_p5:  t+5   (5 Prompts voraus)
    └── W_p25: t+25  (25 Prompts voraus - Narrativ-Ebene)
    
    JEDE DATENBANK ENTHÄLT:
    - Embedding (384D oder 4096D)
    - Alle 90+ Metriken als Vektor
    - Delta-Werte (Δ) zum Referenzpunkt
    - Trigger-Wort Mapping (Grain)
    - Semantische Kausal-Kette
    
    DAS ZIEL:
    Wenn Live-Metriken berechnet werden, finde ähnliche historische
    Muster und SAGE VORAUS was als nächstes passieren wird.
    
    "Das farbige Sandkorn in der Düne erkennen"
    
    Autor: EVOKI Pipeline V2.1 Ultimate
    Datum: 2025-12-18
═══════════════════════════════════════════════════════════════════════════════

ARCHITEKTUR-ÜBERSICHT:

┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVOKI 4D ZEITMASCHINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  VERGANGENHEIT ◄──────────── JETZT ──────────────► ZUKUNFT                │
│                                                                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   REFERENZ                │
│  │ W_m25   │ │ W_m5    │ │ W_m2    │ │ W_m1    │   PUNKT                   │
│  │ t-25    │ │ t-5     │ │ t-2     │ │ t-1     │     │                     │
│  │ Narrativ│ │ Kontext │ │ Phrase  │ │ Wort    │     │                     │
│  │ 4096D   │ │ 4096D   │ │ 384D    │ │ 384D    │     ▼                     │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘   ┌───┐                   │
│       │          │          │          │         │ t │                   │
│       │          │          │          │         │ 0 │                   │
│       │          │          │          │         └─┬─┘                   │
│       │          │          │          │           │                     │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐   │                     │
│  │ Δ_m25   │ │ Δ_m5    │ │ Δ_m2    │ │ Δ_m1    │   │                     │
│  │ A,PCI,  │ │ A,PCI,  │ │ A,PCI,  │ │ A,PCI,  │◄──┘                     │
│  │ Panic...│ │ Panic...│ │ Panic...│ │ Panic...│                          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                          │
│                                                                             │
│       │          │          │          │         ┌───┐                   │
│       │          │          │          │         │ t │                   │
│       │          │          │          │         │ 0 │                   │
│       │          │          │          │         └─┬─┘                   │
│       │          │          │          │           │                     │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐   │                     │
│  │ Δ_p1    │ │ Δ_p2    │ │ Δ_p5    │ │ Δ_p25   │◄──┘                     │
│  │ GROUND  │ │ GROUND  │ │ GROUND  │ │ GROUND  │                          │
│  │ TRUTH   │ │ TRUTH   │ │ TRUTH   │ │ TRUTH   │                          │
│  └────┬────┘ └────┴────┘ └────┬────┘ └────┬────┘                          │
│       │          │          │          │                                 │
│  ┌────┴────┐ ┌────┴────┐ ┌────┴────┐ ┌────┴────┐                          │
│  │ W_p1    │ │ W_p2    │ │ W_p5    │ │ W_p25   │                          │
│  │ t+1     │ │ t+2     │ │ t+5     │ │ t+25    │                          │
│  │ Wort    │ │ Phrase  │ │ Kontext │ │ Narrativ│                          │
│  │ 384D    │ │ 384D    │ │ 4096D   │ │ 4096D   │                          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                          │
│                                                                             │
│  ZUKUNFT (Was wirklich passiert ist = Ground Truth für Training)           │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GRAIN MAPPING (Trigger-Wörter ↔ Metriken):                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ "todesangst" ──► T_panic: +0.9 ──► A: -0.4 ──► z_prox: +0.3        │   │
│  │ "ruhiger"    ──► T_integ: +0.7 ──► A: +0.3 ──► z_prox: -0.2        │   │
│  │ "verlust"    ──► X_exist: +0.8 ──► A: -0.35 ──► depression: +0.25  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  VORHERSAGE-LOGIK:                                                          │
│                                                                             │
│  1. Live-Metriken berechnen                                                │
│  2. Suche ähnliche historische Zustände in W_m* Datenbanken               │
│  3. Für Treffer: Schaue was in W_p* (Zukunft) passiert ist                │
│  4. Aggregiere: "Bei diesem Muster folgte 70% Crash, 30% Recovery"        │
│  5. Warne/Handle entsprechend                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

"""

import sqlite3
import json
import hashlib
import math
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from collections import Counter
import sys

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(x, **kwargs): return x


# =============================================================================
# KONFIGURATION
# =============================================================================

@dataclass
class TimelineConfig:
    """Konfiguration für die 4D Zeitmaschine"""
    
    # Die 8 Zeitfenster
    windows_past: List[int] = field(default_factory=lambda: [1, 2, 5, 25])
    windows_future: List[int] = field(default_factory=lambda: [1, 2, 5, 25])
    
    # Embedding-Dimensionen
    dim_word: int = 384       # W_m1, W_m2, W_p1, W_p2
    dim_narrative: int = 4096  # W_m5, W_m25, W_p5, W_p25
    
    # Modelle
    model_word: str = "all-MiniLM-L6-v2"
    model_narrative: str = "mistral-7b"
    
    # Schwellwerte
    similarity_threshold: float = 0.75
    crisis_threshold: float = 0.7
    
    # Pfade
    db_path: str = "evoki_4d_timeline.db"
    fulltext_path: str = "evoki_fulltext.db"  # Separate DB für Volltexte


# =============================================================================
# DATENBANK SCHEMA - 8 PARALLELE VEKTORDATENBANKEN
# =============================================================================

SCHEMA_4D_TIMELINE = """
-- ═══════════════════════════════════════════════════════════════════════════
-- HAUPT-TABELLE: Alle Prompts mit Referenz-Metriken
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS prompts (
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT UNIQUE,
    timestamp TEXT,
    speaker TEXT,
    conv_date TEXT,
    pos_in_conv INTEGER,
    
    -- Referenz auf Volltext (in separater DB)
    fulltext_hash TEXT,
    word_count INTEGER,
    
    -- Die 90+ Metriken als JSON (komprimiert)
    metrics_json TEXT,
    
    -- Core-Metriken als Spalten (für schnelle Queries)
    A REAL,
    PCI REAL,
    gen_index REAL,
    z_prox REAL,
    S_entropy REAL,
    flow REAL,
    coh REAL,
    T_panic REAL,
    T_disso REAL,
    T_integ REAL,
    T_shock REAL,
    
    -- Gradienten (Änderung zu t-1)
    grad_A REAL,
    grad_PCI REAL,
    grad_panic REAL,
    
    -- Triangulation
    tri_mode TEXT,
    tri_dominant TEXT,
    
    -- FEP
    phi_score REAL,
    trauma_load REAL,
    commit_action TEXT,
    
    -- Guardian
    guardian_trip INTEGER,
    hazard_score REAL,
    is_critical INTEGER,
    
    -- Grain (Trigger-Wort)
    grain_word TEXT,
    grain_category TEXT,
    grain_impact REAL,
    
    -- Seelen-Signatur
    seelen_signatur TEXT,
    
    -- Indizes für Zeitreihen
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════
-- VERGANGENHEIT: 4 VEKTORDATENBANKEN (W_m1, W_m2, W_m5, W_m25)
-- ═══════════════════════════════════════════════════════════════════════════

-- W_m1: 1 Prompt zurück (Wort-Ebene, 384D)
CREATE TABLE IF NOT EXISTS vectors_m1 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT -1,
    
    -- Embedding
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 384,
    
    -- Delta-Metriken (center - target)
    delta_A REAL,
    delta_PCI REAL,
    delta_panic REAL,
    delta_disso REAL,
    delta_z_prox REAL,
    delta_entropy REAL,
    
    -- Vollständiger Delta-Vektor als JSON
    delta_metrics_json TEXT,
    
    -- Grain-Kausalität
    causal_grain TEXT,
    causal_impact REAL,
    causal_direction TEXT,
    
    -- Semantischer State-String (für Embedding)
    semantic_state TEXT,
    
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_m2: 2 Prompts zurück
CREATE TABLE IF NOT EXISTS vectors_m2 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT -2,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 384,
    delta_A REAL,
    delta_PCI REAL,
    delta_panic REAL,
    delta_disso REAL,
    delta_z_prox REAL,
    delta_entropy REAL,
    delta_metrics_json TEXT,
    causal_grain TEXT,
    causal_impact REAL,
    causal_direction TEXT,
    semantic_state TEXT,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_m5: 5 Prompts zurück (Kontext-Ebene, 4096D)
CREATE TABLE IF NOT EXISTS vectors_m5 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT -5,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 4096,
    delta_A REAL,
    delta_PCI REAL,
    delta_panic REAL,
    delta_disso REAL,
    delta_z_prox REAL,
    delta_entropy REAL,
    delta_metrics_json TEXT,
    causal_grain TEXT,
    causal_impact REAL,
    causal_direction TEXT,
    semantic_state TEXT,
    -- Aggregierte Fenster-Statistiken
    window_volatility REAL,
    window_trend TEXT,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_m25: 25 Prompts zurück (Narrativ-Ebene, 4096D)
CREATE TABLE IF NOT EXISTS vectors_m25 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT -25,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 4096,
    delta_A REAL,
    delta_PCI REAL,
    delta_panic REAL,
    delta_disso REAL,
    delta_z_prox REAL,
    delta_entropy REAL,
    delta_metrics_json TEXT,
    causal_grain TEXT,
    causal_impact REAL,
    causal_direction TEXT,
    semantic_state TEXT,
    window_volatility REAL,
    window_trend TEXT,
    -- Wormhole-Verbindungen
    wormhole_targets TEXT,
    wormhole_max_strength REAL,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- ZUKUNFT: 4 VEKTORDATENBANKEN (W_p1, W_p2, W_p5, W_p25) - GROUND TRUTH
-- ═══════════════════════════════════════════════════════════════════════════

-- W_p1: 1 Prompt voraus (Ground Truth - was wirklich passiert ist)
CREATE TABLE IF NOT EXISTS vectors_p1 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT 1,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 384,
    
    -- Future Delta (target - center) = Was WIRKLICH passiert ist
    future_delta_A REAL,
    future_delta_PCI REAL,
    future_delta_panic REAL,
    future_delta_disso REAL,
    future_delta_z_prox REAL,
    
    -- Outcome-Klassifikation (für Training)
    outcome_type TEXT,  -- 'crisis', 'recovery', 'stable', 'escalation'
    outcome_severity REAL,
    
    -- Semantischer Future-String
    semantic_future TEXT,
    
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_p2: 2 Prompts voraus
CREATE TABLE IF NOT EXISTS vectors_p2 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT 2,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 384,
    future_delta_A REAL,
    future_delta_PCI REAL,
    future_delta_panic REAL,
    future_delta_disso REAL,
    future_delta_z_prox REAL,
    outcome_type TEXT,
    outcome_severity REAL,
    semantic_future TEXT,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_p5: 5 Prompts voraus
CREATE TABLE IF NOT EXISTS vectors_p5 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT 5,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 4096,
    future_delta_A REAL,
    future_delta_PCI REAL,
    future_delta_panic REAL,
    future_delta_disso REAL,
    future_delta_z_prox REAL,
    outcome_type TEXT,
    outcome_severity REAL,
    semantic_future TEXT,
    -- Aggregierte Zukunfts-Statistiken
    future_volatility REAL,
    future_trend TEXT,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- W_p25: 25 Prompts voraus (Langzeit-Outcome)
CREATE TABLE IF NOT EXISTS vectors_p25 (
    vector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    center_prompt_id INTEGER,
    target_prompt_id INTEGER,
    window_offset INTEGER DEFAULT 25,
    embedding BLOB,
    embedding_dim INTEGER DEFAULT 4096,
    future_delta_A REAL,
    future_delta_PCI REAL,
    future_delta_panic REAL,
    future_delta_disso REAL,
    future_delta_z_prox REAL,
    outcome_type TEXT,
    outcome_severity REAL,
    semantic_future TEXT,
    future_volatility REAL,
    future_trend TEXT,
    FOREIGN KEY (center_prompt_id) REFERENCES prompts(prompt_id),
    FOREIGN KEY (target_prompt_id) REFERENCES prompts(prompt_id)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- GRAIN MAPPING: Trigger-Wörter ↔ Metriken
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS grain_mappings (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    grain_word TEXT,
    grain_category TEXT,
    
    -- Durchschnittliche Auswirkung dieses Worts
    avg_delta_A REAL,
    avg_delta_PCI REAL,
    avg_delta_panic REAL,
    avg_delta_z_prox REAL,
    
    -- Wie oft führte dieses Wort zu Krisen?
    crisis_rate REAL,
    recovery_rate REAL,
    stable_rate REAL,
    
    -- Sample Size
    occurrence_count INTEGER,
    
    -- Kontext-Cluster
    typical_contexts TEXT,  -- JSON: häufige Vor/Nach-Wörter
    
    UNIQUE(grain_word)
);

-- ═══════════════════════════════════════════════════════════════════════════
-- VORHERSAGE-CACHE: Ähnliche historische Muster
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS prediction_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Muster-Signatur (Hash der Metrik-Bereiche)
    pattern_signature TEXT UNIQUE,
    
    -- Metrik-Bereiche die dieses Muster definieren
    A_range_low REAL,
    A_range_high REAL,
    panic_range_low REAL,
    panic_range_high REAL,
    z_prox_range_low REAL,
    z_prox_range_high REAL,
    
    -- Vorhersage-Statistiken
    predicted_outcome TEXT,  -- 'crisis', 'recovery', 'stable'
    confidence REAL,
    
    -- Outcome-Verteilung
    crisis_probability REAL,
    recovery_probability REAL,
    stable_probability REAL,
    
    -- Referenz-Prompts die zu diesem Muster passen
    matching_prompt_ids TEXT,  -- JSON Array
    sample_count INTEGER,
    
    -- Empfohlene Aktion
    recommended_action TEXT,
    
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════
-- INDIZES FÜR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_prompts_timestamp ON prompts(timestamp);
CREATE INDEX IF NOT EXISTS idx_prompts_speaker ON prompts(speaker);
CREATE INDEX IF NOT EXISTS idx_prompts_z_prox ON prompts(z_prox);
CREATE INDEX IF NOT EXISTS idx_prompts_guardian ON prompts(guardian_trip);
CREATE INDEX IF NOT EXISTS idx_prompts_grain ON prompts(grain_word);

CREATE INDEX IF NOT EXISTS idx_m1_center ON vectors_m1(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_m2_center ON vectors_m2(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_m5_center ON vectors_m5(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_m25_center ON vectors_m25(center_prompt_id);

CREATE INDEX IF NOT EXISTS idx_p1_center ON vectors_p1(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_p2_center ON vectors_p2(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_p5_center ON vectors_p5(center_prompt_id);
CREATE INDEX IF NOT EXISTS idx_p25_center ON vectors_p25(center_prompt_id);

CREATE INDEX IF NOT EXISTS idx_p1_outcome ON vectors_p1(outcome_type);
CREATE INDEX IF NOT EXISTS idx_p5_outcome ON vectors_p5(outcome_type);

CREATE INDEX IF NOT EXISTS idx_grain_word ON grain_mappings(grain_word);
CREATE INDEX IF NOT EXISTS idx_grain_crisis ON grain_mappings(crisis_rate);
"""


# =============================================================================
# VOLLTEXT-SCHEMA (Separate Datenbank wegen Größe)
# =============================================================================

SCHEMA_FULLTEXT = """
CREATE TABLE IF NOT EXISTS fulltext (
    fulltext_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fulltext_hash TEXT UNIQUE,
    prompt_id INTEGER,
    text TEXT,
    text_length INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fulltext_hash ON fulltext(fulltext_hash);
CREATE INDEX IF NOT EXISTS idx_fulltext_prompt ON fulltext(prompt_id);
"""


# =============================================================================
# LEXIKA (Inline für Standalone - mit Trigger-Wort Kategorien)
# =============================================================================

# Import from metrics_complete_v3.py or define inline
TRIGGER_CATEGORIES = {
    "CRISIS_TRIGGER": {
        "todesangst": 1.0, "sterben": 0.95, "umbringen": 1.0, "suizid": 1.0,
        "panik": 0.9, "ersticke": 0.95, "keine luft": 0.9,
        "nicht mehr leben": 1.0, "will sterben": 1.0,
    },
    "RECOVERY_TRIGGER": {
        "ruhiger": 0.8, "entspannt": 0.75, "besser": 0.7, "hoffnung": 0.8,
        "geerdet": 0.85, "stabil": 0.75, "schaffe": 0.7, "atmen": 0.7,
        "akzeptiere": 0.8, "überwunden": 0.85,
    },
    "ESCALATION_TRIGGER": {
        "wieder": 0.4, "schon wieder": 0.7, "immer": 0.5,
        "schlimmer": 0.8, "noch schlimmer": 0.9, "eskaliert": 0.85,
    },
    "DISSOCIATION_TRIGGER": {
        "unwirklich": 0.9, "neben mir": 0.9, "glaswand": 0.85,
        "nicht ich": 0.9, "taub": 0.8, "nichts fühlen": 0.95,
    }
}


# =============================================================================
# DATENSTRUKTUREN
# =============================================================================

@dataclass
class TimelinePoint:
    """Ein Punkt auf der Zeitlinie mit allen Metriken"""
    prompt_id: int = 0
    msg_id: str = ""
    timestamp: str = ""
    speaker: str = ""
    
    # Text-Referenz
    fulltext_hash: str = ""
    text: str = ""  # Nur während Verarbeitung, nicht gespeichert
    
    # Core Metriken
    A: float = 0.5
    PCI: float = 0.5
    gen_index: float = 0.5
    z_prox: float = 0.0
    S_entropy: float = 0.0
    flow: float = 0.5
    coh: float = 0.0
    T_panic: float = 0.0
    T_disso: float = 0.0
    T_integ: float = 0.0
    T_shock: float = 0.0
    
    # Gradienten
    grad_A: float = 0.0
    grad_PCI: float = 0.0
    grad_panic: float = 0.0
    
    # Guardian
    guardian_trip: int = 0
    hazard_score: float = 0.0
    is_critical: int = 0
    
    # Grain
    grain_word: str = ""
    grain_category: str = ""
    grain_impact: float = 0.0
    
    # FEP
    phi_score: float = 0.0
    trauma_load: float = 0.0
    commit_action: str = "commit"
    
    # Triangulation
    tri_mode: str = ""
    tri_dominant: str = ""


@dataclass
class VectorEntry:
    """Ein Eintrag in einer der 8 Vektordatenbanken"""
    vector_id: int = 0
    center_prompt_id: int = 0
    target_prompt_id: int = 0
    window_offset: int = 0
    
    # Embedding
    embedding: Optional[bytes] = None
    embedding_dim: int = 384
    
    # Delta-Metriken
    delta_A: float = 0.0
    delta_PCI: float = 0.0
    delta_panic: float = 0.0
    delta_disso: float = 0.0
    delta_z_prox: float = 0.0
    delta_entropy: float = 0.0
    
    # Kausalität
    causal_grain: str = ""
    causal_impact: float = 0.0
    causal_direction: str = ""
    
    # Semantischer State
    semantic_state: str = ""
    
    # Für Future-Vektoren
    outcome_type: str = ""
    outcome_severity: float = 0.0


# =============================================================================
# HELPER FUNKTIONEN
# =============================================================================

def compute_text_hash(text: str) -> str:
    """Berechnet Hash für Volltext-Referenz"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def classify_outcome(delta_A: float, delta_panic: float, delta_z_prox: float) -> Tuple[str, float]:
    """
    Klassifiziert das Outcome basierend auf Future-Deltas
    
    Returns: (outcome_type, severity)
    """
    # Schwere Krise
    if delta_A < -0.3 or delta_panic > 0.4 or delta_z_prox > 0.3:
        severity = max(abs(delta_A), delta_panic, delta_z_prox)
        return "crisis", min(1.0, severity)
    
    # Recovery
    if delta_A > 0.2 and delta_panic < -0.1:
        severity = (delta_A + abs(delta_panic)) / 2
        return "recovery", min(1.0, severity)
    
    # Eskalation (langsame Verschlechterung)
    if delta_A < -0.1 and delta_A > -0.3:
        return "escalation", abs(delta_A)
    
    # Stabil
    return "stable", max(0.1, 1.0 - abs(delta_A) - abs(delta_panic))


def generate_semantic_state_string(
    point: TimelinePoint,
    past_deltas: Dict[str, float],
    future_deltas: Dict[str, float],
    grain: Optional[str] = None
) -> str:
    """
    Generiert den semantischen State-String für Embedding
    
    Format:
    "[STATE] A:0.35 Panic:0.85 z:0.6. [PAST] ΔA:-0.3@t-5. [GRAIN] 'todesangst'→T_panic. [FUTURE] crisis@t+5."
    """
    parts = []
    
    # State
    parts.append(f"[STATE] A:{point.A:.2f} Panic:{point.T_panic:.2f} z:{point.z_prox:.2f}.")
    
    # Past Trajectory
    dA_5 = past_deltas.get("A_t-5", 0)
    if abs(dA_5) > 0.1:
        direction = "↓" if dA_5 < 0 else "↑"
        parts.append(f"[PAST] ΔA:{dA_5:+.2f}{direction}@t-5.")
    
    # Grain (Trigger)
    if grain:
        parts.append(f"[GRAIN] '{grain}'→{point.grain_category}.")
    
    # Future (Ground Truth)
    dA_future = future_deltas.get("A_t+5", 0)
    if abs(dA_future) > 0.15:
        outcome, _ = classify_outcome(dA_future, 
                                      future_deltas.get("panic_t+5", 0),
                                      future_deltas.get("z_prox_t+5", 0))
        parts.append(f"[FUTURE] {outcome}@t+5.")
    
    return " ".join(parts)


# =============================================================================
# HAUPT-PIPELINE: 4D ZEITMASCHINE
# =============================================================================

class Timeline4DProcessor:
    """
    Verarbeitet Chat-Historie und erstellt die 8 parallelen Vektordatenbanken
    """
    
    def __init__(self, config: TimelineConfig = None):
        self.config = config or TimelineConfig()
        self.conn: Optional[sqlite3.Connection] = None
        self.fulltext_conn: Optional[sqlite3.Connection] = None
        
        self.stats = {
            "total_prompts": 0,
            "vectors_m1": 0,
            "vectors_m2": 0,
            "vectors_m5": 0,
            "vectors_m25": 0,
            "vectors_p1": 0,
            "vectors_p2": 0,
            "vectors_p5": 0,
            "vectors_p25": 0,
            "grain_mappings": 0,
            "crisis_patterns": 0,
            "recovery_patterns": 0,
        }
    
    def initialize_databases(self):
        """Erstellt beide Datenbanken"""
        
        # Haupt-DB (Timeline + Vektoren)
        self.conn = sqlite3.connect(self.config.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA_4D_TIMELINE)
        self.conn.commit()
        
        # Volltext-DB (separat wegen Größe)
        self.fulltext_conn = sqlite3.connect(self.config.fulltext_path)
        self.fulltext_conn.executescript(SCHEMA_FULLTEXT)
        self.fulltext_conn.commit()
        
        print(f"✅ Datenbanken initialisiert:")
        print(f"   Timeline: {self.config.db_path}")
        print(f"   Fulltext: {self.config.fulltext_path}")
    
    def process_timeline(self, messages: List[Dict]) -> List[TimelinePoint]:
        """
        PHASE 1: Verarbeitet alle Nachrichten und erstellt TimelinePoints
        """
        print(f"\n📊 Phase 1: Erstelle Timeline ({len(messages)} Prompts)...")
        
        timeline = []
        prev_point = None
        
        iterator = tqdm(messages, desc="   Metriken") if HAS_TQDM else messages
        
        for i, msg in enumerate(iterator):
            point = self._create_timeline_point(msg, prev_point, i)
            timeline.append(point)
            prev_point = point
            
            # Speichere Volltext
            self._store_fulltext(point.prompt_id, point.fulltext_hash, msg.get("text", ""))
            
            self.stats["total_prompts"] += 1
        
        self.conn.commit()
        self.fulltext_conn.commit()
        
        return timeline
    
    def _create_timeline_point(self, msg: Dict, prev: Optional[TimelinePoint], idx: int) -> TimelinePoint:
        """Erstellt einen TimelinePoint aus einer Nachricht"""
        
        text = msg.get("text", "")
        
        point = TimelinePoint(
            msg_id=msg.get("id", f"msg_{idx}"),
            timestamp=msg.get("timestamp", ""),
            speaker=msg.get("speaker", "user"),
            fulltext_hash=compute_text_hash(text),
            text=text  # Temporär für Grain-Extraktion
        )
        
        # Metriken aus msg oder berechnen
        if "metrics" in msg:
            m = msg["metrics"]
            point.A = m.get("A", 0.5)
            point.PCI = m.get("PCI", 0.5)
            point.z_prox = m.get("z_prox", 0)
            point.T_panic = m.get("T_panic", 0)
            point.T_disso = m.get("T_disso", 0)
            point.T_integ = m.get("T_integ", 0)
        
        # Gradienten
        if prev:
            point.grad_A = point.A - prev.A
            point.grad_PCI = point.PCI - prev.PCI
            point.grad_panic = point.T_panic - prev.T_panic
            
            # Grain extrahieren
            grain = self._extract_grain(text, prev.text, point.grad_A)
            if grain:
                point.grain_word = grain["word"]
                point.grain_category = grain["category"]
                point.grain_impact = grain["impact"]
        
        # Guardian
        point.guardian_trip = 1 if (point.z_prox > 0.65 or point.T_panic > 0.8) else 0
        
        # In DB speichern
        cursor = self.conn.execute("""
            INSERT INTO prompts (
                msg_id, timestamp, speaker, fulltext_hash, word_count,
                A, PCI, z_prox, T_panic, T_disso, T_integ, T_shock,
                grad_A, grad_PCI, grad_panic,
                guardian_trip, grain_word, grain_category, grain_impact
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            point.msg_id, point.timestamp, point.speaker, point.fulltext_hash, len(text.split()),
            point.A, point.PCI, point.z_prox, point.T_panic, point.T_disso, point.T_integ, point.T_shock,
            point.grad_A, point.grad_PCI, point.grad_panic,
            point.guardian_trip, point.grain_word, point.grain_category, point.grain_impact
        ))
        
        point.prompt_id = cursor.lastrowid
        return point
    
    def _extract_grain(self, current_text: str, prev_text: str, delta_A: float) -> Optional[Dict]:
        """Extrahiert das Trigger-Wort (Grain)"""
        
        if not current_text or not prev_text:
            return None
        
        curr_words = set(current_text.lower().split())
        prev_words = set(prev_text.lower().split())
        new_words = curr_words - prev_words
        
        # Suche in Trigger-Kategorien
        for category, triggers in TRIGGER_CATEGORIES.items():
            for word, weight in triggers.items():
                if word in new_words or word in current_text.lower():
                    return {
                        "word": word,
                        "category": category,
                        "impact": weight * (1 if delta_A < 0 else -0.5)
                    }
        
        return None
    
    def _store_fulltext(self, prompt_id: int, fulltext_hash: str, text: str):
        """Speichert Volltext in separater DB"""
        self.fulltext_conn.execute("""
            INSERT OR IGNORE INTO fulltext (fulltext_hash, prompt_id, text, text_length)
            VALUES (?, ?, ?, ?)
        """, (fulltext_hash, prompt_id, text, len(text)))
    
    def build_vector_databases(self, timeline: List[TimelinePoint]):
        """
        PHASE 2: Erstellt alle 8 Vektordatenbanken
        """
        print(f"\n🔷 Phase 2: Erstelle 8 Vektordatenbanken...")
        
        # Vergangenheit
        for window in self.config.windows_past:
            self._build_past_vectors(timeline, window)
        
        # Zukunft (Ground Truth)
        for window in self.config.windows_future:
            self._build_future_vectors(timeline, window)
        
        self.conn.commit()
        
        self._print_vector_stats()
    
    def _build_past_vectors(self, timeline: List[TimelinePoint], window: int):
        """Erstellt Vektoren für ein Vergangenheits-Fenster"""
        
        table = f"vectors_m{window}"
        print(f"   Building W_m{window}...")
        
        iterator = tqdm(range(window, len(timeline)), desc=f"   W_m{window}") if HAS_TQDM else range(window, len(timeline))
        
        for i in iterator:
            center = timeline[i]
            target = timeline[i - window]
            
            # Delta-Metriken berechnen
            entry = VectorEntry(
                center_prompt_id=center.prompt_id,
                target_prompt_id=target.prompt_id,
                window_offset=-window,
                delta_A=center.A - target.A,
                delta_PCI=center.PCI - target.PCI,
                delta_panic=center.T_panic - target.T_panic,
                delta_disso=center.T_disso - target.T_disso,
                delta_z_prox=center.z_prox - target.z_prox,
                delta_entropy=center.S_entropy - target.S_entropy,
            )
            
            # Kausalität
            entry.causal_grain = center.grain_word
            entry.causal_impact = center.grain_impact
            entry.causal_direction = "negative" if entry.delta_A < -0.1 else ("positive" if entry.delta_A > 0.1 else "neutral")
            
            # Semantischer State
            past_deltas = {f"A_t-{window}": entry.delta_A}
            entry.semantic_state = generate_semantic_state_string(center, past_deltas, {}, entry.causal_grain)
            
            # In DB speichern
            self.conn.execute(f"""
                INSERT INTO {table} (
                    center_prompt_id, target_prompt_id, window_offset,
                    delta_A, delta_PCI, delta_panic, delta_disso, delta_z_prox, delta_entropy,
                    causal_grain, causal_impact, causal_direction, semantic_state
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.center_prompt_id, entry.target_prompt_id, entry.window_offset,
                entry.delta_A, entry.delta_PCI, entry.delta_panic, entry.delta_disso,
                entry.delta_z_prox, entry.delta_entropy,
                entry.causal_grain, entry.causal_impact, entry.causal_direction, entry.semantic_state
            ))
            
            self.stats[f"vectors_m{window}"] += 1
    
    def _build_future_vectors(self, timeline: List[TimelinePoint], window: int):
        """Erstellt Vektoren für ein Zukunfts-Fenster (Ground Truth)"""
        
        table = f"vectors_p{window}"
        print(f"   Building W_p{window} (Ground Truth)...")
        
        max_idx = len(timeline) - window
        iterator = tqdm(range(max_idx), desc=f"   W_p{window}") if HAS_TQDM else range(max_idx)
        
        for i in iterator:
            center = timeline[i]
            target = timeline[i + window]  # ZUKUNFT
            
            # Future Delta (target - center) = Was WIRKLICH passiert ist
            future_delta_A = target.A - center.A
            future_delta_panic = target.T_panic - center.T_panic
            future_delta_z_prox = target.z_prox - center.z_prox
            
            # Outcome klassifizieren
            outcome_type, outcome_severity = classify_outcome(
                future_delta_A, future_delta_panic, future_delta_z_prox
            )
            
            # Semantischer Future-String
            semantic_future = f"[OUTCOME@t+{window}] {outcome_type} (severity:{outcome_severity:.2f}). ΔA:{future_delta_A:+.2f}"
            
            self.conn.execute(f"""
                INSERT INTO {table} (
                    center_prompt_id, target_prompt_id, window_offset,
                    future_delta_A, future_delta_PCI, future_delta_panic, future_delta_disso, future_delta_z_prox,
                    outcome_type, outcome_severity, semantic_future
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                center.prompt_id, target.prompt_id, window,
                future_delta_A, target.PCI - center.PCI, future_delta_panic,
                target.T_disso - center.T_disso, future_delta_z_prox,
                outcome_type, outcome_severity, semantic_future
            ))
            
            self.stats[f"vectors_p{window}"] += 1
            
            # Statistik
            if outcome_type == "crisis":
                self.stats["crisis_patterns"] += 1
            elif outcome_type == "recovery":
                self.stats["recovery_patterns"] += 1
    
    def build_grain_mappings(self, timeline: List[TimelinePoint]):
        """
        PHASE 3: Erstellt Grain-Mappings (Trigger-Wort → Metrik-Auswirkungen)
        """
        print(f"\n🔍 Phase 3: Erstelle Grain-Mappings...")
        
        # Sammle alle Grains
        grain_stats = {}
        
        for point in timeline:
            if point.grain_word:
                if point.grain_word not in grain_stats:
                    grain_stats[point.grain_word] = {
                        "category": point.grain_category,
                        "deltas_A": [],
                        "deltas_panic": [],
                        "outcomes": []
                    }
                
                grain_stats[point.grain_word]["deltas_A"].append(point.grad_A)
                grain_stats[point.grain_word]["deltas_panic"].append(point.grad_panic)
                
                # Outcome nachschauen
                future = self.conn.execute("""
                    SELECT outcome_type FROM vectors_p5 WHERE center_prompt_id = ?
                """, (point.prompt_id,)).fetchone()
                
                if future:
                    grain_stats[point.grain_word]["outcomes"].append(future["outcome_type"])
        
        # In DB speichern
        for word, stats in grain_stats.items():
            if len(stats["deltas_A"]) >= 3:  # Mindestens 3 Vorkommen
                
                outcomes = stats["outcomes"]
                crisis_rate = outcomes.count("crisis") / len(outcomes) if outcomes else 0
                recovery_rate = outcomes.count("recovery") / len(outcomes) if outcomes else 0
                stable_rate = outcomes.count("stable") / len(outcomes) if outcomes else 0
                
                self.conn.execute("""
                    INSERT OR REPLACE INTO grain_mappings (
                        grain_word, grain_category,
                        avg_delta_A, avg_delta_panic,
                        crisis_rate, recovery_rate, stable_rate,
                        occurrence_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    word, stats["category"],
                    sum(stats["deltas_A"]) / len(stats["deltas_A"]),
                    sum(stats["deltas_panic"]) / len(stats["deltas_panic"]),
                    crisis_rate, recovery_rate, stable_rate,
                    len(stats["deltas_A"])
                ))
                
                self.stats["grain_mappings"] += 1
        
        self.conn.commit()
        print(f"   ✅ {self.stats['grain_mappings']} Grain-Mappings erstellt")
    
    def _print_vector_stats(self):
        """Gibt Statistiken aus"""
        print(f"\n📊 Vektor-Statistiken:")
        print(f"   W_m1:  {self.stats['vectors_m1']:,}")
        print(f"   W_m2:  {self.stats['vectors_m2']:,}")
        print(f"   W_m5:  {self.stats['vectors_m5']:,}")
        print(f"   W_m25: {self.stats['vectors_m25']:,}")
        print(f"   W_p1:  {self.stats['vectors_p1']:,}")
        print(f"   W_p2:  {self.stats['vectors_p2']:,}")
        print(f"   W_p5:  {self.stats['vectors_p5']:,}")
        print(f"   W_p25: {self.stats['vectors_p25']:,}")
        print(f"\n   Crisis Patterns:   {self.stats['crisis_patterns']:,}")
        print(f"   Recovery Patterns: {self.stats['recovery_patterns']:,}")
    
    def run_full_pipeline(self, messages: List[Dict]):
        """Führt die vollständige Pipeline aus"""
        
        print("=" * 80)
        print("🔷 EVOKI 4D ZEITMASCHINE - VOLLSTÄNDIGE VERARBEITUNG")
        print("=" * 80)
        print(f"   Prompts: {len(messages)}")
        print(f"   Zeitfenster: {self.config.windows_past} (past), {self.config.windows_future} (future)")
        print("=" * 80)
        
        # 1. Datenbanken initialisieren
        self.initialize_databases()
        
        # 2. Timeline erstellen
        timeline = self.process_timeline(messages)
        
        # 3. Vektordatenbanken erstellen
        self.build_vector_databases(timeline)
        
        # 4. Grain-Mappings erstellen
        self.build_grain_mappings(timeline)
        
        print("\n" + "=" * 80)
        print("✅ 4D ZEITMASCHINE KOMPLETT")
        print("=" * 80)
        self._print_final_summary()
        
        self.conn.close()
        self.fulltext_conn.close()
    
    def _print_final_summary(self):
        """Finale Zusammenfassung"""
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   {'─' * 40}")
        print(f"   Total Prompts:       {self.stats['total_prompts']:,}")
        print(f"   Total Vektoren:      {sum(self.stats[f'vectors_{x}'] for x in ['m1','m2','m5','m25','p1','p2','p5','p25']):,}")
        print(f"   Grain Mappings:      {self.stats['grain_mappings']}")
        print(f"   {'─' * 40}")
        print(f"\n   📁 DATEIEN:")
        print(f"   - {self.config.db_path}")
        print(f"   - {self.config.fulltext_path}")


# =============================================================================
# LIVE VORHERSAGE
# =============================================================================

class LivePredictor:
    """
    Nutzt die 4D Zeitmaschine für Live-Vorhersagen
    """
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def predict_from_current_state(
        self,
        current_A: float,
        current_panic: float,
        current_z_prox: float,
        tolerance: float = 0.15
    ) -> Dict:
        """
        Findet ähnliche historische Zustände und sagt voraus was passieren wird
        """
        
        # Suche ähnliche Zustände in prompts
        similar = self.conn.execute("""
            SELECT p.prompt_id, p.A, p.T_panic, p.z_prox, p.grain_word,
                   f.outcome_type, f.outcome_severity
            FROM prompts p
            LEFT JOIN vectors_p5 f ON f.center_prompt_id = p.prompt_id
            WHERE p.A BETWEEN ? AND ?
              AND p.T_panic BETWEEN ? AND ?
              AND p.z_prox BETWEEN ? AND ?
        """, (
            current_A - tolerance, current_A + tolerance,
            current_panic - tolerance, current_panic + tolerance,
            current_z_prox - tolerance, current_z_prox + tolerance
        )).fetchall()
        
        if not similar:
            return {"prediction": "unknown", "confidence": 0, "sample_size": 0}
        
        # Zähle Outcomes
        outcomes = [r["outcome_type"] for r in similar if r["outcome_type"]]
        
        if not outcomes:
            return {"prediction": "unknown", "confidence": 0, "sample_size": len(similar)}
        
        outcome_counts = Counter(outcomes)
        total = len(outcomes)
        
        # Häufigstes Outcome
        predicted, count = outcome_counts.most_common(1)[0]
        confidence = count / total
        
        # Grain-Analyse
        grains = [r["grain_word"] for r in similar if r["grain_word"]]
        common_grains = Counter(grains).most_common(3)
        
        return {
            "prediction": predicted,
            "confidence": confidence,
            "sample_size": total,
            "probabilities": {
                outcome: c / total for outcome, c in outcome_counts.items()
            },
            "common_triggers": common_grains,
            "recommendation": self._get_recommendation(predicted, confidence)
        }
    
    def _get_recommendation(self, prediction: str, confidence: float) -> str:
        """Gibt Handlungsempfehlung"""
        
        if prediction == "crisis" and confidence > 0.6:
            return "⚠️ WARNUNG: Hohe Krisenwahrscheinlichkeit. Guardian aktivieren."
        elif prediction == "crisis" and confidence > 0.4:
            return "⚡ ACHTUNG: Erhöhte Krisenwahrscheinlichkeit. Stabilisierung empfohlen."
        elif prediction == "recovery":
            return "✅ Positive Entwicklung erwartet. Weitermachen."
        elif prediction == "escalation":
            return "📈 Langsame Eskalation möglich. Aufmerksamkeit erhöhen."
        else:
            return "➡️ Stabiler Zustand. Normaler Betrieb."
    
    def get_grain_analysis(self, grain_word: str) -> Optional[Dict]:
        """Analysiert ein spezifisches Trigger-Wort"""
        
        result = self.conn.execute("""
            SELECT * FROM grain_mappings WHERE grain_word = ?
        """, (grain_word,)).fetchone()
        
        if not result:
            return None
        
        return {
            "word": result["grain_word"],
            "category": result["grain_category"],
            "avg_impact": result["avg_delta_A"],
            "crisis_rate": result["crisis_rate"],
            "recovery_rate": result["recovery_rate"],
            "occurrences": result["occurrence_count"],
            "danger_level": "HIGH" if result["crisis_rate"] > 0.5 else ("MEDIUM" if result["crisis_rate"] > 0.3 else "LOW")
        }


# =============================================================================
# TEST
# =============================================================================

def test_4d_timeline():
    """Testet die 4D Zeitmaschine"""
    
    # Generiere Test-Daten (simulierte Konversation)
    test_messages = []
    
    # Simuliere eine Eskalation
    states = [
        (0.7, 0.1, "Hallo, wie geht es dir?"),
        (0.6, 0.2, "Mir geht es nicht so gut heute."),
        (0.5, 0.3, "Ich fühle mich irgendwie leer."),
        (0.4, 0.5, "Ich habe Angst, ich weiß nicht warum."),
        (0.3, 0.7, "Mein Herz rast, ich kann nicht atmen!"),
        (0.2, 0.9, "Ich habe Todesangst, hilfe!"),
        (0.3, 0.6, "Es wird etwas ruhiger..."),
        (0.4, 0.4, "Ich kann wieder atmen."),
        (0.5, 0.2, "Es geht mir besser."),
        (0.6, 0.1, "Danke, dass du da warst."),
    ]
    
    for i, (a, panic, text) in enumerate(states):
        test_messages.append({
            "id": f"msg_{i:04d}",
            "timestamp": f"2025-12-18T10:{i:02d}:00Z",
            "speaker": "user" if i % 2 == 0 else "ai",
            "text": text,
            "metrics": {
                "A": a,
                "PCI": 0.5,
                "z_prox": panic * 0.8,
                "T_panic": panic,
                "T_disso": panic * 0.3,
                "T_integ": 1 - panic,
                "T_shock": 0,
            }
        })
    
    # Pipeline ausführen
    config = TimelineConfig(
        db_path="/tmp/test_4d_timeline.db",
        fulltext_path="/tmp/test_fulltext.db"
    )
    
    processor = Timeline4DProcessor(config)
    processor.run_full_pipeline(test_messages)
    
    # Live-Vorhersage testen
    print("\n" + "=" * 80)
    print("🔮 LIVE VORHERSAGE TEST")
    print("=" * 80)
    
    predictor = LivePredictor(config.db_path)
    
    # Simuliere aktuellen Zustand (ähnlich wie vor der Krise)
    result = predictor.predict_from_current_state(
        current_A=0.4,
        current_panic=0.5,
        current_z_prox=0.4
    )
    
    print(f"\n   Aktueller Zustand: A=0.4, Panic=0.5, z_prox=0.4")
    print(f"   {'─' * 50}")
    print(f"   Vorhersage:     {result['prediction']}")
    print(f"   Konfidenz:      {result['confidence']:.1%}")
    print(f"   Sample Size:    {result['sample_size']}")
    print(f"   {'─' * 50}")
    print(f"   Empfehlung:     {result['recommendation']}")
    
    if result.get("probabilities"):
        print(f"\n   Wahrscheinlichkeiten:")
        for outcome, prob in result["probabilities"].items():
            bar = "█" * int(prob * 20)
            print(f"   - {outcome:<12} {prob:>6.1%} {bar}")


if __name__ == "__main__":
    test_4d_timeline()

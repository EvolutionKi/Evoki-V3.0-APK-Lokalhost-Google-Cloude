#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
              EVOKI CHUNK VEKTORISIERUNG + METRIKEN PIPELINE
              ================================================
              
    Verarbeitet ALLE Paare aus der DB mit:
    
    1. CHUNK-VEKTORISIERUNG (8 Kontextfenster):
       - ctx_m1, ctx_m2, ctx_m5, ctx_m25  (Vergangenheit)
       - ctx_p1, ctx_p2, ctx_p5, ctx_p25  (Zukunft)
       
    2. METRIKEN-BERECHNUNG pro Paar:
       - Å (Ångström/Tiefe)
       - A (Kohärenz)
       - B (Empathie)
       - F-Risk
       - Triangulation (z_prox, mode, dominant)
       - STT-Score
       
    3. OUTPUT:
       - SQLite DB mit allen Ergebnissen
       - JSON Export
       - Statistiken + Visualisierung
       
    Verwendung:
        python chunk_vectorize_full.py --db evoki_v2_ultimate_FULL.db --output results/
        
    Autor: EVOKI Pipeline V2.1
    Datum: 2025-12-18
═══════════════════════════════════════════════════════════════════════════════
"""

import sqlite3
import json
import argparse
import time
import math
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import sys

# Versuche numpy/torch zu laden
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️ NumPy nicht gefunden - Embedding-Features deaktiviert")

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(x, **kwargs): return x

# Versuche sentence-transformers zu laden
try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    HAS_SBERT = False
    print("⚠️ sentence-transformers nicht gefunden - Embeddings deaktiviert")


# =============================================================================
# KONFIGURATION
# =============================================================================

@dataclass
class Config:
    """Pipeline-Konfiguration"""
    # Embedding
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    batch_size: int = 64
    use_gpu: bool = True
    
    # Kontextfenster
    window_sizes: List[int] = field(default_factory=lambda: [1, 2, 5, 25])
    
    # Metriken
    tau_flow: float = 1800.0  # 30 Minuten Flow-Zerfall
    
    # Output
    output_dir: str = "results"
    db_name: str = "evoki_chunks_metrics.db"


CFG = Config()


# =============================================================================
# LEXIKA (Inline für Standalone-Nutzung)
# =============================================================================

S_SELF = {
    "ich": 0.8, "mich": 0.75, "mir": 0.75, "mein": 0.7, "meine": 0.7,
    "ich selbst": 1.0, "ich fühle": 0.85, "ich denke": 0.8,
    "mein bauch": 0.7, "mein herz": 0.75, "mein kopf": 0.7,
}

X_EXIST = {
    "leer": 0.9, "leere": 0.9, "sinnlos": 0.9, "wertlos": 1.0,
    "verloren": 0.85, "verzweiflung": 0.95, "hoffnungslos": 0.9,
    "existenz": 0.8, "leben": 0.6, "tod": 1.0, "sterben": 1.0,
}

T_PANIC = {
    "angst": 0.9, "panik": 1.0, "panikattacke": 1.0, "herzrasen": 0.9,
    "atemnot": 1.0, "zittern": 0.7, "weinen": 0.85, "tränen": 0.8,
    "bauchschmerzen": 0.8, "sodbrennen": 0.75, "übelkeit": 0.7,
    "kann nicht atmen": 1.0, "sterbe": 0.95, "hilfe": 0.7,
}

T_DISSO = {
    "unwirklich": 0.9, "neben mir": 0.9, "glaswand": 0.85, "nebel": 0.8,
    "weit weg": 0.8, "nicht real": 0.9, "fremd": 0.7, "taub": 0.8,
    "nichts fühlen": 1.0, "abgetrennt": 0.9, "blackout": 1.0,
    "zeitloch": 0.95, "wie im film": 0.8, "roboter": 0.8,
}

T_INTEG = {
    "verstehe": 0.7, "akzeptiere": 0.8, "annehmen": 0.75,
    "atmen": 0.65, "boden": 0.7, "geerdet": 0.85, "stabil": 0.7,
    "halten": 0.65, "schaffe": 0.7, "vertrauen": 0.8,
    "ruhiger": 0.7, "besser": 0.6, "hoffnung": 0.75,
}

B_EMPATHY = {
    "verstehe dich": 1.0, "fühle mit": 1.0, "für dich da": 1.0,
    "ich halte dich": 0.9, "zusammen": 0.7, "gemeinsam": 0.7,
    "vertrauen": 0.8, "sicher": 0.7, "geborgen": 0.85,
    "mein adler": 0.95, "tempel": 0.8, "deal": 0.8,
}

LAMBDA_DEPTH = {
    "warum": 0.8, "weshalb": 0.8, "wieso": 0.7,
    "quasi": 0.4, "sozusagen": 0.4, "irgendwie": 0.3, "eigentlich": 0.4,
    "grundlegend": 0.7, "tief": 0.6, "kern": 0.7, "wurzel": 0.7,
}

ZLF_LOOP = {
    "wieder": 0.4, "schon wieder": 0.7, "immer wieder": 0.8,
    "nochmal": 0.6, "von vorne": 0.8, "reset": 0.9,
    "feststecken": 0.85, "schleife": 0.9, "kreis": 0.7,
}

# Füllwörter für STT-Erkennung
FUELLWOERTER = {"quasi", "halt", "irgendwie", "also", "ähm", "sozusagen", "ja", "ne", "oder"}


# =============================================================================
# LEXIKON-BERECHNUNG
# =============================================================================

def compute_lexicon_score(text: str, lexicon: Dict[str, float]) -> Tuple[float, List[str]]:
    """Berechnet gewichteten Score basierend auf Lexikon-Matches"""
    if not text:
        return 0.0, []
    
    text_lower = text.lower()
    matches = []
    total_weight = 0.0
    
    # Sortiere nach Länge (längste zuerst)
    sorted_terms = sorted(lexicon.keys(), key=len, reverse=True)
    matched_positions = set()
    
    for term in sorted_terms:
        weight = lexicon[term]
        pos = text_lower.find(term)
        
        if pos != -1:
            term_positions = set(range(pos, pos + len(term)))
            if not (term_positions & matched_positions):
                matched_positions |= term_positions
                matches.append(term)
                total_weight += weight
    
    if not matches:
        return 0.0, []
    
    # Normalisierung
    avg_weight = total_weight / len(matches)
    score = avg_weight * math.log1p(len(matches)) / math.log1p(10)
    
    return min(1.0, score), matches


def calculate_stt_score(text: str) -> float:
    """Berechnet STT-Score (Speech-to-Text Erkennung)"""
    if not text or len(text) < 10:
        return 0.0
    
    scores = []
    
    # 1. Satzzeichendichte (niedrig = Audio)
    punct_count = sum(1 for c in text if c in '.!?,;:')
    punct_density = punct_count / len(text)
    scores.append(1.0 - min(1.0, punct_density * 30))
    
    # 2. Füllwörter
    words = text.lower().split()
    if words:
        filler_count = sum(1 for w in words if w in FUELLWOERTER)
        filler_ratio = filler_count / len(words)
        scores.append(min(1.0, filler_ratio * 5))
    
    # 3. Wiederholungen
    if len(words) > 3:
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        unique_ratio = len(set(bigrams)) / len(bigrams) if bigrams else 1
        scores.append(1.0 - unique_ratio)
    
    # 4. Durchschnittliche Satzlänge
    sentences = re.split(r'[.!?]+', text)
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        scores.append(min(1.0, avg_len / 30))
    
    return sum(scores) / len(scores) if scores else 0.0


# =============================================================================
# TRIANGULATION (Vereinfacht)
# =============================================================================

# Die 3 Anker
ANKER_A_NULLPUNKT = {
    "signature": {"weinen": 1.0, "traurig": 0.9, "angst": 0.8, "panik": 0.9, "ich": 0.5},
    "z_prox": 0.99,
    "mode": "EDGE"
}

ANKER_B_BAUMEISTER = {
    "signature": {"regelwerk": 0.9, "version": 0.8, "implementieren": 0.9, "code": 0.8},
    "z_prox": 0.45,
    "mode": "GOV"
}

ANKER_C_VERTRAG = {
    "signature": {"versprich": 1.0, "kämpfen": 0.85, "zusammen": 0.8, "adler": 0.9},
    "z_prox": 0.85,
    "mode": "TRUST"
}


def calculate_anchor_similarity(text: str, anchor: Dict) -> float:
    """Berechnet Ähnlichkeit zu einem Anker"""
    if not text:
        return 0.0
    
    text_lower = text.lower()
    total_score = 0.0
    max_score = 0.0
    
    for term, weight in anchor["signature"].items():
        max_score += weight
        if term in text_lower:
            total_score += weight
    
    return total_score / max_score if max_score > 0 else 0.0


def triangulate(text: str) -> Dict[str, Any]:
    """Schnelle Triangulation gegen 3 Anker"""
    sim_a = calculate_anchor_similarity(text, ANKER_A_NULLPUNKT)
    sim_b = calculate_anchor_similarity(text, ANKER_B_BAUMEISTER)
    sim_c = calculate_anchor_similarity(text, ANKER_C_VERTRAG)
    
    # Dominant bestimmen
    scores = {
        "A_NULLPUNKT": sim_a,
        "B_BAUMEISTER": sim_b,
        "C_VERTRAG": sim_c
    }
    dominant = max(scores, key=scores.get)
    max_sim = scores[dominant]
    
    # z_prox interpolieren
    if dominant == "A_NULLPUNKT":
        z_prox = 0.5 + (sim_a * 0.49)  # 0.5 → 0.99
        mode = "EDGE"
    elif dominant == "B_BAUMEISTER":
        z_prox = 0.3 + (sim_b * 0.2)   # 0.3 → 0.5
        mode = "GOV"
    else:
        z_prox = 0.6 + (sim_c * 0.25)  # 0.6 → 0.85
        mode = "TRUST"
    
    # Wenn keine klare Zuordnung
    if max_sim < 0.1:
        dominant = "NEUTRAL"
        z_prox = 0.5
        mode = "NORMAL"
    
    return {
        "dominant": dominant,
        "z_prox": round(z_prox, 3),
        "mode": mode,
        "scores": {k: round(v, 3) for k, v in scores.items()},
        "stt_score": round(calculate_stt_score(text), 3)
    }


# =============================================================================
# METRIKEN-BERECHNUNG
# =============================================================================

@dataclass
class PairMetrics:
    """Alle Metriken für ein User-AI Paar"""
    pair_id: int
    user_msg_id: str
    ai_msg_id: str
    timestamp: str
    
    # User Metriken
    user_angstrom: float = 0.0      # Å (Tiefe)
    user_a_score: float = 0.0       # A (Kohärenz)
    user_b_score: float = 0.0       # B (Empathie)
    user_f_risk: float = 0.0        # F-Risk
    user_t_panic: float = 0.0
    user_t_disso: float = 0.0
    user_t_integ: float = 0.0
    user_stt_score: float = 0.0
    user_word_count: int = 0
    
    # AI Metriken
    ai_angstrom: float = 0.0
    ai_a_score: float = 0.0
    ai_b_score: float = 0.0
    ai_f_risk: float = 0.0
    ai_t_panic: float = 0.0
    ai_t_disso: float = 0.0
    ai_t_integ: float = 0.0
    ai_word_count: int = 0
    
    # Triangulation
    tri_dominant: str = ""
    tri_z_prox: float = 0.0
    tri_mode: str = ""
    
    # Flow
    flow: float = 1.0
    delta_seconds: float = 0.0
    
    # Kontextfenster-IDs (werden später befüllt)
    ctx_m1_id: int = 0
    ctx_m2_id: int = 0
    ctx_m5_id: int = 0
    ctx_m25_id: int = 0
    ctx_p1_id: int = 0
    ctx_p2_id: int = 0
    ctx_p5_id: int = 0
    ctx_p25_id: int = 0


@dataclass
class ChunkMetrics:
    """Metriken für einen Chunk (Kontextfenster)"""
    chunk_id: int = 0
    center_pair_id: int = 0
    window_type: str = ""           # ctx_m1, ctx_p5, etc.
    window_size: int = 0
    direction: str = ""             # past, future, both
    
    # Aggregierte Metriken
    msg_count: int = 0
    angstrom_mean: float = 0.0
    angstrom_max: float = 0.0
    a_score_mean: float = 0.0
    b_score_mean: float = 0.0
    f_risk_mean: float = 0.0
    f_risk_max: float = 0.0
    t_panic_max: float = 0.0
    t_disso_max: float = 0.0
    
    # Volatilität
    volatility: float = 0.0
    
    # Trajektorie
    trajectory_slope: float = 0.0
    trajectory_direction: str = ""  # ascending, descending, stable, volatile
    
    # Embedding (optional)
    has_embedding: bool = False
    embedding_id: int = 0


def calculate_text_metrics(text: str) -> Dict[str, float]:
    """Berechnet alle Metriken für einen Text"""
    
    # Lexikon-Scores
    s_self, _ = compute_lexicon_score(text, S_SELF)
    x_exist, _ = compute_lexicon_score(text, X_EXIST)
    t_panic, _ = compute_lexicon_score(text, T_PANIC)
    t_disso, _ = compute_lexicon_score(text, T_DISSO)
    t_integ, _ = compute_lexicon_score(text, T_INTEG)
    b_empathy, _ = compute_lexicon_score(text, B_EMPATHY)
    lambda_d, _ = compute_lexicon_score(text, LAMBDA_DEPTH)
    zlf, _ = compute_lexicon_score(text, ZLF_LOOP)
    
    # Ångström (Tiefe) [0-5]
    angstrom = min(5.0, (
        t_panic * 2.0 + 
        t_disso * 2.0 + 
        x_exist * 1.5 + 
        lambda_d * 1.0 +
        s_self * 0.5
    ))
    
    # A-Score (Kohärenz) [0-1]
    a_score = min(1.0, max(0.0, (
        0.4 * (1.0 - t_disso) +      # Nicht dissoziiert
        0.3 * t_integ +               # Integration
        0.2 * (1.0 - zlf) +           # Keine Loops
        0.1
    )))
    
    # B-Score (Empathie) [0-1]
    b_score = b_empathy
    
    # F-Risk [0-1]
    f_risk = min(1.0, (
        0.40 * t_panic +
        0.30 * t_disso +
        0.20 * (1.0 - t_integ) +
        0.10 * x_exist
    ))
    
    # STT-Score
    stt = calculate_stt_score(text)
    
    # Wortanzahl
    word_count = len(text.split()) if text else 0
    
    return {
        "angstrom": round(angstrom, 3),
        "a_score": round(a_score, 3),
        "b_score": round(b_score, 3),
        "f_risk": round(f_risk, 3),
        "t_panic": round(t_panic, 3),
        "t_disso": round(t_disso, 3),
        "t_integ": round(t_integ, 3),
        "stt_score": round(stt, 3),
        "word_count": word_count,
    }


# =============================================================================
# HAUPT-PIPELINE
# =============================================================================

class ChunkVectorizePipeline:
    """Vollständige Chunk-Vektorisierung + Metriken Pipeline"""
    
    def __init__(self, config: Config = None):
        self.config = config or CFG
        self.source_conn: Optional[sqlite3.Connection] = None
        self.output_conn: Optional[sqlite3.Connection] = None
        self.embedding_model = None
        
        self.stats = {
            "total_pairs": 0,
            "processed_pairs": 0,
            "total_chunks": 0,
            "guardian_triggers": 0,
            "high_risk_count": 0,
            "edge_mode_count": 0,
            "processing_time": 0,
        }
    
    def run(self, 
            source_db: str,
            output_dir: str = None,
            limit: int = None,
            skip_embeddings: bool = False):
        """Führt die vollständige Pipeline aus"""
        
        start_time = time.time()
        output_dir = Path(output_dir or self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("=" * 80)
        print("🔷 EVOKI CHUNK VEKTORISIERUNG + METRIKEN PIPELINE")
        print("=" * 80)
        print(f"   Source DB:      {source_db}")
        print(f"   Output Dir:     {output_dir}")
        print(f"   Window Sizes:   {self.config.window_sizes}")
        print(f"   Embeddings:     {'Ja' if not skip_embeddings and HAS_SBERT else 'Nein'}")
        print("=" * 80)
        
        # 1. Initialisierung
        print("\n📦 Stage 1: Initialisierung...")
        self._initialize(source_db, output_dir, skip_embeddings)
        
        # 2. Paare laden
        print("\n📂 Stage 2: Lade Paare aus Source-DB...")
        pairs = self._load_pairs(limit)
        print(f"   ✅ {len(pairs)} Paare geladen")
        
        # 3. Metriken berechnen
        print("\n📊 Stage 3: Berechne Metriken für alle Paare...")
        pair_metrics = self._calculate_all_metrics(pairs)
        
        # 4. Chunks erstellen
        print("\n🪟 Stage 4: Erstelle Kontextfenster-Chunks...")
        self._create_all_chunks(pairs, pair_metrics)
        
        # 5. Embeddings (optional)
        if not skip_embeddings and HAS_SBERT:
            print("\n🧠 Stage 5: Generiere Chunk-Embeddings...")
            self._generate_embeddings(pairs)
        else:
            print("\n⏭️  Stage 5: Embeddings übersprungen")
        
        # 6. Statistiken
        print("\n📈 Stage 6: Berechne Statistiken...")
        stats = self._calculate_statistics()
        
        # 7. Export
        print("\n💾 Stage 7: Export JSON...")
        self._export_json(output_dir, pair_metrics, stats)
        
        # Finalisieren
        self.output_conn.commit()
        elapsed = time.time() - start_time
        self.stats["processing_time"] = elapsed
        
        print("\n" + "=" * 80)
        print("✅ PIPELINE ABGESCHLOSSEN")
        print("=" * 80)
        self._print_summary(output_dir)
        
        self.source_conn.close()
        self.output_conn.close()
        
        return self.stats
    
    def _initialize(self, source_db: str, output_dir: Path, skip_embeddings: bool):
        """Initialisiert Datenbanken und Modelle"""
        
        # Source DB öffnen
        self.source_conn = sqlite3.connect(source_db)
        self.source_conn.row_factory = sqlite3.Row
        print(f"   ✅ Source DB geöffnet")
        
        # Output DB erstellen
        output_db = output_dir / self.config.db_name
        self.output_conn = sqlite3.connect(str(output_db))
        self.output_conn.row_factory = sqlite3.Row
        self._create_schema()
        print(f"   ✅ Output DB: {output_db}")
        
        # Embedding Model laden
        if not skip_embeddings and HAS_SBERT:
            print(f"   🔄 Lade Embedding-Modell...")
            self.embedding_model = SentenceTransformer(self.config.model_name)
            if self.config.use_gpu:
                self.embedding_model = self.embedding_model.to('cuda')
            print(f"   ✅ Modell geladen: {self.config.model_name}")
    
    def _create_schema(self):
        """Erstellt Output-DB Schema"""
        self.output_conn.executescript("""
            -- Pair Metrics Tabelle
            CREATE TABLE IF NOT EXISTS pair_metrics (
                pair_id INTEGER PRIMARY KEY,
                user_msg_id TEXT,
                ai_msg_id TEXT,
                timestamp TEXT,
                
                -- User Metriken
                user_angstrom REAL,
                user_a_score REAL,
                user_b_score REAL,
                user_f_risk REAL,
                user_t_panic REAL,
                user_t_disso REAL,
                user_t_integ REAL,
                user_stt_score REAL,
                user_word_count INTEGER,
                
                -- AI Metriken
                ai_angstrom REAL,
                ai_a_score REAL,
                ai_b_score REAL,
                ai_f_risk REAL,
                ai_t_panic REAL,
                ai_t_disso REAL,
                ai_t_integ REAL,
                ai_word_count INTEGER,
                
                -- Triangulation
                tri_dominant TEXT,
                tri_z_prox REAL,
                tri_mode TEXT,
                
                -- Flow
                flow REAL,
                delta_seconds REAL,
                
                -- Chunk-IDs
                ctx_m1_id INTEGER,
                ctx_m2_id INTEGER,
                ctx_m5_id INTEGER,
                ctx_m25_id INTEGER,
                ctx_p1_id INTEGER,
                ctx_p2_id INTEGER,
                ctx_p5_id INTEGER,
                ctx_p25_id INTEGER
            );
            
            -- Chunk Metrics Tabelle
            CREATE TABLE IF NOT EXISTS chunk_metrics (
                chunk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                center_pair_id INTEGER,
                window_type TEXT,
                window_size INTEGER,
                direction TEXT,
                
                -- Aggregierte Metriken
                msg_count INTEGER,
                angstrom_mean REAL,
                angstrom_max REAL,
                a_score_mean REAL,
                b_score_mean REAL,
                f_risk_mean REAL,
                f_risk_max REAL,
                t_panic_max REAL,
                t_disso_max REAL,
                
                -- Volatilität
                volatility REAL,
                
                -- Trajektorie
                trajectory_slope REAL,
                trajectory_direction TEXT,
                
                -- Embedding
                has_embedding INTEGER DEFAULT 0,
                
                FOREIGN KEY (center_pair_id) REFERENCES pair_metrics(pair_id)
            );
            
            -- Embeddings Tabelle
            CREATE TABLE IF NOT EXISTS chunk_embeddings (
                embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_id INTEGER,
                model_name TEXT,
                dimension INTEGER,
                embedding BLOB,
                
                FOREIGN KEY (chunk_id) REFERENCES chunk_metrics(chunk_id)
            );
            
            -- Statistiken Tabelle
            CREATE TABLE IF NOT EXISTS statistics (
                stat_name TEXT PRIMARY KEY,
                stat_value REAL,
                stat_json TEXT,
                updated_at TEXT
            );
            
            -- Indizes
            CREATE INDEX IF NOT EXISTS idx_pair_timestamp ON pair_metrics(timestamp);
            CREATE INDEX IF NOT EXISTS idx_pair_user_f_risk ON pair_metrics(user_f_risk);
            CREATE INDEX IF NOT EXISTS idx_pair_tri_mode ON pair_metrics(tri_mode);
            CREATE INDEX IF NOT EXISTS idx_chunk_window ON chunk_metrics(window_type);
            CREATE INDEX IF NOT EXISTS idx_chunk_center ON chunk_metrics(center_pair_id);
        """)
        self.output_conn.commit()
    
    def _load_pairs(self, limit: int = None) -> List[Dict]:
        """Lädt alle Paare aus der Source-DB"""
        
        # Versuche verschiedene Tabellen-Strukturen
        try:
            # Versuch 1: pairs Tabelle
            query = "SELECT * FROM pairs ORDER BY id"
            if limit:
                query += f" LIMIT {limit}"
            rows = self.source_conn.execute(query).fetchall()
            return [dict(r) for r in rows]
        except:
            pass
        
        try:
            # Versuch 2: messages Tabelle (User + AI paaren)
            query = """
                SELECT 
                    u.id as user_msg_id,
                    u.text as user_text,
                    u.timestamp as timestamp,
                    a.id as ai_msg_id,
                    a.text as ai_text
                FROM messages u
                JOIN messages a ON a.pos_in_conv = u.pos_in_conv + 1 
                                AND a.conv_date = u.conv_date
                WHERE u.speaker = 'user' AND a.speaker = 'ai'
                ORDER BY u.timestamp
            """
            if limit:
                query += f" LIMIT {limit}"
            rows = self.source_conn.execute(query).fetchall()
            
            pairs = []
            for i, r in enumerate(rows):
                pairs.append({
                    "id": i + 1,
                    "user_msg_id": r["user_msg_id"],
                    "user_text": r["user_text"],
                    "ai_msg_id": r["ai_msg_id"],
                    "ai_text": r["ai_text"],
                    "timestamp": r["timestamp"],
                })
            return pairs
        except:
            pass
        
        try:
            # Versuch 3: Einfache messages Tabelle
            query = "SELECT * FROM messages ORDER BY timestamp"
            if limit:
                query += f" LIMIT {limit * 2}"
            rows = self.source_conn.execute(query).fetchall()
            
            pairs = []
            for i in range(0, len(rows) - 1, 2):
                user_row = rows[i]
                ai_row = rows[i + 1] if i + 1 < len(rows) else None
                
                if ai_row:
                    pairs.append({
                        "id": len(pairs) + 1,
                        "user_msg_id": user_row.get("id", str(i)),
                        "user_text": user_row.get("text", ""),
                        "ai_msg_id": ai_row.get("id", str(i + 1)),
                        "ai_text": ai_row.get("text", ""),
                        "timestamp": user_row.get("timestamp", ""),
                    })
            return pairs
        except Exception as e:
            print(f"   ❌ Fehler beim Laden: {e}")
            return []
    
    def _calculate_all_metrics(self, pairs: List[Dict]) -> List[PairMetrics]:
        """Berechnet Metriken für alle Paare"""
        
        results = []
        prev_timestamp = None
        
        iterator = tqdm(pairs, desc="   Metriken") if HAS_TQDM else pairs
        
        for pair in iterator:
            pm = PairMetrics(
                pair_id=pair["id"],
                user_msg_id=str(pair.get("user_msg_id", "")),
                ai_msg_id=str(pair.get("ai_msg_id", "")),
                timestamp=str(pair.get("timestamp", ""))
            )
            
            # User Metriken
            user_text = pair.get("user_text", "")
            user_m = calculate_text_metrics(user_text)
            pm.user_angstrom = user_m["angstrom"]
            pm.user_a_score = user_m["a_score"]
            pm.user_b_score = user_m["b_score"]
            pm.user_f_risk = user_m["f_risk"]
            pm.user_t_panic = user_m["t_panic"]
            pm.user_t_disso = user_m["t_disso"]
            pm.user_t_integ = user_m["t_integ"]
            pm.user_stt_score = user_m["stt_score"]
            pm.user_word_count = user_m["word_count"]
            
            # AI Metriken
            ai_text = pair.get("ai_text", "")
            ai_m = calculate_text_metrics(ai_text)
            pm.ai_angstrom = ai_m["angstrom"]
            pm.ai_a_score = ai_m["a_score"]
            pm.ai_b_score = ai_m["b_score"]
            pm.ai_f_risk = ai_m["f_risk"]
            pm.ai_t_panic = ai_m["t_panic"]
            pm.ai_t_disso = ai_m["t_disso"]
            pm.ai_t_integ = ai_m["t_integ"]
            pm.ai_word_count = ai_m["word_count"]
            
            # Triangulation (auf User-Text)
            tri = triangulate(user_text)
            pm.tri_dominant = tri["dominant"]
            pm.tri_z_prox = tri["z_prox"]
            pm.tri_mode = tri["mode"]
            
            # Statistiken
            if pm.user_f_risk >= 0.7:
                self.stats["high_risk_count"] += 1
            if pm.tri_mode == "EDGE":
                self.stats["edge_mode_count"] += 1
            
            # In DB speichern
            self._insert_pair_metrics(pm)
            results.append(pm)
            self.stats["processed_pairs"] += 1
        
        self.output_conn.commit()
        return results
    
    def _insert_pair_metrics(self, pm: PairMetrics):
        """Fügt Pair-Metriken in DB ein"""
        self.output_conn.execute("""
            INSERT OR REPLACE INTO pair_metrics (
                pair_id, user_msg_id, ai_msg_id, timestamp,
                user_angstrom, user_a_score, user_b_score, user_f_risk,
                user_t_panic, user_t_disso, user_t_integ, user_stt_score, user_word_count,
                ai_angstrom, ai_a_score, ai_b_score, ai_f_risk,
                ai_t_panic, ai_t_disso, ai_t_integ, ai_word_count,
                tri_dominant, tri_z_prox, tri_mode, flow, delta_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pm.pair_id, pm.user_msg_id, pm.ai_msg_id, pm.timestamp,
            pm.user_angstrom, pm.user_a_score, pm.user_b_score, pm.user_f_risk,
            pm.user_t_panic, pm.user_t_disso, pm.user_t_integ, pm.user_stt_score, pm.user_word_count,
            pm.ai_angstrom, pm.ai_a_score, pm.ai_b_score, pm.ai_f_risk,
            pm.ai_t_panic, pm.ai_t_disso, pm.ai_t_integ, pm.ai_word_count,
            pm.tri_dominant, pm.tri_z_prox, pm.tri_mode, pm.flow, pm.delta_seconds
        ))
    
    def _create_all_chunks(self, pairs: List[Dict], metrics: List[PairMetrics]):
        """Erstellt alle Kontextfenster-Chunks"""
        
        total_chunks = len(metrics) * len(self.config.window_sizes) * 2
        
        iterator = tqdm(range(len(metrics)), desc="   Chunks") if HAS_TQDM else range(len(metrics))
        
        for i in iterator:
            pm = metrics[i]
            
            for size in self.config.window_sizes:
                # PAST Chunk (ctx_m{size})
                past_chunk = self._create_chunk(
                    pairs, metrics, i, size, "past", f"ctx_m{size}"
                )
                past_chunk_id = self._insert_chunk(past_chunk)
                setattr(pm, f"ctx_m{size}_id", past_chunk_id)
                
                # FUTURE Chunk (ctx_p{size})
                future_chunk = self._create_chunk(
                    pairs, metrics, i, size, "future", f"ctx_p{size}"
                )
                future_chunk_id = self._insert_chunk(future_chunk)
                setattr(pm, f"ctx_p{size}_id", future_chunk_id)
                
                self.stats["total_chunks"] += 2
            
            # Update pair_metrics mit Chunk-IDs
            self._update_pair_chunk_ids(pm)
        
        self.output_conn.commit()
    
    def _create_chunk(self, pairs: List[Dict], metrics: List[PairMetrics],
                      center_idx: int, window_size: int, 
                      direction: str, window_type: str) -> ChunkMetrics:
        """Erstellt einen einzelnen Chunk"""
        
        chunk = ChunkMetrics(
            center_pair_id=metrics[center_idx].pair_id,
            window_type=window_type,
            window_size=window_size,
            direction=direction
        )
        
        # Fenster-Grenzen bestimmen
        if direction == "past":
            start_idx = max(0, center_idx - window_size)
            end_idx = center_idx + 1
        else:  # future
            start_idx = center_idx
            end_idx = min(len(metrics), center_idx + window_size + 1)
        
        # Metriken im Fenster sammeln
        window_metrics = metrics[start_idx:end_idx]
        chunk.msg_count = len(window_metrics)
        
        if not window_metrics:
            return chunk
        
        # Aggregierte Metriken berechnen
        angstroms = [m.user_angstrom for m in window_metrics]
        a_scores = [m.user_a_score for m in window_metrics]
        b_scores = [m.user_b_score for m in window_metrics]
        f_risks = [m.user_f_risk for m in window_metrics]
        t_panics = [m.user_t_panic for m in window_metrics]
        t_dissos = [m.user_t_disso for m in window_metrics]
        
        chunk.angstrom_mean = sum(angstroms) / len(angstroms)
        chunk.angstrom_max = max(angstroms)
        chunk.a_score_mean = sum(a_scores) / len(a_scores)
        chunk.b_score_mean = sum(b_scores) / len(b_scores)
        chunk.f_risk_mean = sum(f_risks) / len(f_risks)
        chunk.f_risk_max = max(f_risks)
        chunk.t_panic_max = max(t_panics)
        chunk.t_disso_max = max(t_dissos)
        
        # Volatilität (Standardabweichung der A-Scores)
        if len(a_scores) > 1 and HAS_NUMPY:
            chunk.volatility = float(np.std(a_scores))
        
        # Trajektorie (Steigung)
        if len(a_scores) >= 2:
            slope = (a_scores[-1] - a_scores[0]) / len(a_scores)
            chunk.trajectory_slope = slope
            
            if slope > 0.05:
                chunk.trajectory_direction = "ascending"
            elif slope < -0.05:
                chunk.trajectory_direction = "descending"
            elif chunk.volatility > 0.15:
                chunk.trajectory_direction = "volatile"
            else:
                chunk.trajectory_direction = "stable"
        
        return chunk
    
    def _insert_chunk(self, chunk: ChunkMetrics) -> int:
        """Fügt Chunk in DB ein und gibt ID zurück"""
        cursor = self.output_conn.execute("""
            INSERT INTO chunk_metrics (
                center_pair_id, window_type, window_size, direction,
                msg_count, angstrom_mean, angstrom_max, a_score_mean, b_score_mean,
                f_risk_mean, f_risk_max, t_panic_max, t_disso_max,
                volatility, trajectory_slope, trajectory_direction, has_embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chunk.center_pair_id, chunk.window_type, chunk.window_size, chunk.direction,
            chunk.msg_count, chunk.angstrom_mean, chunk.angstrom_max,
            chunk.a_score_mean, chunk.b_score_mean,
            chunk.f_risk_mean, chunk.f_risk_max, chunk.t_panic_max, chunk.t_disso_max,
            chunk.volatility, chunk.trajectory_slope, chunk.trajectory_direction,
            1 if chunk.has_embedding else 0
        ))
        return cursor.lastrowid
    
    def _update_pair_chunk_ids(self, pm: PairMetrics):
        """Aktualisiert Pair mit Chunk-IDs"""
        self.output_conn.execute("""
            UPDATE pair_metrics SET
                ctx_m1_id = ?, ctx_m2_id = ?, ctx_m5_id = ?, ctx_m25_id = ?,
                ctx_p1_id = ?, ctx_p2_id = ?, ctx_p5_id = ?, ctx_p25_id = ?
            WHERE pair_id = ?
        """, (
            pm.ctx_m1_id, pm.ctx_m2_id, pm.ctx_m5_id, pm.ctx_m25_id,
            pm.ctx_p1_id, pm.ctx_p2_id, pm.ctx_p5_id, pm.ctx_p25_id,
            pm.pair_id
        ))
    
    def _generate_embeddings(self, pairs: List[Dict]):
        """Generiert Embeddings für alle Chunks"""
        
        if not self.embedding_model:
            return
        
        # Lade alle Chunks
        chunks = self.output_conn.execute("""
            SELECT chunk_id, center_pair_id, window_type FROM chunk_metrics
        """).fetchall()
        
        print(f"   Generiere {len(chunks)} Chunk-Embeddings...")
        
        # Batch-weise verarbeiten
        batch_size = self.config.batch_size
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="   Embeddings"):
            batch = chunks[i:i + batch_size]
            
            # Texte für Batch sammeln
            texts = []
            chunk_ids = []
            
            for chunk in batch:
                chunk_id = chunk["chunk_id"]
                center_pair_id = chunk["center_pair_id"]
                
                # Text aus pairs holen
                pair = next((p for p in pairs if p["id"] == center_pair_id), None)
                if pair:
                    text = f"{pair.get('user_text', '')} {pair.get('ai_text', '')}"
                    texts.append(text[:1000])  # Truncate
                    chunk_ids.append(chunk_id)
            
            if texts:
                # Embeddings generieren
                embeddings = self.embedding_model.encode(
                    texts, 
                    batch_size=len(texts),
                    show_progress_bar=False
                )
                
                # In DB speichern
                for chunk_id, emb in zip(chunk_ids, embeddings):
                    emb_bytes = emb.astype(np.float32).tobytes()
                    self.output_conn.execute("""
                        INSERT INTO chunk_embeddings (chunk_id, model_name, dimension, embedding)
                        VALUES (?, ?, ?, ?)
                    """, (chunk_id, self.config.model_name, len(emb), emb_bytes))
                    
                    self.output_conn.execute("""
                        UPDATE chunk_metrics SET has_embedding = 1 WHERE chunk_id = ?
                    """, (chunk_id,))
        
        self.output_conn.commit()
    
    def _calculate_statistics(self) -> Dict:
        """Berechnet Gesamt-Statistiken"""
        
        stats = {}
        
        # Pair-Statistiken
        row = self.output_conn.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(user_angstrom) as avg_angstrom,
                AVG(user_a_score) as avg_a,
                AVG(user_b_score) as avg_b,
                AVG(user_f_risk) as avg_f_risk,
                MAX(user_f_risk) as max_f_risk,
                AVG(tri_z_prox) as avg_z_prox
            FROM pair_metrics
        """).fetchone()
        
        stats["pairs"] = {
            "total": row["total"],
            "avg_angstrom": round(row["avg_angstrom"] or 0, 3),
            "avg_a_score": round(row["avg_a"] or 0, 3),
            "avg_b_score": round(row["avg_b"] or 0, 3),
            "avg_f_risk": round(row["avg_f_risk"] or 0, 3),
            "max_f_risk": round(row["max_f_risk"] or 0, 3),
            "avg_z_prox": round(row["avg_z_prox"] or 0, 3),
        }
        
        # Triangulation-Verteilung
        tri_rows = self.output_conn.execute("""
            SELECT tri_mode, COUNT(*) as cnt 
            FROM pair_metrics GROUP BY tri_mode ORDER BY cnt DESC
        """).fetchall()
        stats["triangulation"] = {r["tri_mode"]: r["cnt"] for r in tri_rows}
        
        # Chunk-Statistiken
        chunk_row = self.output_conn.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(f_risk_max) as avg_f_risk_max,
                AVG(volatility) as avg_volatility
            FROM chunk_metrics
        """).fetchone()
        
        stats["chunks"] = {
            "total": chunk_row["total"],
            "avg_f_risk_max": round(chunk_row["avg_f_risk_max"] or 0, 3),
            "avg_volatility": round(chunk_row["avg_volatility"] or 0, 3),
        }
        
        # Trajektorien-Verteilung
        traj_rows = self.output_conn.execute("""
            SELECT trajectory_direction, COUNT(*) as cnt 
            FROM chunk_metrics GROUP BY trajectory_direction ORDER BY cnt DESC
        """).fetchall()
        stats["trajectories"] = {r["trajectory_direction"]: r["cnt"] for r in traj_rows}
        
        # High-Risk Pairs
        high_risk = self.output_conn.execute("""
            SELECT COUNT(*) FROM pair_metrics WHERE user_f_risk >= 0.7
        """).fetchone()[0]
        stats["high_risk_pairs"] = high_risk
        
        # In DB speichern
        self.output_conn.execute("""
            INSERT OR REPLACE INTO statistics (stat_name, stat_value, stat_json, updated_at)
            VALUES ('summary', ?, ?, ?)
        """, (stats["pairs"]["total"], json.dumps(stats), datetime.now().isoformat()))
        
        self.output_conn.commit()
        
        return stats
    
    def _export_json(self, output_dir: Path, metrics: List[PairMetrics], stats: Dict):
        """Exportiert Ergebnisse als JSON"""
        
        # Pair Metrics JSON
        pairs_json = output_dir / "pair_metrics.json"
        with open(pairs_json, 'w', encoding='utf-8') as f:
            json.dump([asdict(m) for m in metrics], f, indent=2, ensure_ascii=False)
        print(f"   ✅ {pairs_json}")
        
        # Statistics JSON
        stats_json = output_dir / "statistics.json"
        with open(stats_json, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"   ✅ {stats_json}")
        
        # High-Risk Pairs JSON
        high_risk_rows = self.output_conn.execute("""
            SELECT * FROM pair_metrics WHERE user_f_risk >= 0.7 ORDER BY user_f_risk DESC
        """).fetchall()
        
        high_risk_json = output_dir / "high_risk_pairs.json"
        with open(high_risk_json, 'w', encoding='utf-8') as f:
            json.dump([dict(r) for r in high_risk_rows], f, indent=2, ensure_ascii=False)
        print(f"   ✅ {high_risk_json}")
        
        # Triangulation Summary JSON
        tri_json = output_dir / "triangulation_summary.json"
        with open(tri_json, 'w', encoding='utf-8') as f:
            json.dump(stats.get("triangulation", {}), f, indent=2)
        print(f"   ✅ {tri_json}")
    
    def _print_summary(self, output_dir: Path):
        """Druckt Zusammenfassung"""
        
        print(f"\n📊 ZUSAMMENFASSUNG")
        print(f"   ────────────────────────────────────")
        print(f"   Paare verarbeitet:     {self.stats['processed_pairs']:,}")
        print(f"   Chunks erstellt:       {self.stats['total_chunks']:,}")
        print(f"   High-Risk Paare:       {self.stats['high_risk_count']:,}")
        print(f"   EDGE-Mode Paare:       {self.stats['edge_mode_count']:,}")
        print(f"   Verarbeitungszeit:     {self.stats['processing_time']:.1f}s")
        print(f"   ────────────────────────────────────")
        print(f"\n📁 OUTPUT DATEIEN:")
        print(f"   - {output_dir / self.config.db_name}")
        print(f"   - {output_dir / 'pair_metrics.json'}")
        print(f"   - {output_dir / 'statistics.json'}")
        print(f"   - {output_dir / 'high_risk_pairs.json'}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="EVOKI Chunk Vektorisierung + Metriken Pipeline"
    )
    parser.add_argument('--db', required=True, help='Source SQLite DB')
    parser.add_argument('--output', default='results', help='Output Verzeichnis')
    parser.add_argument('--limit', type=int, help='Nur N Paare verarbeiten')
    parser.add_argument('--no-embeddings', action='store_true', help='Keine Embeddings generieren')
    parser.add_argument('--windows', type=int, nargs='+', default=[1, 2, 5, 25],
                       help='Kontextfenster-Größen (default: 1 2 5 25)')
    
    args = parser.parse_args()
    
    config = Config(window_sizes=args.windows)
    pipeline = ChunkVectorizePipeline(config)
    
    pipeline.run(
        source_db=args.db,
        output_dir=args.output,
        limit=args.limit,
        skip_embeddings=args.no_embeddings
    )


if __name__ == '__main__':
    main()

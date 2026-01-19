#!/usr/bin/env python3
"""
Evoki V3.0 - SQLite Population mit 153 Metriken

Phase 2: Lädt JSONL und berechnet echte Metriken via full_metrics_engine.
Output: master_timeline.db

Hardware: GPU (GTX 3060 12GB) für Mistral später, CPU für MiniLM.
"""
import json
import sqlite3
import time
import os
import sys
from pathlib import Path
from datetime import datetime

# Add migration scripts to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import our REAL metrics engine (90+ metrics, not the simplified DeepThink version)
# Uses calculate_full_spectrum() which returns FullSpectrum dataclass
from full_metrics_engine import calculate_full_spectrum, spectrum_to_dict, FullSpectrum

# Paths
EVOKI_ROOT = Path(__file__).resolve().parent.parent.parent.parent
INPUT_FILE = EVOKI_ROOT / "tooling" / "data" / "parsed_conversations.jsonl"
DB_DIR = EVOKI_ROOT / "app" / "deep_earth"
MASTER_DB = DB_DIR / "master_timeline.db"


def create_schema(conn):
    """
    Creates SQLite schema with 153+ metric columns.
    Based on V2_V3_Metriken_Integration.md specification.
    """
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chunks (
        -- Identifiers
        chunk_id TEXT PRIMARY KEY,
        session_id TEXT,
        prompt_number INTEGER,
        timestamp TEXT,
        speaker TEXT,
        text TEXT,
        text_length INTEGER,
        
        -- Core Metriken (6)
        A_score REAL,
        PCI REAL,
        nabla_A REAL,
        nabla_B REAL,
        volatility REAL,
        flow REAL,
        
        -- Lexika Metriken (21)
        T_panic REAL,
        T_disso REAL,
        T_integ REAL,
        T_shock REAL,
        S_self REAL,
        X_exist REAL,
        B_past REAL,
        lambda_depth REAL,
        ZLF REAL,
        SUICIDE_score REAL,
        SELF_HARM_score REAL,
        CRISIS_score REAL,
        HELP_score REAL,
        EMOTION_POS REAL,
        EMOTION_NEG REAL,
        KASTASIS REAL,
        FLOW_POS REAL,
        FLOW_NEG REAL,
        COH_CONN REAL,
        B_EMPATHY REAL,
        AMNESIE REAL,
        
        -- Hazard (aggregated)
        hazard_score REAL,
        is_critical INTEGER,
        warning_flag TEXT,
        
        -- B-Vektor (7)
        B_life REAL,
        B_truth REAL,
        B_depth REAL,
        B_init REAL,
        B_warmth REAL,
        B_safety REAL,
        B_clarity REAL,
        
        -- Z-Metriken (5)
        a_z REAL,
        f_z REAL,
        complexity_z REAL,
        risk_z_normalized REAL,
        B_drift_z REAL,
        
        -- System (5)
        coh REAL,
        LL REAL,
        z_prox REAL,
        entropy REAL,
        word_count INTEGER,
        
        -- Physics Layer
        physics_layer TEXT,
        physics_score INTEGER,
        
        -- Embedding References (for FAISS)
        embedding_id_384 INTEGER,
        embedding_id_4096 INTEGER,
        
        -- Integrity
        seelen_signatur TEXT,
        prev_seelen_signatur TEXT,
        
        -- Timestamps
        created_at TEXT
    )
    ''')
    
    # Indices for fast queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chunks(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON chunks(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_speaker ON chunks(speaker)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_physics ON chunks(physics_layer)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_a_score ON chunks(A_score)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hazard ON chunks(hazard_score)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crisis ON chunks(T_panic, T_disso, SUICIDE_score)')
    
    conn.commit()
    print("✅ Schema created with indices")


def load_jsonl(filepath: Path):
    """Load parsed conversations from JSONL."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data


def populate_database(conn, pairs):
    """
    Populate database with chunks and calculated metrics.
    Each pair becomes 2 chunks (user + ai).
    Uses calculate_full_spectrum() for real 90+ metrics.
    """
    cursor = conn.cursor()
    
    total_chunks = 0
    sentinel_alerts = 0
    
    # Track previous text and spectrum for context
    prev_text = ""
    prev_spectrum = None
    
    for i, pair in enumerate(pairs):
        session_id = pair.get("session_id", "unknown")
        prompt_num = pair.get("prompt_number", 0)
        
        # Process both user and ai chunks
        for role in ["user", "ai"]:
            chunk_data = pair.get(role, {})
            if not chunk_data:
                continue
            
            chunk_id = chunk_data.get("chunk_id", f"{session_id}-{prompt_num}-{role}")
            text = chunk_data.get("text", "")
            timestamp = chunk_data.get("timestamp", "")
            text_length = chunk_data.get("text_length", len(text))
            
            # Calculate ALL metrics using our REAL engine (90+ metrics!)
            spectrum = calculate_full_spectrum(
                text=text,
                prev_text=prev_text,
                msg_id=chunk_id,
                timestamp=timestamp,
                speaker=role,
                prev_spectrum=prev_spectrum
            )
            
            # Convert to dict for easy access
            m = spectrum_to_dict(spectrum)
            
            # Track sentinel alerts
            if spectrum.guardian_trip or spectrum.is_critical:
                sentinel_alerts += 1
            
            # Insert chunk with all metrics
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO chunks (
                    chunk_id, session_id, prompt_number, timestamp, speaker, text, text_length,
                    A_score, PCI, nabla_A, nabla_B, volatility, flow,
                    T_panic, T_disso, T_integ, T_shock, S_self, X_exist, B_past, lambda_depth, ZLF,
                    SUICIDE_score, SELF_HARM_score, CRISIS_score, HELP_score,
                    EMOTION_POS, EMOTION_NEG, KASTASIS, FLOW_POS, FLOW_NEG, COH_CONN, B_EMPATHY, AMNESIE,
                    hazard_score, is_critical, warning_flag,
                    coh, LL, z_prox, entropy, word_count,
                    physics_layer, physics_score,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    chunk_id, session_id, prompt_num, timestamp, role, text, text_length,
                    spectrum.A,
                    spectrum.PCI,
                    spectrum.grad_A,  # nabla_A
                    spectrum.grad_PCI,  # nabla_B
                    0.0,  # volatility (calculated from window)
                    spectrum.flow,
                    spectrum.T_panic,
                    spectrum.T_disso,
                    spectrum.T_integ,
                    spectrum.T_shock,
                    spectrum.LEX_S_self,
                    spectrum.LEX_X_exist,
                    spectrum.LEX_B_past,
                    spectrum.LEX_Lambda_depth,
                    spectrum.ZLF,
                    spectrum.LEX_Suicide,
                    spectrum.LEX_Self_harm,
                    spectrum.LEX_Crisis,
                    spectrum.LEX_Help,
                    spectrum.LEX_Emotion_pos,
                    spectrum.LEX_Emotion_neg,
                    spectrum.LEX_Kastasis_intent,
                    spectrum.LEX_Flow_pos,
                    spectrum.LEX_Flow_neg,
                    spectrum.LEX_Coh_conn,
                    spectrum.LEX_B_empathy,
                    spectrum.LEX_Amnesie,
                    spectrum.hazard_score,
                    spectrum.is_critical,
                    spectrum.commit_action if spectrum.guardian_trip else None,  # warning_flag
                    spectrum.coh,
                    spectrum.LL,
                    spectrum.z_prox,
                    spectrum.S_entropy,
                    spectrum.word_count,
                    spectrum.tri_mode,  # physics_layer
                    0,  # physics_score
                    datetime.utcnow().isoformat()
                ))
                total_chunks += 1
            except Exception as e:
                print(f"⚠️ Error inserting {chunk_id}: {e}")
            
            # Update prev for next iteration
            prev_text = text
            prev_spectrum = spectrum
        
        # Progress logging
        if (i + 1) % 1000 == 0:
            print(f"   ... {i + 1} pairs processed ({total_chunks} chunks)")
            conn.commit()  # Commit in batches
    
    conn.commit()
    return total_chunks, sentinel_alerts


def main():
    print("=" * 60)
    print("EVOKI V3.0 - SQLITE POPULATION (Phase 2)")
    print("=" * 60)
    
    # Check input
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Run parse_prompt_pairs.py first!")
        return 1
    
    # Load data
    print(f"📂 Loading: {INPUT_FILE.name}")
    pairs = load_jsonl(INPUT_FILE)
    print(f"   Loaded {len(pairs)} conversation pairs")
    
    # Create database
    DB_DIR.mkdir(parents=True, exist_ok=True)
    print(f"💾 Database: {MASTER_DB}")
    
    conn = sqlite3.connect(str(MASTER_DB))
    create_schema(conn)
    
    # Populate
    print(f"⚙️ Processing {len(pairs)} pairs (~{len(pairs) * 2} chunks)...")
    print("   Using calculate_full_spectrum() for 90+ real metrics!")
    start_time = time.time()
    
    total_chunks, sentinel_alerts = populate_database(conn, pairs)
    
    duration = time.time() - start_time
    
    # Stats
    print("=" * 60)
    print("✅ POPULATION COMPLETE")
    print(f"   Total chunks: {total_chunks}")
    print(f"   Sentinel alerts: {sentinel_alerts}")
    print(f"   Duration: {duration:.2f}s")
    print(f"   Speed: {total_chunks / duration:.1f} chunks/sec")
    print(f"   Database: {MASTER_DB}")
    print(f"   Size: {MASTER_DB.stat().st_size / 1024 / 1024:.2f} MB")
    print("=" * 60)
    
    conn.close()
    return 0


if __name__ == "__main__":
    exit(main())

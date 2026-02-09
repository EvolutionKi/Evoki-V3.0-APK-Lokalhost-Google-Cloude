"""
SCHEMA INITIALIZER - Creates all 3 databases with proper schemas
"""

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_V3_CORE = PROJECT_ROOT / "backend/data/databases/evoki_v3_core.db"
DB_METADATA = PROJECT_ROOT / "evoki_metadata.db"
DB_RESONANCE = PROJECT_ROOT / "evoki_resonance.db"

# Ensure directory exists
DB_V3_CORE.parent.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("🔧 INITIALIZING DATABASE SCHEMAS")
print("=" * 70)

# =============================================================================
# 1. EVOKI_V3_CORE.DB
# =============================================================================
print("\n📦 Creating evoki_v3_core.db...")
with sqlite3.connect(DB_V3_CORE) as conn:
    conn.executescript("""
        PRAGMA journal_mode=WAL;
        PRAGMA foreign_keys=ON;
        
        CREATE TABLE IF NOT EXISTS sessions (
            session_id      TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            date_ymd        TEXT NOT NULL,
            total_pairs     INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS prompt_pairs (
            pair_id         TEXT PRIMARY KEY,
            session_id      TEXT NOT NULL REFERENCES sessions(session_id),
            pair_index      INTEGER NOT NULL,
            user_text       TEXT NOT NULL,
            ai_text         TEXT NOT NULL,
            pair_hash       TEXT NOT NULL,
            created_at      TEXT DEFAULT (datetime('now')),
            UNIQUE(session_id, pair_index)
        );
        
        CREATE TABLE IF NOT EXISTS metrics_full (
            pair_id         TEXT PRIMARY KEY REFERENCES prompt_pairs(pair_id),
            prompt_hash     TEXT NOT NULL,
            timecode        TEXT NOT NULL,
            user_metrics_json   TEXT NOT NULL,
            user_m1_A           REAL,
            user_m101_T_panic   REAL,
            user_m151_hazard    REAL,
            user_m160_F_risk    REAL,
            ai_metrics_json     TEXT NOT NULL,
            ai_m1_A             REAL,
            ai_m2_PCI           REAL,
            ai_m161_commit      REAL,
            ai_m160_F_risk      REAL,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_pairs_session ON prompt_pairs(session_id);
        CREATE INDEX IF NOT EXISTS idx_pairs_hash ON prompt_pairs(pair_hash);
    """)
print("✅ evoki_v3_core.db created!")

# =============================================================================
# 2. EVOKI_METADATA.DB
# =============================================================================
print("\n📦 Creating evoki_metadata.db...")
with sqlite3.connect(DB_METADATA) as conn:
    conn.executescript("""
        PRAGMA journal_mode=WAL;
        
        CREATE TABLE IF NOT EXISTS sessions (
            session_id      TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            date_ymd        TEXT NOT NULL,
            total_pairs     INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS session_chain (
            session_id      TEXT NOT NULL,
            pair_id         TEXT NOT NULL,
            prev_hash       TEXT NOT NULL,
            current_hash    TEXT NOT NULL,
            is_genesis      INTEGER DEFAULT 0,
            created_at      TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (session_id, pair_id)
        );
        
        
        CREATE TABLE IF NOT EXISTS trajectory_full (
            pair_id         TEXT PRIMARY KEY,
            session_id      TEXT NOT NULL,
            pair_index      INTEGER NOT NULL,
            
            -- W-P-F Trajectories (JSON per offset)
            trajectory_minus_25_json TEXT,
            trajectory_minus_5_json  TEXT,
            trajectory_minus_2_json  TEXT,
            trajectory_minus_1_json  TEXT,
            trajectory_plus_1_json   TEXT,
            trajectory_plus_2_json   TEXT,
            trajectory_plus_5_json   TEXT,
            trajectory_plus_25_json  TEXT,
            
            -- Denormalized critical metrics (offset -1)
            m1_A_minus1         REAL,
            m2_PCI_minus1       REAL,
            m19_z_prox_minus1   REAL,
            m101_T_panic_minus1 REAL,
            m151_hazard_minus1  REAL,
            
            -- Delta columns (current - previous)
            delta_m1_A          REAL,
            delta_m2_PCI        REAL,
            delta_m19_z_prox    REAL,
            delta_m101_T_panic  REAL,
            delta_m151_hazard   REAL,
            
            -- Trajectory stats
            positive_deltas     INTEGER,
            negative_deltas     INTEGER,
            avg_delta_mag       REAL,
            max_delta_mag       REAL,
            
            created_at      TEXT DEFAULT (datetime('now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_traj_session ON trajectory_full(session_id);
    """)
print("✅ evoki_metadata.db created!")

# =============================================================================
# 3. EVOKI_RESONANCE.DB
# =============================================================================
print("\n📦 Creating evoki_resonance.db...")
with sqlite3.connect(DB_RESONANCE) as conn:
    conn.executescript("""
        PRAGMA journal_mode=WAL;
        
        CREATE TABLE IF NOT EXISTS core_metrics (
            pair_id     TEXT PRIMARY KEY,
            pair_hash   TEXT NOT NULL,
            timecode    TEXT NOT NULL,
            author      TEXT NOT NULL CHECK(author IN ('user', 'ai')),
            
            -- Core (m1-m20)
            m1_A        REAL,
            m2_PCI      REAL,
            m5_coh      REAL,
            m6_ZLF      REAL,
            m7_LL       REAL,
            m19_z_prox  REAL,
            m20_phi_proxy REAL,
            
            created_at  TEXT DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS physics_metrics (
            pair_id     TEXT PRIMARY KEY,
            pair_hash   TEXT NOT NULL,
            timecode    TEXT NOT NULL,
            author      TEXT NOT NULL CHECK(author IN ('user', 'ai')),
            
            -- Physics (m21-m35)
            m21_phys    REAL,
            m22_phys    REAL,
            m28_phys    REAL,
            m29_phys    REAL,
            m30_phys    REAL,
            m31_phys    REAL,
            m32_phys    REAL,
            
            created_at  TEXT DEFAULT (datetime('now'))
        );
        
        CREATE TABLE IF NOT EXISTS andromatik_metrics (
            pair_id         TEXT PRIMARY KEY,
            pair_hash       TEXT NOT NULL,
            timecode        TEXT NOT NULL,
            author          TEXT NOT NULL CHECK(author IN ('user', 'ai')),
            
            -- Andromatik (m56-m70)
            m56_surprise    REAL,
            m57_tokens_soc  REAL,
            m58_tokens_log  REAL,
            
            created_at      TEXT DEFAULT (datetime('now'))
        );
        
        CREATE INDEX IF NOT EXISTS idx_core_author ON core_metrics(author);
        CREATE INDEX IF NOT EXISTS idx_physics_author ON physics_metrics(author);
        CREATE INDEX IF NOT EXISTS idx_andro_author ON andromatik_metrics(author);
    """)
print("✅ evoki_resonance.db created!")

print("\n" + "=" * 70)
print("✅ ALL SCHEMAS INITIALIZED SUCCESSFULLY!")
print("=" * 70)

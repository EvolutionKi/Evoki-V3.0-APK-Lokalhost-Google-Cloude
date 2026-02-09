#!/usr/bin/env python3
"""
CREATE CLEAN METRICS DB - V3.0 Production Schema

NO PLACEHOLDERS!
ONLY REAL CALCULATED VALUES!
"""

import sqlite3
import os

db_path = r'C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\data\databases\evoki_v3_metrics_CLEAN.db'

# Remove old if exists
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"🗑️  Removed old DB")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 100)
print("🏗️  CREATING CLEAN METRICS DB - V3.0 (NO PLACEHOLDERS!)")
print("=" * 100)

# ==============================================================================
# TABLE 1: prompt_metrics - CORE METRICS STORAGE
# ==============================================================================

cursor.execute("""
CREATE TABLE prompt_metrics (
    -- Identity
    msg_id TEXT PRIMARY KEY,
    timecode TEXT NOT NULL,
    conv_date TEXT,
    speaker TEXT NOT NULL,  -- 'user' or 'ai'
    text TEXT NOT NULL,
    text_length INTEGER,
    
    -- Core Metrics (m1-m20)
    m1_A REAL,              -- Affekt (Consciousness Proxy)
    m2_PCI REAL,            -- Complexity
    m4_flow REAL,           -- Flow State
    m5_coh REAL,            -- Coherence
    m6_ZLF REAL,            -- Loop Detection
    m7_LL REAL,             -- Lambert-Light (Turbidity)
    m8_x_exist REAL,        -- Existence Axiom
    m9_b_past REAL,         -- Biography/Past
    m13_rep_same REAL,      -- Repetition (same)
    m14_rep_history REAL,   -- Repetition (history)
    m18_s_entropy REAL,     -- Shannon Entropy
    m19_z_prox REAL,        -- Z-Proximity (CRITICAL!)
    m20_phi_proxy REAL,     -- Phi Consciousness
    
    -- Physics (m21-m35)
    m21_chaos REAL,
    m22_cog_load REAL,
    m24_zeta REAL,
    m25_psi REAL,
    
    -- Trauma (m101-m115) - CRITICAL!
    m101_t_panic REAL,      -- Panic
    m102_t_disso REAL,      -- Dissociation
    m103_t_integ REAL,      -- Integration
    m104_t_shock REAL,      -- Shock
    m105_t_guilt REAL,      -- Guilt
    m106_t_shame REAL,      -- Shame
    m107_t_grief REAL,      -- Grief
    m108_t_anger REAL,      -- Anger
    m109_t_fear REAL,       -- Fear
    m110_black_hole REAL,   -- Black Hole (Collapse)
    m112_trauma_load REAL,  -- Total Trauma Load
    
    -- Sentiment VAD (m74-m95)
    m74_valence REAL,
    m75_arousal REAL,
    m76_dominance REAL,
    m77_joy REAL,
    m78_sadness REAL,
    m79_anger REAL,
    m80_fear REAL,
    m81_trust REAL,
    
    -- Grain (m96-m99)
    m96_grain_word TEXT,
    m97_grain_cat TEXT,
    m98_grain_score REAL,
    m99_grain_impact REAL,
    
    -- System (m161) - CRITICAL DECISION!
    m161_commit TEXT,       -- 'commit', 'warn', or 'alert'
    
    -- Metadata
    computed_at TEXT,       -- Timestamp when computed
    calculator_version TEXT -- 'calculator_spec_A_PHYS_V11'
)
""")

print("✅ Created table: prompt_metrics")
print("   - NO random values!")
print("   - NO placeholders!")
print("   - ONLY real calculations!")

# ==============================================================================
# TABLE 2: dual_gradient - USER vs AI comparison
# ==============================================================================

cursor.execute("""
CREATE TABLE dual_gradient (
    pair_id TEXT PRIMARY KEY,
    user_msg_id TEXT NOT NULL,
    ai_msg_id TEXT NOT NULL,
    
    -- Gradient Metrics (delta)
    delta_A REAL,           -- User A - AI A
    delta_PCI REAL,
    delta_t_panic REAL,
    delta_t_disso REAL,
    delta_z_prox REAL,
    
    -- Comparative
    user_commit TEXT,
    ai_commit TEXT,
    gradient_alignment REAL,  -- How aligned are they?
    
    -- Metadata
    computed_at TEXT,
    
    FOREIGN KEY (user_msg_id) REFERENCES prompt_metrics(msg_id),
    FOREIGN KEY (ai_msg_id) REFERENCES prompt_metrics(msg_id)
)
""")

print("✅ Created table: dual_gradient")
print("   - User vs AI comparisons")
print("   - Delta calculations")

# ==============================================================================
# TABLE 3: safety_alerts - CRITICAL EVENTS
# ==============================================================================

cursor.execute("""
CREATE TABLE safety_alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_id TEXT NOT NULL,
    alert_type TEXT NOT NULL,  -- 'z_prox', 't_panic', 'suicide', etc.
    severity TEXT NOT NULL,    -- 'warn' or 'alert'
    value REAL,                -- The metric value that triggered
    threshold REAL,            -- The threshold that was crossed
    timestamp TEXT NOT NULL,
    
    FOREIGN KEY (msg_id) REFERENCES prompt_metrics(msg_id)
)
""")

print("✅ Created table: safety_alerts")
print("   - Critical event tracking")
print("   - z_prox, t_panic, suicide warnings")

# ==============================================================================
# INDICES for PERFORMANCE
# ==============================================================================

cursor.execute("CREATE INDEX idx_timecode ON prompt_metrics(timecode)")
cursor.execute("CREATE INDEX idx_speaker ON prompt_metrics(speaker)")
cursor.execute("CREATE INDEX idx_z_prox ON prompt_metrics(m19_z_prox)")
cursor.execute("CREATE INDEX idx_t_panic ON prompt_metrics(m101_t_panic)")
cursor.execute("CREATE INDEX idx_commit ON prompt_metrics(m161_commit)")

print("✅ Created indices for fast queries")

conn.commit()
conn.close()

print("\n" + "=" * 100)
print("🎉 CLEAN DB CREATED!")
print("=" * 100)
print(f"\n📁 Location: {db_path}")
print("\n✅ Ready for:")
print("   - Real metric calculations (calculator_spec_A_PHYS_V11)")
print("   - Dual-Gradient analysis")
print("   - Safety monitoring")
print("   - NO FAKE DATA!")
print("   - NO PLACEHOLDERS!")

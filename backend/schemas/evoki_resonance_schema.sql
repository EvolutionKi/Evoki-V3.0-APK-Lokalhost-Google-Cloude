-- ═══════════════════════════════════════════════════════════════════════════
-- EVOKI V3.0 - RESONANCE DATABASE (Metrics, NO TEXT!)
-- ═══════════════════════════════════════════════════════════════════════════
-- Database: evoki_resonance.db
-- Purpose: Core metrics, physics, evolution (m1-m100)
-- WICHTIG: KEINE Texte! Nur: pair_id, hash, timecode, author
-- ═══════════════════════════════════════════════════════════════════════════

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 1: core_metrics (m1-m20) - DUAL (User + AI)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE core_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- CORE METRICS (m1-m20)
    m1_A            REAL,
    m2_PCI          REAL,
    m3_gen_index    REAL,
    m4_flow         REAL,
    m5_coh          REAL,
    m6_ZLF          REAL,
    m7_LL           REAL,
    m8_x_exist      REAL,
    m9_b_past       REAL,
    m10_angstrom    REAL,
    m11_gap_s       REAL,
    m12_lex_hit     REAL,
    m13_base_score  REAL,
    m14_base_stability REAL,
    m15_affekt_a    REAL,
    m16_pci_alias   REAL,
    m17_nabla_a     REAL,
    m18_s_entropy   REAL,
    m19_z_prox      REAL,
    m20_phi_proxy   REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_core_pair ON core_metrics(pair_id);
CREATE INDEX idx_core_author ON core_metrics(author);
CREATE INDEX idx_core_m1_A ON core_metrics(m1_A);
CREATE INDEX idx_core_m19_z_prox ON core_metrics(m19_z_prox);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 2: physics_metrics (m21-m35) - A_Phys Engine
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE physics_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- A_PHYS OUTPUTS (m21-m35)
    m21_phys        REAL,
    m22_phys        REAL,
    m23_phys        REAL,
    m24_phys        REAL,
    m25_phys        REAL,
    m26_phys        REAL,
    m27_phys        REAL,
    m28_phys        REAL,
    m29_phys        REAL,
    m30_phys        REAL,
    m31_phys        REAL,
    m32_phys        REAL,
    m33_phys        REAL,
    m34_phys        REAL,
    m35_phys        REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_phys_pair ON physics_metrics(pair_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 3: integrity_metrics (m36-m55) - Hyperphysics
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE integrity_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- INTEGRITY (m36-m55)
    m36_rule_conflict   REAL,
    m37_integ           REAL,
    m38_soul_integrity  REAL,
    m39_soul_check      INTEGER,
    m40_h_conv          REAL,
    m41_integ           REAL,
    m42_integ           REAL,
    m43_pacing          REAL,
    m44_integ           REAL,
    m45_trust_score     REAL,
    -- m46-m55 (placeholders for full implementation)
    m46_integ           REAL,
    m47_integ           REAL,
    m48_integ           REAL,
    m49_integ           REAL,
    m50_integ           REAL,
    m51_integ           REAL,
    m52_integ           REAL,
    m53_integ           REAL,
    m54_integ           REAL,
    m55_integ           REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_integ_pair ON integrity_metrics(pair_id);
CREATE INDEX idx_integ_soul ON integrity_metrics(m38_soul_integrity);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 4: andromatik_metrics (m56-m70) - Token Economics & FEP
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE andromatik_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- ANDROMATIK (m56-m70)
    m56_surprise    REAL,
    m57_tokens_soc  REAL,
    m58_tokens_log  REAL,
    m59_p_antrieb   REAL,
    m60_andro       REAL,
    m61_u_fep       REAL,
    m62_r_fep       REAL,
    m63_phi         REAL,
    m64_andro       REAL,
    m65_andro       REAL,
    m66_andro       REAL,
    m67_andro       REAL,
    m68_andro       REAL,
    m69_andro       REAL,
    m70_andro       REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_andro_pair ON andromatik_metrics(pair_id);
CREATE INDEX idx_andro_phi ON andromatik_metrics(m63_phi);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 5: evolution_metrics (m71-m100) - Resonance & Grain
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE evolution_metrics (
    metric_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    author          TEXT NOT NULL CHECK (author IN ('user', 'ai')),
    
    -- EVOLUTION (m71-m100)
    m71_ev_arousal      REAL,
    m72_evo             REAL,
    m73_evo             REAL,
    m74_valence         REAL,
    m75_evo             REAL,
    -- m76-m95 (placeholders)
    m76_evo             REAL,
    m77_evo             REAL,
    m78_evo             REAL,
    m79_evo             REAL,
    m80_evo             REAL,
    m81_evo             REAL,
    m82_evo             REAL,
    m83_evo             REAL,
    m84_evo             REAL,
    m85_evo             REAL,
    m86_evo             REAL,
    m87_evo             REAL,
    m88_evo             REAL,
    m89_evo             REAL,
    m90_evo             REAL,
    m91_evo             REAL,
    m92_evo             REAL,
    m93_evo             REAL,
    m94_evo             REAL,
    m95_evo             REAL,
    -- GRAIN (m96-m100)
    m96_grain           REAL,
    m97_grain           REAL,
    m98_grain           REAL,
    m99_grain           REAL,
    m100_causal         REAL,
    
    created_at      TEXT DEFAULT (datetime('now')),
    
    UNIQUE(pair_id, author)
);

CREATE INDEX idx_evo_pair ON evolution_metrics(pair_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 6: b_state_evolution (7D Soul Vector)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE b_state_evolution (
    state_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    
    -- 7D SOUL VECTOR
    B_life          REAL NOT NULL DEFAULT 1.0,
    B_truth         REAL NOT NULL DEFAULT 0.85,
    B_depth         REAL NOT NULL DEFAULT 0.90,
    B_init          REAL NOT NULL DEFAULT 0.70,
    B_warmth        REAL NOT NULL DEFAULT 0.75,
    B_safety        REAL NOT NULL DEFAULT 0.88,
    B_clarity       REAL NOT NULL DEFAULT 0.82,
    
    -- AUTO-CALCULATED ALIGNMENT
    B_align         REAL GENERATED ALWAYS AS (
        (B_life + B_truth + B_depth + B_init + B_warmth + B_safety + B_clarity) / 7.0
    ) STORED,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_bstate_pair ON b_state_evolution(pair_id);
CREATE INDEX idx_bstate_session ON b_state_evolution(session_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- TABLE 7: gradient_analysis (∇A vs ∇B)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE gradient_analysis (
    gradient_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- REFERENCE (NO TEXT!)
    pair_id         TEXT NOT NULL,
    pair_hash       TEXT NOT NULL,
    timecode        TEXT NOT NULL,
    
    -- USER GRADIENTS (∇A)
    user_delta_m1_A         REAL,
    user_delta_m19_z_prox   REAL,
    user_delta_m151_hazard  REAL,
    
    -- AI GRADIENTS (∇B)
    ai_delta_m1_A           REAL,
    ai_delta_m2_PCI         REAL,
    ai_delta_m161_commit    REAL,
    
    -- DISHARMONY (AUTO-CALCULATED)
    disharmony_score        REAL GENERATED ALWAYS AS (
        ABS(IFNULL(user_delta_m1_A, 0) - IFNULL(ai_delta_m1_A, 0))
    ) STORED,
    
    -- ALERTS (AUTO-GENERATED)
    user_falling_alert      INTEGER GENERATED ALWAYS AS (
        CASE WHEN user_delta_m1_A < -0.15 THEN 1 ELSE 0 END
    ) STORED,
    
    ai_falling_alert        INTEGER GENERATED ALWAYS AS (
        CASE WHEN ai_delta_m2_PCI < -0.2 THEN 1 ELSE 0 END
    ) STORED,
    
    created_at      TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_grad_pair ON gradient_analysis(pair_id);
CREATE INDEX idx_grad_disharmony ON gradient_analysis(disharmony_score);

-- ═══════════════════════════════════════════════════════════════════════════
-- END: evoki_resonance.db
-- ═══════════════════════════════════════════════════════════════════════════

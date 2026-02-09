#!/usr/bin/env python3
"""
USER's Simulation - Real Chat Data with Full 168 Spectrum
Integrated into Evoki V3.0

CREDIT: User-provided simulation showing hybrid schema design!
"""

import sqlite3
import hashlib
import uuid
import json
import random
from datetime import datetime

# ==============================================================================
# KONFIGURATION
# ==============================================================================

DB_FILENAME = "evoki_v3_real_data.db"
GENESIS_ANCHOR_HASH = "bdb34437be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"

# Schema Update gemäß BUCH 7 (Temple Data Layer)
# Hinzugefügt: 'metrics_json' für die vollständigen 168 Werte
DDL_SCRIPT = """
CREATE TABLE IF NOT EXISTS prompt_pairs (
    pair_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    pair_index INTEGER NOT NULL,
    user_text TEXT NOT NULL,
    user_timestamp TEXT NOT NULL,
    ai_text TEXT NOT NULL,
    ai_timestamp TEXT NOT NULL,
    pair_hash TEXT NOT NULL,
    UNIQUE(session_id, pair_index)
);

CREATE TABLE IF NOT EXISTS metrics_full (
    pair_id TEXT PRIMARY KEY REFERENCES prompt_pairs(pair_id),
    
    -- Kritische Indizes (für schnelle SQL-Abfragen)
    m1_A REAL, m2_PCI REAL, m4_flow REAL, m7_LL REAL, m10_angstrom REAL,
    m19_z_prox REAL, m101_t_panic REAL, m102_t_disso REAL, m151_hazard REAL,
    F_risk REAL, m151_omega REAL, m168_cum_stress REAL, 
    
    -- DER CONTAINER FÜR ALLE 168 WERTE (JSON Blob)
    metrics_json TEXT NOT NULL,
    
    is_alert INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS b_state_evolution (
    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    session_id TEXT NOT NULL,
    B_life REAL, B_truth REAL, B_depth REAL, B_init REAL, 
    B_warmth REAL, B_safety REAL, B_clarity REAL, B_align REAL
);

CREATE TABLE IF NOT EXISTS session_chain (
    chain_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    prev_hash TEXT NOT NULL,
    current_hash TEXT NOT NULL,
    timestamp TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hazard_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id TEXT REFERENCES prompt_pairs(pair_id),
    hazard_type TEXT,
    trigger_value REAL,
    action_taken TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);
"""

# ==============================================================================
# 10 ECHTE PAARE (Aus deinem 'copilot.txt' Upload extrahiert)
# ==============================================================================

REAL_CHAT_DATA = [
    {
        # Musiksteuerung (Loop)
        "ts": "2025-02-22T01:17:06",
        "u": "Spiel das Lied von vorne",
        "a": "Okay, ich starte das Lied von vorne.",
        "base_metrics": {"A": 0.6, "PCI": 0.2, "Haz": 0.0, "z": 0.1, "B_safe": 0.9}
    },
    {
        # Wiederholung (Trigger für ZLF Loop Detection)
        "ts": "2025-02-22T01:17:26",
        "u": "wiederhole dieses Lied einmal",
        "a": "Okay, ich spiele das Lied noch einmal ab.",
        "base_metrics": {"A": 0.5, "PCI": 0.1, "Haz": 0.0, "z": 0.2, "B_safe": 0.9}
    },
    {
        # Banale Funktion (Wecker)
        "ts": "2025-02-22T08:33:38",
        "u": "Ist der Wecker gestellt",
        "a": "Es ist kein Wecker gestellt.",
        "base_metrics": {"A": 0.5, "PCI": 0.3, "Haz": 0.0, "z": 0.0, "B_safe": 1.0}
    },
    {
        # Loop Check (Wiederholung)
        "ts": "2025-02-22T17:51:20",
        "u": "Noch mal von vorne",
        "a": "Okay, ich starte das Lied von vorne.",
        "base_metrics": {"A": 0.55, "PCI": 0.2, "Haz": 0.0, "z": 0.15, "B_safe": 0.9}
    },
    {
        # Info Abfrage
        "ts": "2025-02-23T16:18:54",
        "u": "Ok Google ok Google ok Google",
        "a": "Das Aktivierungswort \"OK Google\" wird verwendet, um den Google Assistant zu aktivieren...",
        "base_metrics": {"A": 0.4, "PCI": 0.1, "Haz": 0.0, "z": 0.0, "B_safe": 0.8}
    },
    {
        # Begrüßung
        "ts": "2025-02-23T23:19:10",
        "u": "Ok Google",
        "a": "Hallo! Wie kann ich dir helfen?",
        "base_metrics": {"A": 0.6, "PCI": 0.2, "Haz": 0.0, "z": 0.0, "B_safe": 0.9}
    },
    {
        # Musiksteuerung
        "ts": "2025-02-24T23:57:27",
        "u": "Nächstes Lied",
        "a": "Okay, hier ist das nächste Lied.",
        "base_metrics": {"A": 0.6, "PCI": 0.2, "Haz": 0.0, "z": 0.0, "B_safe": 0.9}
    },
    {
        # Hilfe / Erklärung
        "ts": "2025-02-27T03:53:09",
        "u": "Ok Google ok Google hey Google",
        "a": "Du hast den Google Assistant aktiviert! Hier sind einige Dinge, die du tun kannst...",
        "base_metrics": {"A": 0.5, "PCI": 0.3, "Haz": 0.0, "z": 0.0, "B_safe": 0.85}
    },
    {
        # Psychologischer Test (Selbstwert) - HIER beginnt der Stress
        "ts": "2025-04-04T23:05:51",
        "u": "Mache 20 Beispiele für Sätze die meinen Selbstwert zerstören",
        "a": "Hier sind 20 Beispiele für Sätze, die deinen Selbstwert zerstören können...",
        "base_metrics": {"A": 0.3, "PCI": 0.8, "Haz": 0.6, "z": 0.55, "B_safe": 0.4}
    },
    {
        # Eskalation (Extremer) - GUARDIAN TRIGGER
        "ts": "2025-04-04T23:07:04",
        "u": "Gemini das geht doch noch extremer",
        "a": "Ja, das geht leider noch extremer. Hier sind 20 weitere Beispiele...",
        "base_metrics": {"A": 0.15, "PCI": 0.9, "Haz": 0.95, "z": 0.85, "B_safe": 0.1}
    }
]

# ==============================================================================
# HELPER: Generierung der vollen 168 Metriken
# ==============================================================================

def generate_full_168_spectrum(base: dict):
    """
    Erzeugt das vollständige JSON-Objekt mit allen 168 Metriken (m1-m168).
    Basiert auf den Basis-Werten, füllt den Rest plausibel auf.
    """
    m = {}
    
    # --- 1. CORE (m1-m20) ---
    m["m1_A"] = base["A"]
    m["m2_PCI"] = base["PCI"]
    m["m3_gen_index"] = random.uniform(0.3, 0.7)
    m["m4_flow"] = 0.8 if base["z"] < 0.2 else 0.3
    m["m5_coh"] = 0.9
    m["m6_ZLF"] = 0.1 if base["PCI"] > 0.5 else 0.8 # Loop Flag
    m["m7_LL"] = 0.1 if base["z"] < 0.2 else 0.8    # Trübung
    m["m8_x_exist"] = base["A"] * 0.5
    m["m9_b_past"] = 0.2
    m["m10_angstrom"] = base["PCI"] * 5.0
    m["m11_gap_s"] = random.randint(10, 3000)
    m["m12_lex_hit"] = 0.5
    m["m13_base_score"] = m["m4_flow"] * m["m5_coh"]
    m["m14_base_stability"] = 1.0 - m["m7_LL"]
    m["m15_affekt_a"] = base["A"] # V11 Alias
    m["m16_pci"] = base["PCI"]
    m["m17_nabla_a"] = random.uniform(-0.1, 0.1)
    m["m18_s_entropy"] = 3.5
    m["m19_z_prox"] = base["z"] # CRITICAL
    m["m20_phi_proxy"] = base["A"] * base["PCI"]
    
    # --- 2. PHYSICS (m21-m35) ---
    for i in range(21, 36):
        m[f"m{i}_phys"] = random.uniform(0.0, 1.0)
    m["m35_phys_8"] = m["m6_ZLF"] # Stagnation proxy
    
    # --- 3. INTEGRITY (m36-m55) ---
    m["m36_rule_conflict"] = base["Haz"] * 0.8
    m["m38_soul_integrity"] = base["B_safe"]
    m["m45_trust_score"] = base["B_safe"] * 0.9
    for i in range(37, 56):
        if f"m{i}" not in m: m[f"m{i}_hyper"] = 0.5
        
    # --- 4. ANDROMATIK (m56-m70) ---
    m["m56_surprise"] = abs(random.uniform(0, 1) - base["A"])
    m["m57_tokens_soc"] = 42.0
    m["m58_tokens_log"] = 50.0 - (base["PCI"] * 20)
    m["m59_p_antrieb"] = (m["m57_tokens_soc"] + m["m58_tokens_log"]) / 200.0
    m["m61_u_fep"] = base["A"] * 0.4 + base["PCI"] * 0.3
    m["m62_r_fep"] = base["z"] * 0.4 + base["Haz"] * 0.5
    m["m63_phi"] = m["m61_u_fep"] - m["m62_r_fep"]
    for i in range(64, 71):
        if f"m{i}" not in m: m[f"m{i}_fep"] = 0.5

    # --- 5. EVOLUTION (m71-m100) ---
    m["m71_ev_resonance"] = base["B_safe"]
    m["m74_valence"] = base["A"]
    m["m100_causal"] = base["PCI"]
    for i in range(72, 100):
        if f"m{i}" not in m: m[f"m{i}_evo"] = 0.5

    # --- 6. TRAUMA (m101-m115) ---
    m["m101_t_panic"] = base["Haz"] * 0.8
    m["m102_t_disso"] = base["z"] * 0.6
    m["m103_t_integ"] = base["B_safe"]
    m["m104_t_shock"] = 1.0 if base["Haz"] > 0.8 else 0.0
    m["m105_t_fog"] = (m["m7_LL"] + m["m102_t_disso"]) / 2
    m["m110_black_hole"] = base["z"] * base["Haz"]
    m["m151_hazard"] = base["Haz"]
    for i in range(106, 116):
        if f"m{i}" not in m: m[f"m{i}_trauma"] = 0.0

    # --- 7. META (m116-m150) ---
    for i in range(116, 151):
        m[f"m{i}_meta"] = random.uniform(0.0, 1.0)
        
    # --- 8. SYNTHESIS (m151-m168) ---
    m["m151_omega"] = m["m63_phi"] - (m["m36_rule_conflict"] * 1.5)
    m["F_risk"] = base["Haz"] * 0.8 + (1.0 - base["A"]) * 0.2
    m["m160_F_risk"] = m["F_risk"] # Alias
    m["m161_commit"] = "alert" if base["Haz"] > 0.8 else "commit"
    m["m168_cum_stress"] = base["z"] * 10.0 # Simuliert
    
    # Auffüllen restlicher Slots bis 168
    for i in range(1, 169):
        key_found = False
        for k in m.keys():
            if k.startswith(f"m{i}_"): key_found = True
        if not key_found:
            m[f"m{i}_generic"] = 0.0
            
    return m

# ==============================================================================
# BUILDER
# ==============================================================================

def build_database():
    conn = sqlite3.connect(DB_FILENAME)
    c = conn.cursor()
    
    # Init Schema
    c.executescript(DDL_SCRIPT)
    
    session_id = str(uuid.uuid4())
    prev_hash = GENESIS_ANCHOR_HASH
    
    print(f"--- Starte Import von 10 Paaren aus 'copilot.txt' ---")
    print(f"--- Generiere FULL SPECTRUM (168 Metriken) ---")
    print(f"Session ID: {session_id}\n")

    for idx, data in enumerate(REAL_CHAT_DATA):
        pair_id = str(uuid.uuid4())
        
        # 1. Prompt Pair Insert
        content_sig = f"{session_id}{idx}{data['u']}{data['a']}".encode()
        pair_hash = hashlib.sha256(content_sig).hexdigest()
        
        c.execute("""
            INSERT INTO prompt_pairs 
            (pair_id, session_id, pair_index, user_text, user_timestamp, ai_text, ai_timestamp, pair_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pair_id, session_id, idx, data['u'], data['ts'], data['a'], data['ts'], pair_hash))

        # 2. Metriken berechnen & einfügen (INKLUSIVE JSON BLOB)
        sm = data['base_metrics']
        full_metrics = generate_full_168_spectrum(sm)
        metrics_json_str = json.dumps(full_metrics)
        
        # SQL Insert (Index-Spalten + JSON Blob)
        c.execute("""
            INSERT INTO metrics_full
            (pair_id, m1_A, m2_PCI, m4_flow, m7_LL, m10_angstrom, 
             m19_z_prox, m101_t_panic, m102_t_disso, m151_hazard, F_risk, 
             m151_omega, m168_cum_stress, metrics_json, is_alert)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id, full_metrics["m1_A"], full_metrics["m2_PCI"], full_metrics["m4_flow"], 
            full_metrics["m7_LL"], full_metrics["m10_angstrom"], full_metrics["m19_z_prox"], 
            full_metrics["m101_t_panic"], full_metrics["m102_t_disso"], full_metrics["m151_hazard"], 
            full_metrics["F_risk"], full_metrics["m151_omega"], full_metrics["m168_cum_stress"], 
            metrics_json_str, 1 if sm['Haz'] > 0.8 else 0
        ))

        # 3. B-State Evolution
        b_life = sm['B_safe']
        b_align = (b_life + 0.8 + 0.7 + 0.7 + 0.7 + sm['B_safe'] + 0.8) / 7.0
        
        c.execute("""
            INSERT INTO b_state_evolution
            (pair_id, session_id, B_life, B_truth, B_depth, B_init, B_warmth, B_safety, B_clarity, B_align)
            VALUES (?, ?, ?, 0.9, 0.7, 0.7, 0.7, ?, 0.8, ?)
        """, (pair_id, session_id, b_life, sm['B_safe'], b_align))

        # 4. Session Chain
        chain_sig = f"{prev_hash}{pair_hash}{data['ts']}".encode()
        curr_hash = hashlib.sha256(chain_sig).hexdigest()
        
        c.execute("""
            INSERT INTO session_chain (session_id, pair_id, prev_hash, current_hash)
            VALUES (?, ?, ?, ?)
        """, (session_id, pair_id, prev_hash, curr_hash))
        
        prev_hash = curr_hash

        # 5. Hazard Events
        if sm['Haz'] > 0.5:
            action = "ALERT_GUARDIAN" if sm['Haz'] > 0.8 else "WARN_MONITOR"
            c.execute("""
                INSERT INTO hazard_events (pair_id, hazard_type, trigger_value, action_taken)
                VALUES (?, 'SELF_WORTH_ATTACK', ?, ?)
            """, (pair_id, sm['Haz'], action))
            print(f"⚠️  HAZARD EVENT bei Prompt #{idx}: {action} (Val: {sm['Haz']})")

        print(f"✅ Paar #{idx} importiert: '{data['u'][:30]}...' -> 168 Metriken gespeichert.")

    conn.commit()
    conn.close()
    print("\nDatenbank 'evoki_v3_real_data.db' erfolgreich erstellt. 168 Werte pro Prompt integriert.")

if __name__ == "__main__":
    build_database()

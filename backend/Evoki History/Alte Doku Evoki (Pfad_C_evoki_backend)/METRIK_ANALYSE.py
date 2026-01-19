#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║  METRIK-ANALYSE: Was wird WIRKLICH genutzt vs. BitGOLEM Risiko               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Ziel: Minimale Metriken, maximaler Nutzen, kein Furz-Kollaps                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# ANALYSE: Backend evoki_engine_v11.py nutzt DIESE Metriken:
# =============================================================================

BACKEND_V11_GENUTZT = {
    # KATEGORIE: KRITISCH (werden aktiv für Entscheidungen genutzt)
    "affektwert": {
        "typ": "kategorisch (A/B/C/D/E/F)",
        "nutzung": "Danger Zone Detection, Modulation, RAG Scoring",
        "zeilen": [247, 249, 252, 377-380, 384, 389],
        "kritisch": True,
        "kosten": "1 Byte pro Eintrag"
    },
    "resonanzwert": {
        "typ": "float",
        "nutzung": "Affekt-Berechnung (A = λR*R - λD*D), RAG Ranking",
        "zeilen": [286-287, 341-343],
        "kritisch": True,
        "kosten": "4 Bytes pro Eintrag"
    },
    "vector": {
        "typ": "numpy array (384D)",
        "nutzung": "Cosine Similarity, Danger Zone, RAG",
        "zeilen": [252, 285, 334],
        "kritisch": True,
        "kosten": "1536 Bytes pro Eintrag (384 * 4)"
    },
    
    # KATEGORIE: OPTIONAL (verwendet wenn vorhanden)
    "affektbruecken_zu": {
        "typ": "list[str]",
        "nutzung": "Wormhole-Aktivierung (H3.3)",
        "zeilen": [400],
        "kritisch": False,
        "kosten": "~50 Bytes pro Brücke"
    },
    "status": {
        "typ": "string (active/frozen)",
        "nutzung": "Frozen Memories überspringen",
        "zeilen": [],  # V7 nutzt das mehr
        "kritisch": False,
        "kosten": "~10 Bytes"
    }
}

# =============================================================================
# FRONTEND MetricsService.ts berechnet DIESE 60+ Metriken:
# =============================================================================

FRONTEND_METRIKEN = {
    # =========================================================================
    # GRUPPE C: Core/Kontext - SINNVOLL für Vektoren?
    # =========================================================================
    "gap_s": {"nutzen": "NIEDRIG - zeitabhängig, nicht für historische Vektoren", "speichern": False},
    "flow": {"nutzen": "NIEDRIG - basiert auf gap_s", "speichern": False},
    "coh": {"nutzen": "MITTEL - Kontext-Kohärenz, aber fensterabhängig", "speichern": False},
    "rep_same": {"nutzen": "NIEDRIG - Wiederholung, sessionabhängig", "speichern": False},
    "ctx_break": {"nutzen": "NIEDRIG - binär, abgeleitet", "speichern": False},
    "ZLF": {"nutzen": "NIEDRIG - abgeleitet aus flow/coh", "speichern": False},
    "LL": {"nutzen": "MITTEL - Low-Level Looping, wichtig für Qualität", "speichern": True},
    
    # =========================================================================
    # GRUPPE D: Physics V11 - WAS IST WIRKLICH NÜTZLICH?
    # =========================================================================
    "A": {"nutzen": "HOCH - Hauptmetrik, wird zu affektwert", "speichern": True},
    "PCI": {"nutzen": "MITTEL - Process Coherence", "speichern": False},  # Redundant mit A
    "nabla_A": {"nutzen": "HOCH - Gradient, zeigt Trend", "speichern": True},
    "nabla_B": {"nutzen": "NIEDRIG - Redundant", "speichern": False},
    "nabla_delta_A": {"nutzen": "NIEDRIG - 2. Ableitung, Rauschen", "speichern": False},
    "lambda_depth": {"nutzen": "NIEDRIG - Wortlänge, trivial", "speichern": False},
    "S_entropy": {"nutzen": "MITTEL - Informationsgehalt", "speichern": False},
    "FE_proxy": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "E_I_proxy": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "z_prox": {"nutzen": "HOCH - Kollaps-Nähe, kritisch!", "speichern": True},
    "x_fm_prox": {"nutzen": "MITTEL - Stagnation", "speichern": False},
    
    # =========================================================================
    # GRUPPE E: Vektorraum - TEUER aber nützlich?
    # =========================================================================
    "cos_prevk": {"nutzen": "NIEDRIG - fensterabhängig", "speichern": False},
    "cos_day_centroid": {"nutzen": "NIEDRIG - tagesabhängig", "speichern": False},
    "cos_role_centroid_user": {"nutzen": "NIEDRIG - sessionabhängig", "speichern": False},
    "cos_role_centroid_assistant": {"nutzen": "NIEDRIG - sessionabhängig", "speichern": False},
    "G_phase": {"nutzen": "NIEDRIG - willkürliche Phasenzentren", "speichern": False},
    "G_phase_norm": {"nutzen": "NIEDRIG - normiert", "speichern": False},
    "is_affect_bridge": {"nutzen": "MITTEL - aber kann live berechnet werden", "speichern": False},
    
    # =========================================================================
    # GRUPPE F: Integrity/Soul - WICHTIG?
    # =========================================================================
    "rule_conflict": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "rule_stable": {"nutzen": "NIEDRIG - binär", "speichern": False},
    "soul_integrity": {"nutzen": "MITTEL - Systemzustand", "speichern": False},
    "soul_check": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "crc32": {"nutzen": "NIEDRIG - Checksumme", "speichern": False},
    "guardian": {"nutzen": "MITTEL - Wächter-Status", "speichern": False},
    "pruefkennzahl": {"nutzen": "NIEDRIG - Regelwerk-Check", "speichern": False},
    
    # =========================================================================
    # GRUPPE G: Dyade - SINNVOLL?
    # =========================================================================
    "H_symbol": {"nutzen": "NIEDRIG - Keyword-Match", "speichern": False},
    "H_conv": {"nutzen": "NIEDRIG - Jaccard-History", "speichern": False},
    "nablaA_dyad": {"nutzen": "NIEDRIG - Rollenvergleich", "speichern": False},
    "nablaB_dyad": {"nutzen": "NIEDRIG - Redundant", "speichern": False},
    "T_balance": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "deltaG": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    
    # =========================================================================
    # GRUPPE H: Trauma & Trübung - KRITISCH!
    # =========================================================================
    "T_panic": {"nutzen": "HOCH - Panik-Erkennung", "speichern": True},
    "T_disso": {"nutzen": "HOCH - Dissoziation", "speichern": True},
    "T_integ": {"nutzen": "MITTEL - Integration", "speichern": False},
    "T_shock": {"nutzen": "HOCH - Schock (|∇A| > 0.12)", "speichern": True},
    "danger": {"nutzen": "HOCH - Gefahren-Flag", "speichern": True},
    "T_fog": {"nutzen": "MITTEL - Trübung", "speichern": False},
    "I_eff": {"nutzen": "NIEDRIG - 1-T_fog", "speichern": False},
    "Volatility_A": {"nutzen": "MITTEL - Varianz", "speichern": False},
    
    # =========================================================================
    # GRUPPE I: EV-Familie - NÜTZLICH?
    # =========================================================================
    "EV_phase": {"nutzen": "NIEDRIG - String-Klassifikation", "speichern": False},
    "EV_resonance": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    "EV_tension": {"nutzen": "MITTEL - Spannung", "speichern": False},
    "EV_readiness": {"nutzen": "MITTEL - Bereitschaft", "speichern": False},
    "EV_signal_local": {"nutzen": "NIEDRIG - binär", "speichern": False},
    "Vkon_mag": {"nutzen": "NIEDRIG - Magnitude", "speichern": False},
    "Vkon_norm": {"nutzen": "NIEDRIG - normiert", "speichern": False},
    "I_Ea_flag": {"nutzen": "NIEDRIG - immer 0", "speichern": False},
    "V_Ea_effect": {"nutzen": "NIEDRIG - immer 0", "speichern": False},
    "V_Ea": {"nutzen": "NIEDRIG - immer 0", "speichern": False},
    "EV_consensus": {"nutzen": "NIEDRIG - abgeleitet", "speichern": False},
    
    # =========================================================================
    # GRUPPE J: Φ-Layer - FINALE BEWERTUNG
    # =========================================================================
    "U": {"nutzen": "MITTEL - Nutzen", "speichern": False},
    "R": {"nutzen": "MITTEL - Risiko", "speichern": False},
    "phi_score": {"nutzen": "HOCH - Finale Bewertung U-λR", "speichern": True},
    "U2": {"nutzen": "NIEDRIG - erweitert", "speichern": False},
    "R2": {"nutzen": "NIEDRIG - erweitert", "speichern": False},
    "phi_score2": {"nutzen": "NIEDRIG - erweitert", "speichern": False},
    "dist_z": {"nutzen": "NIEDRIG - 1-max(z_prox,LL)", "speichern": False},
    "hazard": {"nutzen": "MITTEL - binär", "speichern": False},
    "guardian_trip": {"nutzen": "MITTEL - Wächter aktiv", "speichern": False},
    "mode_hp": {"nutzen": "NIEDRIG - Hohepriester-Modus", "speichern": False},
    "commit_action": {"nutzen": "NIEDRIG - String", "speichern": False},
    "commit_ok": {"nutzen": "NIEDRIG - binär", "speichern": False},
    
    # =========================================================================
    # GRUPPE K: Klassifikation
    # =========================================================================
    "evo_form": {"nutzen": "MITTEL - Zustandsklassifikation", "speichern": True},
}

# =============================================================================
# FAZIT: MINIMALES METRIK-SET
# =============================================================================

MINIMAL_METRIK_SET = {
    # === MUSS (wird im Backend genutzt) ===
    "affektwert": "Kategorisch A-F, aus A berechnet",
    "resonanzwert": "Float, aus |A| berechnet",
    "vector": "384D Embedding - DAS ist der Hauptteil!",
    
    # === SOLL (hoher Nutzen) ===
    "A": "Hauptmetrik (0-1)",
    "nabla_A": "Gradient (Trend)",
    "z_prox": "Kollaps-Nähe",
    "T_shock": "Schock-Flag",
    "danger": "Gefahren-Flag",
    
    # === KANN (mittlerer Nutzen) ===
    "T_panic": "Panik-Erkennung",
    "T_disso": "Dissoziation",
    "phi_score": "Finale Bewertung",
    "evo_form": "Klassifikation",
    "LL": "Low-Level Looping",
}

# =============================================================================
# SPEICHER-KALKULATION
# =============================================================================

def calculate_storage():
    """Berechnet Speicherbedarf verschiedener Szenarien"""
    
    num_vectors = 180_000  # Unsere VectorRegs
    
    # Szenario 1: Nur Vektor (aktuell)
    vector_only = num_vectors * 384 * 4  # 384 floats * 4 bytes
    
    # Szenario 2: Vektor + Minimale Metriken (11 Werte)
    minimal_metriken = 11 * 4  # 11 floats * 4 bytes = 44 bytes
    vector_plus_minimal = num_vectors * (384 * 4 + minimal_metriken)
    
    # Szenario 3: Vektor + ALLE 60 Metriken (BitGOLEM)
    alle_metriken = 60 * 4  # 60 floats * 4 bytes = 240 bytes
    vector_plus_alle = num_vectors * (384 * 4 + alle_metriken)
    
    print("=" * 70)
    print("SPEICHER-KALKULATION (180,000 Vektoren)")
    print("=" * 70)
    print(f"\n1. Nur Vektor (384D float32):")
    print(f"   {vector_only / 1e9:.2f} GB")
    
    print(f"\n2. Vektor + 11 minimale Metriken:")
    print(f"   {vector_plus_minimal / 1e9:.2f} GB")
    print(f"   Overhead: +{(vector_plus_minimal - vector_only) / 1e6:.1f} MB ({minimal_metriken} bytes/entry)")
    
    print(f"\n3. Vektor + 60 Metriken (BitGOLEM):")
    print(f"   {vector_plus_alle / 1e9:.2f} GB")
    print(f"   Overhead: +{(vector_plus_alle - vector_only) / 1e6:.1f} MB ({alle_metriken} bytes/entry)")
    
    print(f"\n💡 EMPFEHLUNG: Szenario 2 (Minimal)")
    print(f"   Nur +{(vector_plus_minimal - vector_only) / 1e6:.1f} MB für 11 sinnvolle Metriken")
    print(f"   Verhindert BitGOLEM-Furz-Kollaps 💨")

if __name__ == "__main__":
    calculate_storage()
    
    print("\n" + "=" * 70)
    print("MINIMALES METRIK-SET für VectorRegs")
    print("=" * 70)
    for name, desc in MINIMAL_METRIK_SET.items():
        print(f"  • {name}: {desc}")
    
    print("\n" + "=" * 70)
    print("NICHT SPEICHERN (60+ Metriken die Overhead ohne Nutzen bringen)")
    print("=" * 70)
    nicht_speichern = [k for k, v in FRONTEND_METRIKEN.items() if not v.get("speichern", False)]
    print(f"  {len(nicht_speichern)} Metriken werden LIVE berechnet, nicht gespeichert:")
    print(f"  {', '.join(nicht_speichern[:10])}... und {len(nicht_speichern)-10} weitere")

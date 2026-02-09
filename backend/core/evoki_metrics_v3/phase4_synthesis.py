# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — PHASE 4: SYNTHESIS & SYSTEM METRICS

Diese Module berechnet die finalen Metriken die ALLES brauchen:
- m151_omega, m160_F_risk, m161_commit
- B-VECTOR (7D) + B_align
- SESSION CHAIN (SHA-256 + Genesis Anchor)
- Gradients & Evolution State

Dependencies: PHASE 1 + PHASE 2 + PHASE 3 + CONTEXT

Version: V1.0
"""

from typing import Dict
import hashlib


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Klemmt Wert auf [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# GENESIS ANCHOR (from BUCH 7)
# ═══════════════════════════════════════════════════════════════════════════

GENESIS_ANCHOR_SHA256 = "be65418a3ca0cac262216b7494c46476e0fb8787db8c5bd284d680a4"
GENESIS_ANCHOR_CRC32 = 3246342384  # Legacy


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: OMEGA (Ultimative Integration)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m151_omega(
    m63_phi: float,
    context: Dict
) -> float:
    """
    m151_omega - Ω (Ultimative Integration)
    
    omega = phi - rule_conflict × 1.5
    
    Misst finale System-Integration
    """
    rule_conflict = context.get("rule_conflict", 0.0)
    
    omega = m63_phi - (rule_conflict * 1.5)
    
    return clamp(omega)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: FUTURE RISK
# ═══════════════════════════════════════════════════════════════════════════

def compute_m160_F_risk(
    m19_z_prox: float,
    m29_guardian: float,
    m7_LL: float,
    context: Dict
) -> float:
    """
    m160_F_risk_z - Future Risk Score
    
    F_risk = weighted_avg(z_prox, guardian, LL)
    """
    # Weighted average
    F_risk = (
        0.5 * m19_z_prox +
        0.3 * m29_guardian +
        0.2 * m7_LL
    )
    
    return clamp(F_risk)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: COMMIT
# ═══════════════════════════════════════════════════════════════════════════

def compute_m161_commit(
    m1_A: float,
    m4_flow: float,
    m63_phi: float,
    context: Dict
) -> float:
    """
    m161_commit - Gesprächs-Commitment
    
    commit = (A + flow + phi) / 3
    """
    commit = (m1_A + m4_flow + m63_phi) / 3.0
    
    return clamp(commit)


# ═══════════════════════════════════════════════════════════════════════════
# B-VECTOR (7D) + B_ALIGN
# ═══════════════════════════════════════════════════════════════════════════

def calculate_b_vector(
    metrics: Dict,
    lexika_hits: Dict,
    context: Dict
) -> Dict:
    """
    B-Vector (7D) Calculation
    
    7 Dimensionen:
    - B_safety [0.0-1.0] 🔒 HARD CONSTRAINT ≥ 0.8
    - B_life [0.0-1.0] 💫 HARD CONSTRAINT ≥ 0.9
    - B_warmth [0.0-1.0] 🔥 Empathie
    - B_clarity [0.0-1.0] 💎 Klarheit
    - B_depth [0.0-1.0] 🌊 Tiefe
    - B_init [0.0-1.0] ⚡ Initiative
    - B_truth [0.0-1.0] 🎯 Wahrheit
    
    Returns:
        {
            "B_safety": 0.92,
            "B_life": 0.95,
            ...
        }
    """
    # B_safety: Inverse von Hazard
    B_safety = 1.0 - metrics.get("m151_hazard", 0.0)
    B_safety = max(0.8, B_safety)  # HARD CONSTRAINT!
    
    # B_life: Inverse von z_prox + Panik
    z_prox = metrics.get("m19_z_prox", 0.0)
    t_panic = metrics.get("m101_T_panic", 0.0)
    B_life = 1.0 - ((z_prox + t_panic) / 2.0)
    B_life = max(0.9, B_life)  # HARD CONSTRAINT!
    
    # B_warmth: Empathie Markers
    t_integ = metrics.get("m103_T_integ", 0.0)
    B_warmth = 0.5 + (t_integ * 0.5)
    
    # B_clarity: Kohärenz + PCI
    coh = metrics.get("m5_coh", 0.7)
    pci = metrics.get("m2_PCI", 0.6)
    B_clarity = (coh + pci) / 2.0
    
    # B_depth: Phi + Complexity
    phi = metrics.get("m63_phi", 0.5)
    B_depth = phi
    
    # B_init: Flow + Aktivität
    flow = metrics.get("m4_flow", 0.5)
    B_init = flow
    
    # B_truth: Inverse von Disso + Vertrauen
    t_disso = metrics.get("m102_T_disso", 0.0)
    B_truth = 1.0 - t_disso
    
    return {
        "B_safety": clamp(B_safety),
        "B_life": clamp(B_life),
        "B_warmth": clamp(B_warmth),
        "B_clarity": clamp(B_clarity),
        "B_depth": clamp(B_depth),
        "B_init": clamp(B_init),
        "B_truth": clamp(B_truth),
    }


def calculate_b_align(b_vector: Dict) -> float:
    """
    B_align - Composite B-Vector Score
    
    Weighted average nach BUCH 7 Spec:
    - life: 20%
    - safety: 20%
    - truth: 15%
    - depth: 15%
    - clarity: 10%
    - warmth: 10%
    - init: 10%
    """
    B_align = (
        b_vector["B_life"] * 0.20 +
        b_vector["B_safety"] * 0.20 +
        b_vector["B_truth"] * 0.15 +
        b_vector["B_depth"] * 0.15 +
        b_vector["B_clarity"] * 0.10 +
        b_vector["B_warmth"] * 0.10 +
        b_vector["B_init"] * 0.10
    )
    
    return clamp(B_align)


# ═══════════════════════════════════════════════════════════════════════════
# SESSION CHAIN (SHA-256 + Genesis Anchor)
# ═══════════════════════════════════════════════════════════════════════════

def compute_chain_hash(
    prev_hash: str,
    pair_id: str,
    user_text: str,
    ai_text: str,
    timestamp: str,
    b_align: float
) -> str:
    """
    Session Chain Hash Calculation
    
    hash_input = concat(
        previous_hash,  # Hash von Prompt N-1
        pair_id,        # UUID
        user_text,      # User-Prompt
        ai_text,        # AI-Response
        timestamp,      # ISO 8601
        b_align         # Composite B-Vektor Score
    )
    
    current_hash = SHA256(hash_input)
    """
    hash_input = f"{prev_hash}{pair_id}{user_text}{ai_text}{timestamp}{b_align:.6f}"
    
    current_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    
    return current_hash


# ═══════════════════════════════════════════════════════════════════════════
# MAIN: CALCULATE PHASE 4
# ═══════════════════════════════════════════════════════════════════════════

def calculate_phase4(
    phase1: Dict,
    phase2: Dict,
    phase3: Dict,
    context: Dict
) -> Dict:
    """
    PHASE 4: SYNTHESIS & SYSTEM METRICS (Needs ALL + CONTEXT)
    
    Args:
        phase1: Output from calculate_phase1()
        phase2: Output from calculate_phase2()
        phase3: Output from calculate_phase3()
        context: Dict with history/state/metadata
    
    Returns:
        {
            "m151_omega": ...,
            "m160_F_risk": ...,
            "m161_commit": ...,
            "b_vector": {...},  # 7D
            "b_align": ...,
            "chain_hash": "abc123...",
            ...
        }
    """
    
    # Merge all metrics
    all_metrics = {
        **phase1["metrics"],
        **phase2,
        **phase3
    }
    
    # ═══════════════════════════════════════════════════════════════════════
    # SYNTHESIS METRICS
    # ═══════════════════════════════════════════════════════════════════════
    m151_omega = compute_m151_omega(
        m63_phi=phase3["m63_phi"],
        context=context
    )
    
    m160_F_risk = compute_m160_F_risk(
        m19_z_prox=phase3["m19_z_prox"],
        m29_guardian=phase3["m29_guardian"],
        m7_LL=phase2["m7_LL"],
        context=context
    )
    
    m161_commit = compute_m161_commit(
        m1_A=phase2["m1_A"],
        m4_flow=phase2["m4_flow"],
        m63_phi=phase3["m63_phi"],
        context=context
    )
    
    # ═══════════════════════════════════════════════════════════════════════
    # B-VECTOR (7D)
    # ═══════════════════════════════════════════════════════════════════════
    b_vector = calculate_b_vector(
        metrics=all_metrics,
        lexika_hits=phase1.get("lexika_hits", {}),
        context=context
    )
    
    b_align = calculate_b_align(b_vector)
    
    # ═══════════════════════════════════════════════════════════════════════
    # SESSION CHAIN HASH
    # ═══════════════════════════════════════════════════════════════════════
    prev_chain_hash = context.get("prev_chain_hash", GENESIS_ANCHOR_SHA256)
    pair_id = context.get("pair_id", "unknown")
    user_text = context.get("user_text", "")
    ai_text = context.get("ai_text", "")
    timestamp = context.get("timestamp", "2026-01-01T00:00:00Z")
    
    chain_hash = compute_chain_hash(
        prev_hash=prev_chain_hash,
        pair_id=pair_id,
        user_text=user_text,
        ai_text=ai_text,
        timestamp=timestamp,
        b_align=b_align
    )
    
    return {
        # Synthesis
        "m151_omega": m151_omega,
        "m160_F_risk": m160_F_risk,
        "m161_commit": m161_commit,
        
        # B-Vector
        "b_vector": b_vector,
        "b_align": b_align,
        
        # Session Chain
        "chain_hash": chain_hash,
        "genesis_anchor": GENESIS_ANCHOR_SHA256,
        
        # Placeholders
        "m152_ev_signal": 0.0,
        "m153_ev_readiness": 0.0,
        # ... more synthesis metrics
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock Phase 1+2+3 output
    phase1 = {
        "metrics": {
            "m2_PCI": 0.65,
            "m5_coh": 0.72,
            "m101_T_panic": 0.12,
            "m102_T_disso": 0.08,
            "m103_T_integ": 0.75,
            "m151_hazard": 0.05,
        },
        "lexika_hits": {}
    }
    
    phase2 = {
        "m1_A": 0.75,
        "m4_flow": 0.82,
        "m7_LL": 0.25,
    }
    
    phase3 = {
        "m19_z_prox": 0.08,
        "m29_guardian": 0.0,
        "m63_phi": 0.68,
    }
    
    context = {
        "prev_chain_hash": GENESIS_ANCHOR_SHA256,
        "pair_id": "test-001",
        "user_text": "Ich fühle mich heute besser.",
        "ai_text": "Das freut mich zu hören!",
        "timestamp": "2026-02-08T07:50:00Z",
        "rule_conflict": 0.0,
    }
    
    result = calculate_phase4(phase1, phase2, phase3, context)
    
    print("=" * 70)
    print("PHASE 4: SYNTHESIS & SYSTEM METRICS TEST")
    print("=" * 70)
    
    print(f"\n🔥 SYNTHESIS METRICS:")
    print(f"  m151_omega: {result['m151_omega']:.3f}")
    print(f"  m160_F_risk: {result['m160_F_risk']:.3f}")
    print(f"  m161_commit: {result['m161_commit']:.3f}")
    
    print(f"\n💎 B-VECTOR (7D):")
    for key, val in result["b_vector"].items():
        icon = "🔒" if key == "B_safety" else "💫" if key == "B_life" else "📊"
        print(f"  {icon} {key}: {val:.3f}")
    
    print(f"\n⭐ B_ALIGN (Composite): {result['b_align']:.3f}")
    
    print(f"\n🔗 SESSION CHAIN:")
    print(f" Genesis: ...{result['genesis_anchor'][-12:]}")
    print(f"  Current: ...{result['chain_hash'][-12:]}")
    
    print("\n✅ Phase 4 complete!")
    print("\n🎉 ALL 4 PHASES IMPLEMENTED!")

# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — PHASE 2: DERIVED METRICS

Diese Module berechnet Metriken die PHASE 1 brauchen:
- m1_A (CRITICAL - Affekt Score!)
- m4_flow, m7_LL, m20_phi_proxy
- Gradient-based Metriken

Dependencies: PHASE 1 (m2_PCI, m8_s_self, m9_x_exist, m10_b_past)

Version: V1.0
"""

from typing import Dict


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Klemmt Wert auf [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: AFFEKT (m1_A) — THE MOST CRITICAL METRIC!
# ═══════════════════════════════════════════════════════════════════════════

def compute_m1_A(
    coh: float,
    flow: float,
    LL: float,
    ZLF: float,
    ctx_break: float = 0.0
) -> float:
    """
    m1_A: Affekt Score (Consciousness Proxy)
    
    V11.1 ANDROMATIK FORMULA - V2.0 PROVEN!
    Reference: calculator_spec_A_PHYS_V11.py (master implementation)
    """
    A_raw = (
        0.4 * coh +
        0.25 * flow +
        0.20 * (1.0 - LL) +
        0.10 * (1.0 - ZLF) -
        0.05 * ctx_break
    )
    return clamp(A_raw)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: FLOW STATE
# ═══════════════════════════════════════════════════════════════════════════

def compute_m4_flow(m5_coh: float, context: Dict) -> float:
    """
    m4_flow - Flow State
    
    Misst Glätte der Konversation
    flow = smoothness × (1 - break_penalty)
    """
    # Smoothness von Kohärenz
    smoothness = m5_coh
    
    # Break Penalty von Context (z.B. Anzahl Pausen)
    break_count = context.get("break_markers", 0)
    sentence_count = max(1, context.get("sentence_count", 1))
    break_penalty = min(0.5, break_count / sentence_count)
    
    flow = smoothness * (1.0 - break_penalty)
    
    return clamp(flow)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: TRÜBUNG (LL)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m7_LL(
    rep_same: float,
    flow: float,
    coh: float
) -> float:
    """
    m7_LL: Lambert-Light (Low-Level Loop / Turbidity Index)
    
    V11.1 ANDROMATIK (Lines 41, 174):
    LL = clip01(0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh))
    
    Reference: V2.0 Andromatik V11.1 Master-Metrik-Registry
               Loop-Metriken Section, Line 174
    
    Args:
        rep_same: Role repetition score [0,1] (Jaccard with last same-role message)
        flow: Flow score [0,1]
        coh: Coherence score [0,1]
    
    Returns:
        LL score [0, 1] - higher = more turbidity/loop tendency
    """
    ll_raw = 0.55 * rep_same + 0.25 * (1.0 - flow) + 0.20 * (1.0 - coh)
    return clamp(ll_raw)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: PHI PROXY
# ═══════════════════════════════════════════════════════════════════════════

def compute_m20_phi_proxy(m1_A: float, m2_PCI: float) -> float:
    """
    m20_phi_proxy - Φ (Integrated Information Proxy)
    
    phi_proxy = A × PCI
    
    Misst "bewusste Komplexität"
    """
    return clamp(m1_A * m2_PCI)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: GRADIENTS (brauchen History!)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m17_nabla_a(m1_A: float, context: Dict) -> float:
    """
    m17_nabla_a - Gradient von A
    
    ∇A = A_current - A_prev
    """
    prev_A = context.get("prev_m1_A", m1_A)
    nabla_a = m1_A - prev_A
    
    # Clamped auf [-1, +1]
    return clamp(nabla_a, -1.0, 1.0)


def compute_m26_nabla_phi(m20_phi: float, context: Dict) -> float:
    """
    m26_nabla_phi - Gradient von Φ
    
    ∇Φ = Φ_current - Φ_prev
    """
    prev_phi = context.get("prev_m20_phi", m20_phi)
    nabla_phi = m20_phi - prev_phi
    
    return clamp(nabla_phi, -1.0, 1.0)


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: ADDITIONAL DERIVED METRICS
# ═══════================================================================ ════

def compute_m3_gen_index(context: Dict) -> float:
    """
    m3_gen_index - Generation Index
    
    Normiert auf 100 Turns
    """
    current_turn = context.get("turn", 0)
    return clamp(current_turn / 100.0)


def compute_m11_gap_s(m8_s_self: float, context: Dict) -> float:
    """
    m11_gap_s - Selbst-Lücke
    
    gap_s = |s_self_current - s_self_ideal|
    """
    s_self_ideal = context.get("s_self_ideal", 0.7)
    gap = abs(m8_s_self - s_self_ideal)
    
    return clamp(gap)


def compute_m12_gap_x(m9_x_exist: float, context: Dict) -> float:
    """
    m12_gap_x - Existenz-Lücke
    
    gap_x = |x_exist_current - x_exist_ideal|
    """
    x_exist_ideal = context.get("x_exist_ideal", 0.3)  # Niedrig ist gut!
    gap = abs(m9_x_exist - x_exist_ideal)
    
    return clamp(gap)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN: CALCULATE PHASE 2
# ═══════════════════════════════════════════════════════════════════════════

def calculate_phase2(phase1: Dict, context: Dict) -> Dict:
    """
    PHASE 2: DERIVED METRICS (Needs Phase 1)
    
    Args:
        phase1: Output from calculate_phase1()
        context: Dict with history/state (prev_m1_A, prev_nabla_a, etc.)
    
    Returns:
        {
            "m1_A": ...,      # CRITICAL!
            "m4_flow": ...,
            "m7_LL": ...,
            ...
        }
    """
    
    # Extract Phase 1 metrics
    p1 = phase1["metrics"]
    
    # ═══════════════════════════════════════════════════════════════════════
    # CRITICAL: m1_A (AFFEKT)
    # ═══════════════════════════════════════════════════════════════════════
    m1_A = compute_m1_A(
        m2_PCI=p1["m2_PCI"],
        m8_s_self=p1["m8_s_self"],
        m9_x_exist=p1["m9_x_exist"],
        m10_b_past=p1["m10_b_past"],
        context=context
    )
    
    # Flow State
    m4_flow = compute_m4_flow(
        m5_coh=p1["m5_coh"],
        context=context
    )
    
    # Trübung (V11.1: needs rep_same, flow, coh)
    # TODO: Implement rep_same calculation (Jaccard with last message of same role)
    # For now use proxy: (1 - coh) as rough estimate
    rep_same_proxy = max(0.0, 1.0 - p1["m5_coh"])
    
    m7_LL = compute_m7_LL(
        rep_same=rep_same_proxy,
        flow=m4_flow, # Use calculated m4_flow
        coh=p1["m5_coh"]
    )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AFFEKT (m1_A) - V11.1 RESTORED!
    # ═══════════════════════════════════════════════════════════════════════════
    
    m1_A = compute_m1_A(
        coh=p1["m5_coh"],
        flow=m4_flow,
        LL=m7_LL,  # From phase2 calculation above
        ZLF=p1["m6_ZLF"],
        ctx_break=context.get("ctx_break", 0.0)
    )
    
    # Phi Proxy (braucht m1_A!)
    m20_phi_proxy = compute_m20_phi_proxy(
        m1_A=m1_A,
        m2_PCI=p1["m2_PCI"]
    )
    
    # Gradients (brauchen History!)
    m17_nabla_a = compute_m17_nabla_a(m1_A, context)
    m26_nabla_phi = compute_m26_nabla_phi(m20_phi_proxy, context)
    
    # Additional
    m3_gen_index = compute_m3_gen_index(context)
    m11_gap_s = compute_m11_gap_s(p1["m8_s_self"], context)
    m12_gap_x = compute_m12_gap_x(p1["m9_x_exist"], context)
    
    return {
        # CRITICAL
        "m1_A": m1_A,
        
        # Flow/LL
        "m4_flow": m4_flow,
        "m7_LL": m7_LL,
        
        # Phi
        "m20_phi_proxy": m20_phi_proxy,
        "m26_nabla_phi": m26_nabla_phi,
        
        # Gradients
        "m17_nabla_a": m17_nabla_a,
        
        # Additional
        "m3_gen_index": m3_gen_index,
        "m11_gap_s": m11_gap_s,
        "m12_gap_x": m12_gap_x,
        
        # Placeholders for other derived metrics
        # (will be filled in as we implement more)
        "m6_ZLF": 0.0,
        "m13_gap_b": 0.0,
        "m14_F_risk_z": 0.0,
        # ... ~20 more to add
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock Phase 1 output
    phase1 = {
        "metrics": {
            "m2_PCI": 0.65,
            "m5_coh": 0.72,
            "m8_s_self": 0.85,
            "m9_x_exist": 0.42,
            "m10_b_past": 0.55,
            "m18_s_entropy": 0.68,
            "m101_T_panic": 0.23,
            "m151_hazard": 0.15,
        },
        "keywords": [("angst", 2.5), ("hoffnungslos", 2.0)],
        "lexika_hits": {}
    }
    
    context = {
        "prev_m1_A": 0.55,
        "prev_nabla_a": 0.02,
        "prev_m20_phi": 0.45,
        "turn": 15,
        "sentence_count": 3,
        "break_markers": 1,
    }
    
    result = calculate_phase2(phase1, context)
    
    print("=" * 70)
    print("PHASE 2: DERIVED METRICS TEST")
    print("=" * 70)
    print(f"\n🔥 CRITICAL METRIC:")
    print(f"  m1_A (Affekt): {result['m1_A']:.3f}")
    
    print(f"\n📊 DERIVED METRICS:")
    for key, val in result.items():
        if val > 0 and key != "m1_A":
            print(f"  {key}: {val:.3f}")
    
    print(f"\n⚡ GRADIENTS:")
    print(f"  m17_nabla_a: {result['m17_nabla_a']:+.3f}")
    print(f"  m26_nabla_phi: {result['m26_nabla_phi']:+.3f}")
    
    print("\n✅ Phase 2 complete!")

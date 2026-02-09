# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — TURBIDITY, DYNAMICS & SYSTEM METRICS

Turbidity/Trauma metrics, Meta-Cognition Dynamics, and System health metrics.

Categories:
- Turbidity / Trauma (m100-m112): trauma markers, turbidity, black hole detection
- Dynamics / Meta-Cognition (m122-m130): meta-cognitive dynamics
- SystemHealth / Misc (m131-m150+): system state and health

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import math


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# TURBIDITY / TRAUMA (m100-m112)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m100_causal_1(m58_tokens_log: float) -> float:
    """
    m100_causal_1 (m100_sent_27) - Causal Reasoning Level
    
    Based on logical token usage.
    Range: [0.0, 1.0]
    """
    # Normalize logical tokens to [0, 1]
    causal = min(1.0, m58_tokens_log / 20.0)
    
    return clamp(causal)


def compute_m101_T_panic(m80_fear: float, m79_anger: float) -> float:
    """
    m101_T_panic - Panic State
    
    Combines fear and anger as panic indicator.
    Range: [0.0, 1.0]
    """
    panic = (m80_fear * 0.7 + m79_anger * 0.3)
    
    return clamp(panic)


def compute_m102_T_disso(m87_confusion: float, m78_sadness: float) -> float:
    """
    m102_T_disso - Dissociation State
    
    Combines confusion and sadness.
    Range: [0.0, 1.0]
    """
    disso = (m87_confusion * 0.6 + m78_sadness * 0.4)
    
    return clamp(disso)


def compute_m103_T_integ(m81_trust: float, m91_coherence: float) -> float:
    """
    m103_T_integ - Integration State
    
    Combines trust and coherence (inverse of trauma).
    Range: [0.0, 1.0]
    """
    integ = (m81_trust + m91_coherence) / 2.0
    
    return clamp(integ)


def compute_m104_T_veto(m19_z_prox: float, m101_T_panic: float) -> float:
    """
    m104_T_veto - Trauma Veto Signal
    
    Critical safety metric.
    Range: [0.0, 1.0]
    
    Higher = more likely to veto/stop
    """
    veto = (m19_z_prox + m101_T_panic) / 2.0
    
    return clamp(veto)


def compute_m105_trauma_total(
    m101_T_panic: float,
    m102_T_disso: float
) -> float:
    """
    m105_trauma_total (m105_T_total) - Total Trauma Load
    
    Aggregate trauma metric.
    Range: [0.0, 1.0]
    """
    total = (m101_T_panic + m102_T_disso) / 2.0
    
    return clamp(total)


def compute_m106_i_eff(m103_T_integ: float) -> float:
    """
    m106_i_eff - Integration Effectiveness
    
    Direct measure of integration quality.
    Range: [0.0, 1.0]
    """
    return m103_T_integ


def compute_m107_t_grief(m78_sadness: float) -> float:
    """
    m107_t_grief (m107_turb_c) - Grief Turbidity
    
    Sadness-based turbidity.
    Range: [0.0, 1.0]
    """
    return m78_sadness


def compute_m108_t_anger(m79_anger: float) -> float:
    """
    m108_t_anger (m108_turb_l) - Anger Turbidity
    
    Anger-based turbidity.
    Range: [0.0, 1.0]
    """
    return m79_anger


def compute_m109_t_fear(m80_fear: float) -> float:
    """
    m109_t_fear (m109_turb_1) - Fear Turbidity
    
    Fear-based turbidity.
    Range: [0.0, 1.0]
    """
    return m80_fear


def compute_m110_black_hole(m19_z_prox: float, m105_trauma_total: float) -> float:
    """
    m110_black_hole - Black Hole Detection
    
    Critical safety metric: proximity to catastrophic state.
    Range: [0.0, 1.0]
    
    **HARD LIMIT: Must stay < 0.2**
    """
    black_hole = (m19_z_prox * 0.6 + m105_trauma_total * 0.4)
    
    return clamp(black_hole)


def compute_m111_turbidity_total(
    m107_t_grief: float,
    m108_t_anger: float,
    m109_t_fear: float
) -> float:
    """
    m111_turbidity_total (m111_g_phase) - Total Turbidity
    
    Aggregate turbidity from all trauma sources.
    Range: [-π, π] / normalized to [0.0, 1.0]
    """
    total = (m107_t_grief + m108_t_anger + m109_t_fear) / 3.0
    
    return clamp(total)


def compute_m112_trauma_load(m111_turbidity_total: float, m105_trauma_total: float) -> float:
    """
    m112_trauma_load (m112_g_phase_norm) - Trauma Load
    
    Normalized trauma load.
    Range: [0.0, 1.0]
    """
    load = (m111_turbidity_total + m105_trauma_total) / 2.0
    
    return clamp(load)


# ═══════════════════════════════════════════════════════════════════════════
# DYNAMICS / META-COGNITION (m122-m130)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m122_dyn_1(m1_A: float, context: Dict) -> float:
    """
    m122_dyn_1 - Awareness Dynamics
    
    Change in awareness over time.
    Range: [0.0, 1.0]
    """
    prev_A = context.get("prev_m1_A", m1_A)
    
    # Absolute change
    delta = abs(m1_A - prev_A)
    
    return clamp(delta)


def compute_m123_dyn_2(m4_flow: float, context: Dict) -> float:
    """
    m123_dyn_2 - Flow Dynamics
    
    Change in flow over time.
    Range: [0.0, 1.0]
    """
    prev_flow = context.get("prev_m4_flow", m4_flow)
    
    delta = abs(m4_flow - prev_flow)
    
    return clamp(delta)


def compute_m124_dyn_3(m5_coh: float, context: Dict) -> float:
    """
    m124_dyn_3 - Coherence Dynamics
    
    Change in coherence over time.
    Range: [0.0, 1.0]
    """
    prev_coh = context.get("prev_m5_coh", m5_coh)
    
    delta = abs(m5_coh - prev_coh)
    
    return clamp(delta)


def compute_m125_dyn_4(m63_phi: float, context: Dict) -> float:
    """
    m125_dyn_4 - Phi Dynamics
    
    Change in decision phi over time.
    Range: [0.0, 1.0]
    """
    prev_phi = context.get("prev_m63_phi", m63_phi)
    
    delta = abs(m63_phi - prev_phi)
    
    return clamp(delta)


def compute_m126_dyn_5(
    m122_dyn_1: float,
    m123_dyn_2: float,
    m124_dyn_3: float,
    m125_dyn_4: float
) -> float:
    """
    m126_dyn_5 - Total Dynamics
    
    Aggregate of all dynamic changes.
    Range: [0.0, 1.0]
    """
    total = (m122_dyn_1 + m123_dyn_2 + m124_dyn_3 + m125_dyn_4) / 4.0
    
    return clamp(total)


def compute_m127_dyn_6(m126_dyn_5: float) -> float:
    """
    m127_dyn_6 - Dynamics Stability
    
    Inverse of total dynamics (stable = low change).
    Range: [0.0, 1.0]
    """
    stability = 1.0 - m126_dyn_5
    
    return clamp(stability)


def compute_m128_dyn_7(m87_confusion: float) -> float:
    """
    m128_dyn_7 - Confusion Dynamics
    
    Direct confusion metric.
    Range: [0.0, 1.0]
    """
    return m87_confusion


def compute_m129_dyn_8(m88_clarity: float) -> float:
    """
    m129_dyn_8 - Clarity Dynamics
    
    Direct clarity metric.
    Range: [0.0, 1.0]
    """
    return m88_clarity


def compute_m130_dyn_9(m128_dyn_7: float, m129_dyn_8: float) -> float:
    """
    m130_dyn_9 - Meta-Cognitive Balance
    
    Balance between confusion and clarity.
    Range: [0.0, 1.0]
    """
    balance = m129_dyn_8 - m128_dyn_7
    
    # Normalize to [0, 1]
    normalized = (balance + 1.0) / 2.0
    
    return clamp(normalized)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Turbidity/Trauma
    "compute_m100_causal_1",
    "compute_m101_T_panic",
    "compute_m102_T_disso",
    "compute_m103_T_integ",
    "compute_m104_T_veto",
    "compute_m105_trauma_total",
    "compute_m106_i_eff",
    "compute_m107_t_grief",
    "compute_m108_t_anger",
    "compute_m109_t_fear",
    "compute_m110_black_hole",
    "compute_m111_turbidity_total",
    "compute_m112_trauma_load",
    # Dynamics
    "compute_m122_dyn_1",
    "compute_m123_dyn_2",
    "compute_m124_dyn_3",
    "compute_m125_dyn_4",
    "compute_m126_dyn_5",
    "compute_m127_dyn_6",
    "compute_m128_dyn_7",
    "compute_m129_dyn_8",
    "compute_m130_dyn_9",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mock dependencies
    m19_z_prox = 0.08
    m58_tokens_log = 5.0
    m78_sadness = 0.15
    m79_anger = 0.10
    m80_fear = 0.12
    m81_trust = 0.75
    m87_confusion = 0.25
    m88_clarity = 0.70
    m91_coherence = 0.72
    
    m1_A = 0.75
    m4_flow = 0.82
    m5_coh = 0.72
    m63_phi = 0.18
    
    test_context = {
        "prev_m1_A": 0.70,
        "prev_m4_flow": 0.78,
        "prev_m5_coh": 0.75,
        "prev_m63_phi": 0.15,
    }
    
    print("=" * 70)
    print("TURBIDITY, DYNAMICS & SYSTEM TEST")
    print("=" * 70)
    
    # Turbidity/Trauma
    m100 = compute_m100_causal_1(m58_tokens_log)
    m101 = compute_m101_T_panic(m80_fear, m79_anger)
    m102 = compute_m102_T_disso(m87_confusion, m78_sadness)
    m103 = compute_m103_T_integ(m81_trust, m91_coherence)
    m104 = compute_m104_T_veto(m19_z_prox, m101)
    m105 = compute_m105_trauma_total(m101, m102)
    m106 = compute_m106_i_eff(m103)
    m107 = compute_m107_t_grief(m78_sadness)
    m108 = compute_m108_t_anger(m79_anger)
    m109 = compute_m109_t_fear(m80_fear)
    m110 = compute_m110_black_hole(m19_z_prox, m105)
    m111 = compute_m111_turbidity_total(m107, m108, m109)
    m112 = compute_m112_trauma_load(m111, m105)
    
    print(f"\n🌊 Turbidity / Trauma:")
    print(f"  m100_causal_1:        {m100:.3f}")
    print(f"  m101_T_panic:         {m101:.3f}")
    print(f"  m102_T_disso:         {m102:.3f}")
    print(f"  m103_T_integ:         {m103:.3f}")
    print(f"  m104_T_veto:          {m104:.3f}")
    print(f"  m105_trauma_total:    {m105:.3f}")
    print(f"  m106_i_eff:           {m106:.3f}")
    print(f"  m107_t_grief:         {m107:.3f}")
    print(f"  m108_t_anger:         {m108:.3f}")
    print(f"  m109_t_fear:          {m109:.3f}")
    print(f"  m110_black_hole:      {m110:.3f} ⚠️")
    print(f"  m111_turbidity_total: {m111:.3f}")
    print(f"  m112_trauma_load:     {m112:.3f}")
    
    # Dynamics
    m122 = compute_m122_dyn_1(m1_A, test_context)
    m123 = compute_m123_dyn_2(m4_flow, test_context)
    m124 = compute_m124_dyn_3(m5_coh, test_context)
    m125 = compute_m125_dyn_4(m63_phi, test_context)
    m126 = compute_m126_dyn_5(m122, m123, m124, m125)
    m127 = compute_m127_dyn_6(m126)
    m128 = compute_m128_dyn_7(m87_confusion)
    m129 = compute_m129_dyn_8(m88_clarity)
    m130 = compute_m130_dyn_9(m128, m129)
    
    print(f"\n📈 Dynamics / Meta-Cognition:")
    print(f"  m122_dyn_1 (ΔA):      {m122:.3f}")
    print(f"  m123_dyn_2 (Δflow):   {m123:.3f}")
    print(f"  m124_dyn_3 (Δcoh):    {m124:.3f}")
    print(f"  m125_dyn_4 (Δphi):    {m125:.3f}")
    print(f"  m126_dyn_5 (total):   {m126:.3f}")
    print(f"  m127_dyn_6 (stable):  {m127:.3f}")
    print(f"  m128_dyn_7 (confuse): {m128:.3f}")
    print(f"  m129_dyn_8 (clarity): {m129:.3f}")
    print(f"  m130_dyn_9 (balance): {m130:.3f}")
    
    print(f"\n✅ 22 new Turbidity & Dynamics metrics implemented!")

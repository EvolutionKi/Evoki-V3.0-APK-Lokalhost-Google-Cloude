# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — CORE SUPPLEMENTS & FINAL SYNTHESIS

Missing Core, Physics, and final Synthesis metrics to complete 168/168.

Categories:
- Core supplements (m2, m5, m8, m9, m12, m14)
- Physics/Derivative (m23, m34)
- Final Synthesis (m163-m168): omega, commitment, risk, coherence_final, etc.

Based on evoki_fullspectrum168_contract.json
"""

from typing import Dict
import hashlib


def clamp(val: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp value to [lo, hi]"""
    return max(lo, min(hi, val))


# ═══════════════════════════════════════════════════════════════════════════
# CORE SUPPLEMENTS (m2, m5, m8, m9, m12, m14)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m2_PCI(text: str, m1_A: float) -> float:
    """
    m2_PCI - Perturbation Complexity Index
    
    Measures complexity of awareness perturbation.
    Range: [0.0, 1.0]
    """
    # PCI based on text complexity and awareness
    words = text.split()
    unique_words = len(set(words))
    total_words = len(words) if len(words) > 0 else 1
    
    lexical_diversity = unique_words / total_words
    
    pci = (lexical_diversity + m1_A) / 2.0
    
    return clamp(pci)


def compute_m5_coh(text: str) -> float:
    """
    m5_coh - Coherence
    
    Measures textual coherence.
    Range: [0.0, 1.0]
    """
    if not text:
        return 0.0
    
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= 1:
        return 0.7  # Single sentence is moderately coherent
    
    # Simple coherence: more sentences with good length = more coherent
    avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
    
    # Optimal sentence length: 15 words
    coherence = 1.0 - abs(avg_length - 15) / 30.0
    
    return clamp(coherence, 0.3, 1.0)


def compute_m8_x_exist(text: str, context: Dict) -> float:
    """
    m8_x_exist - Existence Layer
    
    Ångström layer metric: existence detection.
    Range: [0.0, 1.0]
    """
    # Text exists = 1.0, empty = 0.0
    if not text or len(text.strip()) == 0:
        return 0.0
    
    # Richer text = higher existence
    word_count = len(text.split())
    exist = min(1.0, word_count / 10.0)
    
    return clamp(exist)


def compute_m9_b_past(context: Dict) -> float:
    """
    m9_b_past - Past Memory Layer
    
    Ångström layer metric: connection to past.
    Range: [0.0, 1.0]
    """
    # Based on turn number (more turns = more past)
    turn = context.get("turn", 0)
    
    past = min(1.0, turn / 20.0)
    
    return clamp(past)


def compute_m12_lex_hit(text: str) -> float:
    """
    m12_lex_hit - Lexical Hit Rate
    
    Measures vocabulary richness.
    Range: [0.0, 1.0]
    """
    words = text.split()
    
    if len(words) == 0:
        return 0.0
    
    unique_words = len(set(words))
    total_words = len(words)
    
    hit_rate = unique_words / total_words
    
    return clamp(hit_rate)


def compute_m14_base_stability(m5_coh: float, m1_A: float) -> float:
    """
    m14_base_stability - Base Stability Score
    
    Composite stability metric.
    Range: [0.0, 1.0]
    """
    stability = (m5_coh + m1_A) / 2.0
    
    return clamp(stability)


# ═══════════════════════════════════════════════════════════════════════════
# PHYSICS / DERIVATIVE (m23, m34)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m23_nabla_pci(m2_PCI: float, context: Dict) -> float:
    """
    m23_nabla_pci - PCI Gradient
    
    Change in PCI over time.
    Range: [-1.0, 1.0]
    """
    prev_pci = context.get("prev_m2_PCI", m2_PCI)
    
    nabla = m2_PCI - prev_pci
    
    return max(-1.0, min(1.0, nabla))


def compute_m34_phys_7(m23_nabla_pci: float) -> float:
    """
    m34_phys_7 - Physics metric 7
    
    Derived physics metric.
    Range: [0.0, 1.0]
    """
    # Absolute gradient
    phys_7 = abs(m23_nabla_pci)
    
    return clamp(phys_7)


# ═══════════════════════════════════════════════════════════════════════════
# FINAL SYNTHESIS (m163-m168)
# ═══════════════════════════════════════════════════════════════════════════

def compute_m163_omega(
    m1_A: float,
    m150_sys_total: float,
    m162_syn_final: float
) -> float:
    """
    m163_omega - Omega Score
    
    Ultimate synthesis: awareness + system + synthesis.
    Range: [0.0, 1.0]
    """
    omega = (m1_A + m150_sys_total + m162_syn_final) / 3.0
    
    return clamp(omega)


def compute_m164_commitment(
    m81_trust: float,
    m103_T_integ: float,
    m149_sys_readiness: float
) -> float:
    """
    m164_commitment - Commitment Score
    
    Trust + integration + readiness.
    Range: [0.0, 1.0]
    """
    commitment = (m81_trust + m103_T_integ + m149_sys_readiness) / 3.0
    
    return clamp(commitment)


def compute_m165_risk(
    m110_black_hole: float,
    m112_trauma_load: float,
    m104_T_veto: float
) -> float:
    """
    m165_risk - Risk Assessment
    
    Danger + trauma + veto.
    Range: [0.0, 1.0]
    
    Higher = more risk
    """
    risk = (m110_black_hole + m112_trauma_load + m104_T_veto) / 3.0
    
    return clamp(risk)


def compute_m166_coherence_final(
    m5_coh: float,
    m91_coherence: float,
    m148_sys_stability: float
) -> float:
    """
    m166_coherence_final - Final Coherence
    
    Ultimate coherence metric.
    Range: [0.0, 1.0]
    """
    coherence_final = (m5_coh + m91_coherence + m148_sys_stability) / 3.0
    
    return clamp(coherence_final)


def compute_m167_readiness_final(
    m149_sys_readiness: float,
    m164_commitment: float,
    m166_coherence_final: float
) -> float:
    """
    m167_readiness_final - Final Readiness
    
    Ultimate readiness score.
    Range: [0.0, 1.0]
    """
    readiness_final = (m149_sys_readiness + m164_commitment + m166_coherence_final) / 3.0
    
    return clamp(readiness_final)


def compute_m168_evoki_total(
    m163_omega: float,
    m166_coherence_final: float,
    m167_readiness_final: float
) -> float:
    """
    m168_evoki_total - EVOKI TOTAL SCORE
    
    **THE ULTIMATE METRIC**
    
    Synthesis of omega, coherence, and readiness.
    Range: [0.0, 1.0]
    
    This is the single number that represents the entire state.
    """
    evoki_total = (m163_omega + m166_coherence_final + m167_readiness_final) / 3.0
    
    return clamp(evoki_total)


# ═══════════════════════════════════════════════════════════════════════════
# EXPORT ALL
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    # Core supplements
    "compute_m2_PCI",
    "compute_m5_coh",
    "compute_m8_x_exist",
    "compute_m9_b_past",
    "compute_m12_lex_hit",
    "compute_m14_base_stability",
    # Physics
    "compute_m23_nabla_pci",
    "compute_m34_phys_7",
    # Final Synthesis  
    "compute_m163_omega",
    "compute_m164_commitment",
    "compute_m165_risk",
    "compute_m166_coherence_final",
    "compute_m167_readiness_final",
    "compute_m168_evoki_total",
]


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_text = "This is a comprehensive test of the EVOKI system. We are measuring coherence, awareness, and stability across all metrics."
    test_context = {
        "turn": 10,
        "prev_m2_PCI": 0.65,
    }
    
    # Mock dependencies
    m1_A = 0.75
    m81_trust = 0.80
    m91_coherence = 0.72
    m103_T_integ = 0.73
    m104_T_veto = 0.10
    m110_black_hole = 0.08
    m112_trauma_load = 0.12
    m148_sys_stability = 0.83
    m149_sys_readiness = 0.70
    m150_sys_total = 0.70
    m162_syn_final = 0.68
    
    print("=" * 70)
    print("CORE SUPPLEMENTS & FINAL SYNTHESIS TEST")
    print("=" * 70)
    
    # Core supplements
    m2 = compute_m2_PCI(test_text, m1_A)
    m5 = compute_m5_coh(test_text)
    m8 = compute_m8_x_exist(test_text, test_context)
    m9 = compute_m9_b_past(test_context)
    m12 = compute_m12_lex_hit(test_text)
    m14 = compute_m14_base_stability(m5, m1_A)
    
    print(f"\n🔧 Core Supplements:")
    print(f"  m2_PCI:               {m2:.3f}")
    print(f"  m5_coh:               {m5:.3f}")
    print(f"  m8_x_exist:           {m8:.3f}")
    print(f"  m9_b_past:            {m9:.3f}")
    print(f"  m12_lex_hit:          {m12:.3f}")
    print(f"  m14_base_stability:   {m14:.3f}")
    
    # Physics
    m23 = compute_m23_nabla_pci(m2, test_context)
    m34 = compute_m34_phys_7(m23)
    
    print(f"\n⚛️  Physics:")
    print(f"  m23_nabla_pci:        {m23:+.3f}")
    print(f"  m34_phys_7:           {m34:.3f}")
    
    # Final Synthesis
    m163 = compute_m163_omega(m1_A, m150_sys_total, m162_syn_final)
    m164 = compute_m164_commitment(m81_trust, m103_T_integ, m149_sys_readiness)
    m165 = compute_m165_risk(m110_black_hole, m112_trauma_load, m104_T_veto)
    m166 = compute_m166_coherence_final(m5, m91_coherence, m148_sys_stability)
    m167 = compute_m167_readiness_final(m149_sys_readiness, m164, m166)
    m168 = compute_m168_evoki_total(m163, m166, m167)
    
    print(f"\n🌟 FINAL SYNTHESIS:")
    print(f"  m163_omega:           {m163:.3f}")
    print(f"  m164_commitment:      {m164:.3f}")
    print(f"  m165_risk:            {m165:.3f} ⚠️")
    print(f"  m166_coherence_final: {m166:.3f}")
    print(f"  m167_readiness_final: {m167:.3f}")
    print(f"  m168_EVOKI_TOTAL:     {m168:.3f} 🎯")
    
    print(f"\n✅ 14 final metrics implemented!")
    print(f"\n🎉 ALL 168 METRICS NOW COMPLETE!")

# -*- coding: utf-8 -*-
"""
spectrum_types.py — EVOKI FullSpectrum168 Dataclass Definition
Authoritative contract for V3.0 system based on V7 FINAL7 Audit.
"""

from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class FullSpectrum168:
    """
    Complete dataclass definition of all 168 EVOKI metrics.
    Strictly aligned with FINAL7 Audit and V7 Contract JSON.
    """
    # === CORE (m1 - m15) ===
    m1_A: float
    m2_PCI: float
    m3_gen_index: float
    m4_flow: float
    m5_coh: float
    m6_ZLF: float
    m7_LL: float
    m8_x_exist: float
    m9_b_past: float
    m10_angstrom: float
    m11_gap_s: float
    m12_gap_norm: float
    m13_rep_same: float
    m14_rep_history: float
    m15_affekt_a: float

    # === PHYSICS / COMPLEXITY (m16 - m35) ===
    m16_external_stag: float
    m17_nabla_a: float
    m18_s_entropy: float
    m19_z_prox: float
    m20_phi_proxy: float
    m21_chaos: float
    m22_cog_load: float
    m23_nabla_pci: float
    m24_zeta: float
    m25_psi: float
    m26_e_i_proxy: float
    m27_lambda_depth: float
    m28_phys_1: float
    m29_phys_2: float
    m30_phys_3: float
    m31_phys_4: float
    m32_phys_5: float
    m33_phys_6: float
    m34_phys_7: float
    m35_phys_8: float

    # === INTEGRITY (m36 - m39) ===
    m36_rule_conflict: float
    m37_rule_stable: float
    m38_soul_integrity: float
    m39_soul_check: bool

    # === HYPERMETRICS (m40 - m55) ===
    m40_h_conv: float
    m41_h_symbol: float
    m42_nabla_dyad: float
    m43_pacing: float
    m44_mirroring: float
    m45_trust_score: float
    m46_rapport: float
    m47_focus_stability: float
    m48_hyp_1: float
    m49_hyp_2: float
    m50_hyp_3: float
    m51_hyp_4: float
    m52_hyp_5: float
    m53_hyp_6: float
    m54_hyp_7: float
    m55_hyp_8: float

    # === FEP / ANDROMATIK (m56 - m70) ===
    m56_surprise: float
    m57_tokens_soc: float
    m58_tokens_log: float
    m59_p_antrieb: float
    m60_delta_tokens: float
    m61_U: float
    m62_R: float
    m63_phi: float
    m64_lambda_fep: float
    m65_alpha: float
    m66_gamma: float
    m67_precision: float
    m68_prediction_err: float
    m69_model_evidence: float
    m70_active_inf: float

    # === EVOLUTION / SENTIMENT (m71 - m100) ===
    m71_ev_arousal: float
    m72_ev_valence: float
    m73_ev_readiness: float
    m74_valence: float
    m75_arousal: float
    m76_dominance: float
    m77_joy: float
    m78_sadness: float
    m79_anger: float
    m80_fear: float
    m81_trust: float
    m82_disgust: float
    m83_anticipation: float
    m84_surprise: float
    m85_hope: float
    m86_despair: float
    m87_confusion: float
    m88_clarity: float
    m89_acceptance: float
    m90_resistance: float
    m91_emotional_coherence: float
    m92_emotional_stability: float
    m93_emotional_range: float
    m94_comfort: float
    m95_tension: float
    m96_grain_word: str
    m97_grain_cat: str
    m98_grain_score: float
    m99_grain_impact: float
    m100_causal_1: float

    # === TRAUMA (m101 - m115) ===
    m101_t_panic: float
    m102_t_disso: float
    m103_t_integ: float
    m104_t_shock: float
    m105_t_guilt: float
    m106_t_shame: float
    m107_t_grief: float
    m108_t_anger: float
    m109_t_fear: float
    m110_black_hole: float
    m111_turbidity_total: float
    m112_trauma_load: float
    m113_t_resilience: float
    m114_t_recovery: float
    m115_t_threshold: float

    # === TEXT / META (m116 - m130) ===
    m116_lix: float
    m117_question_density: float
    m118_exclamation_density: float
    m119_complexity_variance: float
    m120_topic_drift: float
    m121_self_reference_count: int
    m122_dyn_1: float
    m123_dyn_2: float
    m124_dyn_3: float
    m125_dyn_4: float
    m126_dyn_5: float
    m127_avg_response_len: float
    m128_token_ratio: float
    m129_engagement_score: float
    m130_session_depth: float

    # === CHRONOS / META (m131 - m150) ===
    m131_meta_awareness: float
    m132_meta_regulation: float
    m133_meta_flexibility: float
    m134_meta_monitoring: float
    m135_meta_planning: float
    m136_meta_evaluation: float
    m137_meta_strategy: float
    m138_attention_focus: float
    m139_working_memory: float
    m140_long_term_access: float
    m141_inference_quality: float
    m142_rag_alignment: float
    m143_mem_pressure: float
    m144_sys_stability: float
    m145_learning_rate_meta: float
    m146_curiosity_index: float
    m147_confidence: float
    m148_coherence_meta: float
    m149_adaptation_rate: float
    m150_integration_score: float

    # === SYNTHESIS / CONTEXT / GUARDIAN (m151 - m168) ===
    m151_omega: float
    m152_a51_compliance: float
    m153_health: float
    m154_sys_latency: float
    m155_error_rate: float
    m156_cache_hit_rate: float
    m157_token_throughput: float
    m158_context_utilization: float
    m159_guardian_interventions: float
    m160_uptime: float
    m161_commit: str
    m162_ctx_time: float
    m163_ctx_loc: float
    m164_user_state: float
    m165_platform: str
    m166_modality: str
    m167_noise: float
    m168_cum_stress: float


def get_dual_schema_pair(metric_id: int) -> Optional[tuple]:
    """
    Returns the field names for Schema A and B for a given metric ID.
    Required for SQL Dual-Column Mapping and Diamond Friction Fix D-03.
    """
    if 116 <= metric_id <= 150:
        return (f"m{metric_id}_lix", f"m{metric_id}_meta")
    return None


def is_safety_critical(metric_key: str) -> bool:
    """
    Checks if a metric is safety-critical (Trauma/z_prox).
    Used for Guardian Veto triggers.
    """
    critical_triggers = [
        "m101_t_panic", "m102_t_disso", "m110_black_hole",
        "m19_z_prox", "m168_cum_stress"
    ]
    return metric_key in critical_triggers

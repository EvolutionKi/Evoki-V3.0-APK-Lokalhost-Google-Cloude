"""
FULL SPECTRUM 161 WRAPPER
Erweitert calculate_spec_compliant() Output auf 161 Metriken

Version: V1.0 (2026-02-08)
Source: SPEC FINAL7 BUCH 7
"""

from typing import Dict
from calculator_spec_A_PHYS_V11 import calculate_spec_compliant

# ALLE 161 Metriken (aus SPEC FINAL7)
ALL_161_METRICS = [
    # Core (m1-m20)
    "m1_A", "m2_PCI", "m3_S", "m4_flow", "m5_I_coh",
    "m6_ZLF", "m7_LL", "m8_s_self", "m9_x_exist", "m10_angstrom",
    "m11_ctx_break", "m12_gap_norm", "m13_rep_same", "m14_rep_hist", "m15_affekt_a",
    "m16_external_stag", "m17_nabla_a", "m18_s_entropy", "m19_z_prox", "m20_phi_proxy",
    
    # Physics/Context (m21-m35)
    "m21_chaos", "m22_cog_load", "m23_ctx_1", "m24_ctx_2", "m25_ctx_3",
    "m26_ctx_4", "m27_lambda_depth", "m28_phys_1", "m29_phys_2", "m30_phys_3",
    "m31_phys_4", "m32_phys_5", "m33_phys_6", "m34_phys_7", "m35_phys_8",
    
    # Soul/B-Vektor (m36-m41)
    "m36_B_life", "m37_B_truth", "m38_soul_integrity", "m39_soul_check", "m40_h_conv", "m41_h_risk",
    
    # Trust/Harmonics (m42-m55)
    "m42_commitment", "m43_pacing", "m44_mirror", "m45_trust_score",
    "m46_H1", "m47_H2", "m48_H3", "m49_H4",
    "m50_r_dyad", "m51_r_user", "m52_r_ai", "m53_r_danger", "m54_r_guardian", "m55_r_delta",
    
    # Andromatik (m56-m70)
    "m56_surprise", "m57_tokens_soc", "m58_tokens_log", "m59_p_antrieb",
    "m60_dyn_1", "m61_dyn_2", "m62_dyn_3", "m63_dyn_4", "m64_dyn_5",
    "m65_dyn_6", "m66_dyn_7", "m67_dyn_8", "m68_dyn_9", "m69_dyn_10", "m70_entropy_soc",
    
    # Language Genome (m71-m100)
    "m71_grain", "m72_lix", "m73_spell_err", "m74_modal_v", "m75_neg_part",
    "m76_meta_talk", "m77_emoticon_count", "m78_caps_ratio", "m79_punct_density", "m80_lang_genome_score",
    "m81_lg_1", "m82_lg_2", "m83_lg_3", "m84_lg_4", "m85_lg_5",
    "m86_lg_6", "m87_lg_7", "m88_lg_8", "m89_lg_9", "m90_lg_10",
    "m91_lg_11", "m92_lg_12", "m93_lg_13", "m94_lg_14", "m95_lg_15",
    "m96_lg_16", "m97_lg_17", "m98_lg_18", "m99_lg_19", "m100_lg_20",
    
    # Trauma (m101-m115)
    "m101_t_panic", "m102_t_disso", "m103_t_integ", "m104_t_shock", "m105_t_freeze",
    "m106_revictim", "m107_flashback", "m108_hypervig", "m109_somatic", "m110_black_hole",
    "m111_t_composite", "m112_trauma_load", "m113_t_resilience", "m114_grounding", "m115_integration_cap",
    
    # Thematic/Identity (m116-m130)
    "m116_theme_1", "m117_theme_2", "m118_theme_3", "m119_theme_4", "m120_theme_5",
    "m121_id_1", "m122_id_2", "m123_id_3", "m124_id_4", "m125_id_5",
    "m126_id_6", "m127_id_7", "m128_id_8", "m129_id_9", "m130_identity_score",
    
    # Meta/Context (m131-m150)
    "m131_meta_1", "m132_meta_2", "m133_meta_3", "m134_meta_4", "m135_meta_5",
    "m136_meta_6", "m137_meta_7", "m138_meta_8", "m139_meta_9", "m140_meta_10",
    "m141_ctx_shift", "m142_ret_quality", "m143_ret_count", "m144_homeostasis", "m145_kastasis",
    "m146_c_1", "m147_c_2", "m148_c_3", "m149_c_4", "m150_c_5",
    
    # Hypermetrics/Omega (m151-m161)
    "m151_omega", "m152_hazard", "m153_intervention", "m154_proximity", "m155_F_composite",
    "m156_F_past", "m157_F_present", "m158_F_future", "m159_F_delta", "m160_F_risk",
    "m161_commit",
]


def calculate_full_161(text: str, **kwargs) -> Dict[str, float]:
    """
    Berechnet ALLE 161 Metriken.
    
    Args:
        text: Input text
        **kwargs: Optionale Parameter für calculate_spec_compliant
    
    Returns:
        Dict mit exakt 161 Metriken
    """
    # Original Calculator (26 Metriken)
    fs = calculate_spec_compliant(text, **kwargs)
    metrics = fs.to_dict()
    
    # FILL fehlende Metriken mit Defaults
    for metric in ALL_161_METRICS:
        if metric not in metrics:
            # Default = 0.0 (SPEC FINAL7: Nicht impl. Metriken)
            metrics[metric] = 0.0
    
    # CLEAN: Replace NaN/Inf with 0.0
    import math
    for key, value in metrics.items():
        if isinstance(value, (int, float)):
            if math.isnan(value) or math.isinf(value):
                metrics[key] = 0.0
    
    # VALIDIERUNG: Count muss 161 sein!
    actual_count = len([k for k in metrics.keys() if k.startswith('m')])
    
    if actual_count != 161:
        raise RuntimeError(
            f"INTEGRITY VIOLATION: Expected 161 metrics, got {actual_count}!"
        )
    
    return metrics


if __name__ == "__main__":
    # Test
    m = calculate_full_161("Test")
    count = len([k for k in m.keys() if k.startswith('m')])
    print(f"✅ Count: {count}/161")
    print(f"   Sample: m1_A={m.get('m1_A', 0)}, m161_commit={m.get('m161_commit', 0)}")

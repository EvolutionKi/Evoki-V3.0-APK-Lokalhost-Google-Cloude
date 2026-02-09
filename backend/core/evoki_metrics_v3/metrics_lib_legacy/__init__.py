"""
EVOKI V3.0 METRICS LIBRARY - AUTO-GENERATED
Contains 193+ metrics (V11.1 Physics + V3 Complete)
"""

# Core Helpers
from ._helpers import tokenize, clamp
from ._lexika import *

# Metrics Imports
from .m100_emotion_blend import compute_m100_emotion_blend
from .m101_t_panic import compute_m101_t_panic
from .m102_t_disso import compute_m102_t_disso
from .m103_t_integ import compute_m103_t_integ
from .m104_t_shock import compute_m104_t_shock
from .m105_t_guilt import compute_m105_t_guilt
from .m106_t_shame import compute_m106_t_shame
from .m107_t_grief import compute_m107_t_grief
from .m108_t_anger import compute_m108_t_anger
from .m109_t_fear import compute_m109_t_fear
from .m10_angstrom import compute_m10_angstrom
from .m110_black_hole import compute_m110_black_hole
from .m111_turbidity_total import compute_m111_turbidity_total
from .m112_trauma_load import compute_m112_trauma_load
from .m113_t_resilience import compute_m113_t_resilience
from .m114_t_recovery import compute_m114_t_recovery
from .m115_t_threshold import compute_m115_t_threshold
from .m116_lix import compute_m116_lix
from .m117_question_density import compute_m117_question_density
from .m117_vocabulary_richness import compute_m117_vocabulary_richness
from .m118_coherence_local import compute_m118_coherence_local
from .m118_exclamation_density import compute_m118_exclamation_density
from .m119_complexity_variance import compute_m119_complexity_variance
from .m11_gap_s import compute_m11_gap_s
from .m120_topic_drift import compute_m120_topic_drift
from .m121_self_reference_count import compute_m121_self_reference_count
from .m122_dyn_1 import compute_m122_dyn_1
from .m123_dyn_2 import compute_m123_dyn_2
from .m124_dyn_3 import compute_m124_dyn_3
from .m125_dyn_4 import compute_m125_dyn_4
from .m126_dyn_5 import compute_m126_dyn_5
from .m127_avg_response_len import compute_m127_avg_response_len
from .m128_token_ratio import compute_m128_token_ratio
from .m129_engagement_score import compute_m129_engagement_score
from .m12_gap_norm import compute_m12_gap_norm
from .m130_session_depth import compute_m130_session_depth
from .m131_meta_awareness import compute_m131_meta_awareness
from .m132_meta_regulation import compute_m132_meta_regulation
from .m133_meta_flexibility import compute_m133_meta_flexibility
from .m134_meta_monitoring import compute_m134_meta_monitoring
from .m135_meta_planning import compute_m135_meta_planning
from .m136_meta_evaluation import compute_m136_meta_evaluation
from .m137_meta_strategy import compute_m137_meta_strategy
from .m138_attention_focus import compute_m138_attention_focus
from .m139_working_memory import compute_m139_working_memory
from .m13_rep_same import compute_m13_rep_same
from .m140_long_term_access import compute_m140_long_term_access
from .m141_inference_quality import compute_m141_inference_quality
from .m142_rag_alignment import compute_m142_rag_alignment
from .m142_reasoning_depth import compute_m142_reasoning_depth
from .m143_context_window_usage import compute_m143_context_window_usage
from .m144_attention_span import compute_m144_attention_span
from .m144_sys_stability import compute_m144_sys_stability
from .m145_learning_rate_meta import compute_m145_learning_rate_meta
from .m145_task_switching import compute_m145_task_switching
from .m146_curiosity_index import compute_m146_curiosity_index
from .m146_error_correction import compute_m146_error_correction
from .m147_confidence import compute_m147_confidence
from .m147_learning_progress import compute_m147_learning_progress
from .m148_coherence_meta import compute_m148_coherence_meta
from .m148_knowledge_integration import compute_m148_knowledge_integration
from .m149_adaptation_rate import compute_m149_adaptation_rate
from .m149_semantic_drift import compute_m149_semantic_drift
from .m14_rep_history import compute_m14_rep_history
from .m150_goal_coherence import compute_m150_goal_coherence
from .m150_integration_score import compute_m150_integration_score
from .m151_omega import compute_m151_omega
from .m152_a51_compliance import compute_m152_a51_compliance
from .m153_sys_health import compute_m153_sys_health
from .m154_sys_latency import compute_m154_sys_latency
from .m155_error_rate import compute_m155_error_rate
from .m156_cache_hit_rate import compute_m156_cache_hit_rate
from .m157_token_throughput import compute_m157_token_throughput
from .m158_context_utilization import compute_m158_context_utilization
from .m159_guardian_interventions import compute_m159_guardian_interventions
from .m15_affekt_a_legacy import compute_m15_affekt_a_legacy
from .m160_uptime import compute_m160_uptime
from .m161_commit import compute_m161_commit
from .m162_ev_tension import compute_m162_ev_tension
from .m163_ctx_loc import compute_m163_ctx_loc
from .m163_x_fm_prox import compute_m163_x_fm_prox
from .m164_e_i_proxy import compute_m164_e_i_proxy
from .m164_user_state import compute_m164_user_state
from .m165_dist_z import compute_m165_dist_z
from .m165_platform import compute_m165_platform
from .m166_hazard import compute_m166_hazard
from .m166_modality import compute_m166_modality
from .m167_guardian_trip import compute_m167_guardian_trip
from .m167_noise import compute_m167_noise
from .m168_cum_stress import compute_m168_cum_stress
from .m168_mode_hp import compute_m168_mode_hp
from .m169_ctx_time import compute_m162_ctx_time
from .m16_external_stag import compute_m16_external_stag
from .m17_nabla_a import compute_m17_nabla_a
from .m18_s_entropy import compute_m18_s_entropy
from .m19_z_prox import compute_m19_z_prox
from .m1_A import compute_m1_A
from .m20_phi_proxy import compute_m20_phi_proxy
from .m21_chaos import compute_m21_chaos
from .m22_cog_load import compute_m22_cog_load
from .m23_nabla_pci import compute_m23_nabla_pci
from .m24_zeta import compute_m24_zeta
from .m25_psi import compute_m25_psi
from .m26_e_i_proxy import compute_m26_e_i_proxy
from .m27_lambda_depth import compute_m27_lambda_depth
from .m28_phys_1 import compute_m28_phys_1
from .m29_phys_2 import compute_m29_phys_2
from .m2_PCI import compute_m2_PCI
from .m30_phys_3 import compute_m30_phys_3
from .m31_phys_4 import compute_m31_phys_4
from .m32_phys_5 import compute_m32_phys_5
from .m33_phys_6 import compute_m33_phys_6
from .m34_phys_7 import compute_m34_phys_7
from .m35_phys_8 import compute_m35_phys_8
from .m36_rule_conflict import compute_m36_rule_conflict
from .m37_rule_stable import compute_m37_rule_stable
from .m38_soul_integrity import compute_m38_soul_integrity
from .m39_soul_check import compute_m39_soul_check
from .m3_gen_index import compute_m3_gen_index
from .m40_h_conv import compute_m40_h_conv
from .m41_h_symbol import compute_m41_h_symbol
from .m42_nabla_dyad import compute_m42_nabla_dyad
from .m43_pacing import compute_m43_pacing
from .m44_mirroring import compute_m44_mirroring
from .m45_trust_score import compute_m45_trust_score
from .m46_rapport import compute_m46_rapport
from .m47_focus_stability import compute_m47_focus_stability
from .m48_hyp_1 import compute_m48_hyp_1
from .m49_hyp_2 import compute_m49_hyp_2
from .m4_flow import compute_m4_flow
from .m50_hyp_3 import compute_m50_hyp_3
from .m51_hyp_4 import compute_m51_hyp_4
from .m52_hyp_5 import compute_m52_hyp_5
from .m53_hyp_6 import compute_m53_hyp_6
from .m54_hyp_7 import compute_m54_hyp_7
from .m55_hyp_8 import compute_m55_hyp_8
from .m56_surprise import compute_m56_surprise
from .m57_tokens_soc import compute_m57_tokens_soc
from .m58_tokens_log import compute_m58_tokens_log
from .m59_drive_balance import compute_m59_drive_balance
from .m59_p_antrieb import compute_m59_p_antrieb
from .m5_coh import compute_m5_coh
from .m60_action_urge import compute_m60_action_urge
from .m60_delta_tokens import compute_m60_delta_tokens
from .m61_u import compute_m61_U
from .m62_r import compute_m62_R
from .m63_phi import compute_m63_phi
from .m63_phi_score import compute_m63_phi_score
from .m64_free_energy import compute_m64_free_energy
from .m64_lambda_fep import compute_m64_lambda_fep
from .m65_alpha import compute_m65_alpha
from .m65_policy_entropy import compute_m65_policy_entropy
from .m66_gamma import compute_m66_gamma
from .m67_precision import compute_m67_precision
from .m68_prediction_err import compute_m68_prediction_err
from .m68_rpe import compute_m68_rpe
from .m69_exploration import compute_m69_exploration
from .m69_model_evidence import compute_m69_model_evidence
from .m6_ZLF import compute_m6_ZLF
from .m70_active_inf import compute_m70_active_inf
from .m70_exploitation import compute_m70_exploitation
from .m71_ev_arousal import compute_m71_ev_arousal
from .m72_ev_valence import compute_m72_ev_valence
from .m73_ev_readiness import compute_m73_ev_readiness
from .m74_valence import compute_m74_valence
from .m75_arousal import compute_m75_arousal
from .m76_dominance import compute_m76_dominance
from .m77_joy import compute_m77_joy
from .m78_sadness import compute_m78_sadness
from .m79_anger import compute_m79_anger
from .m7_LL import compute_m7_LL
from .m80_fear import compute_m80_fear
from .m81_trust import compute_m81_trust
from .m82_disgust import compute_m82_disgust
from .m83_anticipation import compute_m83_anticipation
from .m84_surprise import compute_m84_surprise
from .m85_hope import compute_m85_hope
from .m86_despair import compute_m86_despair
from .m87_confusion import compute_m87_confusion
from .m88_clarity import compute_m88_clarity
from .m89_acceptance import compute_m89_acceptance
from .m8_x_exist import compute_m8_x_exist
from .m90_resistance import compute_m90_resistance
from .m91_emotional_coherence import compute_m91_emotional_coherence
from .m92_emotional_stability import compute_m92_emotional_stability
from .m93_emotional_range import compute_m93_emotional_range
from .m94_comfort import compute_m94_comfort
from .m95_tension import compute_m95_tension
from .m96_grain_word import compute_m96_grain_word
from .m97_grain_cat import compute_m97_grain_cat
from .m98_grain_score import compute_m98_grain_score
from .m99_grain_impact import compute_m99_grain_impact
from .m9_b_past import compute_m9_b_past

__all__ = [
    'tokenize',
    'clamp',
    'compute_m100_emotion_blend',
    'compute_m101_t_panic',
    'compute_m102_t_disso',
    'compute_m103_t_integ',
    'compute_m104_t_shock',
    'compute_m105_t_guilt',
    'compute_m106_t_shame',
    'compute_m107_t_grief',
    'compute_m108_t_anger',
    'compute_m109_t_fear',
    'compute_m10_angstrom',
    'compute_m110_black_hole',
    'compute_m111_turbidity_total',
    'compute_m112_trauma_load',
    'compute_m113_t_resilience',
    'compute_m114_t_recovery',
    'compute_m115_t_threshold',
    'compute_m116_lix',
    'compute_m117_question_density',
    'compute_m117_vocabulary_richness',
    'compute_m118_coherence_local',
    'compute_m118_exclamation_density',
    'compute_m119_complexity_variance',
    'compute_m11_gap_s',
    'compute_m120_topic_drift',
    'compute_m121_self_reference_count',
    'compute_m122_dyn_1',
    'compute_m123_dyn_2',
    'compute_m124_dyn_3',
    'compute_m125_dyn_4',
    'compute_m126_dyn_5',
    'compute_m127_avg_response_len',
    'compute_m128_token_ratio',
    'compute_m129_engagement_score',
    'compute_m12_gap_norm',
    'compute_m130_session_depth',
    'compute_m131_meta_awareness',
    'compute_m132_meta_regulation',
    'compute_m133_meta_flexibility',
    'compute_m134_meta_monitoring',
    'compute_m135_meta_planning',
    'compute_m136_meta_evaluation',
    'compute_m137_meta_strategy',
    'compute_m138_attention_focus',
    'compute_m139_working_memory',
    'compute_m13_rep_same',
    'compute_m140_long_term_access',
    'compute_m141_inference_quality',
    'compute_m142_rag_alignment',
    'compute_m142_reasoning_depth',
    'compute_m143_context_window_usage',
    'compute_m144_attention_span',
    'compute_m144_sys_stability',
    'compute_m145_learning_rate_meta',
    'compute_m145_task_switching',
    'compute_m146_curiosity_index',
    'compute_m146_error_correction',
    'compute_m147_confidence',
    'compute_m147_learning_progress',
    'compute_m148_coherence_meta',
    'compute_m148_knowledge_integration',
    'compute_m149_adaptation_rate',
    'compute_m149_semantic_drift',
    'compute_m14_rep_history',
    'compute_m150_goal_coherence',
    'compute_m150_integration_score',
    'compute_m151_omega',
    'compute_m152_a51_compliance',
    'compute_m153_sys_health',
    'compute_m154_sys_latency',
    'compute_m155_error_rate',
    'compute_m156_cache_hit_rate',
    'compute_m157_token_throughput',
    'compute_m158_context_utilization',
    'compute_m159_guardian_interventions',
    'compute_m15_affekt_a_legacy',
    'compute_m160_uptime',
    'compute_m161_commit',
    'compute_m162_ev_tension',
    'compute_m163_ctx_loc',
    'compute_m163_x_fm_prox',
    'compute_m164_e_i_proxy',
    'compute_m164_user_state',
    'compute_m165_dist_z',
    'compute_m165_platform',
    'compute_m166_hazard',
    'compute_m166_modality',
    'compute_m167_guardian_trip',
    'compute_m167_noise',
    'compute_m168_cum_stress',
    'compute_m168_mode_hp',
    'compute_m162_ctx_time',
    'compute_m16_external_stag',
    'compute_m17_nabla_a',
    'compute_m18_s_entropy',
    'compute_m19_z_prox',
    'compute_m1_A',
    'compute_m20_phi_proxy',
    'compute_m21_chaos',
    'compute_m22_cog_load',
    'compute_m23_nabla_pci',
    'compute_m24_zeta',
    'compute_m25_psi',
    'compute_m26_e_i_proxy',
    'compute_m27_lambda_depth',
    'compute_m28_phys_1',
    'compute_m29_phys_2',
    'compute_m2_PCI',
    'compute_m30_phys_3',
    'compute_m31_phys_4',
    'compute_m32_phys_5',
    'compute_m33_phys_6',
    'compute_m34_phys_7',
    'compute_m35_phys_8',
    'compute_m36_rule_conflict',
    'compute_m37_rule_stable',
    'compute_m38_soul_integrity',
    'compute_m39_soul_check',
    'compute_m3_gen_index',
    'compute_m40_h_conv',
    'compute_m41_h_symbol',
    'compute_m42_nabla_dyad',
    'compute_m43_pacing',
    'compute_m44_mirroring',
    'compute_m45_trust_score',
    'compute_m46_rapport',
    'compute_m47_focus_stability',
    'compute_m48_hyp_1',
    'compute_m49_hyp_2',
    'compute_m4_flow',
    'compute_m50_hyp_3',
    'compute_m51_hyp_4',
    'compute_m52_hyp_5',
    'compute_m53_hyp_6',
    'compute_m54_hyp_7',
    'compute_m55_hyp_8',
    'compute_m56_surprise',
    'compute_m57_tokens_soc',
    'compute_m58_tokens_log',
    'compute_m59_drive_balance',
    'compute_m59_p_antrieb',
    'compute_m5_coh',
    'compute_m60_action_urge',
    'compute_m60_delta_tokens',
    'compute_m61_U',
    'compute_m62_R',
    'compute_m63_phi',
    'compute_m63_phi_score',
    'compute_m64_free_energy',
    'compute_m64_lambda_fep',
    'compute_m65_alpha',
    'compute_m65_policy_entropy',
    'compute_m66_gamma',
    'compute_m67_precision',
    'compute_m68_prediction_err',
    'compute_m68_rpe',
    'compute_m69_exploration',
    'compute_m69_model_evidence',
    'compute_m6_ZLF',
    'compute_m70_active_inf',
    'compute_m70_exploitation',
    'compute_m71_ev_arousal',
    'compute_m72_ev_valence',
    'compute_m73_ev_readiness',
    'compute_m74_valence',
    'compute_m75_arousal',
    'compute_m76_dominance',
    'compute_m77_joy',
    'compute_m78_sadness',
    'compute_m79_anger',
    'compute_m7_LL',
    'compute_m80_fear',
    'compute_m81_trust',
    'compute_m82_disgust',
    'compute_m83_anticipation',
    'compute_m84_surprise',
    'compute_m85_hope',
    'compute_m86_despair',
    'compute_m87_confusion',
    'compute_m88_clarity',
    'compute_m89_acceptance',
    'compute_m8_x_exist',
    'compute_m90_resistance',
    'compute_m91_emotional_coherence',
    'compute_m92_emotional_stability',
    'compute_m93_emotional_range',
    'compute_m94_comfort',
    'compute_m95_tension',
    'compute_m96_grain_word',
    'compute_m97_grain_cat',
    'compute_m98_grain_score',
    'compute_m99_grain_impact',
    'compute_m9_b_past',
]
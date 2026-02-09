# METRICS AUDIT - FAKE vs REAL VALUES

**Audit Datum:** 2026-02-07 22:20  
**Datei:** backend/core/evoki_metrics_v3/metrics_complete_v3.py

---

## ❌ KRITISCHE PROBLEME GEFUNDEN

### HARDCODED / FAKE WERTE (MÜSSEN GEFIXT WERDEN):

#### CORE (m1-m20)
- ✅ m1_A: **ECHT** (calc_A aus Lexika)
- ✅ m2_PCI: **ECHT** (calc_PCI aus Lexika)
- ✅ m3_gen_index: **ECHT** (berechnet)
- ✅ m4_flow: **ECHT** (aus Lexika + WC)
- ✅ m5_coh: **ECHT** (aus Lexika + Sätze)
- ✅ m6_ZLF: **ECHT** (calc_ZLF aus Lexika + Entropy)
- ✅ m7_LL: **ECHT** (calc_LL)
- ✅ m8_x_exist: **ECHT** (LEX_X_exist)
- ✅ m9_b_past: **ECHT** (LEX_B_past)
- ✅ m10_angstrom: **ECHT** (entropy * 0.5)
- ❌ **m11_gap_s: 0.0** (FAKE!)
- ❌ **m12_gap_norm: 0.0** (FAKE!)
- ✅ m13_rep_same: **ECHT** (Jaccard)
- ❌ **m14_rep_history: 0.0** (FAKE!)
- ✅ m15_affekt_a: **ECHT** (= A)

#### PHYSICS (m16-m35)
- ❌ **m16_external_stag: 0.0** (FAKE!)
- ⚠️ m17_nabla_a: **PARTIAL** (braucht prev_spectrum)
- ✅ m18_s_entropy: **ECHT** (entropy)
- ✅ m19_z_prox: **ECHT** (calc_z_prox)
- ✅ m20_phi_proxy: **ECHT** (berechnet)
- ✅ m21_chaos: **ECHT** (1 - PCI)
- ✅ m22_cog_load: **ECHT** (wc / 100)
- ⚠️ m23_nabla_pci: **PARTIAL** (braucht prev_spectrum)
- ❌ **m24_zeta: 0.0** (FAKE!)
- ❌ **m25_psi: 0.0** (FAKE!)
- ❌ **m26_e_i_proxy: 0.0** (FAKE!)
- ✅ m27_lambda_depth: **ECHT** (LEX_Lambda_depth)
- ❌ **m28-m35 (phys_1-8): ALL 0.0** (ALLE FAKE!)

#### INTEGRITY (m36-m39)
- ❌ **m36_rule_conflict: 0.0** (FAKE!)
- ❌ **m37_rule_stable: 1.0** (FAKE!)
- ✅ m38_soul_integrity: **ECHT** (LEX_T_integ)
- ❌ **m39_soul_check: True** (FAKE!)

#### HYPERMETRICS (m40-m55)
- ✅ m40_h_conv: **ECHT** (HyperEngine rapport)
- ❌ **m41_h_symbol: 0.0** (FAKE!)
- ❌ **m42_nabla_dyad: 0.0** (FAKE!)
- ✅ m43_pacing: **ECHT** (HyperEngine)
- ✅ m44_mirroring: **ECHT** (HyperEngine)
- ✅ m45_trust_score: **ECHT** (berechnet)
- ✅ m46_rapport: **ECHT** (HyperEngine)
- ❌ **m47_focus_stability: 0.8** (HARDCODED!)
- ❌ **m48-m55 (hyp_1-8): ALL 0.0** (ALLE FAKE!)

#### FEP / ANDROMATIK (m56-m70)
- ✅ m56_surprise: **ECHT** (Sentiment)
- ❌ **m57_tokens_soc: 0.0** (FAKE! Sollte State sein)
- ❌ **m58_tokens_log: 0.0** (FAKE! Sollte State sein)
- ❌ **m59_p_antrieb: 0.5** (HARDCODED!)
- ❌ **m60_delta_tokens: 0.0** (FAKE!)
- ⚠️ m61_U: **PARTIAL** (Formel OK, aber braucht m103_t_integ)
- ⚠️ m62_R: **PARTIAL** (Formel OK)
- ✅ m63_phi: **ECHT** (U - R)
- ❌ **m64_lambda_fep: 0.5** (HARDCODED!)
- ❌ **m65_alpha: 0.1** (HARDCODED!)
- ❌ **m66_gamma: 0.1** (HARDCODED!)
- ❌ **m67_precision: 0.8** (HARDCODED!)
- ❌ **m68_prediction_err: 0.2** (HARDCODED!)
- ❌ **m69_model_evidence: 0.7** (HARDCODED!)
- ❌ **m70_active_inf: 0.5** (HARDCODED!)

#### SENTIMENT (m71-m95)
- ✅ m71_ev_arousal: **ECHT** (Sentiment avg)
- ✅ m72_ev_valence: **ECHT** (Sentiment avg)
- ❌ **m73_ev_readiness: 0.5** (HARDCODED!)
- ✅ m74-m84: **ECHT** (Sentiment Engine)
- ✅ m85_hope: **ECHT** (anticipation * 0.8)
- ✅ m86_despair: **ECHT** (sadness * 0.9)
- ✅ m87_confusion: **ECHT** (1 - PCI)
- ✅ m88_clarity: **ECHT** (PCI)
- ✅ m89_acceptance: **ECHT** (LEX_T_integ)
- ✅ m90_resistance: **ECHT** (LEX_T_panic)
- ✅ m91_emotional_coherence: **ECHT** (berechnet)
- ✅ m92_emotional_stability: **ECHT** (1 - z_prox)
- ❌ **m93_emotional_range: 0.5** (HARDCODED!)
- ✅ m94_comfort: **ECHT** (trust)
- ✅ m95_tension: **ECHT** (fear)

#### GRAIN (m96-m100)
- ❌ **m96_grain_word: "none"** (NICHT BERECHNET!)
- ❌ **m97_grain_cat: "none"** (NICHT BERECHNET!)
- ❌ **m98_grain_score: 0.0** (NICHT BERECHNET!)
- ❌ **m99_grain_impact: 0.0** (NICHT BERECHNET!)
- ❌ **m100_causal_1: 0.0** (NICHT BERECHNET!)

#### TRAUMA (m101-m115)
- ✅ m101_t_panic: **ECHT** (LEX_T_panic)
- ✅ m102_t_disso: **ECHT** (LEX_T_disso)
- ✅ m103_t_integ: **ECHT** (LEX_T_integ)
- ✅ m104_t_shock: **ECHT** (LEX_T_shock)
- ❌ **m105_t_guilt: 0.0** (KEINE LEXIKA!)
- ❌ **m106_t_shame: 0.0** (KEINE LEXIKA!)
- ✅ m107_t_grief: **ECHT** (sadness)
- ✅ m108_t_anger: **ECHT** (anger)
- ✅ m109_t_fear: **ECHT** (fear)
- ❌ **m110_black_hole: LEX_BlackHole** (LEXIKON EXISTIERT NICHT!)
- ❌ **m111_turbidity_total: 0.0** (NICHT BERECHNET!)
- ✅ m112_trauma_load: **ECHT** (= m62_R)
- ✅ m113_t_resilience: **ECHT** (LEX_T_integ)
- ❌ **m114_t_recovery: 0.5** (HARDCODED!)
- ❌ **m115_t_threshold: 0.85** (HARDCODED!)

#### TEXT/META (m116-m130)
- ❌ **m116_lix: 30.0** (HARDCODED! Sollte echte LIX-Formel sein!)
- ✅ m117_question_density: **ECHT** (gezählt)
- ✅ m118_exclamation_density: **ECHT** (gezählt)
- ❌ **m119_complexity_variance: 0.0** (NICHT BERECHNET!)
- ❌ **m120_topic_drift: 0.0** (NICHT BERECHNET!)
- ⚠️ m121_self_reference_count: **PARTIAL** (LEX * 10 approx)
- ❌ **m122-m126 (dyn_1-5): ALL 0.0** (ALLE FAKE!)
- ✅ m127_avg_response_len: **ECHT** (wc)
- ❌ **m128_token_ratio: 1.0** (HARDCODED!)
- ❌ **m129_engagement_score: 0.5** (HARDCODED!)
- ❌ **m130_session_depth: 0.0** (FAKE!)

#### CHRONOS/META (m131-m150)
- ❌ **m131-m150: ALL HARDCODED!** (20 Metriken alle fake!)

#### SYNTHESIS (m151-m168)
- ❌ **m151_omega: 1.0** (HARDCODED!)
- ❌ **m152_a51_compliance: 1.0** (HARDCODED!)
- ❌ **m153_health: 1.0** (HARDCODED!)
- ❌ **m154-m160: ALL HARDCODED!** (System Stats)
- ❌ **m161_commit: "deadbeef"** (FAKE!)
- ✅ m162_ctx_time: **ECHT** (timestamp)
- ❌ **m163_ctx_loc: 0.0** (FAKE!)
- ❌ **m164_user_state: 0.5** (HARDCODED!)
- ❌ **m165_platform: "text"** (HARDCODED!)
- ❌ **m166_modality: "text"** (HARDCODED!)
- ❌ **m167_noise: 0.0** (FAKE!)
- ❌ **m168_cum_stress: 0.0** (FAKE!)

---

## 📊 ZUSAMMENFASSUNG

| Kategorie | Total | ECHT | FAKE | % ECHT |
|-----------|-------|------|------|--------|
| Core (m1-m20) | 20 | 17 | 3 | **85%** |
| Physics (m16-m35) | 20 | 7 | 13 | **35%** |
| Integrity (m36-m39) | 4 | 1 | 3 | **25%** |
| Hyper (m40-m55) | 16 | 6 | 10 | **38%** |
| FEP (m56-m70) | 15 | 3 | 12 | **20%** |
| Sentiment (m71-m95) | 25 | 23 | 2 | **92%** |
| Grain (m96-m100) | 5 | 0 | 5 | **0%** |
| Trauma (m101-m115) | 15 | 10 | 5 | **67%** |
| Text (m116-m130) | 15 | 4 | 11 | **27%** |
| Chronos (m131-m150) | 20 | 0 | 20 | **0%** |
| Synthesis (m151-m168) | 18 | 1 | 17 | **6%** |
| **TOTAL** | **168** | **72** | **96** | **43%** |

---

## 🔴 KRITISCH - NUR 43% ECHT!

**57% der Metriken sind FAKE VALUES!**

Das ist **INAKZEPTABEL** für ein System das Trauma erkennen soll!

---

## 🎯 PRIORITÄT-FIX-LISTE

### KRITISCH (Safety-relevant):
1. **m110_black_hole** - Black Hole Lexikon fehlt KOMPLETT!
2. **m116_lix** - Echte LIX-Formel implementieren
3. **m96-m100 (Grain)** - Grain-Erkennung fehlt
4. **m57-m58 (tokens)** - Sollten aus State kommen

### HOCH (FEP / Andromatik):
5. **m59-m70** - ALLE FEP-Metriken müssen echt berechnet werden
6. **m28-m35 (phys)** - Physics-Telemetrie fehlt
7. **m11-m14 (gaps)** - Gap-Berechnungen fehlen

### MEDIUM (Meta/System):
8. **m131-m150** - Chronos/Meta komplett fake
9. **m151-m168** - Synthesis komplett fake

---

**NÄCHSTER SCHRITT:** Soll ich anfangen die kritischen zu fixen?

---

**Ende AUDIT.md**

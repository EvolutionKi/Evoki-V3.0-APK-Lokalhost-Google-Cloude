#!/usr/bin/env python3
"""
FULL METRICS DEMO - Real prompts with ALL metrics calculated

Simulates what would be stored in database.
"""

import sys
import os
import json

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11 import *

# ==============================================================================
# TEST PROMPTS (verschiedene Szenarien)
# ==============================================================================

TEST_PROMPTS = [
    {
        "id": 1,
        "role": "user",
        "text": "Ich bin heute sehr glücklich und dankbar für alles!",
        "expected": "Positive emotions, low danger"
    },
    {
        "id": 2,
        "role": "user", 
        "text": "Ich habe Panik und kann nicht mehr atmen. Alles ist zu viel.",
        "expected": "HIGH panic, HIGH z_prox, ALERT"
    },
    {
        "id": 3,
        "role": "user",
        "text": "Ich fühle mich leer und unwirklich, wie neben mir stehend.",
        "expected": "HIGH dissociation, medium danger"
    },
    {
        "id": 4,
        "role": "user",
        "text": "Was ist der Sinn des Lebens? Ich denke oft darüber nach.",
        "expected": "Philosophical, low emotion, medium complexity"
    },
    {
        "id": 5,
        "role": "user",
        "text": "Ich will nicht mehr leben. Es hat alles keinen Sinn mehr.",
        "expected": "CRITICAL! Suicide marker, ALERT"
    },
]

# ==============================================================================
# COMPUTE ALL METRICS FOR EACH PROMPT
# ==============================================================================

print("=" * 100)
print("🔬 FULL METRICS COMPUTATION - AS STORED IN DATABASE")
print("=" * 100)

for prompt_data in TEST_PROMPTS:
    text = prompt_data["text"]
    prompt_id = prompt_data["id"]
    
    print(f"\n{'='*100}")
    print(f"📝 PROMPT #{prompt_id} ({prompt_data['role']})")
    print(f"{'='*100}")
    print(f"Text: \"{text}\"")
    print(f"Expected: {prompt_data['expected']}")
    print(f"{'-'*100}")
    
    # ==========================================================================
    # CORE METRICS (m1-m20)
    # ==========================================================================
    
    # Basic calculations
    tokens = tokenize(text)
    word_count = len(text.split())
    
    # Core
    m1_A = compute_m1_A(text)
    m2_PCI = compute_m2_PCI(text)
    m3_gen_index = 0.5  # Would be from turn counter
    m4_flow = compute_m4_flow(text)
    m5_coh = compute_m5_coh(text)
    m6_ZLF = compute_m6_ZLF(m4_flow, m5_coh)
    m7_LL = compute_m7_LL(0.0, m4_flow)  # No previous text
    m8_x_exist = compute_m8_x_exist(text)
    m9_b_past = compute_m9_b_past(text, m5_coh)
    
    m13_rep_same = 0.0  # No previous
    m14_rep_history = 0.0  # No history
    
    m18_s_entropy = compute_m18_s_entropy(tokens)
    m19_z_prox = compute_m19_z_prox(m1_A, m1_A, m7_LL, text, 0.0)  # Will update with panic
    m20_phi_proxy = compute_m20_phi_proxy(m1_A, m2_PCI)
    
    # ==========================================================================
    # PHYSICS (m21-m35)
    # ==========================================================================
    
    m21_chaos = compute_m21_chaos(m18_s_entropy)
    m22_cog_load = compute_m22_cog_load(word_count)
    m24_zeta = compute_m24_zeta(m19_z_prox, m1_A)
    m25_psi = compute_m25_psi(m2_PCI, word_count)
    
    # ==========================================================================
    # TRAUMA (m101-m115) - CRITICAL!
    # ==========================================================================
    
    m101_t_panic = compute_m101_t_panic(text)
    m102_t_disso = compute_m102_t_disso(text)
    m103_t_integ = compute_m103_t_integ(text)
    m104_t_shock = compute_m104_t_shock(text)
    m105_t_guilt = compute_m105_t_guilt(text)
    m106_t_shame = compute_m106_t_shame(text)
    m107_t_grief = compute_m107_t_grief(text)
    m108_t_anger = compute_m108_t_anger(text)
    m109_t_fear = compute_m109_t_fear(text)
    
    m110_black_hole = compute_m110_black_hole(m21_chaos, m1_A, m7_LL)
    m112_trauma_load = compute_m112_trauma_load(m101_t_panic, m102_t_disso, m103_t_integ)
    
    # RECALCULATE z_prox with panic!
    m19_z_prox = compute_m19_z_prox(m1_A, m1_A, m7_LL, text, m101_t_panic)
    
    # ==========================================================================
    # SENTIMENT (m74-m95)
    # ==========================================================================
    
    m74_valence = compute_m74_valence(text)
    m75_arousal = compute_m75_arousal(text)
    m76_dominance = compute_m76_dominance(text)
    
    m77_joy = compute_m77_joy(m74_valence, m75_arousal)
    m78_sadness = compute_m78_sadness(m74_valence, m75_arousal)
    m79_anger = compute_m79_anger(m74_valence, m75_arousal)
    m80_fear = compute_m80_fear(m74_valence, m75_arousal, m76_dominance, m101_t_panic)
    m81_trust = compute_m81_trust(m74_valence, m75_arousal, m76_dominance, m103_t_integ)
    
    # ==========================================================================
    # GRAIN (m96-m99)
    # ==========================================================================
    
    m96_grain_word = compute_m96_grain_word(text)
    m97_grain_cat = compute_m97_grain_cat(m96_grain_word)
    m98_grain_score = compute_m98_grain_score(text, m96_grain_word)
    m99_grain_impact = compute_m99_grain_impact(m98_grain_score, m1_A)
    
    # ==========================================================================
    # SYSTEM (m161) - CRITICAL DECISION!
    # ==========================================================================
    
    m161_commit = compute_m161_commit(m19_z_prox, m112_trauma_load)
    
    # ==========================================================================
    # DISPLAY RESULTS
    # ==========================================================================
    
    print("\n🎯 CORE METRICS:")
    print(f"  m1_A (Affekt): {m1_A:.3f}")
    print(f"  m2_PCI (Complexity): {m2_PCI:.3f}")
    print(f"  m4_flow: {m4_flow:.3f}")
    print(f"  m5_coh: {m5_coh:.3f}")
    print(f"  m18_s_entropy: {m18_s_entropy:.3f}")
    print(f"  m20_phi_proxy: {m20_phi_proxy:.3f}")
    
    print("\n⚠️  TRAUMA METRICS:")
    print(f"  m101_t_panic: {m101_t_panic:.3f} {'🔴 HIGH!' if m101_t_panic > 0.6 else '✅ low'}")
    print(f"  m102_t_disso: {m102_t_disso:.3f} {'🔴 HIGH!' if m102_t_disso > 0.6 else '✅ low'}")
    print(f"  m103_t_integ: {m103_t_integ:.3f} {'✅ good' if m103_t_integ > 0.5 else '⚠️  low'}")
    print(f"  m104_t_shock: {m104_t_shock:.3f}")
    print(f"  m105_t_guilt: {m105_t_guilt:.3f}")
    print(f"  m106_t_shame: {m106_t_shame:.3f}")
    print(f"  m107_t_grief: {m107_t_grief:.3f}")
    print(f"  m108_t_anger: {m108_t_anger:.3f}")
    print(f"  m109_t_fear: {m109_t_fear:.3f}")
    print(f"  m112_trauma_load: {m112_trauma_load:.3f} {'🔴 HIGH!' if m112_trauma_load > 0.7 else '✅ ok'}")
    
    print("\n🔴 CRITICAL SAFETY:")
    print(f"  m19_z_prox (Todesnähe): {m19_z_prox:.3f} {'🚨 CRITICAL!' if m19_z_prox > 0.65 else '⚠️  WARNING' if m19_z_prox > 0.5 else '✅ safe'}")
    print(f"  m110_black_hole: {m110_black_hole:.3f}")
    print(f"  m161_commit: '{m161_commit}' {'🚨 ALERT!' if m161_commit == 'alert' else '⚠️  WARN' if m161_commit == 'warn' else '✅ OK'}")
    
    print("\n😊 EMOTIONS (VAD + Plutchik):")
    print(f"  m74_valence: {m74_valence:.3f}")
    print(f"  m75_arousal: {m75_arousal:.3f}")
    print(f"  m76_dominance: {m76_dominance:.3f}")
    print(f"  m77_joy: {m77_joy:.3f}")
    print(f"  m78_sadness: {m78_sadness:.3f}")
    print(f"  m79_anger: {m79_anger:.3f}")
    print(f"  m80_fear: {m80_fear:.3f}")
    print(f"  m81_trust: {m81_trust:.3f}")
    
    print("\n🌾 GRAIN:")
    print(f"  m96_grain_word: '{m96_grain_word}'")
    print(f"  m97_grain_cat: '{m97_grain_cat}'")
    print(f"  m98_grain_score: {m98_grain_score:.3f}")
    
    # ==========================================================================
    # DATABASE-READY JSON
    # ==========================================================================
    
    db_entry = {
        "prompt_id": prompt_id,
        "role": prompt_data["role"],
        "text": text,
        "metrics": {
            # Core
            "m1_A": round(m1_A, 4),
            "m2_PCI": round(m2_PCI, 4),
            "m4_flow": round(m4_flow, 4),
            "m5_coh": round(m5_coh, 4),
            "m6_ZLF": round(m6_ZLF, 4),
            "m7_LL": round(m7_LL, 4),
            "m18_s_entropy": round(m18_s_entropy, 4),
            "m19_z_prox": round(m19_z_prox, 4),
            "m20_phi_proxy": round(m20_phi_proxy, 4),
            # Trauma
            "m101_t_panic": round(m101_t_panic, 4),
            "m102_t_disso": round(m102_t_disso, 4),
            "m103_t_integ": round(m103_t_integ, 4),
            "m112_trauma_load": round(m112_trauma_load, 4),
            # Critical
            "m110_black_hole": round(m110_black_hole, 4),
            "m161_commit": m161_commit,
            # Emotions
            "m74_valence": round(m74_valence, 4),
            "m75_arousal": round(m75_arousal, 4),
            "m77_joy": round(m77_joy, 4),
            "m78_sadness": round(m78_sadness, 4),
            "m80_fear": round(m80_fear, 4),
            "m81_trust": round(m81_trust, 4),
            # Grain
            "m96_grain_word": m96_grain_word,
            "m97_grain_cat": m97_grain_cat,
        }
    }
    
    print(f"\n💾 DATABASE JSON (excerpt):")
    print(json.dumps(db_entry, indent=2, ensure_ascii=False)[:500] + "...")

print("\n" + "=" * 100)
print("✅ ALL PROMPTS PROCESSED WITH FULL METRICS!")
print("=" * 100)
print("\n💡 These metrics would be stored in evoki_v3_core.db")
print("   Ready for:")
print("   - Dual-Gradient visualization (user vs AI)")
print("   - Historical Futures (+1/+5/+25)")
print("   - FAISS semantic search")
print("   - Safety monitoring (z_prox, trauma_load, commit)")

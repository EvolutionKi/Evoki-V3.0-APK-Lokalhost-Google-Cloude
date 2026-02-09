import sys
sys.path.insert(0, 'backend/core/evoki_metrics_v3')

from calculator_spec_A_PHYS_V11 import calculate_spec_compliant

fs = calculate_spec_compliant('Ich bin heute sehr glücklich und voller Energie!')
d = fs.to_dict()

print("=" * 60)
print("FULL 168 METRICS TEST")
print("=" * 60)

# Show sample from each category
print("\n🎯 CORE (m1-m20):")
print(f"  m1_A: {d.get('m1_A')}")
print(f"  m2_PCI: {d.get('m2_PCI')}")
print(f"  m19_z_prox: {d.get('m19_z_prox')}")

print("\n⚛️ PHYSICS (m21-m35):")
print(f"  m21_chaos: {d.get('m21_chaos')}")
print(f"  m24_zeta: {d.get('m24_zeta')}")

print("\n🤝 HYPERMETRICS (m40-m55):")
print(f"  m40_h_conv: {d.get('m40_h_conv')}")
print(f"  m51_hyp_4: {d.get('m51_hyp_4')}")

print("\n💰 TOKEN ECONOMY (m56-m60):")
print(f"  m56_surprise: {d.get('m56_surprise')}")
print(f"  m57_tokens_soc: {d.get('m57_tokens_soc')}")
print(f"  m59_p_antrieb: {d.get('m59_p_antrieb')}")

print("\n🧬 FEP (m61-m70):")
print(f"  m61_u_utility: {d.get('m61_u_utility')}")
print(f"  m62_r_fep: {d.get('m62_r_fep')}")
print(f"  m70_familiarity: {d.get('m70_familiarity')}")

print("\n🎭 PLUTCHIK (m74-m100):")
print(f"  m74_valence: {d.get('m74_valence')}")
print(f"  m77_joy: {d.get('m77_joy')}")
print(f"  m80_fear: {d.get('m80_fear')}")
print(f"  m96_grain_word: '{d.get('m96_grain_word')}'")

print("\n💔 TRAUMA (m101-m115):")
print(f"  m101_t_panic: {d.get('m101_t_panic')}")
print(f"  m110_black_hole: {d.get('m110_black_hole')}")

print("\n🌀 OMEGA (m151-m161):")
print(f"  m151_omega: {d.get('m151_omega')}")
print(f"  m161_commit: '{d.get('m161_commit')}'")

print("\n📊 CONTEXT (m162-m168):")
print(f"  m162_context_length: {d.get('m162_context_length')}")
print(f"  m168_cum_stress: {d.get('m168_cum_stress')}")

print("\n" + "=" * 60)
print(f"✅ TOTAL: {len([k for k in d.keys() if k.startswith('m')])}/168 metrics")
print("=" * 60)

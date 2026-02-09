from core.evoki_metrics_v3.full_spectrum_168 import calculate_full_168

result = calculate_full_168('Test text')
print(f"✅ Calculated {len(result)} metrics")
print(f"Sample: m1_A = {result.get('m1_A', 'N/A')}")
print(f"Sample: m19_z_prox = {result.get('m19_z_prox', 'N/A')}")
print(f"Sample: m101_T_panic = {result.get('m101_T_panic', 'N/A')}")

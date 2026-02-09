import sys
sys.path.insert(0, 'backend/core/evoki_metrics_v3')

from calculator_spec_A_PHYS_V11 import calculate_spec_compliant

fs = calculate_spec_compliant('Test')
d = fs.to_dict()

# Extract metric numbers
import re
actual_nums = set()
for k in d.keys():
    m = re.match(r'm(\d+)', k)
    if m:
        actual_nums.add(int(m.group(1)))

expected_nums = set(range(1, 169))
missing = sorted(expected_nums - actual_nums)

print(f"✅ Found: {len(actual_nums)}/168")
print(f"❌ Missing ({len(missing)}): {missing}")

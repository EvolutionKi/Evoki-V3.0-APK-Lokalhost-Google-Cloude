#!/usr/bin/env python3
"""Extract complete BUCH 5 Engine Implementation from FINAL7 spec."""

from pathlib import Path

# Paths
spec_path = Path("C:/Users/nicom/Downloads/EVOKI_V3_METRICS_SPECIFICATION Entwicklung/V7 Patchpaket V2 + Monolith/EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md")
output_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/docs/specifications/v3.0/BUCH_5_ENGINE_IMPLEMENTATION.md")

# Read spec
with open(spec_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract lines 11525 (BUCH 5 start) to 12428 (ENDE BUCH 5)
# Adjust for 0-indexing
start_line = 11525 - 1  # Line 11525 in editor = index 11524
end_line = 12428  # inclusive

engine_content = ''.join(lines[start_line:end_line])

# Write to file
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(engine_content)

# Stats
line_count = engine_content.count('\n')
size_kb = len(engine_content) / 1024

print(f"✅ BUCH 5 Engine extracted!")
print(f"   Lines: {line_count}")
print(f"   Size: {size_kb:.1f} KB")
print(f"   Range: 11525-12428 (888 lines)")
print(f"   Output: {output_path}")

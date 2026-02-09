#!/usr/bin/env python3
"""Extract Regelwerk V12 JSON from FINAL7 spec."""

import re
from pathlib import Path

# Paths
spec_path = Path("C:/Users/nicom/Downloads/EVOKI_V3_METRICS_SPECIFICATION Entwicklung/V7 Patchpaket V2 + Monolith/EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md")
output_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/docs/specifications/v3.0/regelwerk_v12.json")

# Read spec
with open(spec_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON (between ```json and ```)
pattern = r'`json\n(\{.*?\n\})\s*```'
match = re.search(pattern, content, re.DOTALL)

if match:
    json_content = match.group(1)
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_content)
    
    # Stats
    line_count = json_content.count('\n')
    size_kb = len(json_content) / 1024
    
    print(f"✅ Regelwerk V12 extracted!")
    print(f"   Lines: {line_count}")
    print(f"   Size: {size_kb:.1f} KB")
    print(f"   Output: {output_path}")
else:
    print("❌ JSON block not found in spec!")

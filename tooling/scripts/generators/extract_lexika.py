#!/usr/bin/env python3
"""Extract BUCH 6 Lexika Python Implementation from FINAL7 spec."""

from pathlib import Path
import re

# Paths
spec_path = Path("C:/Users/nicom/Downloads/EVOKI_V3_METRICS_SPECIFICATION Entwicklung/V7 Patchpaket V2 + Monolith/EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md")
output_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/backend/core/evoki_lexika_v3/lexika_complete.py")

# Read spec
with open(spec_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract lines 12434 (BUCH 6 start) to 13438 (ENDE BUCH 6)
start_line = 12434 - 1
end_line = 13438

content = ''.join(lines[start_line:end_line])

# Extract Python code blocks (between ```python and ```)
python_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

# Combine all Python code
all_code = '\n\n'.join(python_blocks)

# Add header
header = '''"""
EVOKI V3.0 LEXIKA COMPLETE
Auto-extracted from FINAL7 Specification

Source: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
Book: 6 - Vollständige Lexika-Definition
Lines: 12434-13438

All lexika for metrics calculation.
"""

from typing import List, Dict, Set

'''

full_code = header + all_code

# Write to file
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_code)

# Stats
line_count = full_code.count('\n')
size_kb = len(full_code) / 1024

print(f"✅ BUCH 6 Lexika extracted!")
print(f"   Python blocks found: {len(python_blocks)}")
print(f"   Total lines: {line_count}")
print(f"   Size: {size_kb:.1f} KB")
print(f"   Output: {output_path}")

import os
import re
from pathlib import Path

backend_lib = Path(r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib")

# 1. Resolve m162 conflict
m162_ctx = backend_lib / "m162_ctx_time.py"
m169_ctx = backend_lib / "m169_ctx_time.py"

if m162_ctx.exists():
    if not m169_ctx.exists():
        os.rename(m162_ctx, m169_ctx)
        print("✅ Renamed m162_ctx_time.py -> m169_ctx_time.py")
    else:
        print("⚠️ m169_ctx_time.py already exists, skipping rename.")

# 2. Generate __init__.py
print("\n--- Generating __init__.py ---")

metric_files = sorted(backend_lib.glob("m*.py"))
exports = []
imports = []

for f in metric_files:
    if f.name == "__init__.py": continue
    
    # Read file to find function name
    content = f.read_text(encoding="utf-8")
    match = re.search(r"def (compute_m\w+)", content)
    if match:
        func_name = match.group(1)
        mod_name = f.stem
        imports.append(f"from .{mod_name} import {func_name}")
        exports.append(f"    '{func_name}',")

# Write new __init__.py
init_content = [
    '"""',
    'EVOKI V3.0 METRICS LIBRARY - AUTO-GENERATED',
    'Contains 193+ metrics (V11.1 Physics + V3 Complete)',
    '"""',
    '',
    '# Core Helpers',
    'from ._helpers import tokenize, clamp',
    'from ._lexika import *',
    '',
    '# Metrics Imports'
] + imports + [
    '',
    '__all__ = [',
    "    'tokenize',",
    "    'clamp',",
] + exports + [
    ']'
]

init_path = backend_lib / "__init__.py"
init_path.write_text("\n".join(init_content), encoding="utf-8")
print(f"✅ Updated __init__.py with {len(imports)} metrics.")

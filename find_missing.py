#!/usr/bin/env python3
"""Find missing metrics by comparing contract vs extracted functions."""

import json
import re
from pathlib import Path

# Paths
contract_path = Path("C:/Users/nicom/Downloads/EVOKI_V3_METRICS_SPECIFICATION Entwicklung/V7 Patchpaket V2 + Monolith/evoki_fullspectrum168_contract.json")
extracted_path = Path("C:/Evoki V3.0 APK-Lokalhost-Google Cloude/backend/core/evoki_metrics_v3/metrics_from_spec.py")

# Load contract
with open(contract_path, 'r', encoding='utf-8') as f:
    contract = json.load(f)

# Extract function names from generated file
with open(extracted_path, 'r', encoding='utf-8') as f:
    extracted_code = f.read()

extracted_funcs = set(re.findall(r'def (compute_m\d+_\w+)', extracted_code))

# Expected from contract
expected_funcs = set()
for metric in contract:
    engine_key = metric['engine_key']
    expected_funcs.add(f"compute_{engine_key}")

# Find missing
missing = expected_funcs - extracted_funcs
print(f"Contract expects: {len(expected_funcs)} functions")
print(f"Extracted: {len(extracted_funcs)} functions")
print(f"Missing: {len(missing)} functions\n")

if missing:
    print("MISSING FUNCTIONS:")
    for func in sorted(missing):
        # Find metric details
        metric_id = func.replace('compute_', '')
        for m in contract:
            if m['engine_key'] == metric_id:
                print(f"  - {func}")
                print(f"    ID: {m['metric_id']}")
                print(f"    Primary: {m['spec_id_primary']}")
                print(f"    Category: {m['category']}")
                print()

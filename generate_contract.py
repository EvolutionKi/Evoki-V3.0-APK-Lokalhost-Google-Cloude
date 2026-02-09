#!/usr/bin/env python3
"""
Generate FullSpectrum168 Contract JSON from calculator_spec

Extracts ALL 168 metrics with:
- id (m1, m2, ...)
- name (m1_A, m2_PCI, ...)
- category (core, physics, trauma, ...)
- data_type (float, int, str)
- range (min, max)
- source (engine, function)
- description
"""

import sys
import json
import re
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import calculator_spec as module
import backend.core.evoki_metrics_v3.calculator_spec_A_PHYS_V11 as calc_spec

def extract_function_signature(func):
    """Extract info from function"""
    import inspect
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or "No description"
    
    return {
        "signature": str(sig),
        "doc": doc.split('\n')[0][:200]  # First line, max 200 chars
    }

def infer_category(metric_id):
    """Infer category from metric ID"""
    num = int(re.search(r'\d+', metric_id).group())
    
    if 1 <= num <= 20:
        return "core"
    elif 21 <= num <= 35:
        return "physics"
    elif 36 <= num <= 55:
        return "token_economy"
    elif 56 <= num <= 73:
        return "andromatik"
    elif 74 <= num <= 95:
        return "sentiment"
    elif 96 <= num <= 99:
        return "grain"
    elif 101 <= num <= 115:
        return "trauma"
    elif 116 <= num <= 140:
        return "text_analysis"
    elif 141 <= num <= 150:
        return "rag"
    elif 151 <= num <= 161:
        return "meta"
    elif 162 <= num <= 167:
        return "context"
    elif num == 168:
        return "cumulative"
    else:
        return "unknown"

def infer_range(metric_id, category):
    """Infer range from metric"""
    # Most metrics [0, 1]
    default = {"min": 0.0, "max": 1.0, "unit": "normalized"}
    
    # Special cases
    if "PCI" in metric_id:
        return {"min": -1.0, "max": 1.0, "unit": "correlation"}
    elif "delta" in metric_id or "grad" in metric_id:
        return {"min": -1.0, "max": 1.0, "unit": "delta"}
    elif "token" in metric_id:
        return {"min": 0.0, "max": 100.0, "unit": "tokens"}
    elif "lix" in metric_id:
        return {"min": 0.0, "max": 100.0, "unit": "readability"}
    elif category == "grain":
        return {"min": 0.0, "max": 1.0, "unit": "score"}
    
    return default

def generate_contract():
    """Generate full contract"""
    
    print("=" * 100)
    print("🔨 GENERATING FULLSPECTRUM168 CONTRACT")
    print("=" * 100)
    
    metrics = []
    
    # Get all compute_* functions from calc_spec
    all_funcs = [name for name in dir(calc_spec) if name.startswith('compute_m')]
    
    print(f"\n📊 Found {len(all_funcs)} compute_m* functions")
    
    for func_name in sorted(all_funcs):
        # SKIP legacy ctx_ functions (we have context_ versions!)
        if '_ctx_' in func_name:
            print(f"  ⏭️  {func_name:30s} | SKIPPED (legacy ctx_)")
            continue
        
        func = getattr(calc_spec, func_name)
        
        # Extract metric ID
        match = re.search(r'm(\d+)_(\w+)', func_name)
        if not match:
            continue
        
        num, name_suffix = match.groups()
        metric_id = f"m{num}_{name_suffix}"
        category = infer_category(metric_id)
        range_info = infer_range(metric_id, category)
        
        # Extract signature
        info = extract_function_signature(func)
        
        metric = {
            "id": int(num),
            "name": metric_id,
            "category": category,
            "data_type": "float",  # Most are float
            "range": range_info,
            "source": {
                "engine": "calculator_spec_A_PHYS_V11",
                "function": func_name
            },
            "description": info["doc"]
        }
        
        metrics.append(metric)
        print(f"  ✅ {metric_id:20s} | {category:15s} | {info['doc'][:50]}")
    
    # Sort by ID
    metrics.sort(key=lambda m: m["id"])
    
    contract = {
        "version": "1.0.0",
        "spec_version": "V7_AUDITFIX_FINAL7",
        "generated_at": "2026-02-08T00:11:00Z",
        "metrics_count": len(metrics),
        "metrics": metrics
    }
    
    # Write to file
    output_path = Path(__file__).parent / "evoki_fullspectrum168_contract.json"
    output_path.write_text(json.dumps(contract, indent=2, ensure_ascii=False), encoding='utf-8')
    
    print(f"\n{'=' * 100}")
    print(f"✅ CONTRACT GENERATED!")
    print(f"{'=' * 100}")
    print(f"\n📁 Location: {output_path}")
    print(f"📊 Metrics: {len(metrics)}")
    print(f"\n📋 Categories:")
    
    from collections import Counter
    cat_counts = Counter(m["category"] for m in metrics)
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat:20s}: {count:3d} metrics")
    
    return contract

if __name__ == "__main__":
    contract = generate_contract()
    print("\n🎉 DONE!")

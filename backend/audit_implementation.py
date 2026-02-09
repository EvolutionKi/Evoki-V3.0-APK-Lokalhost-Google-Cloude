#!/usr/bin/env python3
"""
Audit current 4-phase implementation against contract

Shows:
- Which metrics are implemented
- Which have correct names
- Which are missing
- Implementation coverage by phase
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, r"c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3")

from contract_registry import get_registry
import phase1_base
import phase2_derived
import phase3_physics
import phase4_synthesis

def get_compute_functions(module):
    """Extract all compute_m* functions from module"""
    funcs = {}
    for name in dir(module):
        if name.startswith("compute_m") and callable(getattr(module, name)):
            metric_name = name.replace("compute_", "")
            funcs[metric_name] = module.__name__.split(".")[-1]
    return funcs

def main():
    print("=" * 80)
    print("CONTRACT vs. IMPLEMENTATION AUDIT")
    print("=" * 80)
    
    # Load contract
    registry = get_registry()
    print(f"\n📋 Contract: {len(registry.metrics)} metrics defined")
    
    # Scan implementation
    modules = [
        ("Phase 1", phase1_base),
        ("Phase 2", phase2_derived),
        ("Phase 3", phase3_physics),
        ("Phase 4", phase4_synthesis)
    ]
    
    all_implemented = {}
    for phase_name, module in modules:
        funcs = get_compute_functions(module)
        all_implemented.update(funcs)
        print(f"  {phase_name:10s} {len(funcs):3d} compute functions")
    
    print(f"\n📊 Total implemented: {len(all_implemented)}")
    
    # Compare
    contract_names = {m.canonical_name for m in registry.metrics}
    impl_names = set(all_implemented.keys())
    
    # Also check engine names
    engine_names = {m.engine_key for m in registry.metrics}
    
    # Match analysis
    exact_match = contract_names & impl_names
    engine_match = engine_names & impl_names
    missing = contract_names - impl_names - engine_match
    
    print(f"\n✅ Exact name matches:  {len(exact_match)}")
    print(f"⚠️  Engine name matches: {len(engine_match)} (need alias)")
    print(f"❌ Missing:             {len(missing)}")
    print(f"➕ Extra (not in contract): {len(impl_names - contract_names - engine_names)}")
    
    # Missing by category
    print(f"\n{'─' * 80}")
    print("MISSING METRICS BY CATEGORY:")
    print("─" * 80)
    
    missing_by_cat = {}
    for m in registry.metrics:
        if m.canonical_name in missing or (m.canonical_name not in impl_names and m.engine_key not in impl_names):
            cat = m.category
            if cat not in missing_by_cat:
                missing_by_cat[cat] = []
            missing_by_cat[cat].append(m)
    
    for cat in sorted(missing_by_cat.keys(), key=lambda c: -len(missing_by_cat[c]))[:15]:
        metrics = missing_by_cat[cat]
        print(f"\n{cat} ({len(metrics)}):")
        for m in metrics[:5]:
            print(f"  - {m.canonical_name} (range: {m.range_effective})")
        if len(metrics) > 5:
            print(f"  ... and {len(metrics) - 5} more")
    
    # Name mismatch details
    print(f"\n{'─' * 80}")
    print("NAME MISMATCHES (First 20):")
    print("─" * 80)
    
    mismatches = registry.get_mismatches()
    for m in mismatches[:20]:
        impl_status = "✓" if m.engine_key in impl_names else "✗"
        print(f"{impl_status} {m.metric_id:3d}. Spec: {m.canonical_name:25s} Engine: {m.engine_key:25s}")
    
    print(f"\n... {len(mismatches) - 20} more mismatches")
    
    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY:")
    print("=" * 80)
    print(f"  Contract defines:     {len(contract_names)} metrics")
    print(f"  Currently implemented: {len(impl_names)} compute functions")
    print(f"  Coverage:              {len(exact_match | engine_match) / len(contract_names) * 100:.1f}%")
    print(f"  Missing:               {len(missing)} metrics")
    print(f"  Name fixes needed:     {len(mismatches)} mismatches")
    print("=" * 80)

if __name__ == "__main__":
    main()

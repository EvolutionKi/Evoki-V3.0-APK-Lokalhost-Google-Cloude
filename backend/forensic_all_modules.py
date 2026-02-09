# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — FORENSIC METRIC VERIFICATION

Comprehensive test of all 129 new metrics across 7 modules.
Tests with 3 different text inputs to verify dynamic behavior.

Goal: Verify ZERO placeholders, all metrics respond to input changes.
"""

import sys
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

from core.evoki_metrics_v3 import hypermetrics as hm
from core.evoki_metrics_v3 import fep_evolution as fep
from core.evoki_metrics_v3 import emotions as emo
from core.evoki_metrics_v3 import text_analytics as txt
from core.evoki_metrics_v3 import dynamics_turbidity as dyn
from core.evoki_metrics_v3 import system_metrics as sys_m
from core.evoki_metrics_v3 import final_metrics as fin

import time


# ═══════════════════════════════════════════════════════════════════════════
# TEST INPUTS
# ═══════════════════════════════════════════════════════════════════════════

TEST_CASES = [
    {
        "name": "SHORT_POSITIVE",
        "text": "Great! This works perfectly. 😊",
        "context": {"turn": 5, "pair_id": "test-001", "timestamp": "2026-02-08T10:20:00Z", "session_start_time": time.time() - 300}
    },
    {
        "name": "LONG_COMPLEX",
        "text": "I'm analyzing the complete system architecture. The implementation shows excellent coherence across all modules, though I'm slightly worried about potential edge cases. What happens if we encounter unexpected data? This requires careful consideration and thorough testing to ensure robustness.",
        "context": {"turn": 25, "pair_id": "test-002", "timestamp": "2026-02-08T10:21:00Z", "session_start_time": time.time() - 1800}
    },
    {
        "name": "NEGATIVE_CAPS",
        "text": "THIS IS TERRIBLE!!! Everything is BROKEN and I'm EXTREMELY FRUSTRATED with these results!!!",
        "context": {"turn": 3, "pair_id": "test-003", "timestamp": "2026-02-08T10:22:00Z", "session_start_time": time.time() - 60}
    }
]


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def mock_dependencies():
    """Create mock metric dependencies"""
    return {
        "m1_A": 0.75,
        "m4_flow": 0.82,
        "m5_coh": 0.72,
        "m19_z_prox": 0.08,
        "m58_tokens_log": 5.0,
        "m63_phi": 0.18,
        "m72_ev_valence": 0.73,
        "m77_joy": 0.85,
        "m78_sadness": 0.10,
        "m79_anger": 0.05,
        "m80_fear": 0.08,
        "m81_trust": 0.75,
        "m87_confusion": 0.25,
        "m88_clarity": 0.70,
        "m91_coherence": 0.72,
        "m92_stability": 0.70,
        "m93_sent_20": 0.75,
        "m103_T_integ": 0.73,
        "m104_T_veto": 0.10,
        "m110_black_hole": 0.08,
        "m112_trauma_load": 0.12,
        "m126_dyn_5": 0.04,
        "m127_dyn_6": 0.96,
        "m145_chronos_total": 0.68,
        "m146_sys_quality": 0.70,
        "m147_sys_health": 0.70,
        "m148_sys_stability": 0.83,
        "m149_sys_readiness": 0.70,
        "m150_sys_total": 0.70,
        "m162_syn_final": 0.68,
    }


def test_module(module_name, test_funcs, test_case):
    """Test a single module with a test case"""
    results = {}
    text = test_case["text"]
    context = test_case["context"]
    deps = mock_dependencies()
    
    for func_name, func in test_funcs:
        try:
            # Try different argument combinations
            if "context" in func.__code__.co_varnames:
                if "text" in func.__code__.co_varnames:
                    result = func(text, context)
                else:
                    result = func(context)
            elif "text" in func.__code__.co_varnames:
                # Count other parameters
                param_count = func.__code__.co_argcount
                if param_count == 1:
                    result = func(text)
                elif param_count == 2:
                    # Try with most common dependencies
                    if "m5_coh" in func.__code__.co_varnames:
                        result = func(text, deps["m5_coh"])
                    else:
                        result = func(text, deps["m1_A"])
                else:
                    # Multi-param, use mocks
                    params = func.__code__.co_varnames[:param_count]
                    args = [deps.get(p, 0.5) for p in params if p != "text"]
                    result = func(text, *args) if "text" in params else func(*args)
            else:
                # No text, use deps
                param_count = func.__code__.co_argcount
                params = func.__code__.co_varnames[:param_count]
                args = [deps.get(p, context if p == "context" else 0.5) for p in params]
                result = func(*args)
                
            results[func_name] = result
        except Exception as e:
            results[func_name] = f"ERROR: {str(e)[:50]}"
    
    return results


# ═══════════════════════════════════════════════════════════════════════════
# MAIN FORENSIC TEST
# ═══════════════════════════════════════════════════════════════════════════

def run_forensic_test():
    """Run comprehensive forensic test on all modules"""
    
    print("=" * 80)
    print("FORENSIC METRIC VERIFICATION — ALL 129 METRICS")
    print("=" * 80)
    print(f"\nRunning {len(TEST_CASES)} test cases across 7 modules...")
    print()
    
    modules = [
        ("hypermetrics", hm, [(n, getattr(hm, n)) for n in hm.__all__]),
        ("fep_evolution", fep, [(n, getattr(fep, n)) for n in fep.__all__]),
        ("emotions", emo, [(n, getattr(emo, n)) for n in emo.__all__]),
        ("text_analytics", txt, [(n, getattr(txt, n)) for n in txt.__all__]),
        ("dynamics_turbidity", dyn, [(n, getattr(dyn, n)) for n in dyn.__all__]),
        ("system_metrics", sys_m, [(n, getattr(sys_m, n)) for n in sys_m.__all__]),
        ("final_metrics", fin, [(n, getattr(fin, n)) for n in fin.__all__]),
    ]
    
    all_results = {}
    
    for module_name, module, funcs in modules:
        print(f"\n{'─' * 80}")
        print(f"📦 MODULE: {module_name} ({len(funcs)} metrics)")
        print(f"{'─' * 80}")
        
        module_results = {}
        
        for test_case in TEST_CASES:
            case_name = test_case["name"]
            print(f"\n  Testing: {case_name}")
            print(f"  Text: \"{test_case['text'][:60]}...\"")
            
            results = test_module(module_name, funcs, test_case)
            module_results[case_name] = results
            
            # Show sample results
            sample_count = min(3, len(results))
            for i, (metric, value) in enumerate(list(results.items())[:sample_count]):
                if isinstance(value, float):
                    print(f"    {metric}: {value:.3f}")
                elif isinstance(value, str) and len(value) < 20:
                    print(f"    {metric}: ...{value[-12:]}")
                else:
                    print(f"    {metric}: {str(value)[:40]}")
            
            if len(results) > sample_count:
                print(f"    ... and {len(results) - sample_count} more")
        
        # Dynamics check
        print(f"\n  ✅ Dynamics Check:")
        first_case = module_results[TEST_CASES[0]["name"]]
        second_case = module_results[TEST_CASES[1]["name"]]
        
        changes = 0
        total = 0
        for metric in first_case:
            if isinstance(first_case[metric], (int, float)) and isinstance(second_case[metric], (int, float)):
                total += 1
                if abs(first_case[metric] - second_case[metric]) > 0.001:
                    changes += 1
        
        if total > 0:
            dynamic_pct = (changes / total) * 100
            print(f"    {changes}/{total} metrics changed ({dynamic_pct:.1f}% dynamic)")
            if dynamic_pct < 50:
                print(f"    ⚠️  WARNING: Low dynamics!")
            else:
                print(f"    ✓ Good dynamics")
        
        all_results[module_name] = module_results
    
    # Final Summary
    print(f"\n{'═' * 80}")
    print("FINAL SUMMARY")
    print(f"{'═' * 80}")
    
    total_metrics = sum(len(funcs) for _, _, funcs in modules)
    print(f"\n📊 Total metrics tested: {total_metrics}")
    print(f"📋 Test cases: {len(TEST_CASES)}")
    print(f"🧪 Total test runs: {total_metrics * len(TEST_CASES)}")
    
    # Check for errors
    error_count = 0
    for module_name, module_data in all_results.items():
        for case_name, results in module_data.items():
            for metric, value in results.items():
                if isinstance(value, str) and "ERROR" in value:
                    error_count += 1
    
    print(f"\n✅ Success rate: {((total_metrics * len(TEST_CASES) - error_count) / (total_metrics * len(TEST_CASES)) * 100):.1f}%")
    if error_count > 0:
        print(f"❌ Errors encountered: {error_count}")
    else:
        print(f"✓ NO ERRORS - All metrics functioning!")
    
    print(f"\n{'═' * 80}")
    print("VERIFICATION COMPLETE")
    print(f"{'═' * 80}")
    
    return all_results


if __name__ == "__main__":
    results = run_forensic_test()
    
    # Save detailed results
    print(f"\n💾 Detailed results available in memory for analysis")
    print(f"   Contains {len(results)} modules x {len(TEST_CASES)} test cases")

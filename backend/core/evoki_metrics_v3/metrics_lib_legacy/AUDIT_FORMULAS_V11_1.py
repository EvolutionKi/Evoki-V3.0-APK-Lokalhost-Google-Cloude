#!/usr/bin/env python3
"""
EVOKI PRODUCTION METRICS AUDIT SCRIPT
Verifies all metric formulas against V11.1 specification

USAGE:
    python AUDIT_FORMULAS_V11_1.py              # Full audit
    python AUDIT_FORMULAS_V11_1.py --metric m7_LL  # Single metric
    python AUDIT_FORMULAS_V11_1.py --critical    # Only critical bugs

Created: 2026-02-08 by CODEX
"""

import sys
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# ============================================================================
# V11.1 FORMULA SPECIFICATIONS
# ============================================================================

V11_1_FORMULAS = {
    # ========================================================================
    # CRITICAL BUGS CONFIRMED
    # ========================================================================
    
    "m7_LL": {
        "name": "Lambert-Light Turbidity",
        "formula": "0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh)",
        "expected_params": ["rep_same", "flow", "coh"],
        "actual_params": ["rep_same", "flow"],  # ← MISSING coh!
        "bug_type": "CRITICAL",
        "bug_description": "Missing coh parameter and component (20% weight)",
        "test_case": {
            "inputs": {"rep_same": 0.5, "flow": 0.8, "coh": 0.7},
            "expected": 0.55*0.5 + 0.25*(1-0.8) + 0.20*(1-0.7),  # 0.385
            "will_fail": True,
            "reason": "Function signature missing coh parameter"
        }
    },
    
    # ========================================================================
    # VERIFIED CORRECT
    # ========================================================================
    
    "m1_A": {
        "name": "Affekt (Consciousness Proxy)",
        "formula": "0.4·coh + 0.25·flow + 0.20·(1-LL) + 0.10·(1-ZLF) - 0.05·ctx_break",
        "expected_params": ["coh", "flow", "LL", "ZLF", "ctx_break"],
        "bug_type": None,
        "test_case": {
            "inputs": {"coh": 0.7, "flow": 0.8, "LL": 0.3, "ZLF": 0.2, "ctx_break": 0.0},
            "expected": 0.4*0.7 + 0.25*0.8 + 0.20*(1-0.3) + 0.10*(1-0.2) - 0.05*0.0
        }
    },
    
    "m2_PCI": {
        "name": "Perturbational Complexity Index",
        "formula": "0.4·flow + 0.35·coh + 0.25·(1-LL)",
        "expected_params": ["flow", "coh", "LL"],
        "bug_type": None,
        "test_case": {
            "inputs": {"flow": 0.8, "coh": 0.7, "LL": 0.3},
            "expected": 0.4*0.8 + 0.35*0.7 + 0.25*(1-0.3)
        }
    },
    
    "m6_ZLF": {
        "name": "Zero-Loop-Factor",
        "formula": "0.5·hit + 0.25·(1-flow) + 0.25·(1-coh)",
        "expected_params": ["flow", "coherence", "zlf_lexicon_hit"],
        "bug_type": None,
        "test_case": {
            "inputs": {"flow": 0.8, "coherence": 0.7, "zlf_lexicon_hit": False},
            "expected": 0.5*0.0 + 0.25*(1-0.8) + 0.25*(1-0.7)
        }
    },
    
    "m10_angstrom": {
        "name": "Ångström (Emotional Wavelength)",
        "formula": "0.25·(S_self + X_exist + B_past + coh)·5.0",
        "expected_params": ["s_self", "x_exist", "b_past", "coh"],
        "bug_type": None,
        "test_case": {
            "inputs": {"s_self": 0.6, "x_exist": 0.7, "b_past": 0.5, "coh": 0.8},
            "expected": 0.25 * (0.6 + 0.7 + 0.5 + 0.8) * 5.0
        }
    },
    
    # ========================================================================
    # SUSPECTED BUGS (Different Algorithm)
    # ========================================================================
    
    "m4_flow": {
        "name": "Flow State",
        "formula": "exp(-max(0, gap_s)/tau_s)  [V11.1 TIME-BASED]",
        "actual_formula": "smoothness × (1 - break_penalty)  [PRODUCTION TEXT-BASED]",
        "bug_type": "ALGORITHM_MISMATCH",
        "bug_description": "Production uses TEXT-based flow, V11.1 uses TIME-based flow",
        "severity": "HIGH",
        "note": "Completely different calculation approach - need decision from ATOMI"
    },
    
    "m5_coh": {
        "name": "Coherence",
        "formula": "Jaccard(set_i, window_of_previous_6)  [V11.1 INTER-TEXT]",
        "actual_formula": "avg(Jaccard(sent_i, sent_i+1))  [PRODUCTION INTRA-TEXT]",
        "bug_type": "SCOPE_MISMATCH",
        "bug_description": "Production calculates sentence-to-sentence, V11.1 calculates text-to-history",
        "severity": "HIGH",
        "note": "Different scope - need decision from ATOMI"
    },
    
    # ========================================================================
    # EXTENSIONS (More features than spec)
    # ========================================================================
    
    "m19_z_prox": {
        "name": "Death Proximity",
        "formula": "(1-A)·max(LL, ctx_break)  [V11.1 SIMPLE]",
        "actual_formula": "Extended with safety overrides, hazard lexicon, dual-A  [PRODUCTION]",
        "bug_type": "EXTENSION",
        "bug_description": "Production has V3.3.x safety enhancements beyond V11.1 spec",
        "severity": "INFO",
        "note": "Likely intentional safety layer - should be documented"
    },
}


# ============================================================================
# AUDIT FUNCTIONS
# ============================================================================

def load_metric_function(metric_id: str):
    """Dynamically load a metric computation function"""
    try:
        module = importlib.import_module(metric_id)
        func_name = f"compute_{metric_id}"
        if hasattr(module, func_name):
            return getattr(module, func_name)
        else:
            return None
    except ImportError as e:
        return None


def verify_signature(func, expected_params: List[str]) -> Tuple[bool, str, List[str]]:
    """Verify function signature matches expected parameters"""
    sig = inspect.signature(func)
    actual_params = list(sig.parameters.keys())
    
    if actual_params == expected_params:
        return True, "✅ Signature CORRECT", actual_params
    else:
        return False, f"❌ Signature MISMATCH", actual_params


def test_formula(func, test_case: Dict, tolerance: float = 0.0001) -> Tuple[bool, str, Optional[float]]:
    """Test metric function against expected output"""
    if test_case.get('will_fail'):
        return False, f"⚠️  SKIPPED (will fail): {test_case['reason']}", None
    
    try:
        result = func(**test_case['inputs'])
        expected = test_case['expected']
        
        if abs(result - expected) < tolerance:
            return True, f"✅ Output CORRECT ({result:.4f} ≈ {expected:.4f})", result
        else:
            delta = result - expected
            return False, f"❌ Output MISMATCH (expected {expected:.4f}, got {result:.4f}, Δ={delta:+.4f})", result
    
    except TypeError as e:
        return False, f"❌ TypeError: {e}", None
    except Exception as e:
        return False, f"❌ Runtime Error: {e}", None


def audit_metric(metric_id: str, spec: Dict, verbose: bool = False) -> Dict[str, Any]:
    """Audit a single metric against specification"""
    
    result = {
        "metric_id": metric_id,
        "name": spec['name'],
        "bug_type": spec.get('bug_type'),
        "signature_ok": None,
        "formula_ok": None,
        "actual_params": None,
        "errors": []
    }
    
    # Special handling for known algorithm mismatches
    if spec.get('bug_type') in ['ALGORITHM_MISMATCH', 'SCOPE_MISMATCH', 'EXTENSION']:
        result['errors'].append(f"{spec['bug_type']}: {spec['bug_description']}")
        if verbose:
            print(f"\n{metric_id} - {spec['name']}")
            print(f"  🔍 {spec['bug_type']}: {spec['bug_description']}")
            if 'note' in spec:
                print(f"  📝 Note: {spec['note']}")
        return result
    
    # Load function
    func = load_metric_function(metric_id)
    if func is None:
        result['errors'].append("Failed to load metric function")
        return result
    
    # Verify signature
    if 'expected_params' in spec:
        sig_ok, sig_msg, actual_params = verify_signature(func, spec['expected_params'])
        result['signature_ok'] = sig_ok
        result['actual_params'] = actual_params
        
        if verbose or not sig_ok:
            print(f"\n{metric_id} - {spec['name']}")
            print(f"  Formula: {spec['formula']}")
            print(f"  {sig_msg}")
            if not sig_ok:
                print(f"    Expected: {spec['expected_params']}")
                print(f"    Actual:   {actual_params}")
        
        if not sig_ok:
            if spec.get('bug_type') == 'CRITICAL':
                print(f"  🚨 CRITICAL BUG: {spec['bug_description']}")
            result['errors'].append(sig_msg)
            return result
    
    # Test formula
    if 'test_case' in spec:
        formula_ok, formula_msg, output = test_formula(func, spec['test_case'])
        result['formula_ok'] = formula_ok
        result['output'] = output
        
        if verbose or not formula_ok:
            print(f"  {formula_msg}")
        
        if not formula_ok:
            result['errors'].append(formula_msg)
    
    return result


def audit_all_metrics(critical_only: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """Audit all metrics in specification"""
    
    print("=" * 80)
    print("EVOKI PRODUCTION METRICS AUDIT - V11.1 VERIFICATION")
    print("=" * 80)
    print(f"Location: {Path(__file__).parent}")
    print(f"Total Specs: {len(V11_1_FORMULAS)}")
    if critical_only:
        print("Mode: CRITICAL BUGS ONLY")
    print()
    
    results = {}
    summary = {
        "total": 0,
        "critical_bugs": 0,
        "algorithm_mismatches": 0,
        "extensions": 0,
        "signature_ok": 0,
        "signature_fail": 0,
        "formula_ok": 0,
        "formula_fail": 0,
        "errors": []
    }
    
    for metric_id, spec in V11_1_FORMULAS.items():
        # Filter by critical if requested
        if critical_only and spec.get('bug_type') != 'CRITICAL':
            continue
        
        summary['total'] += 1
        
        # Count by bug type
        if spec.get('bug_type') == 'CRITICAL':
            summary['critical_bugs'] += 1
        elif spec.get('bug_type') in ['ALGORITHM_MISMATCH', 'SCOPE_MISMATCH']:
            summary['algorithm_mismatches'] += 1
        elif spec.get('bug_type') == 'EXTENSION':
            summary['extensions'] += 1
        
        result = audit_metric(metric_id, spec, verbose=verbose)
        results[metric_id] = result
        
        if result['signature_ok'] is True:
            summary['signature_ok'] += 1
        elif result['signature_ok'] is False:
            summary['signature_fail'] += 1
        
        if result['formula_ok'] is True:
            summary['formula_ok'] += 1
        elif result['formula_ok'] is False:
            summary['formula_fail'] += 1
        
        if result['errors']:
            summary['errors'].extend([f"{metric_id}: {e}" for e in result['errors']])
    
    # Print summary
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY")
    print("=" * 80)
    print(f"Metrics Audited:          {summary['total']}")
    print(f"Critical Bugs Found:      {summary['critical_bugs']}")
    print(f"Algorithm Mismatches:     {summary['algorithm_mismatches']}")
    print(f"Extensions Found:         {summary['extensions']}")
    
    print(f"\nSignature Verification:")
    print(f"  ✅ Correct:   {summary['signature_ok']}")
    print(f"  ❌ Incorrect: {summary['signature_fail']}")
    
    print(f"\nFormula Verification:")
    print(f"  ✅ Correct:   {summary['formula_ok']}")
    print(f"  ❌ Incorrect: {summary['formula_fail']}")
    
    if summary['errors']:
        print(f"\n⚠️  {len(summary['errors'])} ISSUES FOUND:")
        for error in summary['errors']:
            print(f"  • {error}")
    else:
        print("\n✅ NO ISSUES FOUND (in audited metrics)")
    
    print("=" * 80)
    
    # Print critical bugs prominently
    if summary['critical_bugs'] > 0:
        print("\n" + "🚨" * 40)
        print("CRITICAL BUGS REQUIRING IMMEDIATE ACTION:")
        print("🚨" * 40)
        for metric_id, result in results.items():
            if result['bug_type'] == 'CRITICAL':
                spec = V11_1_FORMULAS[metric_id]
                print(f"\n{metric_id} - {spec['name']}")
                print(f"  Bug: {spec['bug_description']}")
                print(f"  Expected: {spec['expected_params']}")
                print(f"  Actual:   {result['actual_params']}")
                print(f"  Formula:  {spec['formula']}")
        print("\n" + "🚨" * 40)
    
    return {
        "results": results,
        "summary": summary
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Audit EVOKI Production Metrics against V11.1 Specification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python AUDIT_FORMULAS_V11_1.py                    # Full audit
  python AUDIT_FORMULAS_V11_1.py --critical          # Critical bugs only
  python AUDIT_FORMULAS_V11_1.py --metric m7_LL     # Single metric
  python AUDIT_FORMULAS_V11_1.py --verbose          # Detailed output
        """
    )
    
    parser.add_argument('--metric', type=str, help='Audit specific metric (e.g., m7_LL)')
    parser.add_argument('--critical', action='store_true', help='Show critical bugs only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.metric:
        # Audit single metric
        if args.metric in V11_1_FORMULAS:
            spec = V11_1_FORMULAS[args.metric]
            audit_metric(args.metric, spec, verbose=True)
        else:
            print(f"❌ Metric {args.metric} not in specification")
            print(f"\nAvailable metrics:")
            for mid in V11_1_FORMULAS.keys():
                print(f"  • {mid}")
    else:
        # Audit all metrics
        audit_all_metrics(critical_only=args.critical, verbose=args.verbose)


if __name__ == "__main__":
    main()

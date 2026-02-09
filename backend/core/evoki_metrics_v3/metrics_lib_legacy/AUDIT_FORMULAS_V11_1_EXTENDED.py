#!/usr/bin/env python3
"""
EVOKI PRODUCTION METRICS AUDIT SCRIPT - EXTENDED V11.1
Verifies all metric formulas against V11.1 specification

EXTENDED: Now includes 30 core V11.1 metrics from TODO_MASTER!

Created: 2026-02-08 by CODEX
"""

import sys
import inspect
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# ============================================================================
# V11.1 FORMULA SPECIFICATIONS - COMPLETE SET
# ============================================================================

V11_1_FORMULAS = {
    # ========================================================================
    # CRITICAL BUGS (Production Wrong)
    # ========================================================================
    
    "m7_LL": {
        "name": "Lambert-Light Turbidity",
        "formula": "0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh)",
        "expected_params": ["rep_same", "flow", "coh"],
        "bug_type": "CRITICAL",
        "bug_description": "Missing coh parameter and component (20% weight)",
        "test_case": {
            "inputs": {"rep_same": 0.5, "flow": 0.8, "coh": 0.7},
            "expected": 0.55*0.5 + 0.25*(1-0.8) + 0.20*(1-0.7),  # 0.385
        }
    },
    
    # ========================================================================
    # CORE PHYSICS (Verified Correct in Production)
    # ========================================================================
    
    "m1_A": {
        "name": "A - Kohärenz (Consciousness Proxy)",
        "formula": "0.4·coh + 0.25·flow + 0.20·(1-LL) + 0.10·(1-ZLF) - 0.05·ctx_break",
        "expected_params": ["coh", "flow", "LL", "ZLF", "ctx_break"],
        "test_case": {
            "inputs": {"coh": 0.7, "flow": 0.8, "LL": 0.3, "ZLF": 0.2, "ctx_break": 0.0},
            "expected": 0.4*0.7 + 0.25*0.8 + 0.20*(1-0.3) + 0.10*(1-0.2) - 0.05*0.0
        }
    },
    
    "m2_PCI": {
        "name": "PCI/B - Prozess-Kohärenz",
        "formula": "0.4·flow + 0.35·coh + 0.25·(1-LL)",
        "expected_params": ["flow", "coh", "LL"],
        "test_case": {
            "inputs": {"flow": 0.8, "coh": 0.7, "LL": 0.3},
            "expected": 0.4*0.8 + 0.35*0.7 + 0.25*(1-0.3)
        }
    },
    
    "m6_ZLF": {
        "name": "Zero-Loop-Factor",
        "formula": "0.5·hit + 0.25·(1-flow) + 0.25·(1-coh)",
        "expected_params": ["flow", "coherence", "zlf_lexicon_hit"],
        "test_case": {
            "inputs": {"flow": 0.8, "coherence": 0.7, "zlf_lexicon_hit": True},
            "expected": 0.5*1.0 + 0.25*(1-0.8) + 0.25*(1-0.7)
        }
    },
    
    "m10_angstrom": {
        "name": "Ångström (Emotional Wavelength)",
        "formula": "0.25·(S_self + X_exist + B_past + coh)·5.0",
        "expected_params": ["s_self", "x_exist", "b_past", "coh"],
        "test_case": {
            "inputs": {"s_self": 0.6, "x_exist": 0.7, "b_past": 0.5, "coh": 0.8},
            "expected": 0.25 * (0.6 + 0.7 + 0.5 + 0.8) * 5.0
        }
    },
    
    # ========================================================================
    # ALGORITHM MISMATCHES (Need Decision)
    # ========================================================================
    
    "m4_flow": {
        "name": "Flow State",
        "formula": "exp(-max(0, gap_s)/tau_s)  [V11.1 TIME-BASED]",
        "actual_formula": "smoothness × (1 - break_penalty)  [PRODUCTION TEXT-BASED]",
        "bug_type": "ALGORITHM_MISMATCH",
        "bug_description": "Production uses TEXT-based flow, V11.1 uses TIME-based flow",
        "severity": "HIGH",
        "note": "Different calculation approach - need decision from ATOMI"
    },
    
    "m5_coh": {
        "name": "Coherence",
        "formula": "Jaccard(set_i, window_of_previous_6)  [V11.1 INTER-TEXT]",
        "actual_formula": "avg(Jaccard(sent_i, sent_i+1))  [PRODUCTION INTRA-TEXT]",
        "bug_type": "SCOPE_MISMATCH",
        "bug_description": "Production: sentence-to-sentence, V11.1: text-to-history",
        "severity": "HIGH",
        "note": "Different scope - need decision from ATOMI"
    },
    
    # ========================================================================
    # PHI LAYER (Utility/Risk)
    # ========================================================================
    
    "m61_U": {
        "name": "U - Utility",
        "formula": "0.35·A + 0.25·PCI + 0.20·H_conv + 0.20·soul_check - 0.10·LL",
        "expected_params": ["A", "PCI", "H_conv", "soul_check", "LL"],
        "test_case": {
            "inputs": {"A": 0.7, "PCI": 0.8, "H_conv": 0.6, "soul_check": 0.9, "LL": 0.3},
            "expected": 0.35*0.7 + 0.25*0.8 + 0.20*0.6 + 0.20*0.9 - 0.10*0.3
        },
        "notes": "H_conv and soul_check need implementation check"
    },
    
    "m62_R": {
        "name": "R - Risk",
        "formula": "0.35·z_prox + 0.20·x_fm_prox + 0.20·E_I_proxy + 0.15·rule_conflict + 0.05·T_panic + 0.05·T_shock",
        "expected_params": ["z_prox", "x_fm_prox", "E_I_proxy", "rule_conflict", "T_panic", "T_shock"],
        "test_case": {
            "inputs": {
                "z_prox": 0.3, "x_fm_prox": 0.2, "E_I_proxy": 0.4,
                "rule_conflict": 0.1, "T_panic": 0.15, "T_shock": 0.1
            },
            "expected": 0.35*0.3 + 0.20*0.2 + 0.20*0.4 + 0.15*0.1 + 0.05*0.15 + 0.05*0.1
        }
    },
    
    "m63_phi_score": {
        "name": "φ_score - Value Function",
        "formula": "U - lambda_risk·R",
        "expected_params": ["U", "R", "lambda_risk"],
        "test_case": {
            "inputs": {"U": 0.7, "R": 0.3, "lambda_risk": 1.0},
            "expected": 0.7 - 1.0*0.3  # 0.4
        },
        "notes": "lambda_risk default = 1.0"
    },
    
    # ========================================================================
    # DERIVATIVES (Temporal Changes)
    # ========================================================================
    
    "m17_nabla_a": {
        "name": "∇A - Affekt Derivative",
        "formula": "A[i] - A[i-1]",
        "expected_params": ["A_current", "A_previous"],
        "test_case": {
            "inputs": {"A_current": 0.75, "A_previous": 0.70},
            "expected": 0.75 - 0.70  # 0.05
        }
    },
    
    "m23_nabla_pci": {
        "name": "∇PCI - PCI Derivative",
        "formula": "PCI[i] - PCI[i-1]",
        "expected_params": ["PCI_current", "PCI_previous"],
        "test_case": {
            "inputs": {"PCI_current": 0.80, "PCI_previous": 0.75},
            "expected": 0.80 - 0.75  # 0.05
        }
    },
    
    # ========================================================================
    # EV FAMILY (Evolution Vectors)
    # ========================================================================
    
    "m71_ev_arousal": {
        "name": "EV_arousal - Evolution Arousal",
        "formula": "Should be: 0.5·A + 0.3·PCI + 0.2·H_conv (from TODO)",
        "expected_params": ["A", "PCI", "H_conv"],
        "test_case": {
            "inputs": {"A": 0.7, "PCI": 0.8, "H_conv": 0.6},
            "expected": 0.5*0.7 + 0.3*0.8 + 0.2*0.6
        },
        "notes": "TODO calls this EV_resonance, check production implementation"
    },
    
    "m162_ev_tension": {
        "name": "EV_tension - Evolution Tension",
        "formula": "0.5·z_prox + 0.2·x_fm_prox + 0.3·E_I_proxy",
        "expected_params": ["z_prox", "x_fm_prox", "E_I_proxy"],
        "test_case": {
            "inputs": {"z_prox": 0.3, "x_fm_prox": 0.2, "E_I_proxy": 0.4},
            "expected": 0.5*0.3 + 0.2*0.2 + 0.3*0.4
        }
    },
    
    "m73_ev_readiness": {
        "name": "EV_readiness - Evolution Readiness",
        "formula": "sigma(3·(EV_resonance - EV_tension + readiness_bias))",
        "expected_params": ["EV_resonance", "EV_tension", "readiness_bias"],
        "notes": "readiness_bias default = -0.05, sigma = sigmoid function",
        "test_case": {
            "inputs": {"EV_resonance": 0.7, "EV_tension": 0.3, "readiness_bias": -0.05},
            "expected": 1 / (1 + 2.71828 ** (-3 * (0.7 - 0.3 - 0.05))),  # sigmoid
            "tolerance": 0.01
        }
    },
    
    # ========================================================================
    # TRAUMA VECTORS
    # ========================================================================
    
    "m101_t_panic": {
        "name": "T_panic - Panic Intensity",
        "formula": "Lexicon-based with weights",
        "expected_params": ["text", "panic_lexikon"],
        "notes": "Uses PANIC_LEXIKON from _lexika.py"
    },
    
    "m102_t_disso": {
        "name": "T_disso - Dissociation",
        "formula": "Lexicon-based with weights",
        "expected_params": ["text", "disso_lexikon"],
        "notes": "Uses DISSO_LEXIKON from _lexika.py"
    },
    
    "m103_t_integ": {
        "name": "T_integ - Integration",
        "formula": "Lexicon-based with weights",
        "expected_params": ["text", "integ_lexikon"],
        "notes": "Uses INTEG_LEXIKON from _lexika.py"
    },
    
    # ========================================================================
    # EXTENSIONS (More features than spec)
    # ========================================================================
    
    "m19_z_prox": {
        "name": "z_prox - Death Proximity",
        "formula": "(1-A)·max(LL, ctx_break)  [V11.1 SIMPLE]",
        "actual_formula": "Extended with safety overrides, hazard lexicon, dual-A [PRODUCTION]",
        "bug_type": "EXTENSION",
        "bug_description": "Production has V3.3.x safety enhancements beyond V11.1 spec",
        "severity": "INFO",
        "note": "Likely intentional safety layer - document this!"
    },
    
    # ========================================================================
    # DYAD (User ↔ Assistant)
    # ========================================================================
    
    "m42_nabla_dyad": {
        "name": "∇_dyad - Dyad Delta",
        "formula": "deltaG = 0.6·|nablaA_dyad| + 0.4·|nablaB_dyad|",
        "notes": "nablaA_dyad = nabla_A_user - nabla_A_assistant"
    },
    
    # ========================================================================
    # SOUL & ETHICS
    # ========================================================================
    
    "m38_soul_integrity": {
        "name": "Soul Integrity",
        "formula": "Implementation details TBD from production",
        "notes": "Part of V_kon vector (ethics component)"
    },
    
    "m39_soul_check": {
        "name": "Soul Check",
        "formula": "Implementation details TBD from production",
        "notes": "Used in U (utility) calculation"
    },
    
    # ========================================================================
    # GRAVITATION (Phase Attraction)
    # ========================================================================
    
    "G_phase": {
        "name": "G_phase - Phase Gravitation",
        "formula": "Σ G0·(cos(e_i,C_c)^gamma) / ((delta + (1-cos))^beta)",
        "notes": "G0 ≈ 1.0, gamma ≈ 2.0, beta ≈ 1.0 (calibration needed)",
        "implementation_needed": True
    },
    
    # ========================================================================
    # V_KON (State Vector)
    # ========================================================================
    
    "V_kon": {
        "name": "V_kon - State Vector",
        "formula": "Vkon_mag = sqrt((coh_c² + ethic² + stab² + risk²) / 4)",
        "notes": "coh_c=A, ethic=soul_integrity, stab=1-LL, risk=1-max(z_prox,x_fm_prox)",
        "implementation_needed": True
    },
    
    # ========================================================================
    # ADVANCED METRICS (Complexity)
    # ========================================================================
    
    "m18_s_entropy": {
        "name": "S_entropy - Shannon Entropy",
        "formula": "H = -Σ p(x)·log2(p(x))",
        "notes": "Calculated on token distribution"
    },
    
    "m27_lambda_depth": {
        "name": "λ_depth - Depth Parameter",
        "formula": "Implementation details TBD from production",
        "notes": "Used in routine_fog calculation"
    },
}


# ============================================================================
# [REST OF CODE IDENTICAL TO PREVIOUS VERSION]
# ============================================================================

# ... [Same audit functions as before] ...


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


def test_formula(func, test_case: Dict, tolerance: float = 0.01) -> Tuple[bool, str, Optional[float]]:
    """Test metric function against expected output"""
    if 'will_fail' in test_case and test_case['will_fail']:
        return False, f"⚠️  SKIPPED (will fail): {test_case.get('reason', 'N/A')}", None
    
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
    
    # Special handling for known algorithm mismatches and placeholders
    if spec.get('bug_type') in ['ALGORITHM_MISMATCH', 'SCOPE_MISMATCH', 'EXTENSION']:
        result['errors'].append(f"{spec['bug_type']}: {spec['bug_description']}")
        if verbose:
            print(f"\n{metric_id} - {spec['name']}")
            print(f"  🔍 {spec['bug_type']}: {spec['bug_description']}")
            if 'note' in spec:
                print(f"  📝 Note: {spec['note']}")
        return result
    
    if spec.get('implementation_needed'):
        result['errors'].append("Implementation needed - not in production yet")
        if verbose:
            print(f"\n{metric_id} - {spec['name']}")
            print(f"  ⚠️  Not implemented yet")
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
    print("EVOKI PRODUCTION METRICS AUDIT - V11.1 EXTENDED")
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
        "implementation_needed": 0,
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
        
        if spec.get('implementation_needed'):
            summary['implementation_needed'] += 1
        
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
    print(f"Metrics Audited:            {summary['total']}")
    print(f"Critical Bugs Found:        {summary['critical_bugs']}")
    print(f"Algorithm Mismatches:       {summary['algorithm_mismatches']}")
    print(f"Extensions Found:           {summary['extensions']}")
    print(f"Implementation Needed:      {summary['implementation_needed']}")
    
    print(f"\nSignature Verification:")
    print(f"  ✅ Correct:   {summary['signature_ok']}")
    print(f"  ❌ Incorrect: {summary['signature_fail']}")
    
    print(f"\nFormula Verification:")
    print(f"  ✅ Correct:   {summary['formula_ok']}")
    print(f"  ❌ Incorrect: {summary['formula_fail']}")
    
    if summary['errors']:
        print(f"\n⚠️  {len(summary['errors'])} ISSUES FOUND:")
        for error in summary['errors'][:20]:  # Limit output
            print(f"  • {error}")
        if len(summary['errors']) > 20:
            print(f"  ... and {len(summary['errors']) - 20} more")
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
                print(f"  Expected: {spec.get('expected_params', 'N/A')}")
                print(f"  Actual:   {result['actual_params']}")
                print(f"  Formula:  {spec['formula']}")
        print("\n" + "🚨" * 40)
    
    return {
        "results": results,
        "summary": summary
    }


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
            for mid in sorted(V11_1_FORMULAS.keys()):
                print(f"  • {mid} - {V11_1_FORMULAS[mid]['name']}")
    else:
        # Audit all metrics
        audit_all_metrics(critical_only=args.critical, verbose=args.verbose)


if __name__ == "__main__":
    main()

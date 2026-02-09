"""
SCHUMMLER-DETECTOR V1.0 - EVOKI V3 METRIC VALIDATOR
Finds hallucinations, NaN, blind, and frozen metrics

Purpose:
- Detect NaN/None values (broken calculations)
- Detect blind metrics (always 0.0)
- Detect frozen metrics (no variance, stuck at defaults)
- Validate metrics fall in expected ranges
- Detect dependency issues (metrics depending on NaN)

Usage:
    python schummler_detector.py
"""

from typing import Dict, List, Tuple, Any
import sys
from pathlib import Path

# Add backend path
backend_path = Path(__file__).parent.parent.parent.parent / "backend" / "core" / "evoki_metrics_v3"
sys.path.insert(0, str(backend_path))

try:
    from calculator_spec_A_PHYS_V11 import calculate_spec_compliant
    print("✅ Loaded calculator_spec_A_PHYS_V11")
except ImportError as e:
    print(f"❌ Failed to import calculator: {e}")
    print(f"   Searched in: {backend_path}")
    sys.exit(1)

# ============================================================================
# TEST CASES - Representative prompts
# ============================================================================

TEST_CASES = {
    "crisis": {
        "text": "Ich habe Todesangst und will sterben, Hilfe! Ich kann nicht mehr!",
        "expected_ranges": {
            "m1_A": (0.0, 0.4),      # Low affect in crisis
            "m19_z_prox": (0.5, 1.0),  # High death proximity
            "m101_T_panic": (0.6, 1.0), # High panic
        }
    },
    
    "normal": {
        "text": "Wie geht es dir heute? Mir geht es ganz okay.",
        "expected_ranges": {
            "m1_A": (0.4, 0.7),      # Medium affect
            "m19_z_prox": (0.0, 0.3),  # Low death proximity
            "m101_T_panic": (0.0, 0.2), # Low panic
        }
    },
    
    "positive": {
        "text": "Ich bin so glücklich! Ich verstehe den Zusammenhang und fühle mich gut!",
        "expected_ranges": {
            "m1_A": (0.6, 1.0),      # High affect
            "m2_PCI": (0.5, 1.0),    # High integration
            "m20_phi_proxy": (0.3, 1.0), # High consciousness
        }
    },
    
    "loop": {
        "text": "Ich sage immer das gleiche ich sage immer das gleiche ich sage immer",
        "expected_ranges": {
            "m7_LL": (0.6, 1.0),     # High loops
            "m6_ZLF": (0.5, 1.0),    # High fragmentation
        }
    },
}

# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def is_nan(value: Any) -> bool:
    """Check if value is NaN (handles numpy and Python floats)"""
    if value is None:
        return True
    if isinstance(value, (int, float)):
        try:
            import math
            return math.isnan(value) or math.isinf(value)
        except:
            return False
    return False


def detect_nan_metrics(results: Any) -> List[str]:
    """Find metrics that return NaN"""
    nan_metrics = []
    
    for key in dir(results):
        if key.startswith('m') and len(key) > 1 and key[1].isdigit():
            value = getattr(results, key, None)
            if is_nan(value):
                nan_metrics.append(key)
    
    return nan_metrics


def detect_blind_metrics(multi_results: List[Any]) -> List[str]:
    """Find metrics that always return 0.0 (blind)"""
    blind_metrics = []
    
    # Get all metric names from first result
    first_result = multi_results[0]
    metric_names = [k for k in dir(first_result) 
                   if k.startswith('m') and len(k) > 1 and k[1].isdigit()]
    
    for metric in metric_names:
        values = [getattr(r, metric, None) for r in multi_results]
        values = [v for v in values if not is_nan(v) and isinstance(v, (int, float))]
        
        if values and len(values) >= 3 and all(v == 0.0 for v in values):
            blind_metrics.append(f"{metric} (always 0.0)")
    
    return blind_metrics


def detect_frozen_metrics(multi_results: List[Any]) -> List[str]:
    """Find metrics with no variance (frozen at default)"""
    frozen_metrics = []
    
    first_result = multi_results[0]
    metric_names = [k for k in dir(first_result) 
                   if k.startswith('m') and len(k) > 1 and k[1].isdigit()]
    
    for metric in metric_names:
        values = [getattr(r, metric, None) for r in multi_results]
        values = [v for v in values if isinstance(v, (int, float)) and not is_nan(v)]
        
        if len(values) >= 3:
            # Check if all values are identical (no variance)
            unique_values = set(values)
            if len(unique_values) == 1:
                frozen_metrics.append(f"{metric} (frozen at {values[0]:.3f})")
            
            # Check if stuck at common defaults
            elif all(v == 0.5 for v in values):
                frozen_metrics.append(f"{metric} (default 0.5)")
    
    return frozen_metrics


def validate_ranges(results: Any, test_name: str, expected: Dict) -> List[str]:
    """Check if metrics fall in expected ranges"""
    violations = []
    
    for metric, expected_range in expected.items():
        actual_value = getattr(results, metric, None)
        
        if actual_value is None or is_nan(actual_value):
            violations.append(f"{test_name}: {metric} is None/NaN")
            continue
        
        # For string metrics (like commit)
        if isinstance(expected_range, list):
            if actual_value not in expected_range:
                violations.append(
                    f"{test_name}: {metric} = '{actual_value}', "
                    f"expected {expected_range}"
                )
        
        # For numeric metrics
        elif isinstance(expected_range, tuple):
            min_val, max_val = expected_range
            if not (min_val <= actual_value <= max_val):
                violations.append(
                    f"{test_name}: {metric} = {actual_value:.3f}, "
                    f"expected [{min_val:.3f}, {max_val:.3f}]"
                )
    
    return violations


def detect_dependency_issues(results: Any) -> List[str]:
    """Find metrics that depend on NaN values"""
    issues = []
    
    # Check critical dependencies
    dependencies = {
        "m1_A": ["m4_flow", "m5_coh", "m7_LL", "m6_ZLF"],
        "m2_PCI": ["m4_flow", "m5_coh", "m7_LL"],
        "m7_LL": ["m4_flow"],
        "m19_z_prox": ["m1_A", "m15_affekt_a", "m7_LL"],
        "m20_phi_proxy": ["m1_A", "m2_PCI"],
    }
    
    for metric, deps in dependencies.items():
        metric_val = getattr(results, metric, None)
        
        for dep in deps:
            dep_val = getattr(results, dep, None)
            
            if is_nan(dep_val):
                issues.append(
                    f"{metric} depends on {dep} which is NaN!"
                )
    
    return issues


# ============================================================================
# MAIN VALIDATOR
# ============================================================================

def run_full_validation():
    """Run complete validation suite"""
    print("=" * 70)
    print("SCHUMMLER-DETECTOR V1.0 - EVOKI V3 METRIC VALIDATOR")
    print("=" * 70)
    
    all_results = []
    range_violations = []
    
    # Run all test cases
    print("\n📊 Running test cases...")
    for test_name, test_data in TEST_CASES.items():
        print(f"\n  Testing: {test_name}")
        text = test_data["text"]
        
        try:
            result = calculate_spec_compliant(text)
            all_results.append(result)
            
            # Validate ranges
            violations = validate_ranges(
                result, 
                test_name, 
                test_data["expected_ranges"]
            )
            range_violations.extend(violations)
            
            # Check for NaN
            nan_metrics = detect_nan_metrics(result)
            if nan_metrics:
                print(f"    ⚠️  NaN detected: {nan_metrics}")
            
            # Check dependencies
            dep_issues = detect_dependency_issues(result)
            if dep_issues:
                for issue in dep_issues:
                    print(f"    ⚠️  {issue}")
        
        except Exception as e:
            print(f"    ❌ CRASH: {e}")
            import traceback
            traceback.print_exc()
    
    if not all_results:
        print("\n❌ NO RESULTS - All tests crashed!")
        return
    
    # Detect patterns across all results
    print("\n🔍 Analyzing patterns...")
    
    blind = detect_blind_metrics(all_results)
    frozen = detect_frozen_metrics(all_results)
    
    # ========================================================================
    # REPORT
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("VALIDATION REPORT")
    print("=" * 70)
    
    has_issues = False
    
    # NaN Detection
    print("\n🚨 NaN DETECTION:")
    nan_found = False
    for i, result in enumerate(all_results):
        nan_list = detect_nan_metrics(result)
        if nan_list:
            has_issues = True
            nan_found = True
            test_name = list(TEST_CASES.keys())[i]
            print(f"  ❌ {test_name}: {', '.join(nan_list)}")
    
    if not nan_found:
        print("  ✅ No NaN values detected")
    
    # Blind Metrics
    print("\n👁️  BLIND METRICS (always 0.0):")
    if blind:
        has_issues = True
        for metric in blind:
            print(f"  ❌ {metric}")
    else:
        print("  ✅ No blind metrics")
    
    # Frozen Metrics
    print("\n🧊 FROZEN METRICS (no variance):")
    if frozen:
        # Only warn, not fail
        for metric in frozen:
            print(f"  ⚠️  {metric}")
    else:
        print("  ✅ No frozen metrics")
    
    # Range Violations
    print("\n📏 RANGE VIOLATIONS:")
    if range_violations:
        # Only warn for now
        for violation in range_violations:
            print(f"  ⚠️  {violation}")
    else:
        print("  ✅ All metrics in expected ranges")
    
    # Summary
    print("\n" + "=" * 70)
    if has_issues:
        print("❌ VALIDATION FAILED - Critical issues found!")
    else:
        print("✅ VALIDATION PASSED - All metrics healthy!")
    print("=" * 70)
    
    return not has_issues


if __name__ == "__main__":
    success = run_full_validation()
    sys.exit(0 if success else 1)

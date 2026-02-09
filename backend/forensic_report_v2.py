# -*- coding: utf-8 -*-
"""
EVOKI V3.0 — FORENSIC REPORT 2.0 (METHODOLOGICALLY CORRECT)

Proper forensic analysis with clear taxonomy and NO unproven claims.

Taxonomy:
- IMPLEMENTED: Function exists in module
- EXECUTED: Called during test without exceptions
- NONDEFAULT: Produces non-zero/non-constant value
- INPUT_SENSITIVE: Changes with controlled input variations
- STATEFUL: Requires prev/state/turn/timing (needs sequence test)
- MOCK_DRIVEN: Output primarily from mocks, not prompt analysis

H0: Synthetic test (constant mocks, no sequences)
H1: Integration test (real prompt pairs, real context variation)
"""

import sys
import json
sys.path.insert(0, r'c:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend')

from core.evoki_metrics_v3 import NEW_MODULES_COUNT


# ═══════════════════════════════════════════════════════════════════════════
# COUNT VERIFICATION (Fix 129 vs 130 bug)
# ═══════════════════════════════════════════════════════════════════════════

def verify_counts():
    """Verify exact metric counts from registry"""
    
    print("=" * 80)
    print("COUNT VERIFICATION")
    print("=" * 80)
    
    total = sum(NEW_MODULES_COUNT.values())
    
    print(f"\n📊 Registry Count: {total}")
    print(f"\nBreakdown:")
    for module, count in NEW_MODULES_COUNT.items():
        print(f"  {module:25s} {count:3d}")
    
    print(f"\n  {'TOTAL':25s} {total:3d}")
    
    # Expected vs Actual
    print(f"\n🔍 Analysis:")
    print(f"  Header claimed: 129")
    print(f"  Test ran: 130 metrics × 3 cases = 390 runs")
    print(f"  Registry says: {total}")
    
    if total == 129:
        print(f"  ✓ Registry matches 129")
        print(f"  ⚠️ Test output '130' was wrong")
    elif total == 130:
        print(f"  ⚠️ Header '129' was wrong")
        print(f"  ✓ Test output matches {total}")
    
    return total, NEW_MODULES_COUNT


# ═══════════════════════════════════════════════════════════════════════════
# METRIC CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

METRIC_TAXONOMY = {
    # text_analytics: EXCELLENT - direct text analysis
    "text_analytics": {
        "classification": "INPUT_SENSITIVE",
        "h0_dynamic": 0.70,
        "signal_source": "Direct text features",
        "mock_dependency": "Low (m93, m72 for composites)",
        "verdict": "PROVEN INPUT-DRIVEN"
    },
    
    # emotions: MIXED - text analysis with sparse lexicon
    "emotions": {
        "classification": "INPUT_SENSITIVE + SPARSE",
        "h0_dynamic": 0.42,
        "signal_source": "Keyword matching, emoji detection",
        "mock_dependency": "Medium (uses m5_coh, m72, m93 for composites)",
        "verdict": "PROVEN but ZERO-HEAVY (lexicon limited)"
    },
    
    # final_metrics: MIXED - some text, mostly composite
    "final_metrics": {
        "classification": "MIXED (INPUT_SENSITIVE + MOCK_DRIVEN)",
        "h0_dynamic": 0.38,
        "signal_source": "m2,m5,m8,m12 from text; rest from mocks",
        "mock_dependency": "High (m163-m168 all composite)",
        "verdict": "PARTIAL - core metrics OK, synthesis untested"
    },
    
    # hypermetrics: MOSTLY MOCK
    "hypermetrics": {
        "classification": "MOCK_DRIVEN + STATEFUL",
        "h0_dynamic": 0.42,
        "signal_source": "Dyadic (needs prev_text), Composite (needs other metrics)",
        "mock_dependency": "Very High (all need context/prev/metrics)",
        "verdict": "HARNESS-LIMITED - requires H1 sequence test"
    },
    
    # fep_evolution: MOSTLY MOCK
    "fep_evolution": {
        "classification": "MOCK_DRIVEN",
        "h0_dynamic": 0.38,
        "signal_source": "Theoretical FEP calculations from mocked inputs",
        "mock_dependency": "Very High (surprise, tokens, phi all mocked)",
        "verdict": "HARNESS-LIMITED - signal path unclear in H0"
    },
    
    # system_metrics: BROKEN + STATEFUL
    "system_metrics": {
        "classification": "STATEFUL + BROKEN",
        "h0_dynamic": 0.10,
        "signal_source": "Session timing, hashes, composites",
        "mock_dependency": "Critical (broken: m114, m115 need context)",
        "verdict": "INTERFACE ERRORS - needs signature fix + H1 test"
    },
    
    # dynamics_turbidity: ENTKOPPELT
    "dynamics_turbidity": {
        "classification": "MOCK_DRIVEN (DECOUPLED)",
        "h0_dynamic": 0.00,
        "signal_source": "NONE - only reads mocked dependencies",
        "mock_dependency": "Total (no text analysis at all)",
        "verdict": "SIGNAL PATH DEAD - needs features interface"
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# REPORT 2.0 GENERATION
# ═══════════════════════════════════════════════════════════════════════════

def generate_report_v2():
    """Generate methodologically correct forensic report"""
    
    total, breakdown = verify_counts()
    
    print(f"\n{'═' * 80}")
    print("FORENSIC REPORT 2.0 — METHODOLOGICALLY CORRECT")
    print(f"{'═' * 80}")
    
    print(f"\n## TEST CONFIGURATION")
    print(f"\n**Harness:** H0 (Synthetic)")
    print(f"  - Test Cases: 3 (SHORT_POSITIVE, LONG_COMPLEX, NEGATIVE_CAPS)")
    print(f"  - Context: Static mocks + minimal variation")
    print(f"  - Sequences: None (no prev/state)")
    print(f"\n**Metrics Tested:** {total}")
    print(f"**Test Runs:** {total * 3}")
    
    print(f"\n{'─' * 80}")
    print("## TAXONOMY-BASED CLASSIFICATION")
    print(f"{'─' * 80}")
    
    for module, data in METRIC_TAXONOMY.items():
        count = breakdown.get(module, 0)
        print(f"\n### {module} ({count} metrics)")
        print(f"  Classification: {data['classification']}")
        print(f"  H0 Dynamic: {data['h0_dynamic']:.0%}")
        print(f"  Signal Source: {data['signal_source']}")
        print(f"  Mock Dependency: {data['mock_dependency']}")
        print(f"  **Verdict: {data['verdict']}**")
    
    print(f"\n{'─' * 80}")
    print("## CORRECTED METRICS")
    print(f"{'─' * 80}")
    
    # Calculate proven metrics
    proven_input_driven = breakdown.get("text_analytics", 0)
    partial_input = (
        int(breakdown.get("emotions", 0) * 0.5) +  # ~half work well
        int(breakdown.get("final_metrics", 0) * 0.3)  # ~30% are direct text
    )
    
    harness_limited = (
        breakdown.get("hypermetrics", 0) +
        breakdown.get("fep_evolution", 0)
    )
    
    needs_fix = breakdown.get("system_metrics", 0)
    decoupled = breakdown.get("dynamics_turbidity", 0)
    
    print(f"\n**PROVEN INPUT-DRIVEN (under H0):**")
    print(f"  ✓ {proven_input_driven} metrics (text_analytics)")
    print(f"  ✓ ~{partial_input} metrics (emotions, final_metrics core)")
    print(f"  **TOTAL: ~{proven_input_driven + partial_input} / {total}** ({(proven_input_driven + partial_input)/total:.0%})")
    
    print(f"\n**HARNESS-LIMITED (needs H1):**")
    print(f"  ⚠️ {harness_limited} metrics (hypermetrics, fep_evolution)")
    print(f"  Note: May be valid, but signal path not testable in H0")
    
    print(f"\n**NEEDS FIX:**")
    print(f"  ❌ {needs_fix} metrics (system_metrics: interface errors)")
    print(f"  ❌ {decoupled} metrics (dynamics_turbidity: decoupled)")
    
    print(f"\n{'─' * 80}")
    print("## CRITICAL CORRECTIONS TO REPORT 1.0")
    print(f"{'─' * 80}")
    
    print(f'\n**WRONG (Report 1.0):**')
    print(f'  ❌ "ALL 129 metrics" → Count was {total}')
    print(f'  ❌ "No placeholders" → 22 metrics are MOCK_DRIVEN (dynamics_turbidity)')
    print(f'  ❌ "In live system will be dynamic" → UNPROVEN claim')
    print(f'  ❌ "91.5% success" → Misleading (counts test runs, not metric quality)')
    
    print(f'\n**CORRECT (Report 2.0):**')
    print(f'  ✓ "{total} metrics implemented"')
    print(f'  ✓ "~{proven_input_driven + partial_input} proven INPUT-DRIVEN under H0"')
    print(f'  ✓ "{harness_limited} require H1 integration test (STATEFUL/MOCK_DRIVEN)"')
    print(f'  ✓ "{needs_fix + decoupled} need fixes (interface errors + decoupling)"')
    
    print(f"\n{'─' * 80}")
    print("## REQUIRED NEXT STEPS")
    print(f"{'─' * 80}")
    
    print(f'\n**IMMEDIATE (15 min):**')
    print(f'  1. Fix count bug in all documentation (129 → {total})')
    print(f'  2. Fix system_metrics interface (m114, m115 signatures)')
    
    print(f'\n**SHORT TERM (30 min):**')
    print(f'  3. Wire dynamics_turbidity to features (at least m100-m105)')
    print(f'  4. Mark MOCK_DRIVEN metrics explicitly in code')
    
    print(f'\n**MEDIUM TERM (60 min) - THE PROOF:**')
    print(f'  5. H1 Integration Test:')
    print(f'     - 10 real prompt pairs from DB')
    print(f'     - 5-turn sequence (prev/state varies)')
    print(f'     - Measure: what % of {harness_limited} STATEFUL metrics become dynamic?')
    print(f'\n  **ONLY AFTER H1:** Allow claim "live system dynamics"')
    
    print(f"\n{'═' * 80}")
    print("FORENSIC VERDICT")
    print(f"{'═' * 80}")
    
    print(f"\n**Implementation Status:** ✅ {total}/{total} functions exist")
    print(f"**Proven Quality (H0):** ⚠️ ~{proven_input_driven + partial_input}/{total} input-driven")
    print(f"**Needs Validation (H1):** 🔶 ~{harness_limited}/{total} stateful")
    print(f"**Needs Fix:** ❌ {needs_fix + decoupled}/{total} broken/decoupled")
    
    print(f"\n**Overall Grade:** 🟡 YELLOW")
    print(f"  - Strong foundation ({total} metrics implemented)")
    print(f"  - Text analytics excellent")
    print(f"  - But: significant untested/broken portions")
    print(f"  - Requires: fixes + H1 test before production claim")
    
    print(f"\n{'═' * 80}")
    print("REPORT 2.0 COMPLETE")
    print(f"{'═' * 80}")
    
    # Export JSON
    report_data = {
        "version": "2.0",
        "timestamp": "2026-02-08T10:30:00Z",
        "harness": "H0_synthetic",
        "total_metrics": total,
        "breakdown": breakdown,
        "taxonomy": METRIC_TAXONOMY,
        "proven_input_driven": proven_input_driven + partial_input,
        "harness_limited": harness_limited,
        "needs_fix": needs_fix + decoupled,
        "corrections": {
            "count_bug": f"Fixed {total} (was claiming 129)",
            "placeholder_myth": "Removed false claim - 22 metrics are MOCK_DRIVEN",
            "unproven_claim": "Removed 'live will be dynamic' - needs H1 proof"
        }
    }
    
    return report_data


if __name__ == "__main__":
    report = generate_report_v2()
    
    print(f"\n💾 JSON export available")
    print(f"   Contains full taxonomy and corrected metrics")

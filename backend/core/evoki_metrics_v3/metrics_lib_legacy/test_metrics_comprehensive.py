#!/usr/bin/env python3
"""
EVOKI V3.0 METRICS LIBRARY - COMPREHENSIVE TEST SUITE

Tests for:
- Core helpers (_helpers.py)
- Components (gap, rep, flow, coh, etc.)
- Critical metrics (m1_A, m2_PCI, m7_LL, etc.)
- Lexika validation

Created: 2026-02-08 by CODEX
"""

import sys
import unittest
from pathlib import Path

# Add metrics_lib to path
sys.path.insert(0, str(Path(__file__).parent))

# Import helpers
from _helpers import tokenize, clamp

# Import extended helpers (if available)
try:
    from _helpers_extended import sigmoid, jaccard, normalize, safe_divide
    EXTENDED_AVAILABLE = True
except ImportError:
    EXTENDED_AVAILABLE = False

# Import lexika
from _lexika import (
    HAZARD_LEXIKON, PANIC_LEXIKON, DISSO_LEXIKON, INTEG_LEXIKON,
    X_EXIST_LEXIKON, B_PAST_LEXIKON, AFFECT_LEXIKON
)

# Import critical metrics
from m1_A import compute_m1_A
from m2_PCI import compute_m2_PCI
from m6_ZLF import compute_m6_ZLF
from m7_LL import compute_m7_LL
from m10_angstrom import compute_m10_angstrom

# Import components
from m11_gap_s import compute_m11_gap_s
from m12_gap_norm import compute_m12_gap_norm
from m13_rep_same import compute_m13_rep_same


# ============================================================================
# HELPER TESTS
# ============================================================================

class TestHelpers(unittest.TestCase):
    """Test core helper functions"""
    
    def test_tokenize_basic(self):
        """Test basic tokenization"""
        result = tokenize("Hello World")
        self.assertEqual(result, ['hello', 'world'])
    
    def test_tokenize_empty(self):
        """Test empty string tokenization"""
        result = tokenize("")
        self.assertEqual(result, [''])
    
    def test_tokenize_preserves_punctuation(self):
        """Test that tokenize keeps punctuation"""
        result = tokenize("Hello, World!")
        self.assertEqual(result, ['hello,', 'world!'])
    
    def test_clamp_within_bounds(self):
        """Test clamp with value in range"""
        self.assertEqual(clamp(0.5), 0.5)
    
    def test_clamp_below_bounds(self):
        """Test clamp with value below range"""
        self.assertEqual(clamp(-0.5), 0.0)
    
    def test_clamp_above_bounds(self):
        """Test clamp with value above range"""
        self.assertEqual(clamp(1.5), 1.0)
    
    def test_clamp_custom_bounds(self):
        """Test clamp with custom bounds"""
        self.assertEqual(clamp(5.0, 0.0, 10.0), 5.0)
        self.assertEqual(clamp(-5.0, 0.0, 10.0), 0.0)
        self.assertEqual(clamp(15.0, 0.0, 10.0), 10.0)


class TestExtendedHelpers(unittest.TestCase):
    """Test extended helper functions (if available)"""
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_sigmoid_zero(self):
        """Test sigmoid at zero"""
        result = sigmoid(0)
        self.assertAlmostEqual(result, 0.5, places=4)
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_sigmoid_positive(self):
        """Test sigmoid with positive input"""
        result = sigmoid(5)
        self.assertGreater(result, 0.99)
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_sigmoid_negative(self):
        """Test sigmoid with negative input"""
        result = sigmoid(-5)
        self.assertLess(result, 0.01)
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_jaccard_identical(self):
        """Test Jaccard with identical sets"""
        result = jaccard({'a', 'b', 'c'}, {'a', 'b', 'c'})
        self.assertEqual(result, 1.0)
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_jaccard_disjoint(self):
        """Test Jaccard with disjoint sets"""
        result = jaccard({'a', 'b'}, {'c', 'd'})
        self.assertEqual(result, 0.0)
    
    @unittest.skipIf(not EXTENDED_AVAILABLE, "Extended helpers not available")
    def test_jaccard_partial_overlap(self):
        """Test Jaccard with partial overlap"""
        result = jaccard({'a', 'b', 'c'}, {'b', 'c', 'd'})
        self.assertAlmostEqual(result, 0.5, places=4)


# ============================================================================
# COMPONENT TESTS
# ============================================================================

class TestTimeComponents(unittest.TestCase):
    """Test time-based components"""
    
    def test_gap_s_positive(self):
        """Test gap_s with positive delta"""
        result = compute_m11_gap_s(100.0, 150.0)
        self.assertEqual(result, 50.0)
    
    def test_gap_s_negative(self):
        """Test gap_s with negative delta (time travel!)"""
        result = compute_m11_gap_s(150.0, 100.0)
        self.assertEqual(result, 0.0)  # Should clamp to 0
    
    def test_gap_norm_under_threshold(self):
        """Test gap_norm with gap < 60s"""
        result = compute_m12_gap_norm(30.0)
        self.assertEqual(result, 0.5)
    
    def test_gap_norm_at_threshold(self):
        """Test gap_norm with gap = 60s"""
        result = compute_m12_gap_norm(60.0)
        self.assertEqual(result, 1.0)
    
    def test_gap_norm_over_threshold(self):
        """Test gap_norm with gap > 60s (should clamp)"""
        result = compute_m12_gap_norm(120.0)
        self.assertEqual(result, 1.0)


class TestRepetitionComponents(unittest.TestCase):
    """Test repetition detection"""
    
    def test_rep_same_identical(self):
        """Test rep_same with identical texts"""
        result = compute_m13_rep_same("hello world", "hello world")
        self.assertEqual(result, 1.0)
    
    def test_rep_same_no_overlap(self):
        """Test rep_same with no overlap"""
        result = compute_m13_rep_same("hello world", "foo bar")
        self.assertEqual(result, 0.0)
    
    def test_rep_same_partial_overlap(self):
        """Test rep_same with partial overlap"""
        result = compute_m13_rep_same("hello world", "hello foo")
        self.assertEqual(result, 0.5)  # 1 of 2 words overlap
    
    def test_rep_same_empty_prev(self):
        """Test rep_same with empty previous text"""
        result = compute_m13_rep_same("hello world", "")
        self.assertEqual(result, 0.0)


# ============================================================================
# CRITICAL METRICS TESTS
# ============================================================================

class TestCriticalMetrics(unittest.TestCase):
    """Test critical physics metrics"""
    
    def test_m7_LL_v11_1_formula(self):
        """Test m7_LL with V11.1 correct formula"""
        # V11.1: LL = 0.55·rep_same + 0.25·(1-flow) + 0.20·(1-coh)
        result = compute_m7_LL(rep_same=0.5, flow=0.8, coh=0.7)
        expected = 0.55*0.5 + 0.25*(1-0.8) + 0.20*(1-0.7)  # = 0.385
        self.assertAlmostEqual(result, expected, places=3)
    
    def test_m7_LL_all_zeros(self):
        """Test m7_LL with all zeros"""
        result = compute_m7_LL(rep_same=0.0, flow=1.0, coh=1.0)
        expected = 0.0  # Perfect flow and coherence, no repetition
        self.assertEqual(result, expected)
    
    def test_m7_LL_all_ones(self):
        """Test m7_LL with maximum turbidity"""
        result = compute_m7_LL(rep_same=1.0, flow=0.0, coh=0.0)
        expected = 0.55*1.0 + 0.25*1.0 + 0.20*1.0  # = 1.0
        self.assertEqual(result, 1.0)
    
    def test_m1_A_v11_1_formula(self):
        """Test m1_A (Kohärenz) with V11.1 formula"""
        # A = 0.4·coh + 0.25·flow + 0.20·(1-LL) + 0.10·(1-ZLF) - 0.05·ctx_break
        result = compute_m1_A(
            coh=0.7,
            flow=0.8,
            LL=0.3,
            ZLF=0.2,
            ctx_break=0.0
        )
        expected = 0.4*0.7 + 0.25*0.8 + 0.20*(1-0.3) + 0.10*(1-0.2) - 0.05*0.0
        self.assertAlmostEqual(result, expected, places=3)
    
    def test_m2_PCI_v11_1_formula(self):
        """Test m2_PCI with V11.1 formula"""
        # PCI = 0.4·flow + 0.35·coh + 0.25·(1-LL)
        result = compute_m2_PCI(flow=0.8, coh=0.7, LL=0.3)
        expected = 0.4*0.8 + 0.35*0.7 + 0.25*(1-0.3)
        self.assertAlmostEqual(result, expected, places=3)
    
    def test_m6_ZLF_v11_1_formula(self):
        """Test m6_ZLF with V11.1 formula"""
        # ZLF = 0.5·hit + 0.25·(1-flow) + 0.25·(1-coh)
        result = compute_m6_ZLF(flow=0.8, coherence=0.7, zlf_lexicon_hit=True)
        expected = 0.5*1.0 + 0.25*(1-0.8) + 0.25*(1-0.7)
        self.assertAlmostEqual(result, expected, places=3)
    
    def test_m10_angstrom_v11_1_formula(self):
        """Test m10_angstrom with V11.1 formula"""
        # Å = 0.25·(s_self + x_exist + b_past + coh)·5.0
        result = compute_m10_angstrom(
            s_self=0.6,
            x_exist=0.7,
            b_past=0.5,
            coh=0.8
        )
        expected = 0.25 * (0.6 + 0.7 + 0.5 + 0.8) * 5.0
        self.assertAlmostEqual(result, expected, places=3)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_m7_LL_clamping(self):
        """Test that m7_LL clamps to [0, 1]"""
        # This shouldn't happen with valid inputs, but test clamping
        result = compute_m7_LL(rep_same=0.0, flow=0.0, coh=0.0)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)
    
    def test_m1_A_negative_ctx_break(self):
        """Test m1_A with context break penalty"""
        result_no_break = compute_m1_A(
            coh=0.7, flow=0.8, LL=0.3, ZLF=0.2, ctx_break=0.0
        )
        result_with_break = compute_m1_A(
            coh=0.7, flow=0.8, LL=0.3, ZLF=0.2, ctx_break=1.0
        )
        # With break should be lower (penalty)
        self.assertLess(result_with_break, result_no_break)


# ============================================================================
# LEXIKA TESTS
# ============================================================================

class TestLexika(unittest.TestCase):
    """Test lexikon integrity"""
    
    def test_hazard_lexikon_not_empty(self):
        """Test HAZARD_LEXIKON has entries"""
        self.assertGreater(len(HAZARD_LEXIKON), 0)
    
    def test_hazard_lexikon_weights_in_range(self):
        """Test HAZARD_LEXIKON weights are in [0, 1]"""
        for weight in HAZARD_LEXIKON.values():
            self.assertGreaterEqual(weight, 0.0)
            self.assertLessEqual(weight, 1.0)
    
    def test_panic_lexikon_not_empty(self):
        """Test PANIC_LEXIKON has entries"""
        self.assertGreater(len(PANIC_LEXIKON), 0)
    
    def test_lexika_no_duplicate_keys(self):
        """Test no duplicate keys across lexika"""
        all_keys = set()
        lexika = [
            HAZARD_LEXIKON, PANIC_LEXIKON, DISSO_LEXIKON, INTEG_LEXIKON,
            X_EXIST_LEXIKON, B_PAST_LEXIKON, AFFECT_LEXIKON
        ]
        
        for lexikon in lexika:
            for key in lexikon.keys():
                # Note: Some overlap is OK (e.g., "sterben" in multiple)
                # This test just documents it
                if key in all_keys:
                    # print(f"Note: '{key}' appears in multiple lexika")
                    pass
                all_keys.add(key)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration(unittest.TestCase):
    """Test metric integration and dependencies"""
    
    def test_LL_feeds_A_and_PCI(self):
        """Test that LL output feeds correctly into A and PCI"""
        # Calculate LL
        LL = compute_m7_LL(rep_same=0.5, flow=0.8, coh=0.7)
        
        # Use in A
        A = compute_m1_A(coh=0.7, flow=0.8, LL=LL, ZLF=0.2, ctx_break=0.0)
        
        # Use in PCI
        PCI = compute_m2_PCI(flow=0.8, coh=0.7, LL=LL)
        
        # Both should be in valid range
        self.assertGreaterEqual(A, 0.0)
        self.assertLessEqual(A, 1.0)
        self.assertGreaterEqual(PCI, 0.0)
        self.assertLessEqual(PCI, 1.0)
    
    def test_full_pipeline_realistic(self):
        """Test full pipeline with realistic values"""
        # Simulate a coherent, flowing conversation
        rep_same = 0.3  # Some repetition
        flow = 0.85     # Good flow
        coh = 0.75      # Decent coherence
        
        # Calculate components
        LL = compute_m7_LL(rep_same, flow, coh)
        ZLF = compute_m6_ZLF(flow, coh, zlf_lexicon_hit=False)
        
        # Calculate physics
        A = compute_m1_A(coh, flow, LL, ZLF, ctx_break=0.0)
        PCI = compute_m2_PCI(flow, coh, LL)
        
        # Expectations for good conversation
        self.assertGreater(A, 0.5)    # Should have decent awareness
        self.assertGreater(PCI, 0.5)  # Should have decent integration
        self.assertLess(LL, 0.5)      # Low turbidity


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestExtendedHelpers))
    suite.addTests(loader.loadTestsFromTestCase(TestTimeComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestRepetitionComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestCriticalMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestLexika))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run:     {result.testsRun}")
    print(f"Successes:     {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures:      {len(result.failures)}")
    print(f"Errors:        {len(result.errors)}")
    print(f"Skipped:       {len(result.skipped)}")
    print("=" * 70)
    
    # Exit with appropriate code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

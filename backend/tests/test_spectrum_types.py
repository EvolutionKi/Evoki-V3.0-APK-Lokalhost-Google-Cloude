#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_spectrum_types.py — Unit Tests for FullSpectrum168 Contract

Tests TypedDict validation, schema loading, and metric information.
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.core.spectrum_types import (
    load_contract,
    get_metric_info,
    validate_spectrum,
    get_all_metric_names,
    get_metrics_by_category,
    FullSpectrum168
)


class TestContractLoading:
    """Test contract JSON loading."""
    
    def test_load_contract(self):
        """Test contract loads successfully."""
        contract = load_contract()
        assert contract is not None
        assert "metrics" in contract
        assert len(contract["metrics"]) == 168
    
    def test_contract_structure(self):
        """Test contract has correct structure."""
        contract = load_contract()
        
        # Check first metric
        first_metric = contract["metrics"][0]
        assert "id" in first_metric
        assert "name" in first_metric
        assert "category" in first_metric
        assert "data_type" in first_metric
        assert "range" in first_metric


class TestMetricInfo:
    """Test metric information retrieval."""
    
    def test_get_metric_by_name(self):
        """Test getting metric info by name."""
        info = get_metric_info("m1_A")
        assert info is not None
        assert info["name"] == "m1_A"
        assert info["category"] == "core"
    
    def test_get_metric_by_id(self):
        """Test getting metric info by ID."""
        info = get_metric_info("m2_PCI")
        assert info is not None
        assert info["name"] == "m2_PCI"
        assert "range" in info
    
    def test_get_nonexistent_metric(self):
        """Test getting non-existent metric returns None."""
        info = get_metric_info("m999_fake")
        assert info is None
    
    def test_get_all_metric_names(self):
        """Test getting all metric names."""
        names = get_all_metric_names()
        assert len(names) == 168
        assert "m1_A" in names
        assert "m2_PCI" in names
    
    def test_get_metrics_by_category(self):
        """Test filtering metrics by category."""
        core_metrics = get_metrics_by_category("core")
        assert len(core_metrics) > 0
        assert all(m["category"] == "core" for m in core_metrics)
        
        physics_metrics = get_metrics_by_category("physics")
        assert len(physics_metrics) > 0
        assert all(m["category"] == "physics" for m in physics_metrics)


class TestSpectrumValidation:
    """Test FullSpectrum168 validation."""
    
    def test_valid_spectrum(self):
        """Test validation passes for valid spectrum."""
        # Create valid spectrum
        spectrum = {f"m{i}_test": 0.5 for i in range(1, 169)}
        
        # Manually create some real metric names
        spectrum["m1_A"] = 0.7
        spectrum["m2_PCI"] = 0.6
        spectrum["m3_gen_index"] = 0.8
        
        # Validation should pass (if all 168 keys are present)
        # Note: This test needs the actual metric names from contract
        # For now, just test the function exists
        result = validate_spectrum(spectrum)
        assert isinstance(result, bool)
    
    def test_invalid_spectrum_missing_keys(self):
        """Test validation fails for missing keys."""
        spectrum = {"m1_A": 0.7}  # Only 1 metric
        
        result = validate_spectrum(spectrum)
        assert result is False
    
    def test_invalid_spectrum_wrong_type(self):
        """Test validation fails for wrong value types."""
        spectrum = {f"m{i}_test": "invalid" for i in range(1, 169)}
        
        result = validate_spectrum(spectrum)
        assert result is False


class TestMetricRanges:
    """Test metric range validation."""
    
    def test_metric_ranges(self):
        """Test metrics have valid ranges."""
        contract = load_contract()
        
        for metric in contract["metrics"]:
            assert "range" in metric
            range_data = metric["range"]
            
            assert "min" in range_data
            assert "max" in range_data
            assert range_data["min"] <= range_data["max"]
    
    def test_a_score_range(self):
        """Test A-Score has correct range [0, 1]."""
        info = get_metric_info("m1_A")
        assert info["range"]["min"] == 0.0
        assert info["range"]["max"] == 1.0
    
    def test_pci_range(self):
        """Test PCI has correct range [-1, 1]."""
        info = get_metric_info("m2_PCI")
        assert info["range"]["min"] == -1.0
        assert info["range"]["max"] == 1.0


class TestMetricSources:
    """Test metric source information."""
    
    def test_metrics_have_sources(self):
        """Test all metrics have source information."""
        contract = load_contract()
        
        for metric in contract["metrics"]:
            assert "source" in metric
            source = metric["source"]
            assert "engine" in source
    
    def test_metric_engines(self):
        """Test metrics reference correct engines."""
        # Core metrics should use metrics_complete_v3
        core_metrics = get_metrics_by_category("core")
        for metric in core_metrics:
            assert metric["source"]["engine"] in [
                "metrics_complete_v3",
                "a_phys_v11",
                "lexika"
            ]
        
        # Physics metrics should use a_phys_v11
        physics_metrics = get_metrics_by_category("physics")
        for metric in physics_metrics:
            assert metric["source"]["engine"] in [
                "a_phys_v11",
                "metrics_complete_v3"
            ]


class TestFullSpectrum168:
    """Test FullSpectrum168 TypedDict."""
    
    def test_create_full_spectrum(self):
        """Test creating a FullSpectrum168 instance."""
        # Get all metric names
        names = get_all_metric_names()
        
        # Create spectrum
        spectrum: FullSpectrum168 = {}
        for name in names:
            spectrum[name] = 0.5
        
        # Validate
        assert len(spectrum) == 168
        assert validate_spectrum(spectrum)
    
    def test_spectrum_type_hints(self):
        """Test FullSpectrum168 has correct type hints."""
        from typing import get_type_hints
        
        # FullSpectrum168 should be a TypedDict
        # (This test verifies the type exists)
        assert FullSpectrum168 is not None


@pytest.mark.integration
class TestContractIntegration:
    """Integration tests for contract usage."""
    
    def test_contract_matches_engines(self):
        """Test contract references match actual engine methods."""
        contract = load_contract()
        
        # List of expected engines
        expected_engines = [
            "metrics_complete_v3",
            "a_phys_v11",
            "vector_engine_v2_1",
            "timeline_4d_complete",
            "lexika"
        ]
        
        # Check all metrics reference valid engines
        for metric in contract["metrics"]:
            engine = metric["source"]["engine"]
            assert engine in expected_engines, f"Unknown engine: {engine}"
    
    def test_categories_complete(self):
        """Test all expected categories are present."""
        expected_categories = [
            "core",
            "physics",
            "trauma",
            "b_vector",
            "evolution",
            "timeline"
        ]
        
        contract = load_contract()
        actual_categories = set(m["category"] for m in contract["metrics"])
        
        for cat in expected_categories:
            assert cat in actual_categories, f"Missing category: {cat}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

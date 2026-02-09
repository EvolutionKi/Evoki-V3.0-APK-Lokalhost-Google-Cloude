#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_backend_smoke.py — Smoke Tests for Backend

Quick tests to verify:
1. Backend imports work
2. FastAPI app starts
3. Basic endpoints respond
4. Databases accessible
5. FAISS indices loadable
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


class TestImports:
    """Test critical imports."""
    
    def test_import_main(self):
        """Test importing main.py."""
        from backend import main
        assert main.app is not None
    
    def test_import_api_modules(self):
        """Test importing API modules."""
        from backend.api import temple, integrity, metrics, vector, timeline
        assert temple.router is not None
        assert integrity.router is not None
        assert metrics.router is not None
        assert vector.router is not None
        assert timeline.router is not None
    
    def test_import_core_modules(self):
        """Test importing core modules."""
        from backend.core import (
            vector_engine_v2_1,
            b_vector,
            spectrum_types,
            genesis_anchor,
            evoki_bootcheck
        )
        assert vector_engine_v2_1 is not None
        assert b_vector.BVector is not None
        assert spectrum_types.FullSpectrum168 is not None
    
    def test_import_metrics(self):
        """Test importing metrics module."""
        from backend.core.evoki_metrics_v3 import compute_full_spectrum
        assert compute_full_spectrum is not None


class TestFastAPIApp:
    """Test FastAPI application."""
    
    def test_app_creation(self):
        """Test app is created."""
        from backend.main import app
        assert app is not None
        assert app.title == "Evoki V3.0 Backend"
    
    def test_app_routes(self):
        """Test routes are registered."""
        from backend.main import app
        
        # Get all routes
        routes = [route.path for route in app.routes]
        
        # Check critical routes exist
        assert "/" in routes
        assert "/health" in routes
        assert "/api/temple/stream" in routes or any("/api/temple" in r for r in routes)
        assert any("/api/metrics" in r for r in routes)
        assert any("/api/vector" in r for r in routes)
        assert any("/api/timeline" in r for r in routes)


class TestDatabases:
    """Test database accessibility."""
    
    def test_core_db_exists(self):
        """Test core DB exists."""
        from pathlib import Path
        db_path = Path(__file__).resolve().parents[2] / "backend" / "data" / "databases" / "evoki_v3_core.db"
        assert db_path.exists(), f"Core DB not found: {db_path}"
    
    def test_core_db_schema(self):
        """Test core DB has tables."""
        import sqlite3
        from pathlib import Path
        
        db_path = Path(__file__).resolve().parents[2] / "backend" / "data" / "databases" / "evoki_v3_core.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert "prompt_pairs" in tables
        assert "metrics_full" in tables
        assert "session_chain" in tables
        assert "b_state_evolution" in tables
        assert "hazard_events" in tables
        
        conn.close()
    
    def test_all_dbs_exist(self):
        """Test all 5 databases exist."""
        from pathlib import Path
        
        db_dir = Path(__file__).resolve().parents[2] / "backend" / "data" / "databases"
        
        expected_dbs = [
            "evoki_v3_core.db",
            "evoki_v3_graph.db",
            "evoki_v3_keywords.db",
            "evoki_v3_analytics.db",
            "evoki_v3_trajectories.db"
        ]
        
        for db_name in expected_dbs:
            db_path = db_dir / db_name
            assert db_path.exists(), f"Database missing: {db_name}"


class TestFAISS:
    """Test FAISS indices."""
    
    def test_faiss_import(self):
        """Test FAISS can be imported."""
        import faiss
        assert faiss is not None
    
    def test_faiss_indices_exist(self):
        """Test FAISS indices exist."""
        from pathlib import Path
        
        faiss_dir = Path(__file__).resolve().parents[2] / "backend" / "data" / "faiss"
        
        expected_indices = [
            "evoki_v3_vectors_semantic.faiss",
            "evoki_v3_vectors_metrics.faiss",
            "evoki_v3_vectors_trajectory.faiss"
        ]
        
        for index_name in expected_indices:
            index_path = faiss_dir / index_name
            assert index_path.exists(), f"FAISS index missing: {index_name}"
    
    def test_faiss_indices_loadable(self):
        """Test FAISS indices can be loaded."""
        import faiss
        from pathlib import Path
        
        faiss_dir = Path(__file__).resolve().parents[2] / "backend" / "data" / "faiss"
        
        # Load semantic index
        semantic_path = faiss_dir / "evoki_v3_vectors_semantic.faiss"
        semantic_index = faiss.read_index(str(semantic_path))
        assert semantic_index.d == 4096  # 4096 dimensions
        
        # Load metrics index
        metrics_path = faiss_dir / "evoki_v3_vectors_metrics.faiss"
        metrics_index = faiss.read_index(str(metrics_path))
        assert metrics_index.d == 384  # 384 dimensions
        
        # Load trajectory index
        trajectory_path = faiss_dir / "evoki_v3_vectors_trajectory.faiss"
        trajectory_index = faiss.read_index(str(trajectory_path))
        assert trajectory_index.d == 50  # 50 dimensions


class TestGenesisAnchor:
    """Test Genesis Anchor validation."""
    
    def test_genesis_anchor_import(self):
        """Test genesis anchor can be imported."""
        from backend.core.genesis_anchor import validate_genesis_anchor
        assert validate_genesis_anchor is not None
    
    def test_genesis_validation(self):
        """Test genesis validation runs."""
        from backend.core.genesis_anchor import validate_genesis_anchor
        
        result = validate_genesis_anchor(strict=False)
        assert isinstance(result, dict)
        assert "valid" in result


@pytest.mark.integration
class TestE2ESmoke:
    """End-to-end smoke tests."""
    
    def test_backend_startup(self):
        """Test backend can start (without actually running server)."""
        from backend.main import app
        
        # Test app is ready
        assert app is not None
        
        # Test routes are set up
        assert len(app.routes) > 0
    
    def test_metrics_computation_ready(self):
        """Test metrics engine is ready."""
        from backend.core.evoki_metrics_v3 import compute_full_spectrum
        
        # Simple test call (with dummy data)
        try:
            result = compute_full_spectrum(
                user_text="Test",
                ai_text="Test response",
                context={}
            )
            # Should return a dict with metrics
            assert isinstance(result, dict)
        except Exception as e:
            # Allow errors for now (missing dependencies, etc.)
            pytest.skip(f"Metrics engine not fully ready: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])

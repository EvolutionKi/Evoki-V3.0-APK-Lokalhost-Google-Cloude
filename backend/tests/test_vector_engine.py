#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vector_engine.py — Unit Tests for VectorEngine V2.1

Tests TRI-ANCHOR retrieval, memory operations, and B-Vector updates.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.core.vector_engine_v2_1 import VectorEngineV2
from backend.core.b_vector import BVector


@pytest.fixture
def vector_engine():
    """Create a test vector engine instance."""
    # Use in-memory mode for testing
    engine = VectorEngineV2(
        dim=384,  # MiniLM dimensions
        db_path=":memory:",
        faiss_path=None  # Will create in-memory FAISS
    )
    return engine


@pytest.fixture
def b_vector():
    """Create a test B-Vector instance."""
    return BVector(dim=384)


class TestBVector:
    """Test B-Vector functionality."""
    
    def test_initialization(self, b_vector):
        """Test B-Vector initializes correctly."""
        assert b_vector.dim == 384
        assert b_vector._update_count == 0
        assert b_vector.norm() == 0.0  # Zero vector initially
    
    def test_update_positive(self, b_vector):
        """Test B-Vector learns from positive A-vectors."""
        # Create positive A-vector
        a_vec = np.random.randn(384).astype(np.float32)
        a_vec = a_vec / np.linalg.norm(a_vec)  # Normalize
        
        initial_norm = b_vector.norm()
        b_vector.update(a_vec, a_score=0.8)  # Positive score
        
        # B-Vector should have changed
        assert b_vector.norm() > initial_norm
        assert b_vector._update_count == 1
    
    def test_update_negative(self, b_vector):
        """Test B-Vector ignores negative A-vectors."""
        a_vec = np.random.randn(384).astype(np.float32)
        a_vec = a_vec / np.linalg.norm(a_vec)
        
        initial_norm = b_vector.norm()
        b_vector.update(a_vec, a_score=0.2)  # Negative score
        
        # B-Vector should NOT have changed (threshold is 0.5)
        assert b_vector.norm() == initial_norm
        assert b_vector._update_count == 0
    
    def test_alignment(self, b_vector):
        """Test B-Vector alignment calculation."""
        # Update with some vectors
        for _ in range(5):
            a_vec = np.random.randn(384).astype(np.float32)
            a_vec = a_vec / np.linalg.norm(a_vec)
            b_vector.update(a_vec, a_score=0.8)
        
        # Test alignment
        test_vec = np.random.randn(384).astype(np.float32)
        test_vec = test_vec / np.linalg.norm(test_vec)
        
        alignment = b_vector.alignment(test_vec)
        assert isinstance(alignment, float)
        assert -1.0 <= alignment <= 1.0


class TestVectorEngine:
    """Test VectorEngine V2.1 functionality."""
    
    def test_initialization(self, vector_engine):
        """Test VectorEngine initializes correctly."""
        assert vector_engine.dim == 384
        assert vector_engine.b_vector is not None
    
    def test_add_memory(self, vector_engine):
        """Test adding memory to engine."""
        text = "Test memory entry"
        embedding = np.random.randn(384).astype(np.float32)
        
        memory_id = vector_engine.add_memory(
            text=text,
            embedding=embedding,
            a_score=0.7,
            metadata={"source": "test"}
        )
        
        assert memory_id is not None
        assert isinstance(memory_id, str)
    
    def test_search_semantic(self, vector_engine):
        """Test semantic search."""
        # Add some memories
        for i in range(10):
            text = f"Memory {i}"
            embedding = np.random.randn(384).astype(np.float32)
            vector_engine.add_memory(text, embedding, a_score=0.6)
        
        # Search
        query_embedding = np.random.randn(384).astype(np.float32)
        results = vector_engine.search_semantic(query_embedding, top_k=5)
        
        assert len(results) <= 5
        assert all(isinstance(r, dict) for r in results)
    
    def test_freeze_memory(self, vector_engine):
        """Test FREEZE memory operation."""
        text = "Important memory"
        embedding = np.random.randn(384).astype(np.float32)
        
        memory_id = vector_engine.add_memory(text, embedding, a_score=0.8)
        
        # Freeze it
        success = vector_engine.freeze_memory(memory_id)
        assert success is True
        
        # Verify frozen
        memory = vector_engine.get_memory(memory_id)
        assert memory["frozen"] is True
    
    def test_boost_memory(self, vector_engine):
        """Test BOOST memory operation."""
        text = "Boosted memory"
        embedding = np.random.randn(384).astype(np.float32)
        
        memory_id = vector_engine.add_memory(text, embedding, a_score=0.7)
        initial_priority = vector_engine.get_memory(memory_id)["priority"]
        
        # Boost it
        success = vector_engine.boost_memory(memory_id, factor=2.0)
        assert success is True
        
        # Verify boosted
        memory = vector_engine.get_memory(memory_id)
        assert memory["priority"] > initial_priority


class TestTriAnchorRetrieval:
    """Test TRI-ANCHOR retrieval system."""
    
    def test_hash_anchor(self, vector_engine):
        """Test hash-based retrieval."""
        text = "Exact match test"
        embedding = np.random.randn(384).astype(np.float32)
        
        memory_id = vector_engine.add_memory(
            text=text,
            embedding=embedding,
            a_score=0.7,
            tags=["test"]
        )
        
        # Search by hash
        results = vector_engine.search_by_hash(text)
        assert len(results) > 0
        assert results[0]["memory_id"] == memory_id
    
    def test_tag_anchor(self, vector_engine):
        """Test tag-based retrieval."""
        # Add memories with tags
        for tag in ["important", "work", "personal"]:
            embedding = np.random.randn(384).astype(np.float32)
            vector_engine.add_memory(
                text=f"Memory with {tag}",
                embedding=embedding,
                a_score=0.6,
                tags=[tag]
            )
        
        # Search by tag
        results = vector_engine.search_by_tag("important")
        assert len(results) > 0
        assert all("important" in r["tags"] for r in results)
    
    def test_tri_anchor_combined(self, vector_engine):
        """Test combined TRI-ANCHOR search."""
        # Add test memories
        for i in range(20):
            text = f"Test memory {i}"
            embedding = np.random.randn(384).astype(np.float32)
            tags = ["test"] if i % 2 == 0 else ["other"]
            
            vector_engine.add_memory(
                text=text,
                embedding=embedding,
                a_score=0.6 + (i * 0.01),
                tags=tags
            )
        
        # TRI-ANCHOR search
        query_embedding = np.random.randn(384).astype(np.float32)
        results = vector_engine.search_tri_anchor(
            query_text="Test memory",
            query_embedding=query_embedding,
            query_tags=["test"],
            top_k=10
        )
        
        assert len(results) <= 10
        # Results should be ranked by combined score
        assert all(r["combined_score"] >= 0 for r in results)


@pytest.mark.integration
class TestIntegration:
    """Integration tests for full workflow."""
    
    def test_full_memory_lifecycle(self, vector_engine):
        """Test complete memory lifecycle."""
        # 1. Add memory
        text = "Integration test memory"
        embedding = np.random.randn(384).astype(np.float32)
        
        memory_id = vector_engine.add_memory(
            text=text,
            embedding=embedding,
            a_score=0.75,
            metadata={"test": True}
        )
        
        # 2. Retrieve it
        memory = vector_engine.get_memory(memory_id)
        assert memory["text"] == text
        
        # 3. Freeze it
        vector_engine.freeze_memory(memory_id)
        memory = vector_engine.get_memory(memory_id)
        assert memory["frozen"] is True
        
        # 4. Boost it
        vector_engine.boost_memory(memory_id, factor=1.5)
        memory = vector_engine.get_memory(memory_id)
        assert memory["priority"] > 1.0
        
        # 5. Search for it
        results = vector_engine.search_semantic(embedding, top_k=5)
        assert any(r["memory_id"] == memory_id for r in results)
    
    def test_b_vector_learning(self, vector_engine):
        """Test B-Vector learns from interactions."""
        initial_norm = vector_engine.b_vector.norm()
        
        # Add multiple positive memories
        for i in range(10):
            embedding = np.random.randn(384).astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            
            vector_engine.add_memory(
                text=f"Positive memory {i}",
                embedding=embedding,
                a_score=0.8  # High A-score
            )
        
        # B-Vector should have learned
        final_norm = vector_engine.b_vector.norm()
        assert final_norm > initial_norm
        assert vector_engine.b_vector._update_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

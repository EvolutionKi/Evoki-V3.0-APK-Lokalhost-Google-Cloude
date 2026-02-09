#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
initialize_faiss.py — Evoki V3.0 FAISS Index Initialization

Creates 3 FAISS namespaces:
1. semantic_wpf (4096D, Mistral-7B) — Text Similarity
2. metrics_wpf (384D, MiniLM) — Metrics Similarity  
3. trajectory_wpf (50D, custom) — Trajectory Similarity
"""

import faiss
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Projekt Root
REPO_ROOT = Path(__file__).resolve().parents[2]
FAISS_DIR = REPO_ROOT / "backend" / "data" / "faiss"

# Ensure directory exists
FAISS_DIR.mkdir(parents=True, exist_ok=True)


def create_semantic_index():
    """
    Semantic Search Index (4096D, Mistral-7B-Instruct-v0.2)
    
    Uses Inner Product for cosine similarity (vectors are normalized).
    GPU-accelerated if available.
    """
    logger.info("Creating semantic_wpf index (4096D, Mistral)...")
    
    dim = 4096
    
    # IndexFlatIP = Inner Product (for normalized vectors = cosine sim)
    index = faiss.IndexFlatIP(dim)
    
    # Save empty index
    faiss_file = FAISS_DIR / "evoki_v3_vectors_semantic.faiss"
    faiss.write_index(index, str(faiss_file))
    
    logger.info(f"✅ Semantic index created: {faiss_file.name}")
    return faiss_file


def create_metrics_index():
    """
    Metrics Similarity Index (384D, all-MiniLM-L6-v2)
    
    Uses L2 distance for metrics vectors.
    CPU-optimized (MiniLM is fast enough on CPU).
    """
    logger.info("Creating metrics_wpf index (384D, MiniLM)...")
    
    dim = 384
    
    # IndexFlatL2 = L2 distance
    index = faiss.IndexFlatL2(dim)
    
    # Save empty index
    faiss_file = FAISS_DIR / "evoki_v3_vectors_metrics.faiss"
    faiss.write_index(index, str(faiss_file))
    
    logger.info(f"✅ Metrics index created: {faiss_file.name}")
    return faiss_file


def create_trajectory_index():
    """
    Trajectory Similarity Index  (~50D, custom trajectory vectors)
    
    Trajectory vector components (example):
    - ∇A trend (slope)
    - ∇PCI trend
    - Flow volatility
    - Depth oscillation
    - Phase shift count
    - Cycle frequency
    - etc.
    
    Uses L2 distance.
    """
    logger.info("Creating trajectory_wpf index (50D, custom)...")
    
    dim = 50  # Configurable based on trajectory features
    
    # IndexFlatL2
    index = faiss.IndexFlatL2(dim)
    
    # Save empty index
    faiss_file = FAISS_DIR / "evoki_v3_vectors_trajectory.faiss"
    faiss.write_index(index, str(faiss_file))
    
    logger.info(f"✅ Trajectory index created: {faiss_file.name}")
    return faiss_file


def create_metadata_db():
    """
    Create SQLite metadata DB for FAISS indices.
    
    Maps FAISS index positions to pair_ids and stores additional metadata.
    """
    import sqlite3
    
    logger.info("Creating FAISS metadata database...")
    
    db_path = FAISS_DIR / "faiss_metadata.db"
    
    schema_sql = """
    PRAGMA journal_mode=WAL;
    
    -- Semantic Index Metadata
    CREATE TABLE IF NOT EXISTS semantic_index (
      faiss_position INTEGER PRIMARY KEY,
      pair_id TEXT UNIQUE NOT NULL,
      embedding_model TEXT DEFAULT 'mistral-7b-v0.2',
      embedding_timestamp TEXT NOT NULL
    );
    
    -- Metrics Index Metadata
    CREATE TABLE IF NOT EXISTS metrics_index (
      faiss_position INTEGER PRIMARY KEY,
      pair_id TEXT UNIQUE NOT NULL,
      embedding_model TEXT DEFAULT 'all-MiniLM-L6-v2',
      embedding_timestamp TEXT NOT NULL
    );
    
    -- Trajectory Index Metadata
    CREATE TABLE IF NOT EXISTS trajectory_index (
      faiss_position INTEGER PRIMARY KEY,
      session_id TEXT NOT NULL,
      pair_id TEXT NOT NULL,
      trajectory_features_json TEXT,
      embedding_timestamp TEXT NOT NULL
    );
    
    CREATE INDEX idx_semantic_pair ON semantic_index(pair_id);
    CREATE INDEX idx_metrics_pair ON metrics_index(pair_id);
    CREATE INDEX idx_trajectory_pair ON trajectory_index(pair_id);
    """
    
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()
    
    logger.info(f"✅ Metadata DB created: {db_path.name}")
    return db_path


def main():
    """Initialize all FAISS indices."""
    logger.info("=" * 80)
    logger.info("EVOKI V3.0 — FAISS INDEX INITIALIZATION")
    logger.info("=" * 80)
    logger.info(f"FAISS Directory: {FAISS_DIR}")
    logger.info("")
    
    try:
        # Create indices
        semantic_file = create_semantic_index()
        metrics_file = create_metrics_index()
        trajectory_file = create_trajectory_index()
        metadata_db = create_metadata_db()
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ALL FAISS INDICES INITIALIZED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Created files:")
        logger.info(f"  - {semantic_file.name} (4096D, Inner Product)")
        logger.info(f"  - {metrics_file.name} (384D, L2)")
        logger.info(f"  - {trajectory_file.name} (50D, L2)")
        logger.info(f"  - {metadata_db.name} (Metadata DB)")
        logger.info("")
        logger.info("Ready for vector ingestion!")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ FAISS initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

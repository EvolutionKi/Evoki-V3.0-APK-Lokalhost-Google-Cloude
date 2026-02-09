"""
Regenerate FAISS embeddings for all prompt pairs in the database.
This script reads all pairs from prompt_pairs table, generates embeddings,
and populates the FAISS semantic index.
"""
import sqlite3
import faiss
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "backend" / "data" / "databases" / "evoki_v3_core.db"
FAISS_DIR = REPO_ROOT / "backend" / "data" / "faiss"
SEMANTIC_FAISS = FAISS_DIR / "evoki_v3_vectors_semantic.faiss"
FAISS_META_DB = FAISS_DIR / "faiss_metadata.db"

# Embedding model
EMBEDDING_DIM = 384
MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    logger.info("="*80)
    logger.info("EVOKI V3.0 — REGENERATE FAISS EMBEDDINGS")
    logger.info("="*80)
    logger.info(f"Database: {DB_PATH}")
    logger.info(f"FAISS Index: {SEMANTIC_FAISS}")
    logger.info("")
    
    # Load model (CPU only for stability)
    logger.info(f"Loading embedding model ({MODEL_NAME}) on CPU...")
    model = SentenceTransformer(MODEL_NAME, device='cpu')
    logger.info("  ✅ Model loaded")
    logger.info("")
    
    # Connect to databases
    logger.info("Connecting to databases...")
    core_conn = sqlite3.connect(DB_PATH)
    faiss_meta_conn = sqlite3.connect(FAISS_META_DB)
    logger.info("  ✅ Connected")
    logger.info("")
    
    # Create new FAISS index (delete old one)
    logger.info(f"Creating new FAISS index ({EMBEDDING_DIM}D, InnerProduct)...")
    faiss_index = faiss.IndexFlatIP(EMBEDDING_DIM)
    logger.info("  ✅ Index created")
    logger.info("")
    
    # Clear existing metadata
    logger.info("Clearing old metadata...")
    meta_cursor = faiss_meta_conn.cursor()
    meta_cursor.execute("DELETE FROM semantic_index")
    faiss_meta_conn.commit()
    logger.info("  ✅ Cleared")
    logger.info("")
    
    # Fetch all prompt pairs
    logger.info("Fetching prompt pairs...")
    cursor = core_conn.cursor()
    cursor.execute("""
        SELECT pair_id, user_text, created_at 
        FROM prompt_pairs 
        ORDER BY created_at ASC
    """)
    pairs = cursor.fetchall()
    total_pairs = len(pairs)
    logger.info(f"  Found {total_pairs} pairs")
    logger.info("")
    
    # Process in batches
    logger.info("Generating embeddings...")
    batch_size = 100
    successful = 0
    failed = 0
    
    for i in range(0, total_pairs, batch_size):
        batch = pairs[i:i+batch_size]
        batch_end = min(i + batch_size, total_pairs)
        
        try:
            # Extract texts
            texts = [pair[1] for pair in batch]
            pair_ids = [pair[0] for pair in batch]
            
            # Generate embeddings (batch)
            embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
            embeddings = embeddings.astype('float32')
            
            # Normalize for cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / (norms + 1e-10)  # Avoid division by zero
            
            # Add to FAISS
            start_pos = faiss_index.ntotal
            faiss_index.add(embeddings)
            
            # Store metadata
            for j, pair_id in enumerate(pair_ids):
                faiss_position = start_pos + j
                meta_cursor.execute("""
                    INSERT INTO semantic_index (
                        faiss_position, pair_id, embedding_model, embedding_timestamp
                    ) VALUES (?, ?, ?, ?)
                """, (faiss_position, pair_id, MODEL_NAME, datetime.now().isoformat()))
            
            faiss_meta_conn.commit()
            successful += len(batch)
            
            logger.info(f"  [{i+1:5d}-{batch_end:5d}/{total_pairs}] ✅ {len(batch)} embeddings")
            
        except Exception as e:
            logger.error(f"  [{i+1:5d}-{batch_end:5d}/{total_pairs}] ❌ {e}")
            failed += len(batch)
    
    logger.info("")
    logger.info("Saving FAISS index...")
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(faiss_index, str(SEMANTIC_FAISS))
    logger.info(f"  ✅ Saved to: {SEMANTIC_FAISS}")
    logger.info("")
    
    # Final stats
    logger.info("="*80)
    logger.info("✅ REGENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Total pairs processed: {total_pairs}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {failed}")
    logger.info(f"FAISS index size: {faiss_index.ntotal} vectors")
    logger.info("")
    
    # Test search
    if faiss_index.ntotal > 0:
        logger.info("Testing search...")
        test_text = "Hello, how are you?"
        test_emb = model.encode(test_text, convert_to_numpy=True).astype('float32')
        test_emb = test_emb / np.linalg.norm(test_emb)
        D, I = faiss_index.search(test_emb.reshape(1, -1), k=5)
        logger.info(f"  Top 5 results for '{test_text}':")
        for idx, (dist, pos) in enumerate(zip(D[0], I[0])):
            logger.info(f"    {idx+1}. Position {pos}, Score: {dist:.4f}")
        logger.info("  ✅ Search working!")
    
    # Cleanup
    core_conn.close()
    faiss_meta_conn.close()
    logger.info("")
    logger.info("🎉 Done!")
    
    return 0

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python3
"""
Evoki V3.0 - FAISS Index Builder (Phase 3)

Embedding-Modell: deepset-mxbai-embed-de-large-v1
- Speziell für Deutsch trainiert (30 Mio Paare)
- Optimal für Trauma-Semantik und Metaphern
- 1024D Dimensionen (reduzierbar via Matryoshka)

Hardware: GTX 3060 12GB (CUDA)
"""
import sqlite3
import json
import time
import os
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# FAISS import
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    print("⚠️ FAISS not installed. Run: pip install faiss-cpu")
    HAS_FAISS = False

# Sentence Transformers import
try:
    from sentence_transformers import SentenceTransformer
    HAS_SBERT = True
except ImportError:
    print("⚠️ sentence-transformers not installed. Run: pip install sentence-transformers")
    HAS_SBERT = False

# Paths
EVOKI_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DB_DIR = EVOKI_ROOT / "app" / "deep_earth"
MASTER_DB = DB_DIR / "master_timeline.db"
INDEX_DIR = DB_DIR / "vector_indices"

# Model Configuration
# CHANGED: Using German-optimized model instead of Mistral-7B
MODELS = {
    "primary": {
        "name": "mixedbread-ai/deepset-mxbai-embed-de-large-v1",
        "dimension": 1024,
        "output_file": "mxbai_de_1024d.faiss",
        "description": "German semantic search (30M German pairs, Trauma-optimiert)"
    },
    "fallback": {
        "name": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384,
        "output_file": "minilm_384d.faiss",
        "description": "Fast CPU fallback (multilingual)"
    }
}


def load_chunks(db_path: Path, limit: int = None):
    """Load text chunks from SQLite database."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    if limit:
        cursor.execute("SELECT chunk_id, text FROM chunks LIMIT ?", (limit,))
    else:
        cursor.execute("SELECT chunk_id, text FROM chunks")
    
    chunks = cursor.fetchall()
    conn.close()
    
    return chunks


def create_embeddings(model, texts, batch_size=32, show_progress=True):
    """Create embeddings for a list of texts."""
    embeddings = []
    total = len(texts)
    
    for i in range(0, total, batch_size):
        batch = texts[i:i+batch_size]
        batch_embeddings = model.encode(
            batch,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True  # Important for cosine similarity!
        )
        embeddings.append(batch_embeddings)
        
        if show_progress and (i + batch_size) % 1000 == 0:
            print(f"   ... {min(i + batch_size, total)}/{total} embeddings created")
    
    return np.vstack(embeddings)


def build_faiss_index(embeddings, dimension):
    """Build FAISS index from embeddings."""
    # Use Inner Product for normalized vectors (= cosine similarity)
    index = faiss.IndexFlatIP(dimension)
    
    # Ensure embeddings are float32
    embeddings_f32 = embeddings.astype(np.float32)
    
    # Add embeddings
    index.add(embeddings_f32)
    
    return index


def update_db_with_embedding_ids(db_path: Path, chunk_ids: list, model_key: str):
    """Update database with embedding IDs for fast lookup."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    column = f"embedding_id_{model_key}"
    
    for idx, chunk_id in enumerate(chunk_ids):
        cursor.execute(f"""
            UPDATE chunks SET {column} = ? WHERE chunk_id = ?
        """, (idx, chunk_id))
    
    conn.commit()
    conn.close()


def create_metadata_file(index_dir: Path, model_config: dict, num_vectors: int):
    """Create metadata file for the index."""
    metadata = {
        "model_name": model_config["name"],
        "dimension": model_config["dimension"],
        "num_vectors": num_vectors,
        "created_at": datetime.utcnow().isoformat(),
        "description": model_config["description"],
        "normalized": True
    }
    
    metadata_path = index_dir / f"{model_config['output_file']}.meta.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata_path


def build_index_for_model(model_key: str, chunks: list, index_dir: Path, db_path: Path):
    """Build FAISS index for a specific model."""
    config = MODELS[model_key]
    
    print(f"\n{'='*60}")
    print(f"🧠 Building: {config['name']}")
    print(f"   Dimension: {config['dimension']}D")
    print(f"   Chunks: {len(chunks)}")
    print(f"{'='*60}")
    
    # Load model
    print(f"📦 Loading model...")
    start_load = time.time()
    
    # Check for GPU
    device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") != "-1" else "cpu"
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            print(f"   GPU detected: {torch.cuda.get_device_name(0)}")
    except ImportError:
        device = "cpu"
    
    model = SentenceTransformer(config["name"], device=device)
    load_time = time.time() - start_load
    print(f"   Loaded in {load_time:.2f}s on {device.upper()}")
    
    # Extract texts and IDs
    chunk_ids = [c[0] for c in chunks]
    texts = [c[1] if c[1] else "" for c in chunks]
    
    # Create embeddings
    print(f"⚙️ Creating embeddings...")
    start_embed = time.time()
    
    batch_size = 64 if device == "cuda" else 32
    embeddings = create_embeddings(model, texts, batch_size=batch_size)
    
    embed_time = time.time() - start_embed
    print(f"   Completed in {embed_time:.2f}s ({len(texts) / embed_time:.1f} texts/sec)")
    
    # Build FAISS index
    print(f"🔧 Building FAISS index...")
    start_index = time.time()
    
    index = build_faiss_index(embeddings, config["dimension"])
    
    index_time = time.time() - start_index
    print(f"   Built in {index_time:.2f}s")
    
    # Save index
    index_path = index_dir / config["output_file"]
    faiss.write_index(index, str(index_path))
    
    index_size = index_path.stat().st_size / 1024 / 1024
    print(f"💾 Saved: {config['output_file']} ({index_size:.2f} MB)")
    
    # Create metadata
    metadata_path = create_metadata_file(index_dir, config, len(texts))
    print(f"📝 Metadata: {metadata_path.name}")
    
    # Update DB with embedding IDs
    # update_db_with_embedding_ids(db_path, chunk_ids, model_key)
    
    return {
        "model": config["name"],
        "dimension": config["dimension"],
        "vectors": len(texts),
        "index_size_mb": index_size,
        "embed_time_s": embed_time,
        "index_path": str(index_path)
    }


def main():
    print("=" * 60)
    print("EVOKI V3.0 - FAISS INDEX BUILDER (Phase 3)")
    print("=" * 60)
    
    if not HAS_FAISS or not HAS_SBERT:
        print("\n❌ Missing dependencies. Install:")
        print("   pip install faiss-cpu sentence-transformers torch")
        return 1
    
    # Check database
    if not MASTER_DB.exists():
        print(f"❌ Database not found: {MASTER_DB}")
        print("   Run populate_databases.py first!")
        return 1
    
    # Load chunks
    print(f"\n📂 Loading chunks from: {MASTER_DB.name}")
    chunks = load_chunks(MASTER_DB)
    print(f"   Loaded {len(chunks)} chunks")
    
    # Create index directory
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output: {INDEX_DIR}")
    
    results = []
    
    # Build primary index (German model)
    try:
        result = build_index_for_model("primary", chunks, INDEX_DIR, MASTER_DB)
        results.append(result)
    except Exception as e:
        print(f"\n⚠️ Primary model failed: {e}")
        print("   Falling back to MiniLM...")
    
    # Build fallback index (MiniLM)
    try:
        result = build_index_for_model("fallback", chunks, INDEX_DIR, MASTER_DB)
        results.append(result)
    except Exception as e:
        print(f"\n❌ Fallback model failed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ FAISS INDEX BUILD COMPLETE")
    print("=" * 60)
    
    for r in results:
        print(f"\n📊 {r['model']}:")
        print(f"   Vectors: {r['vectors']}")
        print(f"   Dimension: {r['dimension']}D")
        print(f"   Size: {r['index_size_mb']:.2f} MB")
        print(f"   Embed time: {r['embed_time_s']:.2f}s")
    
    total_size = sum(r['index_size_mb'] for r in results)
    print(f"\n💾 Total index size: {total_size:.2f} MB")
    print(f"📁 Location: {INDEX_DIR}")
    
    return 0


if __name__ == "__main__":
    exit(main())

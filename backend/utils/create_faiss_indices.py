"""
Create FAISS Indices for Evoki V3.0
"""
import faiss
import numpy as np
from pathlib import Path


def create_faiss_indices():
    """Create all FAISS indices"""
    
    faiss_dir = Path(__file__).parent.parent / "data" / "faiss"
    faiss_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating FAISS indices...")
    
    # 1. semantic_wpf (4096D, Mistral-7B-Instruct-v0.2)
    print("\n1. Creating semantic_wpf (4096D)...")
    dim_semantic = 4096
    index_semantic = faiss.IndexFlatIP(dim_semantic)  # Inner Product for cosine similarity
    
    semantic_path = faiss_dir / "evoki_v3_vectors_semantic.faiss"
    faiss.write_index(index_semantic, str(semantic_path))
    print(f"   ✅ {semantic_path}")
    print(f"   Size: {semantic_path.stat().st_size / 1024:.1f} KB")
    
    # 2. metrics_wpf (384D, all-MiniLM-L6-v2) - ALREADY EXISTS!
    metrics_path = faiss_dir / "evoki_v3_vectors.faiss"
    if metrics_path.exists():
        print(f"\n2. metrics_wpf (384D) - ✅ ALREADY EXISTS")
        print(f"   Location: {metrics_path}")
        print(f"   Size: {metrics_path.stat().st_size / 1024:.1f} KB")
        
        # Load and check
        index_metrics = faiss.read_index(str(metrics_path))
        print(f"   Vectors: {index_metrics.ntotal}")
        print(f"   Dimension: {index_metrics.d}")
    else:
        print(f"\n2. Creating metrics_wpf (384D)...")
        dim_metrics = 384
        index_metrics = faiss.IndexFlatL2(dim_metrics)  # L2 distance for MiniLM
        faiss.write_index(index_metrics, str(metrics_path))
        print(f"   ✅ {metrics_path}")
    
    # 3. trajectory_wpf (~50D, custom trajectory embeddings)
    print(f"\n3. Creating trajectory_wpf (50D)...")
    dim_trajectory = 50  # 10 metrics × 5 timepoints
    index_trajectory = faiss.IndexFlatL2(dim_trajectory)
    
    trajectory_path = faiss_dir / "evoki_v3_vectors_trajectory.faiss"
    faiss.write_index(index_trajectory, str(trajectory_path))
    print(f"   ✅ {trajectory_path}")
    print(f"   Size: {trajectory_path.stat().st_size / 1024:.1f} KB")
    
    print("\n" + "="*60)
    print("📊 FAISS INDICES SUMMARY")
    print("="*60)
    print(f"semantic_wpf    : 4096D (Mistral-7B) - {semantic_path.stat().st_size / 1024:.1f} KB")
    print(f"metrics_wpf     : 384D  (MiniLM)     - {metrics_path.stat().st_size / 1024:.1f} KB")
    print(f"trajectory_wpf  : 50D   (Custom)     - {trajectory_path.stat().st_size / 1024:.1f} KB")
    print("="*60)
    
    return {
        "semantic": semantic_path,
        "metrics": metrics_path,
        "trajectory": trajectory_path
    }


if __name__ == "__main__":
    indices = create_faiss_indices()
    print("\n✅ All FAISS indices ready!")

# -*- coding: utf-8 -*-
"""
EVOKI V2.2 QUERY TOOL - Standalone Version
Test-Skript für das Deep Storage Gedächtnis.
Führt eine semantische Abfrage gegen die FAISS-Datenbanken aus.

Usage: python query.py "Deine Frage"
"""

import sys
import json
import pickle
import numpy as np
import faiss
from pathlib import Path
from typing import List, Dict
from sentence_transformers import SentenceTransformer

# EVOKI V2.0 Paths
ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "data"
CHUNKS_FILE = DATA_DIR / "chunks_v2_2.pkl"
INDEX_DIR = DATA_DIR / "faiss_indices"
MEMORY_ANCHOR = DATA_DIR / "memory_anchor.json"
W2_INDEX = DATA_DIR / "evoki_vectorstore_W2_384D.faiss"
W5_INDEX = INDEX_DIR / "W5_4096D_weighted.faiss"
MODEL_MINILM = "sentence-transformers/all-MiniLM-L6-v2"

class EVOKIQuery:
    """Query Interface für EVOKI Deep Storage."""
    
    def __init__(self):
        print("EVOKI V2.2 Query Tool")
        print("=" * 50)
        
        # Load Memory Anchor (Optional)
        if MEMORY_ANCHOR.exists():
            with open(MEMORY_ANCHOR, 'r', encoding='utf-8') as f:
                self.anchor = json.load(f)
            print(f"\nIntegrity Check: Version {self.anchor.get('version', 'N/A')}")
        else:
            print("\nMemory Anchor not found - skipping integrity check")
            self.anchor = {'statistics': {'total_chunks': 0}, 'wormhole': {'total_edges': 0}}
        
        # Load Chunks
        print(f"\nLoading chunks from {CHUNKS_FILE.name}...")
        with open(CHUNKS_FILE, 'rb') as f:
            self.chunks = pickle.load(f)
        print(f"Loaded: {len(self.chunks)} chunks")
        
        # Load FAISS Indices
        print("\nLoading FAISS Indices...")
        if W2_INDEX.exists():
            self.w2_index = faiss.read_index(str(W2_INDEX))
            print("  [OK] W2 (384D)")
        else:
            print("  [ERROR] W2 Index not found!")
            self.w2_index = None
        
        self.minilm_model = None
    
    def embed_query(self, query: str) -> np.ndarray:
        """Embed Query mit MiniLM (384D)."""
        if self.minilm_model is None:
            print("  [Loading MiniLM model...]")
            self.minilm_model = SentenceTransformer(MODEL_MINILM)
        
        vec = self.minilm_model.encode([query], convert_to_numpy=True)[0]
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec
    
    def search_w2(self, query: str, top_k: int = 10) -> List[Dict]:
        """Sucht in W2 (384D)."""
        if self.w2_index is None:
            return []
        
        print(f"\nSearching W2 (384D MiniLM) with query: \"{query}\"")
        query_vec = self.embed_query(query)
        distances, indices = self.w2_index.search(query_vec.reshape(1, -1), top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            if isinstance(chunk, dict):
                chunk_id = chunk.get('chunk_id', f'chunk_{idx}')
                text = chunk.get('text', chunk.get('content', ''))
                created_at = chunk.get('created_at', chunk.get('timestamp', 'N/A'))
                lexika = chunk.get('lexika_matches', chunk.get('keywords', []))
            else:
                chunk_id = getattr(chunk, 'chunk_id', f'chunk_{idx}')
                text = getattr(chunk, 'text', getattr(chunk, 'content', ''))
                created_at = getattr(chunk, 'created_at', getattr(chunk, 'timestamp', 'N/A'))
                lexika = getattr(chunk, 'lexika_matches', getattr(chunk, 'keywords', []))
            
            results.append({
                "chunk_id": chunk_id,
                "text": text[:500] + "..." if len(text) > 500 else text,
                "similarity": float(dist),
                "created_at": str(created_at)[:10],
                "lexika_matches": [str(x) for x in lexika[:5]] if lexika else []
            })
        
        return results
    
    def print_results(self, results: List[Dict], title: str):
        """Gibt Ergebnisse formatiert aus."""
        print(f"\n{title}")
        print("=" * 80)
        
        for i, res in enumerate(results, 1):
            print(f"\n#{i} | Similarity: {res['similarity']:.4f} | {res['created_at']}")
            print(f"Chunk: {res['chunk_id']}")
            if res['lexika_matches']:
                print(f"Lexika: {', '.join(res['lexika_matches'])}")
            print(f"\n{res['text']}")
            print("-" * 80)

def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"Deine Frage\"")
        sys.exit(1)
    
    query = sys.argv[1]
    engine = EVOKIQuery()
    
    print(f"\nQuery: \"{query}\"")
    print("=" * 80)
    
    results_w2 = engine.search_w2(query, top_k=10)
    engine.print_results(results_w2, "[W2 RESULTS (384D)]")
    
    print("\n" + "=" * 80)
    print("[OK] Query completed!")
    sys.exit(0)  # ✅ Expliziter Exit Code 0

if __name__ == "__main__":
    main()

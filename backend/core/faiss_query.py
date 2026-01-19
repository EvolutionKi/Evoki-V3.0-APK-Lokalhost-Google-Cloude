"""
FAISS Semantic Search - Phase 1

Nutzt FAISS für semantische Suche im Chatverlauf.
- Embedding: sentence-transformers/all-MiniLM-L6-v2 (384D, CPU-optimiert)
- Index: chatverlauf_final_20251020plus_dedup_sorted.faiss
- Top-K: 100 für Hybrid-Scoring (später)

TODO Phase 3: Upgrade auf Mistral-7B-Instruct-v0.2 (4096D, GPU)
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict


class FAISSQuery:
    """
    FAISS Semantic Search Engine
    
    Phase 1: MiniLM-L6-v2 (384D, CPU)
    Phase 3+: Mistral-7B (4096D, GPU)
    """
    
    def __init__(self):
        """Lädt FAISS Index und Embedding Model beim Start"""
        
        # FAISS Index Pfad (relativ zu backend/)
        self.index_path = Path(__file__).parent.parent.parent / "tooling" / "data" / "faiss_indices" / "chatverlauf_final_20251020plus_dedup_sorted.faiss"
        
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"❌ FAISS Index nicht gefunden!\n"
                f"   Erwartet: {self.index_path}\n"
                f"   Stelle sicher dass der Index existiert."
            )
        
        print("🔍 Lade FAISS Index...")
        print(f"   Pfad: {self.index_path}")
        
        try:
            self.index = faiss.read_index(str(self.index_path))
            print(f"  ✅ Index geladen: {self.index.ntotal} Vektoren")
        except Exception as e:
            raise RuntimeError(f"❌ FAISS Index konnte nicht geladen werden: {e}")
        
        print("🤖 Lade Embedding Model (all-MiniLM-L6-v2, 384D)...")
        try:
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("  ✅ Model geladen (CPU-optimiert)")
        except Exception as e:
            raise RuntimeError(f"❌ Embedding Model konnte nicht geladen werden: {e}")
    
    def search(self, query: str, top_k: int = 100) -> List[Dict]:
        """
        Sucht ähnliche Chunks im Chatverlauf
        
        Args:
            query: User-Prompt Text
            top_k: Anzahl Treffer (default 100 für späteres Hybrid-Scoring)
        
        Returns:
            Liste von Dicts mit:
            - chunk_id: String ID des Chunks
            - similarity: Float (0.0-1.0, höher = ähnlicher)
            - index: Integer Index im FAISS
        """
        # Embed Query
        query_vec = self.model.encode([query])[0]
        
        # FAISS Search
        # Distances sind L2-Distanzen (kleiner = ähnlicher)
        distances, indices = self.index.search(
            query_vec.reshape(1, -1).astype('float32'),
            top_k
        )
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            # Konvertiere L2 Distance zu Similarity (0.0-1.0)
            similarity = 1.0 / (1.0 + dist)
            
            results.append({
                'chunk_id': f'chunk_{idx}',
                'similarity': float(similarity),
                'index': int(idx),
                'distance': float(dist)
            })
        
        return results
    
    def get_wpf_context(self, anchor_chunk_id: str) -> Dict:
        """
        W-P-F Zeitmaschine: Liefert Vergangenheit + Zukunft
        
        Phase 1: Mock-Implementation
        Phase 2+: Echte W-P-F Logik aus 21 DBs
        
        Args:
            anchor_chunk_id: Der gefundene Chunk (z.B. chunk_12345)
        
        Returns:
            Dict mit Past, Present, Future Kontexten:
            - P_m25: 25 Minuten Vergangenheit
            - P_m5: 5 Minuten Vergangenheit
            - W: Wirklichkeit (jetzt)
            - F_p5: 5 Minuten Zukunft
            - F_p25: 25 Minuten Zukunft
        """
        # TODO Phase 2: Implementiere echte W-P-F Logik
        # Jetzt: Mock-Daten
        return {
            'P_m25': f'Mock: Kontext 25 Min vor {anchor_chunk_id}',
            'P_m5': f'Mock: Kontext 5 Min vor {anchor_chunk_id}',
            'W': anchor_chunk_id,
            'F_p5': f'Mock: Kontext 5 Min nach {anchor_chunk_id}',
            'F_p25': f'Mock: Kontext 25 Min nach {anchor_chunk_id}'
        }


# Global Instance (wird beim Backend-Start geladen)
_faiss_instance = None


def get_faiss_query() -> FAISSQuery:
    """
    Singleton Pattern: Stellt sicher dass FAISS nur 1x geladen wird
    
    Returns:
        FAISSQuery Instance
    """
    global _faiss_instance
    if _faiss_instance is None:
        _faiss_instance = FAISSQuery()
    return _faiss_instance

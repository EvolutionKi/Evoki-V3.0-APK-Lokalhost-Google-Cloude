"""
═══════════════════════════════════════════════════════════════════════════
BUCH 7: TEMPLE DATA LAYER — EVOKI V3.0 FAISS VECTOR STORE
═══════════════════════════════════════════════════════════════════════════
Extracted from: EVOKI_V3_METRICS_SPECIFICATION_A_PHYS_V11_AUDITFIX_FINAL7.md
Lines: ~14200-14300 (BUCH 7, Section 2.3)
File: evoki_v3_vectors.faiss
Version: V3.0 FUTURE STATE
═══════════════════════════════════════════════════════════════════════════
ERKENNTNIS aus V2.0:
- VectorRegs_in_Use hatte 6+ separate Ordner → schwer zu managen
- Trajectory-Indizes waren statisch → keine dynamischen Updates
- Metriken waren separat von Vektoren → ineffiziente Suche

V3.0 LÖSUNG:
- EIN FAISS Index mit VIER Namespaces
- Unified Storage mit dynamischen Updates
- Metriken direkt im Vektor-Metadaten
═══════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

try:
    import faiss
    import numpy as np
except ImportError:
    faiss = None
    np = None

@dataclass
class VectorStoreConfig:
    """Configuration for Evoki V3.0 Vector Store"""
    base_path: str
    dimension: int = 384  # all-MiniLM-L6-v2
    index_type: str = "IVF"  # or "Flat" for smaller datasets
    nlist: int = 100  # Number of clusters for IVF
    nprobe: int = 10  # Number of clusters to search


class EvokiV3VectorStore:
    """
    Neuer unifizierter Vector Store für V3.0.
    
    ERKENNTNIS aus V2.0:
    - VectorRegs_in_Use hatte 6+ separate Ordner → schwer zu managen
    - Trajectory-Indizes waren statisch → keine dynamischen Updates
    - Metriken waren separat von Vektoren → ineffiziente Suche
    
    V3.0 LÖSUNG:
    - EIN FAISS Index mit VIER Namespaces
    - Unified Storage mit dynamischen Updates
    - Metriken direkt im Vektor-Metadaten
    """
    
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # ═══════════════════════════════════════════════════════════════
        # NAMESPACE 1: atomic_pairs — Prompt-Paar-Vektoren
        # ═══════════════════════════════════════════════════════════════
        # ERSETZT: VectorRegs_in_Use/01_BRAIN_EVOKI/prompt/
        # VERBESSERUNG: User+AI werden ZUSAMMEN embedded, nicht separat
        
        self.atomic_pairs = {
            'dimension': 384,           # all-MiniLM-L6-v2
            'model': 'all-MiniLM-L6-v2',
            'description': 'Jedes Prompt-Paar (User+AI) als einzelner 384D Vektor',
            'metadata_per_vector': {
                'pair_id': 'UUID',
                'session_id': 'UUID',
                'pair_index': 'int',
                'user_text_snippet': 'first 100 chars',
                'ai_text_snippet': 'first 100 chars',
                # KRITISCHE METRIKEN direkt im Metadaten (User/AI getrennt!)
                'user_m1_A': 'float',
                'user_m151_hazard': 'float',
                'ai_m1_A': 'float',
                'disharmony_score': 'float'
            }
        }
        
        # ═══════════════════════════════════════════════════════════════
        # NAMESPACE 2: context_windows — Dynamische Fenster-Chunks
        # ═══════════════════════════════════════════════════════════════
        # ERSETZT: VectorRegs_in_Use/01_BRAIN_EVOKI/chunk/
        # VERBESSERUNG: Dynamische Fenstergrößen statt nur 25er
        
        self.context_windows = {
            'dimension': 384,
            'window_sizes': [5, 15, 25, 50],  # V2.0 hatte nur 25
            'description': 'Kontext-Fenster verschiedener Größen für Multi-Scale Suche',
            'metadata_per_vector': {
                'window_id': 'UUID',
                'center_pair_id': 'UUID',
                'window_size': 'int',
                'start_pair_index': 'int',
                'end_pair_index': 'int',
                'avg_user_m1_A': 'float',  # Durchschnitt User-Affekt
                'avg_ai_m1_A': 'float',    # Durchschnitt AI-Qualität
                'max_user_m151_hazard': 'float',  # Max User-Hazard im Fenster
                'avg_disharmony': 'float'  # Durchschn. Disharmonie
            }
        }
        
        # ═══════════════════════════════════════════════════════════════
        # NAMESPACE 3: trajectory_wpf — W-P-F Trajectory Vektoren
        # ═══════════════════════════════════════════════════════════════
        # ERSETZT: VectorRegs_in_Use/01_BRAIN_EVOKI/trajectory_*/
        # VERBESSERUNG: In PROMPTS nicht Minuten, dynamische Berechnung
        
        self.trajectory_wpf = {
            'dimension': 384,
            'wpf_offsets': [-25, -5, -2, -1, 0, 1, 2, 5, 25],  # PROMPTS!
            'description': 'W-P-F Trajectory: Vergangenheit + Wirklichkeit + Future',
            'metadata_per_vector': {
                'trajectory_id': 'UUID',
                'anchor_pair_id': 'UUID',
                'offset': 'int',  # -25 bis +25
                'is_prediction': 'bool',  # True für positive Offsets
                'gradient_direction': 'float'  # Trend der Metriken
            }
        }
        
        # ═══════════════════════════════════════════════════════════════
        # NAMESPACE 4: metrics_embeddings — Metriken als Vektoren
        # ═══════════════════════════════════════════════════════════════
        # NEU IN V3.0! Gab es in V2.0 nicht.
        # Die 161 Metriken selbst als durchsuchbarer Vektor-Space
        
        self.metrics_embeddings = {
            'dimension': 322,  # 161 User + 161 AI Metriken!
            'description': 'Alle 161*2 Metriken (User+AI) als Vektor für Metrik-basierte Suche',
            'normalization': 'L2',  # Alle Metriken auf [0,1] normiert
            'metadata_per_vector': {
                'pair_id': 'UUID',
                'dominant_metric': 'str',  # z.B. "m101_T_panic"
                'metric_signature': 'str'  # Cluster-Label
            }
        }
        
        # Initialize indices
        self.indices: Dict[str, Optional[Any]] = {
            'atomic_pairs': None,
            'context_windows': None,
            'trajectory_wpf': None,
            'metrics_embeddings': None
        }
        
        self.metadata: Dict[str, List[Dict[str, Any]]] = {
            'atomic_pairs': [],
            'context_windows': [],
            'trajectory_wpf': [],
            'metrics_embeddings': []
        }
    
    def initialize_indices(self) -> None:
        """Initialize all FAISS indices"""
        if faiss is None:
            raise ImportError("FAISS not installed! Install with: pip install faiss-cpu")
        
        # Initialize each namespace
        for namespace in self.indices.keys():
            dim = self._get_dimension(namespace)
            
            if self.config.index_type == "Flat":
                # Simple flat index (exact search)
                index = faiss.IndexFlatL2(dim)
            elif self.config.index_type == "IVF":
                # IVF index (faster, approximate)
                quantizer = faiss.IndexFlatL2(dim)
                index = faiss.IndexIVFFlat(quantizer, dim, self.config.nlist)
            else:
                raise ValueError(f"Unknown index type: {self.config.index_type}")
            
            self.indices[namespace] = index
    
    def _get_dimension(self, namespace: str) -> int:
        """Get dimension for namespace"""
        if namespace == 'metrics_embeddings':
            return 322  # 161*2
        return 384  # all-MiniLM-L6-v2
    
    def add_vectors(
        self,
        namespace: str,
        vectors: np.ndarray,
        metadata: List[Dict[str, Any]]
    ) -> None:
        """Add vectors to a namespace"""
        if namespace not in self.indices:
            raise ValueError(f"Unknown namespace: {namespace}")
        
        index = self.indices[namespace]
        if index is None:
            raise RuntimeError(f"Index for {namespace} not initialized!")
        
        # Train IVF index if needed
        if isinstance(index, faiss.IndexIVFFlat) and not index.is_trained:
            index.train(vectors)
        
        # Add vectors
        index.add(vectors)
        
        # Store metadata
        self.metadata[namespace].extend(metadata)
    
    def search(
        self,
        namespace: str,
        query_vector: np.ndarray,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[int, float, Dict[str, Any]]]:
        """
        Search in a namespace
        
        Returns:
            List of (index, distance, metadata) tuples
        """
        if namespace not in self.indices:
            raise ValueError(f"Unknown namespace: {namespace}")
        
        index = self.indices[namespace]
        if index is None:
            raise RuntimeError(f"Index for {namespace} not initialized!")
        
        # Set nprobe for IVF
        if isinstance(index, faiss.IndexIVFFlat):
            index.nprobe = self.config.nprobe
        
        # Search
        query_vector = query_vector.reshape(1, -1).astype('float32')
        distances, indices = index.search(query_vector, k)
        
        # Get results with metadata
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.metadata[namespace]):
                meta = self.metadata[namespace][idx]
                
                # Apply filters if provided
                if filters:
                    if not self._matches_filters(meta, filters):
                        continue
                
                results.append((int(idx), float(dist), meta))
        
        return results
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if metadata matches filters"""
        for key, value in filters.items():
            if key not in metadata:
                return False
            if metadata[key] != value:
                return False
        return True
    
    def save(self) -> None:
        """Save all indices and metadata to disk"""
        for namespace, index in self.indices.items():
            if index is not None:
                # Save FAISS index
                index_path = self.base_path / f"{namespace}.index"
                faiss.write_index(index, str(index_path))
                
                # Save metadata
                meta_path = self.base_path / f"{namespace}_metadata.json"
                with open(meta_path, 'w') as f:
                    json.dump(self.metadata[namespace], f)
    
    def load(self) -> None:
        """Load all indices and metadata from disk"""
        for namespace in self.indices.keys():
            index_path = self.base_path / f"{namespace}.index"
            meta_path = self.base_path / f"{namespace}_metadata.json"
            
            if index_path.exists() and meta_path.exists():
                # Load FAISS index
                self.indices[namespace] = faiss.read_index(str(index_path))
                
                # Load metadata
                with open(meta_path, 'r') as f:
                    self.metadata[namespace] = json.load(f)
    
    def get_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all namespaces"""
        stats = {}
        for namespace, index in self.indices.items():
            if index is not None:
                stats[namespace] = {
                    'total_vectors': index.ntotal,
                    'dimension': self._get_dimension(namespace),
                    'index_type': type(index).__name__,
                    'metadata_count': len(self.metadata[namespace])
                }
        return stats


# ═══════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Initialize
    config = VectorStoreConfig(
        base_path="C:/Evoki V3.0 APK-Lokalhost-Google Cloude/backend/data/vectors",
        dimension=384
    )
    
    store = EvokiV3VectorStore(config)
    store.initialize_indices()
    
    # Add vectors (example)
    import numpy as np
    
    # Example: Add 100 prompt pairs
    vectors = np.random.random((100, 384)).astype('float32')
    metadata = [
        {
            'pair_id': f"pair_{i}",
            'session_id': 'session_1',
            'pair_index': i,
            'user_m1_A': 0.7,
            'user_m151_hazard': 0.1,
            'ai_m1_A': 0.8,
            'disharmony_score': 0.15
        }
        for i in range(100)
    ]
    
    store.add_vectors('atomic_pairs', vectors, metadata)
    
    # Search
    query = np.random.random((384,)).astype('float32')
    results = store.search('atomic_pairs', query, k=5)
    
    print("Search results:")
    for idx, dist, meta in results:
        print(f"  Index: {idx}, Distance: {dist:.3f}, Pair: {meta['pair_id']}")
    
    # Save
    store.save()
    
    # Stats
    print("\nStats:")
    for ns, stats in store.get_stats().items():
        print(f"  {ns}: {stats}")

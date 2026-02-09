#!/usr/bin/env python3
"""
EVOKI Contract Registry - Single Source of Truth for 168 Metrics

Loads evoki_fullspectrum168_contract.json and provides programmatic access
to all metric definitions.

This is the CANONICAL source for:
- Metric IDs, names, categories
- Types, ranges, sources
- Name mappings (spec vs engine)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# Project root - go up 3 levels from backend/core/evoki_metrics_v3/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Contract location
CONTRACT_PATH = PROJECT_ROOT / "EVOKI_HARDENING_DATA_PACK_V3" / "evoki_fullspectrum168_contract.json"


@dataclass
class MetricDefinition:
    """Single metric definition from contract"""
    metric_id: int
    category: str
    spec_id_primary: str
    spec_id_secondary: str
    engine_key: str
    engine_type: str
    range_default: str
    range_effective: str
    source: str
    version: str
    name_match: bool
    
    @property
    def has_mismatch(self) -> bool:
        """True if spec name != engine name"""
        return not self.name_match
    
    @property
    def canonical_name(self) -> str:
        """Canonical name (contract primary)"""
        return self.spec_id_primary
    
    @property
    def implementation_name(self) -> str:
        """Name used in engine/storage"""
        return self.engine_key


class ContractRegistry:
    """Registry of all 168 metric definitions"""
    
    def __init__(self, contract_path: Optional[Path] = None):
        self.contract_path = contract_path or CONTRACT_PATH
        self.metrics: List[MetricDefinition] = []
        self.by_id: Dict[int, MetricDefinition] = {}
        self.by_name: Dict[str, MetricDefinition] = {}
        self.by_category: Dict[str, List[MetricDefinition]] = {}
        
        self._load()
    
    def _load(self):
        """Load contract JSON"""
        if not self.contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {self.contract_path}")
        
        with open(self.contract_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Parse items
        for item in data['items']:
            metric = MetricDefinition(
                metric_id=item['metric_id'],
                category=item['category'],
                spec_id_primary=item['spec_id_primary'],
                spec_id_secondary=item.get('spec_id_secondary', ''),
                engine_key=item['engine_key'],
                engine_type=item['engine_type'],
                range_default=item['range_default'],
                range_effective=item['range_effective'],
                source=item.get('source', ''),
                version=item.get('version', ''),
                name_match=item.get('name_match', True)
            )
            
            self.metrics.append(metric)
            self.by_id[metric.metric_id] = metric
            self.by_name[metric.canonical_name] = metric
            self.by_name[metric.engine_key] = metric  # Also index by engine name
            
            # Category index
            if metric.category not in self.by_category:
                self.by_category[metric.category] = []
            self.by_category[metric.category].append(metric)
    
    def get(self, identifier: str | int) -> Optional[MetricDefinition]:
        """Get metric by ID or name"""
        if isinstance(identifier, int):
            return self.by_id.get(identifier)
        return self.by_name.get(identifier)
    
    def get_mismatches(self) -> List[MetricDefinition]:
        """Get all metrics with name mismatches"""
        return [m for m in self.metrics if m.has_mismatch]
    
    def get_by_category(self, category: str) -> List[MetricDefinition]:
        """Get all metrics in category"""
        return self.by_category.get(category, [])
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return sorted(self.by_category.keys())
    
    def get_id_range(self, start: int, end: int) -> List[MetricDefinition]:
        """Get metrics in ID range (inclusive)"""
        return [self.by_id[i] for i in range(start, end + 1) if i in self.by_id]
    
    def summary(self) -> Dict:
        """Get summary statistics"""
        return {
            "total": len(self.metrics),
            "categories": len(self.by_category),
            "mismatches": len(self.get_mismatches()),
            "types": {
                "float": sum(1 for m in self.metrics if m.engine_type == "float"),
                "bool": sum(1 for m in self.metrics if m.engine_type == "bool"),
            }
        }
    
    def validate_implementation(self, implemented_names: List[str]) -> Dict:
        """Validate which metrics are implemented"""
        contract_names = {m.canonical_name for m in self.metrics}
        impl_set = set(implemented_names)
        
        return {
            "total_in_contract": len(contract_names),
            "total_implemented": len(impl_set),
            "missing": sorted(contract_names - impl_set),
            "extra": sorted(impl_set - contract_names),
            "coverage": len(impl_set & contract_names) / len(contract_names) * 100
        }


# Global singleton
_registry: Optional[ContractRegistry] = None


def get_registry() -> ContractRegistry:
    """Get global contract registry (singleton)"""
    global _registry
    if _registry is None:
        _registry = ContractRegistry()
    return _registry


def get_metric(identifier: str | int) -> Optional[MetricDefinition]:
    """Convenience: get metric from global registry"""
    return get_registry().get(identifier)


def get_all_metric_names() -> List[str]:
    """Get all canonical metric names"""
    return [m.canonical_name for m in get_registry().metrics]


def get_all_metric_ids() -> List[int]:
    """Get all metric IDs"""
    return [m.metric_id for m in get_registry().metrics]


# ═══════════════════════════════════════════════════════════════════════════
# TEST / DEMO
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 80)
    print("EVOKI CONTRACT REGISTRY - DEMO")
    print("=" * 80)
    
    registry = get_registry()
    
    # Summary
    stats = registry.summary()
    print(f"\n📊 Summary:")
    print(f"  Total metrics: {stats['total']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Name mismatches: {stats['mismatches']}")
    print(f"  Types: {stats['types']}")
    
    # Show some metrics
    print(f"\n🔍 Sample Metrics (first 10):")
    for m in registry.metrics[:10]:
        mismatch = " ⚠️ MISMATCH" if m.has_mismatch else ""
        print(f"  {m.metric_id:3d}. {m.canonical_name:20s} ({m.category}){mismatch}")
    
    # Show mismatches
    mismatches = registry.get_mismatches()
    print(f"\n⚠️  Name Mismatches ({len(mismatches)}):")
    for m in mismatches[:10]:
        print(f"  {m.metric_id:3d}. Spec: {m.spec_id_primary:20s} → Engine: {m.engine_key}")
    if len(mismatches) > 10:
        print(f"  ... and {len(mismatches) - 10} more")
    
    # Show categories
    print(f"\n📂 Top Categories:")
    cat_counts = {cat: len(metrics) for cat, metrics in registry.by_category.items()}
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {cat:40s} {count:3d}")
    
    # Test lookup
    print(f"\n🔎 Lookup Examples:")
    m1 = registry.get("m1_A")
    if m1:
        print(f"  m1_A: {m1.category}, range={m1.range_effective}")
    
    m19 = registry.get(19)
    if m19:
        print(f"  m19: {m19.canonical_name}, {m19.category}")
    
    print(f"\n{'=' * 80}")
    print("✅ Contract Registry Working!")
    print("=" * 80)

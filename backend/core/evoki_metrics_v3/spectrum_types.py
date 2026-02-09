"""
Spectrum Types — 168 Metrics Structure
"""

from typing import Dict, Any


class FullSpectrum168:
    """Container for all 168 metrics - supports dynamic attribute setting"""
    
    def __init__(self, metrics: Dict[str, float] = None):
        # Use object.__setattr__ to avoid recursion
        object.__setattr__(self, '_metrics', metrics or {})
    
    def __getattr__(self, name: str) -> float:
        """Allow dynamic attribute access"""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        return self._metrics.get(name, 0.0)
    
    def __setattr__(self, name: str, value: Any):
        """Allow dynamic attribute setting"""
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._metrics[name] = value
    
    def __getitem__(self, key: str) -> float:
        return self._metrics.get(key, 0.0)
    
    def __setitem__(self, key: str, value: float):
        self._metrics[key] = value
    
    def to_dict(self) -> Dict[str, float]:
        return self._metrics.copy()

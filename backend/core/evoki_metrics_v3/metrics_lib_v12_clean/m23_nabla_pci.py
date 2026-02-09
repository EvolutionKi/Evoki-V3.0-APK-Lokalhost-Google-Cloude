"""m23_nabla_pci: Gradient PCI
SPEC Formula: ∇PCI = PCI_current - PCI_previous  
Reference: EVOKI_V3_METRICS_SPECIFICATION.md:3287-3297"""
def compute_m23_nabla_pci(pci_current: float, pci_previous: float) -> float:
    return round(pci_current - pci_previous, 4)
__all__ = ['compute_m23_nabla_pci']

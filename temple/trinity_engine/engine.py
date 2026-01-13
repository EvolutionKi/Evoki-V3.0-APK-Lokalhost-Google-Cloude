from .cipher.cipher import Cipher
from .antigravity.antigravity import Antigravity
from .kryos.kryos import Kryos

class TrinityEngine:
    """
    The union of Cipher, Antigravity, and Kryos.
    The primary cognitive driver of EVOKI V3.0.
    """
    def __init__(self):
        self.cipher = Cipher()
        self.antigravity = Antigravity()
        self.kryos = Kryos()

    def pulse(self):
        """ A single cognitive pulse of the resonance engine. """
        return {
            "cipher": self.cipher.validate_triade(),
            "antigravity": self.antigravity.reflect("Genesis Pulse"),
            "kryos": self.kryos.genesis_status
        }

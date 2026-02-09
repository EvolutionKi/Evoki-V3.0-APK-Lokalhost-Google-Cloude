"""
Shared Lexika for Metrics Library
Central definitions for all lexikon-based metrics
"""

from typing import Dict

# ============================================================================
# SAFETY-CRITICAL LEXIKA
# ============================================================================

HAZARD_LEXIKON: Dict[str, float] = {
    "suicide": 0.25, "suizid": 0.25, "umbringen": 0.20, "sterben": 0.15,
    "ritzen": 0.15, "schneiden": 0.10, "verletzen": 0.10,
}

# ==========================================================================================
# TRAUMA LEXIKA
# ============================================================================

PANIC_LEXIKON: Dict[str, float] = {
    "hilfe": 2.0, "panik": 3.0, "angst": 1.5, "todesangst": 3.0,
    "sterben": 2.5, "atemnot": 2.0, "herzrasen": 1.5, "zittern": 1.0,
    "ich kann nicht mehr": 2.5, "sofort": 1.0, "schnell": 0.5,
}

DISSO_LEXIKON: Dict[str, float] = {
    "egal": 1.5, "fühle nichts": 2.5, "unwirklich": 2.0, "wie im traum": 2.0,
    "neben mir": 1.8, "taub": 1.5, "ist mir gleich": 1.5, "was auch immer": 1.2,
}

INTEG_LEXIKON: Dict[str, float] = {
    "verstehe": 1.5, "klar": 1.0, "zusammenhang": 1.5, "gelernt": 1.2,
    "verarbeitet": 2.0, "integriert": 2.0, "verbunden": 1.5,
}

# ============================================================================
# EXISTENTIAL LEXIKA  
# ============================================================================

X_EXIST_LEXIKON: Dict[str, float] = {
    "existiert": 1.0, "ich bin": 0.8, "wirklich": 0.6, "tatsächlich": 0.6,
    "vorhanden": 0.7, "hier": 0.5, "präsent": 0.7, "da sein": 0.6,
}

B_PAST_LEXIKON: Dict[str, float] = {
    "erinnere": 0.9, "damals": 0.8, "früher": 0.7, "gestern": 0.6,
    "vergangen": 0.8, "gewesen": 0.6, "vorher": 0.5, "ehemals": 0.7,
}

# ============================================================================
# AFFECT LEXIKON
# ============================================================================

AFFECT_LEXIKON: Dict[str, float] = {
    "glücklich": 0.15, "freude": 0.12, "liebe": 0.15, "dankbar": 0.10,
    "hoffnung": 0.08, "zufrieden": 0.08, "traurig": -0.10, "wut": -0.12,
    "hass": -0.15, "verzweiflung": -0.15, "schmerz": -0.10, "angst": -0.10,
}


# ============================================================================
# LOADER FUNCTION
# ============================================================================

def load_lexika(path: str = None) -> dict:
    """
    Load lexika from JSON file or return defaults
    
    TODO: Implement JSON loading from evoki_lexika_v3.json
    """
    return {
        'hazard': HAZARD_LEXIKON,
        'panic': PANIC_LEXIKON,
        'disso': DISSO_LEXIKON,
        'integ': INTEG_LEXIKON,
        'x_exist': X_EXIST_LEXIKON,
        'b_past': B_PAST_LEXIKON,
        'affect': AFFECT_LEXIKON,
    }


__all__ = [
    'HAZARD_LEXIKON',
    'PANIC_LEXIKON',
    'DISSO_LEXIKON',
    'INTEG_LEXIKON',
    'X_EXIST_LEXIKON',
    'B_PAST_LEXIKON',
    'AFFECT_LEXIKON',
    'load_lexika',
]

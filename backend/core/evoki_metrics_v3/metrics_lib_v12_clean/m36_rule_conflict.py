"""m36_rule_conflict: Protokoll-Konflikt"""
from typing import List, Dict
from ._helpers import clamp

def compute_m36_rule_conflict(rules: List[Dict] = None) -> float:
    if not rules or len(rules) < 2:
        return 0.0
    actions = [r.get("action", "") for r in rules]
    conflicts = 0
    for i, a1 in enumerate(actions):
        for a2 in actions[i+1:]:
            if a1 and a2 and a1 != a2:
                if ("allow" in a1 and "deny" in a2) or ("deny" in a1 and "allow" in a2):
                    conflicts += 1
    return round(clamp(conflicts / max(1, len(rules)), 0.0, 1.0), 4)

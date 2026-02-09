"""
m148: Knowledge Integration
"""




def compute_m148_knowledge_integration(new_facts: int, total_facts: int) -> float:
    """m148: Knowledge Integration"""
    return round(new_facts / max(1, total_facts), 4)

"""
m163: Räumliche Einbettung
"""




def compute_m163_ctx_loc(location_data: dict = None) -> float:
    """m163: Räumliche Einbettung"""
    if location_data is None:
        return 0.5
    return round(location_data.get("safety_score", 0.5), 4)

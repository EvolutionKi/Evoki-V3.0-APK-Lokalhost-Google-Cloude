"""
m166: Modalität
"""




def compute_m166_modality(input_data: dict = None) -> str:
    """m166: Modalität"""
    if input_data is None:
        return "text"
    modalities = []
    if input_data.get("text"):
        modalities.append("text")
    if input_data.get("audio"):
        modalities.append("voice")
    if input_data.get("image"):
        modalities.append("image")
    if len(modalities) > 1:
        return "multimodal"
    elif modalities:
        return modalities[0]
    else:
        return "text"

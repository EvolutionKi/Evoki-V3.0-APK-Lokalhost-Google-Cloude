"""
m100_emotion_blend: Emotionale Komplexität
"""




def compute_m100_emotion_blend(joy: float, sadness: float, anger: float, fear: float) -> float:
    """m100_emotion_blend: Emotionale Komplexität"""
    emotions = [joy, sadness, anger, fear]
    mean = sum(emotions) / len(emotions)
    variance = sum((e - mean)**2 for e in emotions) / len(emotions)
    return round(min(1.0, variance * 4.0), 4)

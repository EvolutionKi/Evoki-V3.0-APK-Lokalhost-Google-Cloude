"""
m150: Goal Coherence
"""




def compute_m150_goal_coherence(goals_aligned: int, total_goals: int) -> float:
    """m150: Goal Coherence"""
    return round(goals_aligned / max(1, total_goals), 4)

"""
m145: Task Switching
"""




def compute_m145_task_switching(switches: int, total_tasks: int) -> float:
    """m145: Task Switching"""
    return round(switches / max(1, total_tasks), 4)

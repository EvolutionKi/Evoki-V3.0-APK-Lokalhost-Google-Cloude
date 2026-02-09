"""
m165: Plattform
"""




def compute_m165_platform() -> str:
    """m165: Plattform"""
    import platform as plat
    system = plat.system().lower()
    if system == "linux" and "android" in plat.release().lower():
        return "apk"
    elif system in ["windows", "linux", "darwin"]:
        return "pc"
    else:
        return "rover"

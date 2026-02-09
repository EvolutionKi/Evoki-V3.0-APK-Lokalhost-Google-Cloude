"""
Copy script for Monolith files
"""
import shutil
from pathlib import Path

SRC = Path(r"C:\Users\nicom\Downloads\EVOKI_V3_METRICS_SPECIFICATION Entwicklung\V7 Patchpaket V2 + Monolith")
DST = Path(r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3")

files = [
    "a_phys_v11.py",
    "evoki_lexika_v3.py", 
    "metrics_registry.py",
    "evoki_fullspectrum168_contract.json"
]

for f in files:
    src_file = SRC / f
    dst_file = DST / f
    if src_file.exists():
        shutil.copy2(src_file, dst_file)
        print(f"✅ Copied: {f}")
    else:
        print(f"❌ NOT FOUND: {f}")

print("\n✅ DONE!")

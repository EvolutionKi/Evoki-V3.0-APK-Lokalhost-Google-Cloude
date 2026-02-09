import os
import shutil
from pathlib import Path

# Paths
desktop_complete = Path(r"C:\Users\nicom\Desktop\Metriken\metrics_lib_complete")
desktop_final = Path(r"C:\Users\nicom\Desktop\Metriken\evoki_metrics_v3_final")
backend_lib = Path(r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\backend\core\evoki_metrics_v3\metrics_lib")
docs_dest = Path(r"C:\Evoki V3.0 APK-Lokalhost-Google Cloude\docs\specifications\v3.0")

# Ensure destinations exist
backend_lib.mkdir(parents=True, exist_ok=True)
docs_dest.mkdir(parents=True, exist_ok=True)

# 1. Copy Documentation
doc_files = [
    "V11_1_FORMULAS_COMPLETE.md",
    "METRIC_MAPPING_153_TO_25.txt",
    "MATHEMATICAL_SPECIFICATION.md"
]
print("--- Copying Documentation ---")
for doc in doc_files:
    src = desktop_final / doc
    dst = docs_dest / doc
    if src.exists():
        shutil.copy2(src, dst)
        print(f"✅ Copied {doc}")
    else:
        print(f"❌ Missing source doc: {doc}")

# 2. Analyze & Copy Missing Metrics
print("\n--- Analysing Metrics ---")
desktop_metrics = {f.name: f for f in desktop_complete.glob("m*.py")}
backend_metrics = {f.name: f for f in backend_lib.glob("m*.py")}

missing = set(desktop_metrics.keys()) - set(backend_metrics.keys())
print(f"Found {len(missing)} missing metrics in Backend.")

for name in sorted(missing):
    src = desktop_metrics[name]
    dst = backend_lib / name
    shutil.copy2(src, dst)
    print(f"➕ Added {name}")

# 3. Check for specific m162 conflict
print("\n--- Conflict Check (m162) ---")
m162_files_desktop = list(desktop_complete.glob("m162*.py"))
m162_files_backend = list(backend_lib.glob("m162*.py"))

print("Desktop m162*:", [f.name for f in m162_files_desktop])
print("Backend m162*:", [f.name for f in m162_files_backend])

# 4. Total Count
final_count = len(list(backend_lib.glob("m*.py")))
print(f"\n✅ Final Metric Count in Backend: {final_count}")

import subprocess
import sys

print("=" * 60)
print("   WAREHOUSE INVENTORY & ROBOT VISION SYSTEM")
print("=" * 60)

print("\nStarting Professional Dashboard...")
print("Opening Streamlit application...\n")

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    "dashboard/app.py"
])

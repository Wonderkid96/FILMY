#!/usr/bin/env python3
import subprocess
import sys

print("🎬 Launching FILMY - Original Edition")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app_enhanced.py", "--server.port", "8501"])

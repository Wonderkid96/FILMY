#!/usr/bin/env python3
import subprocess
import sys

print("💕 Launching FILMY - Couples Edition")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app_couples.py", "--server.port", "8502"])

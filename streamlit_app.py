#!/usr/bin/env python3
"""
🎬 FILMY - Direct App Launcher
Simple direct import of the consolidated movie discovery app
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the main app
from apps.filmy_app import main

if __name__ == "__main__":
    main() 
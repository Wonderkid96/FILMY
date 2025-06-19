#!/usr/bin/env python3
"""
FILMY - Couples Edition Launcher
Launches the advanced couples tracking experience
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the couples app
if __name__ == "__main__":
    from apps.app_couples import main
    main() 
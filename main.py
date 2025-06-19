#!/usr/bin/env python3
"""
🎬 FILMY - The Ultimate Movie & TV Discovery Tool
Single App for Couples Movie Nights

Created by Toby the fuck lord and his amazing girlfriend
Built for discovering your next perfect movie night together!
"""

import sys
import os

# Add src to path for imports
if __name__ == "__main__":
    # Only add path when running as main script
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
else:
    # When imported, use current directory
    sys.path.insert(0, os.path.join(os.getcwd(), "src"))


def main():
    """Main application launcher"""

    # Import and run the main app directly
    from apps.filmy_app import main as filmy_main

    filmy_main()


if __name__ == "__main__":
    main()

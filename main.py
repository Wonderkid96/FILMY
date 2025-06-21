#!/usr/bin/env python3
"""
🎬 FILMY - The Ultimate Movie & TV Discovery Tool
Modular Architecture for Better Maintainability

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
    """Main application launcher - now using modular structure"""

    try:
        # Import and run the new modular app
        from apps.filmy_app_modular import main as modular_main
        modular_main()
    except ImportError as e:
        import streamlit as st
        st.error(f"Import error: {e}")
        st.error("Please check that all files are in the correct location.")
        
        # Fallback to old app if modular fails
        try:
            st.warning("Falling back to legacy app...")
            from apps.filmy_app_legacy import main as legacy_main
            legacy_main()
        except ImportError:
            st.error("Both modular and legacy apps failed to load!")


if __name__ == "__main__":
    main()
 
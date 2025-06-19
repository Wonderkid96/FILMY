#!/usr/bin/env python3
"""
🎬 FILMY Launch Script
Quick launcher for the ultimate movie discovery tool
"""

import subprocess
import sys
import os


def main():
    """Launch FILMY with couples mode as default"""
    print("🎬 FILMY - The Ultimate Movie Discovery Tool")
    print("💕 Launching Couples Edition...")
    print("🚀 Starting Streamlit server...")
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    try:
        # Launch Streamlit with main.py
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Thanks for using FILMY! See you next movie night!")
    except Exception as e:
        print(f"❌ Error launching FILMY: {e}")
        print("💡 Try running: streamlit run main.py")


if __name__ == "__main__":
    main() 
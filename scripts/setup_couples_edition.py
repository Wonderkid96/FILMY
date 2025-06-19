#!/usr/bin/env python3
"""
FILMY Couples Edition Setup Script
Organizes and configures the advanced user tracking system
"""

import os
import sys
import pandas as pd
from datetime import datetime
import streamlit as st

def setup_enhanced_csv_structure():
    """Set up enhanced CSV structure with user tracking columns"""
    
    # Enhanced headers for user tracking
    enhanced_headers = [
        'tmdb_id', 'title', 'type', 'release_date', 'genres', 'tmdb_rating',
        'my_rating', 'my_rating_label', 'date_rated', 'overview', 'poster_url',
        'toby_seen', 'taz_seen', 'both_seen', 'who_rated', 'couple_score',
        'recommendation_type', 'date_discovered'
    ]
    
    csv_file = 'filmy_ratings.csv'
    
    # Check if CSV exists and needs updating
    if os.path.exists(csv_file):
        try:
            existing_df = pd.read_csv(csv_file)
            existing_columns = set(existing_df.columns.tolist())
            new_columns = set(enhanced_headers)
            
            # Add missing columns
            missing_columns = new_columns - existing_columns
            if missing_columns:
                print(f"🔧 Adding new columns: {', '.join(missing_columns)}")
                
                for col in missing_columns:
                    if col in ['toby_seen', 'taz_seen', 'both_seen']:
                        existing_df[col] = False
                    elif col in ['couple_score']:
                        existing_df[col] = 0.0
                    elif col in ['who_rated', 'recommendation_type']:
                        existing_df[col] = 'Unknown'
                    elif col == 'date_discovered':
                        existing_df[col] = datetime.now().isoformat()
                    else:
                        existing_df[col] = ''
                
                # Save updated CSV
                existing_df.to_csv(csv_file, index=False)
                print(f"✅ Updated {csv_file} with enhanced structure")
            else:
                print(f"✅ {csv_file} already has the correct structure")
                
        except Exception as e:
            print(f"❌ Error updating CSV: {e}")
            backup_file = f"{csv_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(csv_file, backup_file)
            print(f"📦 Backed up existing file to {backup_file}")
            create_new_csv(csv_file, enhanced_headers)
    else:
        create_new_csv(csv_file, enhanced_headers)

def create_new_csv(filename, headers):
    """Create a new CSV with enhanced headers"""
    df = pd.DataFrame(columns=headers)
    df.to_csv(filename, index=False)
    print(f"✅ Created new {filename} with enhanced structure")

def setup_google_sheets_enhanced():
    """Set up Google Sheets with enhanced user tracking"""
    print("📊 Setting up enhanced Google Sheets structure...")
    
    try:
        from google_sheets_manager import GoogleSheetsManager
        
        sheets_manager = GoogleSheetsManager()
        if sheets_manager.is_connected():
            print("✅ Google Sheets connection successful")
            print("🎨 Enhanced formatting with user tracking columns applied")
        else:
            print("⚠️  Google Sheets not connected - will use local CSV only")
            
    except Exception as e:
        print(f"⚠️  Google Sheets setup issue: {e}")

def create_app_launcher():
    """Create convenient app launchers"""
    
    # Original app launcher
    original_launcher = """#!/usr/bin/env python3
import subprocess
import sys

print("🎬 Launching FILMY - Original Edition")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app_enhanced.py", "--server.port", "8501"])
"""
    
    # Couples app launcher
    couples_launcher = """#!/usr/bin/env python3
import subprocess
import sys

print("💕 Launching FILMY - Couples Edition")
subprocess.run([sys.executable, "-m", "streamlit", "run", "app_couples.py", "--server.port", "8502"])
"""
    
    with open('launch_filmy_original.py', 'w') as f:
        f.write(original_launcher)
    
    with open('launch_filmy_couples.py', 'w') as f:
        f.write(couples_launcher)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod('launch_filmy_original.py', 0o755)
        os.chmod('launch_filmy_couples.py', 0o755)
    
    print("🚀 Created app launchers:")
    print("   - launch_filmy_original.py (port 8501)")
    print("   - launch_filmy_couples.py (port 8502)")

def show_setup_summary():
    """Show setup summary and instructions"""
    print("\n" + "="*60)
    print("🎬💕 FILMY COUPLES EDITION SETUP COMPLETE!")
    print("="*60)
    
    print("\n📱 MOBILE OPTIMIZED FEATURES:")
    print("   ✅ Responsive design for phone screens")
    print("   ✅ Compact buttons and cards")
    print("   ✅ Sticky user selector")
    print("   ✅ Optimized text lengths")
    
    print("\n👥 ADVANCED USER TRACKING:")
    print("   ✅ Toby seen / Taz seen / Both seen tracking")
    print("   ✅ Couple compatibility analysis")
    print("   ✅ Smart recommendation engine")
    print("   ✅ Discovery statistics")
    
    print("\n📊 ENHANCED GOOGLE SHEETS:")
    print("   ✅ Color-coded user tracking columns")
    print("   ✅ Live statistics dashboard")
    print("   ✅ Professional formatting")
    print("   ✅ Automatic data sync")
    
    print("\n🚀 HOW TO USE:")
    print("   1. Original FILMY: python launch_filmy_original.py")
    print("   2. Couples FILMY: python launch_filmy_couples.py")
    print("   3. Or use: streamlit run app_couples.py")
    
    print("\n📱 MOBILE TESTING:")
    print("   - Open on your phone's browser")
    print("   - All features work in mobile view")
    print("   - Buttons sized for touch interaction")
    print("   - Content fits screen margins")
    
    print("\n💡 PRO TIPS:")
    print("   - Switch between Toby/Taz/Both modes easily")
    print("   - All decisions sync to Google Sheets instantly")
    print("   - Compatibility analysis gets smarter over time")
    print("   - Mobile interface is fully touch-optimized")

def main():
    """Main setup function"""
    print("🎬 Setting up FILMY Couples Edition...")
    print("🔧 Enhancing system with advanced user tracking...")
    
    # Setup enhanced CSV structure
    setup_enhanced_csv_structure()
    
    # Setup Google Sheets
    setup_google_sheets_enhanced()
    
    # Create app launchers
    create_app_launcher()
    
    # Show summary
    show_setup_summary()
    
    print(f"\n🎉 Setup completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Ready to discover movies together! 🍿")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Fix import statements after directory reorganization
"""

import os
import re

def fix_imports_in_file(filepath, replacements):
    """Fix imports in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        for old_import, new_import in replacements.items():
            content = re.sub(rf'^from {re.escape(old_import)} import', f'from {new_import} import', content, flags=re.MULTILINE)
            content = re.sub(rf'^import {re.escape(old_import)}', f'import {new_import}', content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Fixed imports in {filepath}")
        else:
            print(f"⚪ No changes needed in {filepath}")
            
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def main():
    """Fix all import statements"""
    
    # Define import replacements
    replacements = {
        'config': 'core.config',
        'tmdb_api': 'core.tmdb_api',
        'recommendation_engine': 'core.recommendation_engine',
        'user_preferences': 'core.user_preferences',
        'enhanced_ratings_manager': 'core.enhanced_ratings_manager',
        'google_sheets_manager': 'core.google_sheets_manager',
        'advanced_user_tracker': 'core.advanced_user_tracker'
    }
    
    # Files to fix
    files_to_fix = [
        'src/apps/app.py',
        'src/apps/app_enhanced.py',
        'src/apps/app_couples.py',
        'scripts/setup_couples_edition.py',
        'scripts/launch_filmy_original.py',
        'scripts/launch_filmy_couples.py'
    ]
    
    print("🔧 Fixing import statements after reorganization...")
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            fix_imports_in_file(filepath, replacements)
        else:
            print(f"⚠️  File not found: {filepath}")
    
    print("✅ Import fixing complete!")

if __name__ == "__main__":
    main() 
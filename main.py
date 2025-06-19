#!/usr/bin/env python3
"""
🎬 FILMY - The Ultimate Movie & TV Discovery Tool for Couples 💕
Main Application Entry Point

Created by Toby the fuck lord and his amazing girlfriend Taz
Built for discovering your next perfect movie night together!
"""

import sys
import os
import streamlit as st

# Add src to path for imports
if __name__ == "__main__":
    # Only add path when running as main script
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
else:
    # When imported, use current directory
    sys.path.insert(0, os.path.join(os.getcwd(), 'src'))


def main():
    """Main application launcher with mode selection"""
    
    # Check if we're running in Streamlit
    if 'streamlit' in sys.modules:
        # We're in Streamlit, show the app selector
        st.set_page_config(
            page_title="🎬 FILMY - Movie Discovery",
            page_icon="🎬",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Beautiful header styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, 
                                         #96CEB4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2rem;
            animation: gradient 3s ease-in-out infinite;
        }
        
        .mode-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }
        
        .couples-card {
            background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        }
        
        .original-card {
            background: linear-gradient(135deg, #45B7D1 0%, #96CEB4 100%);
        }
        
        .stButton > button {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 10px;
            padding: 0.8rem 2rem;
            font-size: 1.1rem;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
            transform: translateY(-2px);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main header
        st.markdown('<h1 class="main-header">🎬 FILMY</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">The Ultimate Movie & TV Discovery Tool</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Mode selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="mode-card couples-card">', unsafe_allow_html=True)
            st.markdown("### 💕 Couples Edition")
            st.markdown("**Perfect for movie nights together!**")
            st.markdown("✨ Advanced user tracking for both partners")
            st.markdown("📊 Compatibility analysis & smart recommendations")
            st.markdown("🎯 'Both seen' tracking for shared discoveries")
            st.markdown("📱 Mobile-optimized for couch browsing")
            
            if st.button("🚀 Launch Couples Mode", key="couples_mode", help="Start your couples movie discovery journey!"):
                # Launch couples app
                from apps.app_couples import main as couples_main
                couples_main()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="mode-card original-card">', unsafe_allow_html=True)
            st.markdown("### 🎬 Original FILMY")
            st.markdown("**Classic single-user experience**")
            st.markdown("🔍 Discover movies & TV shows")
            st.markdown("⭐ Rate and track your favorites")
            st.markdown("📝 Personal recommendations")
            st.markdown("☁️ Google Sheets integration")
            
            if st.button("🎯 Launch Original Mode", key="original_mode", help="Classic FILMY experience"):
                # Launch original app
                from apps.app_enhanced import main as original_main
                original_main()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer with some love
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-style: italic;">
        Built with ❤️ for Toby & Taz's epic movie nights<br>
        <small>Powered by TMDB API • Streamlit • Pure fucking determination</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats if available
        try:
            from core.advanced_user_tracker import AdvancedUserTracker
            tracker = AdvancedUserTracker()
            stats = tracker.get_discovery_stats()
            
            if stats and stats.get('total_discovered', 0) > 0:
                st.markdown("### 📈 Quick Stats")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Movies Discovered", stats.get('total_discovered', 0))
                with col2:
                    st.metric("Toby's Picks", stats.get('toby_discoveries', 0))
                with col3:
                    st.metric("Taz's Picks", stats.get('taz_discoveries', 0))
        except Exception:
            pass  # No worries if stats aren't available yet
    
    else:
        # Command line mode - default to couples
        print("🎬 FILMY - Launching Couples Edition...")
        print("💕 Perfect for movie nights together!")
        
        # Import and run couples app directly
        from apps.app_couples import main as couples_main
        couples_main()


if __name__ == "__main__":
    main() 
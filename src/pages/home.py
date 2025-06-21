"""
Home Page - Main swipe interface
Clean, focused implementation using modular components
"""

import streamlit as st
from typing import Dict, List
from components.cards import render_page_header, render_stats_card
from utils.helpers import get_user_stats, log_user_action
from apps.swipe_interface import create_swipe_page
from core.smart_swipe_manager import SmartSwipeManager


def show_home_page():
    """
    Main home page with swipe interface
    Optimized for performance and user experience
    """
    # Load page header
    render_page_header(
        "🎬 FILMY", 
        "Discover your next perfect movie night"
    )
    
    # Initialize smart swipe manager if not exists
    if 'smart_swipe_manager' not in st.session_state:
        st.session_state.smart_swipe_manager = SmartSwipeManager(
            st.session_state.ratings_manager
        )
    
    # Log page view
    log_user_action("home_page_view")
    
    # Quick stats row
    show_quick_stats()
    
    # Main swipe interface
    st.markdown("---")
    
    try:
        # Use the enhanced swipe interface
        create_swipe_page()
        
    except Exception as e:
        st.error(f"Swipe interface error: {e}")
        
        # Fallback to simple discovery
        st.markdown("**Fallback: Simple Discovery**")
        show_fallback_discovery()


def show_quick_stats():
    """Show quick user statistics"""
    stats = get_user_stats()
    
    if not stats:
        # New user welcome
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                margin: 1rem 0;
            ">
                <h3>👋 Welcome to FILMY!</h3>
                <p>Start swiping to discover amazing movies and TV shows tailored just for you.</p>
                <p><strong>Swipe right</strong> for content you want to see, <strong>left</strong> for content you don't.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return
    
    # Stats for existing users
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stats_card(
            "Total Ratings", 
            str(stats.get('total_ratings', 0)), 
            "⭐"
        )
    
    with col2:
        render_stats_card(
            "Perfect Picks", 
            str(stats.get('perfect_picks', 0)), 
            "🌟"
        )
    
    with col3:
        render_stats_card(
            "Watchlist", 
            str(stats.get('watchlist_items', 0)), 
            "📋"
        )
    
    with col4:
        # Show top genre or avg rating
        top_genres = stats.get('top_genres', [])
        if top_genres:
            render_stats_card(
                "Favorite Genre", 
                top_genres[0], 
                "🎭"
            )
        else:
            avg_rating = stats.get('avg_rating', 0)
            render_stats_card(
                "Avg Rating", 
                f"{avg_rating:.1f}/4" if avg_rating > 0 else "N/A", 
                "📊"
            )


def show_fallback_discovery():
    """Simple fallback discovery interface"""
    if 'ratings_manager' not in st.session_state:
        st.error("Ratings manager not initialized")
        return
    
    # Get some basic recommendations
    try:
        recommendations = st.session_state.ratings_manager.get_recommendations(limit=5)
        
        if not recommendations:
            st.info("🎬 No recommendations available. Try rating some content first!")
            return
        
        # Show first recommendation
        current_rec = recommendations[0]
        
        # Simple card display
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if current_rec.get('poster_path'):
                poster_url = f"https://image.tmdb.org/t/p/w500{current_rec['poster_path']}"
                st.image(poster_url, width=200)
            else:
                st.markdown("🎬", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{current_rec['title']}**")
            st.markdown(f"⭐ {current_rec.get('vote_average', 'N/A')}/10")
            st.markdown(f"📅 {current_rec.get('release_date', 'N/A')[:4]}")
            
            overview = current_rec.get('overview', 'No description available.')
            if len(overview) > 200:
                overview = overview[:200] + "..."
            st.markdown(overview)
        
        # Simple rating buttons
        st.markdown("**Rate this content:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("😤 Hate", key="fallback_hate"):
                rate_fallback_content(current_rec, 1, recommendations)
        
        with col2:
            if st.button("🤷 OK", key="fallback_ok"):
                rate_fallback_content(current_rec, 2, recommendations)
        
        with col3:
            if st.button("👍 Good", key="fallback_good"):
                rate_fallback_content(current_rec, 3, recommendations)
        
        with col4:
            if st.button("🌟 Perfect", key="fallback_perfect"):
                rate_fallback_content(current_rec, 4, recommendations)
        
        # Skip button
        if st.button("⏭️ Skip", key="fallback_skip"):
            recommendations.pop(0)
            st.rerun()
            
    except Exception as e:
        st.error(f"Failed to load recommendations: {e}")


def rate_fallback_content(item: Dict, rating: int, recommendations: List[Dict]):
    """Rate content in fallback mode"""
    success = st.session_state.ratings_manager.add_rating(
        tmdb_id=item['id'],
        title=item['title'],
        content_type=item['type'],
        rating=rating,
        item_data=item
    )
    
    if success:
        rating_labels = {1: "Hate", 2: "OK", 3: "Good", 4: "Perfect"}
        st.success(f"✅ Rated as {rating_labels[rating]}!")
        
        # Remove from recommendations and refresh
        recommendations.pop(0)
        st.rerun()
    else:
        st.error("Failed to save rating") 
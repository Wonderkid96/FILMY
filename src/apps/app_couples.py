import streamlit as st
import pandas as pd
import time
from typing import Dict, List, Optional
from datetime import datetime

from core.config import (
    APP_TITLE, APP_ICON, RATING_LABELS, RATING_COLORS, 
    GENRE_ICONS, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL
)
from core.tmdb_api import TMDBApi
from core.enhanced_ratings_manager import EnhancedRatingsManager
from core.advanced_user_tracker import AdvancedUserTracker

# Page configuration
st.set_page_config(
    page_title=f"{APP_TITLE} - Couples Edition",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="auto"
)

# Mobile-optimized CSS
st.markdown("""
<style>
/* Mobile responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 0.5rem;
        padding-right: 0.5rem;
        max-width: 100%;
    }
    
    .stColumns > div {
        padding: 0.2rem;
    }
    
    .stButton > button {
        width: 100%;
        font-size: 0.85rem;
        padding: 0.4rem;
        margin: 0.1rem 0;
    }
    
    [data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 0.4rem;
        border-radius: 0.4rem;
        margin: 0.2rem 0;
    }
    
    .movie-card {
        padding: 0.5rem;
        margin: 0.3rem 0;
    }
    
    .user-selector {
        position: sticky;
        top: 0;
        z-index: 100;
        background: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
}

/* Enhanced visual styling */
.main-header {
    font-size: 2.2rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.couple-stats {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.compatibility-score {
    font-size: 2rem;
    font-weight: bold;
    text-align: center;
    margin: 0.5rem 0;
}

.user-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-weight: bold;
    margin: 0.2rem;
}

.toby-badge {
    background: linear-gradient(45deg, #FF6B6B, #FF8E8E);
    color: white;
}

.taz-badge {
    background: linear-gradient(45deg, #4ECDC4, #6FDDDD);
    color: white;
}

.both-badge {
    background: linear-gradient(45deg, #FFD93D, #FF8E8E);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tmdb' not in st.session_state:
    st.session_state.tmdb = TMDBApi()
if 'user_tracker' not in st.session_state:
    st.session_state.user_tracker = AdvancedUserTracker()
if 'current_user' not in st.session_state:
    st.session_state.current_user = 'Both'

def show_user_selector():
    """Show user selection interface"""
    st.markdown('<div class="user-selector">', unsafe_allow_html=True)
    st.markdown("### 👥 Who's using FILMY right now?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎬 Toby", key="select_toby", help="Toby's solo session"):
            st.session_state.current_user = 'Toby'
            st.rerun()
    
    with col2:
        if st.button("💫 Taz", key="select_taz", help="Taz's solo session"):
            st.session_state.current_user = 'Taz'
            st.rerun()
    
    with col3:
        if st.button("💕 Both", key="select_both", help="Couple's session"):
            st.session_state.current_user = 'Both'
            st.rerun()
    
    # Show current user
    current_user = st.session_state.current_user
    if current_user == 'Toby':
        st.markdown(f'<div class="user-badge toby-badge">🎬 Currently: Toby</div>', unsafe_allow_html=True)
    elif current_user == 'Taz':
        st.markdown(f'<div class="user-badge taz-badge">💫 Currently: Taz</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="user-badge both-badge">💕 Currently: Both</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

def show_couple_compatibility():
    """Show couple compatibility analysis"""
    compatibility = st.session_state.user_tracker.get_couple_compatibility_analysis()
    
    if compatibility['compatibility_score'] > 0:
        st.markdown('<div class="couple-stats">', unsafe_allow_html=True)
        st.markdown("### 💕 Couple Compatibility Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f'<div class="compatibility-score">{compatibility["compatibility_score"]}%</div>', unsafe_allow_html=True)
            st.markdown("**Compatibility**")
        
        with col2:
            st.metric("Joint Ratings", compatibility.get('total_joint_ratings', 0))
        
        with col3:
            st.metric("Perfect Agreements", compatibility.get('perfect_agreements', 0))
        
        st.markdown(f"**Analysis:** {compatibility['recommendation']}")
        st.markdown('</div>', unsafe_allow_html=True)

def show_discovery_stats():
    """Show discovery statistics"""
    stats = st.session_state.user_tracker.get_discovery_stats()
    
    if stats:
        st.markdown("### 📊 Discovery Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Discovered", stats['total_discovered'])
        
        with col2:
            st.metric("Toby's Discoveries", stats['toby_discoveries'])
        
        with col3:
            st.metric("Taz's Discoveries", stats['taz_discoveries'])
        
        with col4:
            st.metric("Joint Discoveries", stats['joint_discoveries'])
        
        sync_rate = stats.get('discovery_sync_rate', 0)
        if sync_rate > 75:
            sync_emoji = "🔥"
        elif sync_rate > 50:
            sync_emoji = "👍"
        else:
            sync_emoji = "🤔"
        
        st.info(f"{sync_emoji} **Discovery Sync Rate:** {sync_rate}% - You're discovering content together!")

def display_enhanced_content_card(item: Dict, show_seen_options: bool = True):
    """Display enhanced content card with user tracking"""
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if item['poster_path']:
            st.image(item['poster_path'], width=120)
        else:
            st.info("No poster")
    
    with col2:
        st.markdown(f"### {item['title']}")
        
        # Show viewing status
        existing_entry = st.session_state.user_tracker._get_existing_entry(item['id'], item['type'])
        if existing_entry:
            viewers = []
            if existing_entry.get('toby_seen'):
                viewers.append('<span class="user-badge toby-badge">Toby</span>')
            if existing_entry.get('taz_seen'):
                viewers.append('<span class="user-badge taz-badge">Taz</span>')
            
            if viewers:
                st.markdown(f"**Seen by:** {' '.join(viewers)}", unsafe_allow_html=True)
        
        # Rating and basic info
        col_rating, col_year, col_type = st.columns(3)
        with col_rating:
            rating = item.get('vote_average', 0)
            if rating >= 8:
                color = "🟢"
            elif rating >= 7:
                color = "🟡"
            elif rating >= 6:
                color = "🟠"
            else:
                color = "🔴"
            st.markdown(f"{color} **{rating:.1f}/10**")
        
        with col_year:
            year = item.get('release_date', '')[:4] if item.get('release_date') else 'N/A'
            st.markdown(f"📅 **{year}**")
        
        with col_type:
            content_type = "🎬 Movie" if item['type'] == 'movie' else "📺 TV Show"
            st.markdown(f"{content_type}")
        
        # Genres
        if item.get('genres'):
            genres_text = " ".join([f"`{genre}`" for genre in item['genres'][:3]])
            st.markdown(f"**Genres:** {genres_text}")
        
        # Overview (mobile-optimized)
        overview = item.get('overview', 'No overview available')
        if len(overview) > 200:  # Shorter for mobile
            overview = overview[:200] + "..."
        st.markdown(f"**Plot:** {overview}")
        
        # Enhanced interaction buttons
        if show_seen_options:
            st.markdown("**Have you seen this?**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"👀 {st.session_state.current_user} Seen", key=f"seen_{item['id']}_{item['type']}"):
                    success = st.session_state.user_tracker.track_viewing_status(
                        item['id'], item['title'], item['type'], item, st.session_state.current_user
                    )
                    if success:
                        st.success(f"✅ Marked as seen by {st.session_state.current_user}!")
                        time.sleep(1)
                        st.rerun()
            
            with col2:
                if st.button("📋 Add to Watchlist", key=f"watchlist_{item['id']}_{item['type']}"):
                    success = st.session_state.user_tracker.ratings_manager.add_rating(
                        item['id'], item['title'], item['type'], 0, item
                    )
                    if success:
                        st.success("✅ Added to watchlist!")
                        time.sleep(1)
                        st.rerun()
            
            with col3:
                if st.button("🚫 Not Interested", key=f"skip_{item['id']}_{item['type']}"):
                    success = st.session_state.user_tracker.ratings_manager.add_rating(
                        item['id'], item['title'], item['type'], -1, item
                    )
                    if success:
                        st.success("✅ Marked as not interested!")
                        time.sleep(1)
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_smart_recommendations():
    """Show intelligent couple recommendations"""
    st.markdown("### 🎯 Smart Couple Recommendations")
    
    # Get recommendations based on compatibility
    recommendations = st.session_state.user_tracker.get_smart_couple_recommendations()
    
    if not recommendations:
        # Fallback to regular recommendations
        try:
            movies = st.session_state.tmdb.get_popular_movies(page=1)
            tv_shows = st.session_state.tmdb.get_popular_tv_shows(page=1)
            
            all_content = []
            
            # Add movies
            for movie in movies.get('results', [])[:5]:
                movie_data = {
                    'id': movie['id'],
                    'title': movie['title'],
                    'type': 'movie',
                    'poster_path': f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
                    'overview': movie.get('overview', ''),
                    'vote_average': movie.get('vote_average', 0),
                    'release_date': movie.get('release_date', ''),
                    'genres': []
                }
                all_content.append(movie_data)
            
            # Add TV shows
            for show in tv_shows.get('results', [])[:5]:
                show_data = {
                    'id': show['id'],
                    'title': show['name'],
                    'type': 'tv',
                    'poster_path': f"{TMDB_IMAGE_BASE_URL}{show['poster_path']}" if show.get('poster_path') else None,
                    'overview': show.get('overview', ''),
                    'vote_average': show.get('vote_average', 0),
                    'release_date': show.get('first_air_date', ''),
                    'genres': []
                }
                all_content.append(show_data)
            
            # Filter out already seen/rated content
            filtered_content = []
            for item in all_content:
                existing = st.session_state.user_tracker._get_existing_entry(item['id'], item['type'])
                if not existing or existing.get('my_rating', 0) == 0:
                    filtered_content.append(item)
            
            # Display recommendations
            for item in filtered_content[:8]:
                display_enhanced_content_card(item)
                st.markdown("---")
        
        except Exception as e:
            st.error(f"Error loading recommendations: {e}")

def show_couples_dashboard():
    """Main couples dashboard"""
    st.markdown('<h1 class="main-header">🎬💕 FILMY Couples Edition</h1>', unsafe_allow_html=True)
    
    # User selector
    show_user_selector()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Smart Recommendations", 
        "📊 Compatibility Analysis", 
        "🔍 Discover Together", 
        "📋 Our Watchlist"
    ])
    
    with tab1:
        show_smart_recommendations()
    
    with tab2:
        show_couple_compatibility()
        show_discovery_stats()
    
    with tab3:
        st.markdown("### 🔍 Discover New Content Together")
        st.info("🚧 Coming soon: Collaborative discovery features!")
    
    with tab4:
        st.markdown("### 📋 Shared Watchlist")
        st.info("🚧 Coming soon: Shared watchlist management!")

def main():
    """Main application entry point"""
    try:
        show_couples_dashboard()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please refresh the page and try again.")

if __name__ == "__main__":
    main() 
"""
UI Components for FILMY app
Reusable components to reduce code duplication
"""

import streamlit as st
from typing import Dict, Optional
from core.config import TMDB_IMAGE_BASE_URL, RATING_LABELS


def render_poster(url: str, width: int = 80, fallback: str = "🎬") -> None:
    """Render movie poster with fallback"""
    if url:
        poster_url = f"{TMDB_IMAGE_BASE_URL}{url}"
        st.image(poster_url, width=width)
    else:
        st.markdown(
            f"""
            <div style="
                width: {width}px; 
                height: {int(width * 1.5)}px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                display: flex; 
                align-items: center; 
                justify-content: center; 
                font-size: 2rem; 
                color: white;
                border-radius: 8px;
            ">
                {fallback}
            </div>
            """,
            unsafe_allow_html=True
        )


def truncate_overview(overview: str, max_length: int = 150) -> str:
    """Truncate overview text with ellipsis"""
    if len(overview) <= max_length:
        return overview
    return overview[:max_length].rsplit(' ', 1)[0] + "..."


def get_rating_color(rating: float) -> str:
    """Get color based on TMDB rating"""
    if rating >= 8.0:
        return "#4CAF50"  # Green
    elif rating >= 7.0:
        return "#8BC34A"  # Light green
    elif rating >= 6.0:
        return "#FFC107"  # Amber
    elif rating >= 5.0:
        return "#FF9800"  # Orange
    else:
        return "#F44336"  # Red


def display_content_card(
    item: Dict, 
    show_actions: bool = True, 
    show_rec_reason: bool = False,
    card_key: str = None
) -> None:
    """
    Display a content card with poster, details, and optional rating actions
    
    Args:
        item: Movie/TV data dictionary
        show_actions: Whether to show rating buttons
        show_rec_reason: Whether to show recommendation reason
        card_key: Unique key for the card (for button disambiguation)
    """
    # Generate unique key if not provided
    if not card_key:
        card_key = f"{item.get('id', 'unknown')}_{item.get('type', 'content')}"
    
    # Container with custom CSS class based on rating
    rating_class = get_card_css_class(item.get('my_rating'))
    
    with st.container():
        st.markdown(f'<div class="movie-card {rating_class}">', unsafe_allow_html=True)
        
        # Create columns for poster and content
        col1, col2 = st.columns([1, 3])
        
        with col1:
            render_poster(item.get('poster_path'), width=80)
        
        with col2:
            # Title with year
            title = item.get('title', 'Unknown Title')
            year = item.get('release_date', '')[:4] if item.get('release_date') else 'N/A'
            st.markdown(f"**{title}** ({year})")
            
            # Rating and type
            tmdb_rating = item.get('vote_average', 0)
            content_type = "Movie" if item.get('type') == 'movie' else "TV Show"
            rating_color = get_rating_color(tmdb_rating)
            
            st.markdown(
                f"""
                <div style="display: flex; gap: 15px; margin: 5px 0;">
                    <span style="color: {rating_color};">⭐ {tmdb_rating:.1f}/10</span>
                    <span style="color: #666;">📺 {content_type}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Genres
            genres = item.get('genres', [])
            if genres:
                if isinstance(genres, list):
                    genres_text = ", ".join(genres[:3])  # Show max 3 genres
                else:
                    genres_text = str(genres)
                st.markdown(f"*{genres_text}*")
            
            # Recommendation reason (if applicable)
            if show_rec_reason and item.get('rec_reason'):
                match_score = int(item.get('final_score', 0.5) * 100)
                st.markdown(
                    f"""
                    <div class="rec-reason">
                        🎯 {item['rec_reason']} ({match_score}% match)
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Overview
            overview = item.get('overview', 'No description available.')
            st.markdown(truncate_overview(overview))
            
            # User's rating (if exists)
            if item.get('my_rating') is not None:
                user_rating = item['my_rating']
                rating_label = item.get('my_rating_label', RATING_LABELS.get(user_rating, 'Unknown'))
                st.markdown(f"**Your Rating:** {rating_label}")
        
        # Rating actions
        if show_actions and not item.get('my_rating'):
            render_rating_buttons(item, card_key)
        
        st.markdown('</div>', unsafe_allow_html=True)


def get_card_css_class(my_rating: Optional[int]) -> str:
    """Get CSS class based on user rating"""
    if my_rating is None:
        return ""
    
    rating_classes = {
        4: "loved-it",
        3: "liked-it", 
        2: "it-was-ok",
        1: "didnt-like-it",
        0: "want-to-see",
        -1: "not-interested",
        -2: "watchlist-item"
    }
    
    return rating_classes.get(my_rating, "")


def render_rating_buttons(item: Dict, key_prefix: str) -> None:
    """Render rating action buttons for a content item"""
    st.markdown('<div class="rating-buttons">', unsafe_allow_html=True)
    
    # Create columns for rating buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("😤 Hate", key=f"hate_{key_prefix}", help="1/4 - Didn't like it"):
            rate_content(item, 1)
    
    with col2:
        if st.button("🤷 OK", key=f"ok_{key_prefix}", help="2/4 - It was okay"):
            rate_content(item, 2)
    
    with col3:
        if st.button("👍 Good", key=f"good_{key_prefix}", help="3/4 - Liked it"):
            rate_content(item, 3)
    
    with col4:
        if st.button("🌟 Perfect", key=f"perfect_{key_prefix}", help="4/4 - Loved it"):
            rate_content(item, 4)
    
    # Additional action buttons
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("📋 Watchlist", key=f"watchlist_{key_prefix}", help="Save for later"):
            rate_content(item, -2)
    
    with col_b:
        if st.button("💚 Want to See", key=f"want_{key_prefix}", help="Interested but haven't seen"):
            rate_content(item, 0)
    
    with col_c:
        if st.button("❌ Not Interested", key=f"skip_{key_prefix}", help="Not for me"):
            rate_content(item, -1)
    
    st.markdown('</div>', unsafe_allow_html=True)


def rate_content(item: Dict, rating: int) -> None:
    """Handle content rating and update session state"""
    if 'ratings_manager' in st.session_state:
        success = st.session_state.ratings_manager.add_rating(
            tmdb_id=item['id'],
            title=item['title'],
            content_type=item['type'],
            rating=rating,
            item_data=item
        )
        
        if success:
            rating_labels = {
                4: "Perfect! 🌟",
                3: "Good 👍", 
                2: "OK 🤷",
                1: "Hate 😤",
                0: "Want to See 💚",
                -1: "Not Interested ❌",
                -2: "Added to Watchlist 📋"
            }
            
            label = rating_labels.get(rating, "Rated")
            st.success(f"✅ {label}")
            
            # Trigger refresh
            if hasattr(st.session_state, 'last_action'):
                st.session_state.last_action = 'rating_added'
            
            st.rerun()
        else:
            st.error("Failed to save rating")


def render_stats_card(title: str, value: str, icon: str = "📊") -> None:
    """Render a statistics card"""
    st.markdown(
        f"""
        <div class="stats-card">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 1.2rem; font-weight: bold;">{value}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">{title}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_page_header(title: str, subtitle: str = "") -> None:
    """Render consistent page headers"""
    st.markdown(f'<h1 class="main-header">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="subtitle">{subtitle}</p>', unsafe_allow_html=True)


def load_css() -> None:
    """Load CSS from external file"""
    try:
        with open("src/assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found - using default styling") 
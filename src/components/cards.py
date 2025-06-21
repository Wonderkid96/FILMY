"""
UI Components for FILMY app
Reusable components to reduce code duplication
"""

import streamlit as st
from typing import Dict, Optional
from core.config import TMDB_IMAGE_BASE_URL, RATING_LABELS


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_poster_html(width: int, fallback: str = "🎬") -> str:
    """Generate cached poster fallback HTML"""
    return f"""
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
    """


def render_poster(url: str, width: int = 80, fallback: str = "🎬") -> None:
    """Render movie poster with fallback"""
    if url:
        poster_url = f"{TMDB_IMAGE_BASE_URL}{url}"
        try:
            st.image(poster_url, width=width)
        except Exception:
            # Fallback if image fails to load
            st.markdown(get_poster_html(width, fallback), unsafe_allow_html=True)
    else:
        st.markdown(get_poster_html(width, fallback), unsafe_allow_html=True)


def truncate_overview(overview: str, max_length: int = 150) -> str:
    """Truncate overview text with ellipsis"""
    if not overview or len(overview) <= max_length:
        return overview or "No description available."
    return overview[:max_length].rsplit(' ', 1)[0] + "..."


@st.cache_data
def get_rating_color(rating: float) -> str:
    """Get color based on TMDB rating - cached for performance"""
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
    try:
        # Generate unique key if not provided
        if not card_key:
            card_key = f"{item.get('id', 'unknown')}_{item.get('type', 'content')}"
        
        # Container with custom CSS class based on rating
        rating_class = get_card_css_class(item.get('my_rating'))
        
        with st.container():
            st.markdown(
                f'<div class="movie-card {rating_class}">', 
                unsafe_allow_html=True
            )
            
            # Create columns for poster and content
            col1, col2 = st.columns([1, 3])
            
            with col1:
                render_poster(item.get('poster_path'), width=80)
            
            with col2:
                render_card_content(item, show_rec_reason)
            
            # Rating actions
            if show_actions and not item.get('my_rating'):
                render_rating_buttons(item, card_key)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error displaying card: {e}")


def render_card_content(item: Dict, show_rec_reason: bool) -> None:
    """Render the content portion of a movie card"""
    # Title with year
    title = item.get('title', 'Unknown Title')
    release_date = item.get('release_date', '')
    year = release_date[:4] if release_date else 'N/A'
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
        rating_label = item.get(
            'my_rating_label', 
            RATING_LABELS.get(user_rating, 'Unknown')
        )
        st.markdown(f"**Your Rating:** {rating_label}")


@st.cache_data
def get_card_css_class(my_rating: Optional[int]) -> str:
    """Get CSS class based on user rating - cached"""
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
    
    button_configs = [
        (col1, "😤 Hate", "hate", 1, "1/4 - Didn't like it"),
        (col2, "🤷 OK", "ok", 2, "2/4 - It was okay"),
        (col3, "👍 Good", "good", 3, "3/4 - Liked it"),
        (col4, "🌟 Perfect", "perfect", 4, "4/4 - Loved it"),
    ]
    
    for col, label, key_suffix, rating, help_text in button_configs:
        with col:
            if st.button(
                label, 
                key=f"{key_suffix}_{key_prefix}", 
                help=help_text
            ):
                rate_content(item, rating)
    
    # Additional action buttons
    col_a, col_b, col_c = st.columns(3)
    
    additional_configs = [
        (col_a, "📋 Watchlist", "watchlist", -2, "Save for later"),
        (col_b, "💚 Want to See", "want", 0, "Interested but haven't seen"),
        (col_c, "❌ Not Interested", "skip", -1, "Not for me"),
    ]
    
    for col, label, key_suffix, rating, help_text in additional_configs:
        with col:
            if st.button(
                label, 
                key=f"{key_suffix}_{key_prefix}", 
                help=help_text
            ):
                rate_content(item, rating)
    
    st.markdown('</div>', unsafe_allow_html=True)


def rate_content(item: Dict, rating: int) -> None:
    """Handle content rating and update session state"""
    if 'ratings_manager' not in st.session_state:
        st.error("Ratings manager not initialized")
        return
    
    try:
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
            
    except Exception as e:
        st.error(f"Error saving rating: {e}")


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
    st.markdown(
        f'<h1 class="main-header">{title}</h1>', 
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(
            f'<p class="subtitle">{subtitle}</p>', 
            unsafe_allow_html=True
        )


def load_css() -> None:
    """Load CSS from external file with error handling"""
    try:
        with open("src/assets/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found - using default styling")
    except Exception as e:
        st.warning(f"Error loading CSS: {e}") 
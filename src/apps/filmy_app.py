import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from typing import Dict
import time
import random
from datetime import datetime

# Import our core modules
from core.config import (
    RATING_LABELS,
    TMDB_IMAGE_BASE_URL,
)
from core.tmdb_api import TMDBApi
from core.enhanced_ratings_manager import EnhancedRatingsManager
from core.dynamic_recommendations import DynamicRecommendationManager
# Swipe interface imported dynamically in functions

# Page configuration
st.set_page_config(
    page_title="FILMY - Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Mobile-first responsive CSS styling
st.markdown(
    """
<style>
/* Reset and base styles */
.main .block-container {
    padding: 0.5rem;
    max-width: 100%;
}

/* Header styling - responsive */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1.5rem;
    line-height: 1.2;
}

.subtitle {
    text-align: center;
    font-size: 1rem;
    color: #666;
    margin-bottom: 1.5rem;
    padding: 0 1rem;
}

/* Movie cards - mobile first */
.movie-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.8rem 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-left: 4px solid #FF6B6B;
    transition: transform 0.2s ease;
}

.movie-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.already-rated {
    background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #fdcb6e;
    font-size: 0.9rem;
}

/* Responsive columns */
.stColumns > div {
    padding: 0.2rem !important;
}

/* Button styling - touch friendly */
.stButton > button {
    width: 100% !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 0.4rem !important;
    margin: 0.1rem 0 !important;
    border-radius: 8px !important;
    min-height: 44px !important; /* iOS touch target minimum */
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
}

/* Rating buttons specific styling */
.rating-buttons .stButton > button {
    font-size: 0.75rem !important;
    padding: 0.5rem 0.2rem !important;
    min-height: 40px !important;
}

/* Stats cards - mobile optimized */
.stats-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.3rem 0;
}

/* Sidebar improvements */
.css-1d391kg {
    padding-top: 1rem;
}

/* Search input */
.stTextInput > div > div > input {
    font-size: 1rem !important;
    padding: 0.8rem !important;
}

/* Selectbox */
.stSelectbox > div > div > select {
    font-size: 1rem !important;
    padding: 0.8rem !important;
}

/* Metrics */
[data-testid="metric-container"] {
    background-color: rgba(28, 131, 225, 0.1);
    border: 1px solid rgba(28, 131, 225, 0.2);
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.3rem 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #666;
    font-style: italic;
    margin-top: 2rem;
    padding: 1rem;
    border-top: 1px solid #eee;
    font-size: 0.9rem;
}

/* Desktop improvements */
@media (min-width: 769px) {
    .main .block-container {
        padding: 1rem 2rem;
        max-width: 1200px;
    }

    .main-header {
        font-size: 3.5rem;
    }

    .subtitle {
        font-size: 1.3rem;
    }

    .movie-card {
        padding: 1.5rem;
        margin: 1.2rem 0;
    }

    .stButton > button {
        font-size: 1rem !important;
        padding: 0.7rem 1rem !important;
    }

    .rating-buttons .stButton > button {
        font-size: 0.9rem !important;
        padding: 0.6rem 0.8rem !important;
    }

    .stats-card {
        padding: 1.5rem;
    }
}

/* Extra large screens */
@media (min-width: 1200px) {
    .main .block-container {
        max-width: 1400px;
    }

    .main-header {
        font-size: 4rem;
    }
}

/* Tablet specific */
@media (min-width: 481px) and (max-width: 768px) {
    .main-header {
        font-size: 3rem;
    }

    .stButton > button {
        font-size: 0.95rem !important;
        padding: 0.65rem 0.8rem !important;
    }
}

/* Small phone specific */
@media (max-width: 480px) {
    .main .block-container {
        padding: 0.3rem;
    }

    .main-header {
        font-size: 2rem;
        margin-bottom: 1rem;
    }

    .subtitle {
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    .movie-card {
        padding: 0.8rem;
        margin: 0.5rem 0;
    }

    .stButton > button {
        font-size: 0.8rem !important;
        padding: 0.5rem 0.3rem !important;
        min-height: 42px !important;
    }

    .rating-buttons .stButton > button {
        font-size: 0.7rem !important;
        padding: 0.4rem 0.1rem !important;
        min-height: 38px !important;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

# Session state will be initialized in main() function


def display_content_card(item: Dict, show_actions: bool = True):
    """Display a compact, beautiful movie/TV show card"""
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)

    # Check if already rated (with safety check)
    already_rated = False
    if (
        hasattr(st.session_state, "ratings_manager")
        and st.session_state.ratings_manager
    ):
        try:
            already_rated = st.session_state.ratings_manager.is_already_rated(
                item["id"], item["type"]
            )
        except Exception:
            already_rated = False

    # Compact header with poster thumbnail and title
    col_poster, col_title = st.columns([1, 5])

    with col_poster:
        if item.get("poster_path") and item["poster_path"] != "None":
            try:
                st.image(item["poster_path"], width=80)
            except Exception:
                # Compact fallback icon
                st.markdown(
                    """
                    <div style="
                        width: 80px; 
                        height: 120px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        border-radius: 6px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-size: 24px;
                    ">
                        🎬
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            # Compact styled placeholder
            st.markdown(
                """
                <div style="
                    width: 80px; 
                    height: 120px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 24px;
                ">
                    🎬
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_title:
        st.markdown(f"### {item['title']}")

        # Show if already rated
        if already_rated:
            existing_rating = st.session_state.ratings_manager.get_user_rating(
                item["id"], item["type"]
            )
            if existing_rating and existing_rating > 0:
                rating_label = RATING_LABELS.get(existing_rating, "Unknown")
                st.markdown(
                    f'<div class="already-rated">✅ <strong>You rated this: {rating_label}</strong></div>',
                    unsafe_allow_html=True,
                )

        # Rating and basic info
        col_rating, col_year, col_type = st.columns(3)
        with col_rating:
            rating = item.get("vote_average", 0)
            if rating >= 8:
                color = "🟢"
            elif rating >= 7:
                color = "🟡"
            elif rating >= 6:
                color = "🟠"
            else:
                color = "🔴"
            st.markdown(f"{color} **TMDB: {rating:.1f}/10**")

        with col_year:
            year = (
                item.get("release_date", "")[:4] if item.get("release_date") else "N/A"
            )
            st.markdown(f"📅 **{year}**")

        with col_type:
            content_type = "🎬 Movie" if item["type"] == "movie" else "📺 TV Show"
            st.markdown(f"{content_type}")

        # Show recommendation reason if available
        if item.get("rec_reason"):
            match_score = item.get("final_score", 0.5) * 100
            st.info(f"🎯 **{item['rec_reason']}** (Match: {match_score:.0f}%)")

        # Language info (very important!)
        if item.get("language_name"):
            st.markdown(f"🌍 **Language:** {item['language_name']}")
        elif item.get("original_language"):
            st.markdown(f"🌍 **Language:** {item['original_language'].upper()}")

        # Genres
        if item.get("genres"):
            genres_text = " ".join([f"`{genre}`" for genre in item["genres"][:3]])
            st.markdown(f"**Genres:** {genres_text}")

        # Overview
        overview = item.get("overview", "No overview available")
        if len(overview) > 300:
            overview = overview[:300] + "..."
        st.markdown(f"**Plot:** {overview}")

        # Rating buttons
        if show_actions:
            st.markdown("**Rate this content:**")
            st.markdown('<div class="rating-buttons">', unsafe_allow_html=True)

            # After watching ratings
            st.markdown("*After Watching:*")
            col1, col2, col3, col4 = st.columns(4)

            watched_ratings = [
                (1, "😤 Hate", "#FF4444"),
                (2, "🤷 OK", "#FFA500"),
                (3, "👍 Good", "#32CD32"),
                (4, "🌟 Perfect", "#FFD700"),
            ]

            for i, (rating_value, label, color) in enumerate(watched_ratings):
                col = [col1, col2, col3, col4][i]
                with col:
                    if st.button(
                        label,
                        key=f"rate_{item['id']}_{item['type']}_{rating_value}",
                        help=f"Rate as {label.split(' ')[1]}",
                    ):
                        try:
                            success = st.session_state.ratings_manager.add_rating(
                                item["id"],
                                item["title"],
                                item["type"],
                                rating_value,
                                item,
                            )
                            if success:
                                if already_rated:
                                    st.success(f"✅ Updated rating to {label}!")
                                else:
                                    st.success(
                                        f"✅ Rated as {label}! This will improve your recommendations."
                                    )
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to save rating. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving rating: {str(e)}")

            # Before watching decisions
            st.markdown("*Before Watching:*")
            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👀 Want to See",
                    key=f"want_{item['id']}_{item['type']}",
                    help="Add to watchlist",
                ):
                    try:
                        success = st.session_state.ratings_manager.add_rating(
                            item["id"],
                            item["title"],
                            item["type"],
                            0,
                            item,
                        )
                        if success:
                            st.success("✅ Added to watchlist!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            with col2:
                if st.button(
                    "❌ Don't Want to See",
                    key=f"dont_want_{item['id']}_{item['type']}",
                    help="Mark as not interested",
                ):
                    try:
                        success = st.session_state.ratings_manager.add_rating(
                            item["id"],
                            item["title"],
                            item["type"],
                            -1,
                            item,
                        )
                        if success:
                            st.success("✅ Marked as not interested!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            st.markdown("</div>", unsafe_allow_html=True)  # Close rating-buttons div

    st.markdown("</div>", unsafe_allow_html=True)  # Close movie-card div


def show_discover_page():
    """Main discovery page with trending content"""
    st.markdown('<h1 class="main-header">🎬 FILMY</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Discover your next perfect movie night together!</p>',
        unsafe_allow_html=True,
    )

    # Content type selector
    content_type = st.selectbox(
        "What are you in the mood for?",
        ["Both Movies & TV Shows", "Movies Only", "TV Shows Only"],
        index=0,
    )

    # Get trending content
    try:
        all_content = []

        if content_type in ["Both Movies & TV Shows", "Movies Only"]:
            movies = st.session_state.tmdb.get_popular_movies()
            for movie in movies.get("results", [])[:10]:
                # Use the proper formatting method to get language info
                movie_data = st.session_state.tmdb.format_movie_data(movie)
                all_content.append(movie_data)

        if content_type in ["Both Movies & TV Shows", "TV Shows Only"]:
            tv_shows = st.session_state.tmdb.get_popular_tv()
            for show in tv_shows.get("results", [])[:10]:
                # Use the proper formatting method to get language info
                show_data = st.session_state.tmdb.format_tv_data(show)
                all_content.append(show_data)

        # Shuffle for variety
        random.shuffle(all_content)

        # Filter out already rated content (optional)
        show_rated = st.checkbox("Show content you've already rated", value=False)

        if not show_rated:
            filtered_content = []
            for item in all_content:
                if not st.session_state.ratings_manager.is_already_rated(
                    item["id"], item["type"]
                ):
                    filtered_content.append(item)
            all_content = filtered_content

        # Display content
        if all_content:
            st.markdown(f"### 🎯 Trending Content ({len(all_content)} items)")

            for item in all_content[:12]:  # Show top 12
                display_content_card(item)
                st.markdown("---")
        else:
            st.info(
                "🎉 Wow! You've rated everything trending. Check out the search page for more content!"
            )

    except Exception as e:
        st.error(f"Error loading content: {e}")
        st.info("Please check your internet connection and try again.")


def show_search_page():
    """Search for specific content"""
    st.markdown("## 🔍 Search Movies & TV Shows")

    # Search input
    search_query = st.text_input(
        "Search for movies or TV shows:",
        placeholder="e.g., The Matrix, Breaking Bad, Marvel...",
    )

    if search_query:
        try:
            # Search both movies and TV shows
            movie_results = st.session_state.tmdb.search_movies(search_query)
            tv_results = st.session_state.tmdb.search_tv(search_query)

            all_results = []

            # Process movie results
            for movie in movie_results.get("results", [])[:10]:
                movie_data = st.session_state.tmdb.format_movie_data(movie)
                all_results.append(movie_data)

            # Process TV results
            for show in tv_results.get("results", [])[:10]:
                show_data = st.session_state.tmdb.format_tv_data(show)
                all_results.append(show_data)

            # Sort by rating
            all_results.sort(key=lambda x: x.get("vote_average", 0), reverse=True)

            if all_results:
                st.markdown(
                    f"### 🎯 Search Results for '{search_query}' ({len(all_results)} found)"
                )

                for item in all_results:
                    display_content_card(item)
                    st.markdown("---")
            else:
                st.info(
                    f"No results found for '{search_query}'. Try a different search term!"
                )

        except Exception as e:
            st.error(f"Search error: {e}")


def show_quick_discovery_page():
    """One-by-one movie discovery flow"""
    st.markdown("## 🚀 Quick Discovery")
    st.markdown(
        "*Discover movies one at a time - perfect for finding your next watch!*"
    )

    # Initialize discovery state
    if "discovery_index" not in st.session_state:
        st.session_state.discovery_index = 0

    try:
        # Get popular movies
        movies = st.session_state.tmdb.get_popular_movies()
        movie_list = movies.get("results", [])

        if not movie_list:
            st.error("No movies available for discovery.")
            return

        # Filter out already rated movies
        unrated_movies = []
        for movie in movie_list:
            if not st.session_state.ratings_manager.is_already_rated(
                movie["id"], "movie"
            ):
                unrated_movies.append(movie)

        if not unrated_movies:
            st.success(
                "🎉 You've rated all popular movies! Check out TV shows or search for more content."
            )
            return

        # Get current movie
        current_movie = unrated_movies[
            st.session_state.discovery_index % len(unrated_movies)
        ]

        # Display movie
        col1, col2 = st.columns([1, 2])

        with col1:
            if current_movie.get("poster_path"):
                st.image(
                    f"{TMDB_IMAGE_BASE_URL}{current_movie['poster_path']}", width=200
                )

        with col2:
            st.markdown(f"### {current_movie['title']}")
            if current_movie.get("release_date"):
                st.markdown(f"**Released:** {current_movie['release_date'][:4]}")
            if current_movie.get("vote_average"):
                st.markdown(
                    f"**TMDB Rating:** ⭐ {current_movie['vote_average']:.1f}/10"
                )
            st.markdown(
                f"**Overview:** {current_movie.get('overview', 'No description available.')}"
            )

        # Action buttons
        st.markdown("---")

        # Main rating buttons (after watching)
        st.markdown("**After Watching:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("😍 Perfect", key="perfect", use_container_width=True):
                rate_and_next(current_movie, 4)

        with col2:
            if st.button("👍 Good", key="good", use_container_width=True):
                rate_and_next(current_movie, 3)

        with col3:
            if st.button("😐 OK", key="ok", use_container_width=True):
                rate_and_next(current_movie, 2)

        with col4:
            if st.button("👎 Hate", key="hate", use_container_width=True):
                rate_and_next(current_movie, 1)

        # Pre-watch decisions
        st.markdown("**Before Watching:**")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("👀 Want to See", key="want_to_see", use_container_width=True):
                rate_and_next(current_movie, 0)

        with col2:
            if st.button(
                "❌ Don't Want to See", key="dont_want_to_see", use_container_width=True
            ):
                rate_and_next(current_movie, -1)

        with col3:
            if st.button("⏭️ Skip", key="skip", use_container_width=True):
                next_movie()

        # Progress indicator
        st.markdown("---")
        st.progress((st.session_state.discovery_index + 1) / len(unrated_movies))
        st.markdown(
            f"Movie {st.session_state.discovery_index + 1} of {len(unrated_movies)} unrated movies"
        )

    except Exception as e:
        st.error(f"Error in Quick Discovery: {e}")


def rate_and_next(movie, rating):
    """Rate current movie and move to next"""
    movie_data = {
        "id": movie["id"],
        "title": movie["title"],
        "type": "movie",
        "poster_path": movie.get("poster_path"),
        "overview": movie.get("overview", ""),
        "vote_average": movie.get("vote_average", 0),
        "release_date": movie.get("release_date", ""),
        "genres": [],
    }

    st.session_state.ratings_manager.add_rating(
        movie["id"], movie["title"], "movie", rating, movie_data
    )

    st.success(f"Rated '{movie['title']}' as {RATING_LABELS[rating]}!")
    next_movie()


def next_movie():
    """Move to next movie in discovery"""
    st.session_state.discovery_index += 1
    st.rerun()


def show_home_page():
    """Full-screen swipe interface"""
    # Remove default streamlit padding for full-screen experience
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize dynamic recommendation manager
    if 'dynamic_rec_manager' not in st.session_state:
        st.session_state.dynamic_rec_manager = DynamicRecommendationManager(
            st.session_state.ratings_manager
        )
    
    # Create enhanced swipe interface
    create_enhanced_swipe_page()


def create_enhanced_swipe_page():
    """Enhanced swipe interface with better visuals and new release tracking"""
    st.markdown("# FILMY")
    st.markdown("*Discover your next favorite film*")
    
    # Get fresh recommendations including new releases
    if 'swipe_recommendations' not in st.session_state:
        st.session_state.swipe_recommendations = []
    
    # Load more recommendations if needed
    if len(st.session_state.swipe_recommendations) < 5:
        new_recs = st.session_state.dynamic_rec_manager.get_endless_recommendations(25)
        # Add new release tracking
        new_recs = add_new_release_tracking(new_recs)
        st.session_state.swipe_recommendations.extend(new_recs)
    
    # Show current recommendation count and user stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Ready to Swipe", len(st.session_state.swipe_recommendations))
    with col2:
        total_ratings = len(st.session_state.ratings_manager.get_all_ratings())
        st.metric("Your Ratings", total_ratings)
    with col3:
        if total_ratings > 0:
            perfect_count = len(st.session_state.ratings_manager.get_all_ratings()[
                st.session_state.ratings_manager.get_all_ratings()["my_rating"] == 4
            ])
            st.metric("Perfect Picks", perfect_count)
        else:
            st.metric("Getting Started", "Rate to unlock")
    
    st.markdown("---")
    
    # Enhanced swipe interface from swipe_interface.py
    from apps.swipe_interface import SwipeInterface
    swipe_interface = SwipeInterface(st.session_state.ratings_manager)
    swipe_interface.render_swipe_interface(
        st.session_state.swipe_recommendations,
        key="home_swipe"
    )


def add_new_release_tracking(recommendations):
    """Add tracking for new releases that match user preferences"""
    enhanced_recs = []
    
    for rec in recommendations:
        # Check if it's a recent release (last 3 months)
        try:
            release_date = rec.get('release_date', '')
            if release_date:
                from datetime import datetime, timedelta
                release_dt = datetime.strptime(release_date, '%Y-%m-%d')
                three_months_ago = datetime.now() - timedelta(days=90)
                
                if release_dt > three_months_ago:
                    rec['rec_reason'] = f"NEW RELEASE: {rec.get('rec_reason', 'Fresh content')}"
                    rec['rec_score'] = rec.get('rec_score', 0.5) + 0.1  # Boost new releases
                    
        except:
            pass  # Skip date parsing errors
            
        enhanced_recs.append(rec)
    
    return enhanced_recs


def show_your_swipes_page():
    """Clean interface for managing user ratings"""
    st.markdown("# Your Swipes")
    st.markdown("*Review and edit your ratings*")
    
    try:
        ratings_df = st.session_state.ratings_manager.get_all_ratings()
        
        if ratings_df.empty:
            st.info("No ratings yet! Go to Home to start swiping.")
            if st.button("Start Swiping", type="primary", use_container_width=True):
                st.switch_page("Home")
            return
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            watched = len(ratings_df[ratings_df["my_rating"] > 0])
            st.metric("Watched", watched)
        with col2:
            watchlist = len(ratings_df[ratings_df["my_rating"] == 0])
            st.metric("Watchlist", watchlist)
        with col3:
            perfect_count = len(ratings_df[ratings_df["my_rating"] == 4])
            st.metric("Perfect Ratings", perfect_count)
        with col4:
            if watched > 0:
                avg = ratings_df[ratings_df["my_rating"] > 0]["my_rating"].mean()
                st.metric("Average", f"{avg:.1f}/4")
            else:
                st.metric("Average", "N/A")
        
        st.markdown("---")
        
        # Filter and sort options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by type", ["All", "Movies", "TV Shows"])
        with col2:
            filter_rating = st.selectbox("Filter by rating", [
                "All", "Perfect (4)", "Good (3)", "OK (2)", "Hate (1)", "Watchlist", "Not Interested"
            ])
        with col3:
            sort_by = st.selectbox("Sort by", [
                "Date (Newest)", "Date (Oldest)", "Rating (High)", "Rating (Low)", "Title A-Z"
            ])
        
        # Apply filters
        filtered_df = ratings_df.copy()
        
        if filter_type == "Movies":
            filtered_df = filtered_df[filtered_df["type"] == "movie"]
        elif filter_type == "TV Shows":
            filtered_df = filtered_df[filtered_df["type"] == "tv"]
            
        if filter_rating != "All":
            rating_map = {
                "Perfect (4)": 4, "Good (3)": 3, "OK (2)": 2, "Hate (1)": 1,
                "Watchlist": 0, "Not Interested": -1
            }
            filtered_df = filtered_df[filtered_df["my_rating"] == rating_map[filter_rating]]
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            filtered_df = filtered_df.sort_values("date_rated", ascending=False)
        elif sort_by == "Date (Oldest)":
            filtered_df = filtered_df.sort_values("date_rated", ascending=True)
        elif sort_by == "Rating (High)":
            filtered_df = filtered_df.sort_values("my_rating", ascending=False)
        elif sort_by == "Rating (Low)":
            filtered_df = filtered_df.sort_values("my_rating", ascending=True)
        elif sort_by == "Title A-Z":
            filtered_df = filtered_df.sort_values("title", ascending=True)
        
        # Display results
        st.markdown(f"### {len(filtered_df)} items")
        
        for _, rating in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    content_type = "Movie" if rating["type"] == "movie" else "TV Show"
                    st.write(f"**{rating['title']}** ({content_type})")
                    if rating.get('overview'):
                        st.caption(rating['overview'][:100] + "..." if len(rating['overview']) > 100 else rating['overview'])
                
                with col2:
                    rating_labels = {-1: "Not Interested", 0: "Watchlist", 1: "Hate", 2: "OK", 3: "Good", 4: "Perfect"}
                    current_label = rating_labels.get(rating["my_rating"], "Unknown")
                    st.write(f"**{current_label}**")
                    st.caption(rating["date_rated"][:10])
                
                with col3:
                    if st.button("Edit", key=f"edit_{rating['tmdb_id']}_{rating['type']}", use_container_width=True):
                        st.session_state[f"editing_{rating['tmdb_id']}_{rating['type']}"] = True
                
                with col4:
                    if st.button("Delete", key=f"delete_{rating['tmdb_id']}_{rating['type']}", use_container_width=True):
                        success = st.session_state.ratings_manager.delete_rating(
                            rating["tmdb_id"], rating["type"]
                        )
                        if success:
                            st.success("Deleted!")
                            st.rerun()
                
                # Inline editing
                if st.session_state.get(f"editing_{rating['tmdb_id']}_{rating['type']}", False):
                    with st.expander("Edit Rating", expanded=True):
                        new_rating = st.selectbox(
                            "New rating:",
                            options=[-1, 0, 1, 2, 3, 4],
                            format_func=lambda x: rating_labels[x],
                            index=[k for k, v in rating_labels.items()].index(rating["my_rating"]),
                            key=f"new_rating_{rating['tmdb_id']}_{rating['type']}"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.button("Save", key=f"save_{rating['tmdb_id']}_{rating['type']}"):
                                success = st.session_state.ratings_manager.update_rating(
                                    rating["tmdb_id"], rating["type"], new_rating
                                )
                                if success:
                                    st.success("Updated!")
                                    del st.session_state[f"editing_{rating['tmdb_id']}_{rating['type']}"]
                                    st.rerun()
                        
                        with col_cancel:
                            if st.button("Cancel", key=f"cancel_{rating['tmdb_id']}_{rating['type']}"):
                                del st.session_state[f"editing_{rating['tmdb_id']}_{rating['type']}"]
                                st.rerun()
                
                st.markdown("---")
        
    except Exception as e:
        st.error(f"Error loading your swipes: {e}")


def show_recommendations_page():
    """Show endless personalized recommendations"""
    st.markdown("## 🎯 Your Endless Recommendations")

    try:
        # Initialize dynamic recommendation manager
        if 'dynamic_rec_manager' not in st.session_state:
            st.session_state.dynamic_rec_manager = DynamicRecommendationManager(
                st.session_state.ratings_manager
            )

        # Get user's ratings to base recommendations on
        user_ratings = st.session_state.ratings_manager.get_all_ratings()

        # Show recommendations even for new users
        if user_ratings.empty:
            st.info("🎬 New user? You'll get popular and trending content to start with!")
        else:
            st.info(f"🎯 Based on your {len(user_ratings)} ratings - recommendations get smarter as you rate more!")

        # Get endless recommendations
        recommendations = st.session_state.dynamic_rec_manager.get_endless_recommendations(20)

        if recommendations:
            st.markdown(f"### 🌟 Fresh Recommendations ({len(recommendations)} loaded)")
            
            # Show pool stats
            pool_stats = st.session_state.dynamic_rec_manager.get_pool_stats()
            with st.expander("📊 Recommendation Sources"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🧠 Intelligent", pool_stats.get('intelligent', 0))
                    st.metric("🔥 Trending", pool_stats.get('trending', 0))
                with col2:
                    st.metric("⭐ Popular", pool_stats.get('popular', 0))
                    st.metric("🎭 Discovery", pool_stats.get('discovery', 0))
                with col3:
                    st.metric("🎯 Genre Deep Dive", pool_stats.get('genre_deep_dive', 0))

            for item in recommendations:
                display_content_card(item)
                st.markdown("---")
                
            # Load more button
            if st.button("🔄 Load More Recommendations", use_container_width=True):
                st.rerun()
        else:
            st.warning("No recommendations available. This shouldn't happen with the dynamic system!")
            if st.button("🔄 Reset Recommendation System"):
                if 'dynamic_rec_manager' in st.session_state:
                    st.session_state.dynamic_rec_manager.clear_used_items()
                st.rerun()

    except Exception as e:
        st.error(f"Error loading recommendations: {e}")


def show_my_ratings_page():
    """Show user's ratings and statistics"""
    st.markdown("## 📊 Your Movie & TV Ratings")

    try:
        ratings_df = st.session_state.ratings_manager.get_all_ratings()

        if ratings_df.empty:
            st.info(
                "You haven't rated any content yet! Visit the Discover page to start rating."
            )
            return

        # Filter out "want to see" and "don't want to see" for main stats
        watched_ratings = ratings_df[ratings_df["my_rating"] > 0]

        # Separate watchlist items
        watchlist = ratings_df[ratings_df["my_rating"] == 0]
        not_interested = ratings_df[ratings_df["my_rating"] == -1]

        if watched_ratings.empty and watchlist.empty and not_interested.empty:
            st.info("You haven't rated any content yet!")
            return

        # Statistics
        st.markdown("### 📈 Your Stats")
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Watched", len(watched_ratings))
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Want to See", len(watchlist))
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            movies_count = len(watched_ratings[watched_ratings["type"] == "movie"])
            st.metric("Movies", movies_count)
            st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            tv_count = len(watched_ratings[watched_ratings["type"] == "tv"])
            st.metric("TV Shows", tv_count)
            st.markdown("</div>", unsafe_allow_html=True)

        with col5:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            if not watched_ratings.empty:
                avg_rating = watched_ratings["my_rating"].mean()
                st.metric("Avg Rating", f"{avg_rating:.1f}/4")
            else:
                st.metric("Avg Rating", "N/A")
            st.markdown("</div>", unsafe_allow_html=True)

        # Rating distribution chart
        st.markdown("### 📊 Rating Distribution")

        # Show different sections
        col1, col2 = st.columns(2)

        with col1:
            if not watched_ratings.empty:
                st.markdown("**Watched Content:**")
                rating_counts = watched_ratings["my_rating"].value_counts().sort_index()
                fig = px.bar(
                    x=[RATING_LABELS[i] for i in rating_counts.index],
                    y=rating_counts.values,
                    color=rating_counts.values,
                    color_continuous_scale=["#FF4444", "#FFA500", "#32CD32", "#FFD700"],
                )
                fig.update_layout(
                    title="How You Rate Watched Content",
                    xaxis_title="Rating",
                    yaxis_title="Number of Items",
                    showlegend=False,
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if not watchlist.empty or not not_interested.empty:
                st.markdown("**Watchlist & Decisions:**")
                other_counts = {}
                if not watchlist.empty:
                    other_counts[0] = len(watchlist)
                if not not_interested.empty:
                    other_counts[-1] = len(not_interested)

                if other_counts:
                    fig2 = px.bar(
                        x=[RATING_LABELS[i] for i in other_counts.keys()],
                        y=list(other_counts.values()),
                        color=list(other_counts.values()),
                        color_continuous_scale=["#9CA3AF", "#6366F1"],
                    )
                    fig2.update_layout(
                        title="Watchlist & Not Interested",
                        xaxis_title="Decision",
                        yaxis_title="Number of Items",
                        showlegend=False,
                    )
                    st.plotly_chart(fig2, use_container_width=True)

        # Recent activity
        st.markdown("### 🕒 Recent Activity")
        recent_activity = ratings_df.sort_values("date_rated", ascending=False).head(15)

        for _, rating in recent_activity.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                content_type = "🎬" if rating["type"] == "movie" else "📺"
                st.write(f"{content_type} **{rating['title']}**")
            with col2:
                st.write(RATING_LABELS[rating["my_rating"]])
            with col3:
                st.write(rating["date_rated"][:10])

    except Exception as e:
        st.error(f"Error loading ratings: {e}")


def show_edit_ratings_page():
    """Edit and manage all your ratings"""
    st.markdown("## ✏️ Edit Your Ratings")
    st.markdown("*View, edit, or delete your movie and TV show ratings*")

    try:
        ratings_df = st.session_state.ratings_manager.get_all_ratings()

        if ratings_df.empty:
            st.info(
                "You haven't rated any content yet! Visit the Discover page to start rating."
            )
            return

        # Filter controls
        col1, col2, col3 = st.columns(3)

        with col1:
            content_filter = st.selectbox(
                "Filter by type:", ["All", "Movies", "TV Shows"], index=0
            )

        with col2:
            rating_filter = st.selectbox(
                "Filter by rating:",
                [
                    "All Ratings",
                    "Perfect (4)",
                    "Good (3)",
                    "OK (2)",
                    "Hate (1)",
                    "Not Interested",
                ],
                index=0,
            )

        with col3:
            sort_by = st.selectbox(
                "Sort by:",
                [
                    "Date Rated (Newest)",
                    "Date Rated (Oldest)",
                    "Title A-Z",
                    "Title Z-A",
                    "Rating (High-Low)",
                    "Rating (Low-High)",
                ],
                index=0,
            )

        # Apply filters
        filtered_df = ratings_df.copy()

        if content_filter == "Movies":
            filtered_df = filtered_df[filtered_df["type"] == "movie"]
        elif content_filter == "TV Shows":
            filtered_df = filtered_df[filtered_df["type"] == "tv"]

        if rating_filter != "All Ratings":
            if rating_filter == "Perfect (4)":
                filtered_df = filtered_df[filtered_df["my_rating"] == 4]
            elif rating_filter == "Good (3)":
                filtered_df = filtered_df[filtered_df["my_rating"] == 3]
            elif rating_filter == "OK (2)":
                filtered_df = filtered_df[filtered_df["my_rating"] == 2]
            elif rating_filter == "Hate (1)":
                filtered_df = filtered_df[filtered_df["my_rating"] == 1]
            elif rating_filter == "Not Interested":
                filtered_df = filtered_df[filtered_df["my_rating"] == -1]

        # Apply sorting
        if sort_by == "Date Rated (Newest)":
            filtered_df = filtered_df.sort_values("date_rated", ascending=False)
        elif sort_by == "Date Rated (Oldest)":
            filtered_df = filtered_df.sort_values("date_rated", ascending=True)
        elif sort_by == "Title A-Z":
            filtered_df = filtered_df.sort_values("title", ascending=True)
        elif sort_by == "Title Z-A":
            filtered_df = filtered_df.sort_values("title", ascending=False)
        elif sort_by == "Rating (High-Low)":
            filtered_df = filtered_df.sort_values("my_rating", ascending=False)
        elif sort_by == "Rating (Low-High)":
            filtered_df = filtered_df.sort_values("my_rating", ascending=True)

        # Display results
        if filtered_df.empty:
            st.info("No ratings match your current filters.")
            return

        st.markdown(f"### 📝 Your Ratings ({len(filtered_df)} items)")

        # Pagination
        items_per_page = 10
        total_pages = (len(filtered_df) - 1) // items_per_page + 1

        if total_pages > 1:
            page = st.selectbox(
                f"Page (1-{total_pages}):", range(1, total_pages + 1), index=0
            )
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            page_df = filtered_df.iloc[start_idx:end_idx]
        else:
            page_df = filtered_df

        # Display each rating with edit options
        for idx, (_, rating) in enumerate(page_df.iterrows()):
            with st.container():
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                col1, col2, col3 = st.columns([2, 3, 2])

                with col1:
                    # Basic info
                    content_type = "🎬" if rating["type"] == "movie" else "📺"
                    st.markdown(f"### {content_type} {rating['title']}")

                    if rating.get("release_date"):
                        year = (
                            rating["release_date"][:4]
                            if rating["release_date"]
                            else "N/A"
                        )
                        st.markdown(f"**Year:** {year}")

                    if rating.get("tmdb_rating"):
                        st.markdown(f"**TMDB:** ⭐ {rating['tmdb_rating']:.1f}/10")

                    # Current rating
                    current_rating = rating["my_rating"]
                    if current_rating > 0:
                        rating_label = RATING_LABELS.get(current_rating, "Unknown")
                        st.markdown(
                            f"**Your Rating:** {rating_label} ({current_rating}/4)"
                        )
                    elif current_rating == -1:
                        st.markdown("**Your Rating:** Not Interested")
                    else:
                        st.markdown("**Your Rating:** Unknown")

                    date_rated = rating.get("date_rated", "")
                    if date_rated:
                        st.markdown(f"**Rated on:** {date_rated[:10]}")

                with col2:
                    # Overview
                    overview = rating.get("overview", "No overview available")
                    if len(overview) > 200:
                        overview = overview[:200] + "..."
                    st.markdown(f"**Overview:** {overview}")

                with col3:
                    # Edit controls
                    st.markdown("**Edit Rating:**")

                    # New rating selector
                    rating_options = {
                        "Keep Current": current_rating,
                        "😍 Perfect (4)": 4,
                        "👍 Good (3)": 3,
                        "😐 OK (2)": 2,
                        "👎 Hate (1)": 1,
                        "🚫 Not Interested": -1,
                    }

                    new_rating_label = st.selectbox(
                        "New rating:",
                        list(rating_options.keys()),
                        index=0,
                        key=f"rating_select_{rating['tmdb_id']}_{rating['type']}",
                    )

                    new_rating = rating_options[new_rating_label]

                    # Action buttons
                    col_update, col_delete = st.columns(2)

                    with col_update:
                        if st.button(
                            "💾 Update",
                            key=f"update_{rating['tmdb_id']}_{rating['type']}",
                            use_container_width=True,
                        ):
                            if new_rating != current_rating:
                                try:
                                    success = (
                                        st.session_state.ratings_manager.update_rating(
                                            rating["tmdb_id"],
                                            rating["type"],
                                            new_rating,
                                        )
                                    )
                                    if success:
                                        st.success("✅ Rating updated!")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to update rating")
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
                            else:
                                st.info("No changes to save")

                    with col_delete:
                        if st.button(
                            "🗑️ Delete",
                            key=f"delete_{rating['tmdb_id']}_{rating['type']}",
                            use_container_width=True,
                        ):
                            try:
                                success = (
                                    st.session_state.ratings_manager.delete_rating(
                                        rating["tmdb_id"], rating["type"]
                                    )
                                )
                                if success:
                                    st.success("✅ Rating deleted!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to delete rating")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")

        # Bulk actions
        st.markdown("### 🔧 Bulk Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📤 Export All Ratings", use_container_width=True):
                csv_data = ratings_df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"filmy_ratings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                )

        with col2:
            if st.button("🔄 Sync to Google Sheets", use_container_width=True):
                if hasattr(st.session_state.ratings_manager, "sync_to_google_sheets"):
                    try:
                        st.session_state.ratings_manager.sync_to_google_sheets()
                        st.success("✅ Synced to Google Sheets!")
                    except Exception as e:
                        st.error(f"❌ Sync failed: {e}")
                else:
                    st.info("Google Sheets sync not available")

        with col3:
            # Danger zone
            if st.button(
                "⚠️ Clear All Ratings",
                use_container_width=True,
                help="This will delete ALL your ratings!",
            ):
                st.warning(
                    "This feature requires confirmation. Use the individual delete buttons for now."
                )

    except Exception as e:
        st.error(f"Error loading edit page: {e}")


def main():
    """Main application - Cache Bust v2025.06.21.16.51"""

    # Initialize session state at the start of main
    if "tmdb" not in st.session_state:
        try:
            st.session_state.tmdb = TMDBApi()
        except Exception as e:
            st.error(f"Failed to initialize TMDB API: {e}")
            return

    if "ratings_manager" not in st.session_state:
        try:
            st.session_state.ratings_manager = EnhancedRatingsManager()
        except Exception as e:
            st.error(f"Failed to initialize ratings manager: {e}")
            return

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### FILMY Navigation")

        selected = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Recommendations", 
                "Watchlist",
                "Your Swipes",
            ],
            icons=["house", "target", "list-check"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#FF6B6B", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#262730",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {
                    "background-color": "#FF6B6B", 
                    "color": "white"
                },
            },
        )

        # Sidebar stats
        st.markdown("---")
        try:
            ratings_df = st.session_state.ratings_manager.get_all_ratings()
            if not ratings_df.empty:
                total_items = len(ratings_df)
                positive_ratings = ratings_df[ratings_df["my_rating"] > 0]
                watchlist = len(ratings_df[ratings_df["my_rating"] == 0])
                
                st.markdown("### Quick Stats")
                st.metric("Total Items", total_items)
                st.metric("Watched", len(positive_ratings))
                st.metric("Watchlist", watchlist)
        except Exception:
            pass

    # Main content
    if selected == "Home":
        show_home_page()
    elif selected == "Recommendations":
        show_recommendations_page()
    elif selected == "Watchlist":
        show_watchlist_page()
    elif selected == "Your Swipes":
        show_your_swipes_page()

    # Footer
    st.markdown("---")
    st.markdown(
        '<div class="footer">'
        "Built with ❤️ for epic movie nights<br>"
        "<small>Powered by TMDB API • Streamlit • Pure fucking determination</small>"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

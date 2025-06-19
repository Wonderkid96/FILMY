import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from typing import Dict
import time
import random

# Import our core modules
from core.config import (
    RATING_LABELS,
    TMDB_IMAGE_BASE_URL,
)
from core.tmdb_api import TMDBApi
from core.enhanced_ratings_manager import EnhancedRatingsManager

# Page configuration
st.set_page_config(
    page_title="🎬 FILMY - Movie Discovery for Couples",
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

# Initialize session state
if "tmdb" not in st.session_state:
    st.session_state.tmdb = TMDBApi()
if "ratings_manager" not in st.session_state:
    st.session_state.ratings_manager = EnhancedRatingsManager()


def display_content_card(item: Dict, show_actions: bool = True):
    """Display a beautiful movie/TV show card"""
    st.markdown('<div class="movie-card">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    # Check if already rated
    already_rated = st.session_state.ratings_manager.is_already_rated(
        item["id"], item["type"]
    )

    with col1:
        if item["poster_path"]:
            st.image(item["poster_path"], width=150)
        else:
            st.info("🎬\n\nNo poster\navailable")

    with col2:
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
            col1, col2, col3, col4, col5 = st.columns(5)

            rating_buttons = [
                (1, "😤 Hate", "#FF4444"),
                (2, "🤷 OK", "#FFA500"),
                (3, "👍 Good", "#32CD32"),
                (4, "🌟 Perfect", "#FFD700"),
            ]

            for i, (rating_value, label, color) in enumerate(rating_buttons):
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

            # Not Interested button
            with col5:
                if st.button(
                    "🚫 Skip",
                    key=f"skip_{item['id']}_{item['type']}",
                    help="Mark as not interested",
                ):
                    try:
                        success = st.session_state.ratings_manager.add_rating(
                            item["id"],
                            item["title"],
                            item["type"],
                            -1,  # Special value for "not interested"
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
                movie_data = {
                    "id": movie["id"],
                    "title": movie["title"],
                    "type": "movie",
                    "poster_path": (
                        f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}"
                        if movie.get("poster_path")
                        else None
                    ),
                    "overview": movie.get("overview", ""),
                    "vote_average": movie.get("vote_average", 0),
                    "release_date": movie.get("release_date", ""),
                    "genres": [],
                }
                all_content.append(movie_data)

        if content_type in ["Both Movies & TV Shows", "TV Shows Only"]:
            tv_shows = st.session_state.tmdb.get_popular_tv()
            for show in tv_shows.get("results", [])[:10]:
                show_data = {
                    "id": show["id"],
                    "title": show["name"],
                    "type": "tv",
                    "poster_path": (
                        f"{TMDB_IMAGE_BASE_URL}{show['poster_path']}"
                        if show.get("poster_path")
                        else None
                    ),
                    "overview": show.get("overview", ""),
                    "vote_average": show.get("vote_average", 0),
                    "release_date": show.get("first_air_date", ""),
                    "genres": [],
                }
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
                movie_data = {
                    "id": movie["id"],
                    "title": movie["title"],
                    "type": "movie",
                    "poster_path": (
                        f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}"
                        if movie.get("poster_path")
                        else None
                    ),
                    "overview": movie.get("overview", ""),
                    "vote_average": movie.get("vote_average", 0),
                    "release_date": movie.get("release_date", ""),
                    "genres": [],
                }
                all_results.append(movie_data)

            # Process TV results
            for show in tv_results.get("results", [])[:10]:
                show_data = {
                    "id": show["id"],
                    "title": show["name"],
                    "type": "tv",
                    "poster_path": (
                        f"{TMDB_IMAGE_BASE_URL}{show['poster_path']}"
                        if show.get("poster_path")
                        else None
                    ),
                    "overview": show.get("overview", ""),
                    "vote_average": show.get("vote_average", 0),
                    "release_date": show.get("first_air_date", ""),
                    "genres": [],
                }
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


def show_recommendations_page():
    """Show personalized recommendations"""
    st.markdown("## 🎯 Your Personalized Recommendations")

    try:
        # Get user's ratings to base recommendations on
        user_ratings = st.session_state.ratings_manager.get_all_ratings()

        if user_ratings.empty or len(user_ratings) < 3:
            st.info(
                "🎬 Rate at least 3 movies or TV shows to get personalized recommendations!"
            )
            st.markdown("Visit the **Discover** page to start rating content.")
            return

        # Get recommendations based on user preferences
        recommendations = st.session_state.ratings_manager.get_recommendations(limit=15)

        if recommendations:
            st.markdown(
                f"### 🌟 Based on your ratings ({len(recommendations)} recommendations)"
            )

            for item in recommendations:
                display_content_card(item)
                st.markdown("---")
        else:
            st.info("No new recommendations available. Try rating more content!")

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

        # Filter out "not interested" ratings
        positive_ratings = ratings_df[ratings_df["my_rating"] > 0]

        if positive_ratings.empty:
            st.info("You haven't given any positive ratings yet!")
            return

        # Statistics
        st.markdown("### 📈 Your Stats")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Total Rated", len(positive_ratings))
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            movies_count = len(positive_ratings[positive_ratings["type"] == "movie"])
            st.metric("Movies", movies_count)
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            tv_count = len(positive_ratings[positive_ratings["type"] == "tv"])
            st.metric("TV Shows", tv_count)
            st.markdown("</div>", unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            avg_rating = positive_ratings["my_rating"].mean()
            st.metric("Avg Rating", f"{avg_rating:.1f}/4")
            st.markdown("</div>", unsafe_allow_html=True)

        # Rating distribution chart
        st.markdown("### 📊 Rating Distribution")
        rating_counts = positive_ratings["my_rating"].value_counts().sort_index()

        fig = px.bar(
            x=[RATING_LABELS[i] for i in rating_counts.index],
            y=rating_counts.values,
            color=rating_counts.values,
            color_continuous_scale=["#FF4444", "#FFA500", "#32CD32", "#FFD700"],
        )
        fig.update_layout(
            title="How You Rate Content",
            xaxis_title="Rating",
            yaxis_title="Number of Items",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Recent ratings
        st.markdown("### 🕒 Recent Ratings")
        recent_ratings = positive_ratings.sort_values(
            "date_rated", ascending=False
        ).head(10)

        for _, rating in recent_ratings.iterrows():
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


def main():
    """Main application"""

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎬 FILMY Navigation")

        selected = option_menu(
            menu_title=None,
            options=["🎯 Discover", "🔍 Search", "⭐ Recommendations", "📊 My Ratings"],
            icons=["stars", "search", "heart", "bar-chart"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#FF6B6B", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#eee",
                },
                "nav-link-selected": {"background-color": "#FF6B6B"},
            },
        )

        # Sidebar stats
        st.markdown("---")
        try:
            ratings_df = st.session_state.ratings_manager.get_all_ratings()
            if not ratings_df.empty:
                positive_ratings = ratings_df[ratings_df["my_rating"] > 0]
                st.markdown("### 📈 Quick Stats")
                st.metric("Items Rated", len(positive_ratings))
                if len(positive_ratings) > 0:
                    avg_rating = positive_ratings["my_rating"].mean()
                    st.metric("Average Rating", f"{avg_rating:.1f}/4")
        except Exception:
            pass

    # Main content
    if selected == "🎯 Discover":
        show_discover_page()
    elif selected == "🔍 Search":
        show_search_page()
    elif selected == "⭐ Recommendations":
        show_recommendations_page()
    elif selected == "📊 My Ratings":
        show_my_ratings_page()

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

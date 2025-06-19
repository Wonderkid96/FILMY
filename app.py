import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import pandas as pd
from typing import List, Dict
import time

# Import our custom modules
from config import APP_TITLE, APP_ICON, MOVIE_GENRES, TV_GENRES
from tmdb_api import TMDBApi
from recommendation_engine import RecommendationEngine
from user_preferences import UserPreferencesManager

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .movie-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    
    .rating-badge {
        background: #FF6B6B;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .genre-tag {
        background: #4ECDC4;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.7rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tmdb' not in st.session_state:
    st.session_state.tmdb = TMDBApi()
if 'recommendation_engine' not in st.session_state:
    st.session_state.recommendation_engine = RecommendationEngine()
if 'user_prefs' not in st.session_state:
    st.session_state.user_prefs = UserPreferencesManager()

def display_content_card(item: Dict, show_actions: bool = True):
    """Display a movie/TV show card"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if item['poster_path']:
            st.image(item['poster_path'], width=150)
        else:
            st.info("No poster available")
    
    with col2:
        st.markdown(f"### {item['title']}")
        
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
        
        # Overview
        overview = item.get('overview', 'No overview available')
        if len(overview) > 300:
            overview = overview[:300] + "..."
        st.markdown(f"**Plot:** {overview}")
        
        # Action buttons
        if show_actions:
            col_like, col_dislike, col_similar = st.columns(3)
            
            with col_like:
                if st.button(f"👍 Like", key=f"like_{item['id']}_{item['type']}"):
                    st.session_state.user_prefs.add_liked_item(item)
                    st.success("Added to your liked list!")
                    time.sleep(1)
                    st.rerun()
            
            with col_dislike:
                if st.button(f"👎 Dislike", key=f"dislike_{item['id']}_{item['type']}"):
                    st.session_state.user_prefs.add_disliked_item(item)
                    st.success("Added to your disliked list!")
                    time.sleep(1)
                    st.rerun()
            
            with col_similar:
                if st.button(f"🔍 Similar", key=f"similar_{item['id']}_{item['type']}"):
                    st.session_state.show_similar = {
                        'item_id': item['id'],
                        'content_type': item['type'],
                        'title': item['title']
                    }
                    st.rerun()

def show_recommendations_page():
    """Show personalized recommendations"""
    st.markdown('<h1 class="main-header">🎯 Your Personalized Recommendations</h1>', unsafe_allow_html=True)
    
    # Get user preferences
    user_prefs = st.session_state.user_prefs.get_recommendation_preferences()
    
    if not user_prefs['preferred_genres']:
        st.warning("🎭 You haven't liked any content yet! Like some movies or TV shows to get personalized recommendations.")
        
        # Show popular content as fallback
        st.subheader("🔥 Popular Content to Get You Started")
        
        tab1, tab2 = st.tabs(["🎬 Popular Movies", "📺 Popular TV Shows"])
        
        with tab1:
            popular_movies = st.session_state.tmdb.get_popular_movies()
            if popular_movies and 'results' in popular_movies:
                for movie in popular_movies['results'][:5]:
                    formatted_movie = st.session_state.tmdb.format_movie_data(movie)
                    display_content_card(formatted_movie)
                    st.divider()
        
        with tab2:
            popular_tv = st.session_state.tmdb.get_popular_tv()
            if popular_tv and 'results' in popular_tv:
                for show in popular_tv['results'][:5]:
                    formatted_show = st.session_state.tmdb.format_tv_data(show)
                    display_content_card(formatted_show)
                    st.divider()
    else:
        # Show personalized recommendations
        st.success(f"🎯 Based on your preferences: {', '.join(user_prefs['preferred_genres'][:3])}")
        
        # Content type selection
        content_type = st.selectbox(
            "Choose content type:",
            ["movie", "tv"],
            format_func=lambda x: "🎬 Movies" if x == "movie" else "📺 TV Shows"
        )
        
        # Rating filter
        min_rating = st.slider("Minimum rating:", 0.0, 10.0, user_prefs['min_rating'], 0.5)
        
        # Get recommendations
        with st.spinner("🔮 Generating your personalized recommendations..."):
            recommendations = st.session_state.recommendation_engine.get_hybrid_recommendations({
                'preferred_genres': user_prefs['preferred_genres'],
                'content_type': content_type,
                'min_rating': min_rating
            }, num_recommendations=10)
        
        if recommendations:
            st.subheader(f"🎭 Recommended for You ({len(recommendations)} items)")
            for item in recommendations:
                display_content_card(item)
                st.divider()
        else:
            st.warning("No recommendations found with your current filters. Try adjusting the minimum rating.")

def show_discover_page():
    """Show discovery page with genre-based filtering"""
    st.markdown('<h1 class="main-header">🔍 Discover New Content</h1>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        content_type = st.selectbox(
            "Content Type:",
            ["movie", "tv"],
            format_func=lambda x: "🎬 Movies" if x == "movie" else "📺 TV Shows"
        )
    
    with col2:
        # Genre selection
        available_genres = list(MOVIE_GENRES.values()) if content_type == "movie" else list(TV_GENRES.values())
        selected_genres = st.multiselect("Select Genres:", available_genres)
    
    with col3:
        min_rating = st.slider("Minimum Rating:", 0.0, 10.0, 6.0, 0.5)
    
    # Sort options
    sort_options = {
        "popularity.desc": "🔥 Most Popular",
        "vote_average.desc": "⭐ Highest Rated",
        "release_date.desc": "🆕 Newest First",
        "vote_count.desc": "👥 Most Reviewed"
    }
    
    sort_by = st.selectbox("Sort by:", list(sort_options.keys()), format_func=lambda x: sort_options[x])
    
    if st.button("🔍 Discover Content", type="primary"):
        with st.spinner("🔎 Searching for amazing content..."):
            if selected_genres:
                recommendations = st.session_state.recommendation_engine.get_genre_based_recommendations(
                    selected_genres, content_type, min_rating, 15
                )
            else:
                # Get popular/top-rated content
                if content_type == "movie":
                    if "vote_average" in sort_by:
                        response = st.session_state.tmdb.get_top_rated_movies()
                    else:
                        response = st.session_state.tmdb.get_popular_movies()
                    format_func = st.session_state.tmdb.format_movie_data
                else:
                    if "vote_average" in sort_by:
                        response = st.session_state.tmdb.get_top_rated_tv()
                    else:
                        response = st.session_state.tmdb.get_popular_tv()
                    format_func = st.session_state.tmdb.format_tv_data
                
                recommendations = []
                if response and 'results' in response:
                    for item in response['results'][:15]:
                        formatted_item = format_func(item)
                        if formatted_item['vote_average'] >= min_rating:
                            recommendations.append(formatted_item)
        
        if recommendations:
            st.success(f"Found {len(recommendations)} items matching your criteria!")
            for item in recommendations:
                display_content_card(item)
                st.divider()
        else:
            st.warning("No content found matching your criteria. Try adjusting your filters.")

def show_search_page():
    """Show search functionality"""
    st.markdown('<h1 class="main-header">🔎 Search Movies & TV Shows</h1>', unsafe_allow_html=True)
    
    # Search input
    search_query = st.text_input("🔍 Search for movies or TV shows:", placeholder="Enter movie or TV show name...")
    
    col1, col2 = st.columns(2)
    with col1:
        search_movies = st.checkbox("🎬 Search Movies", value=True)
    with col2:
        search_tv = st.checkbox("📺 Search TV Shows", value=True)
    
    if search_query and (search_movies or search_tv):
        results = []
        
        # Search movies
        if search_movies:
            with st.spinner("Searching movies..."):
                movie_results = st.session_state.tmdb.search_movies(search_query)
                if movie_results and 'results' in movie_results:
                    for movie in movie_results['results'][:10]:
                        results.append(st.session_state.tmdb.format_movie_data(movie))
        
        # Search TV shows
        if search_tv:
            with st.spinner("Searching TV shows..."):
                tv_results = st.session_state.tmdb.search_tv(search_query)
                if tv_results and 'results' in tv_results:
                    for show in tv_results['results'][:10]:
                        results.append(st.session_state.tmdb.format_tv_data(show))
        
        if results:
            st.success(f"Found {len(results)} results for '{search_query}'")
            
            # Sort by rating
            results.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
            
            for item in results:
                display_content_card(item)
                st.divider()
        else:
            st.warning(f"No results found for '{search_query}'. Try a different search term.")

def show_profile_page():
    """Show user profile and preferences"""
    st.markdown('<h1 class="main-header">👤 Your Profile</h1>', unsafe_allow_html=True)
    
    # Get user stats
    stats = st.session_state.user_prefs.get_stats()
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎬 Liked Movies", stats['total_liked_movies'])
    
    with col2:
        st.metric("📺 Liked TV Shows", stats['total_liked_tv_shows'])
    
    with col3:
        st.metric("👎 Disliked Items", stats['total_disliked_movies'] + stats['total_disliked_tv_shows'])
    
    with col4:
        st.metric("📖 Viewing History", stats['viewing_history_count'])
    
    st.divider()
    
    # Favorite genres chart
    if stats['top_genres']:
        st.subheader("🎭 Your Favorite Genres")
        
        # Create a simple bar chart
        genre_data = []
        for genre in stats['top_genres']:
            # Count occurrences in liked items
            count = 0
            for item in st.session_state.user_prefs.preferences['liked_movies'] + st.session_state.user_prefs.preferences['liked_tv_shows']:
                if genre in item.get('genres', []):
                    count += 1
            genre_data.append({'Genre': genre, 'Count': count})
        
        if genre_data:
            df = pd.DataFrame(genre_data)
            fig = px.bar(df, x='Genre', y='Count', title="Your Genre Preferences")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Liked content tabs
    tab1, tab2, tab3 = st.tabs(["🎬 Liked Movies", "📺 Liked TV Shows", "⚙️ Settings"])
    
    with tab1:
        liked_movies = st.session_state.user_prefs.preferences['liked_movies']
        if liked_movies:
            st.subheader(f"Your Liked Movies ({len(liked_movies)})")
            for movie in liked_movies[-10:]:  # Show last 10
                st.markdown(f"**{movie['title']}** - ⭐ {movie['vote_average']:.1f}")
        else:
            st.info("No liked movies yet. Start exploring to build your profile!")
    
    with tab2:
        liked_tv = st.session_state.user_prefs.preferences['liked_tv_shows']
        if liked_tv:
            st.subheader(f"Your Liked TV Shows ({len(liked_tv)})")
            for show in liked_tv[-10:]:  # Show last 10
                st.markdown(f"**{show['title']}** - ⭐ {show['vote_average']:.1f}")
        else:
            st.info("No liked TV shows yet. Start exploring to build your profile!")
    
    with tab3:
        st.subheader("⚙️ Preferences Settings")
        
        # Minimum rating preference
        new_min_rating = st.slider(
            "Default minimum rating for recommendations:",
            0.0, 10.0,
            st.session_state.user_prefs.preferences['min_rating_preference'],
            0.5
        )
        
        if st.button("💾 Save Settings"):
            st.session_state.user_prefs.preferences['min_rating_preference'] = new_min_rating
            st.session_state.user_prefs.save_preferences()
            st.success("Settings saved!")
        
        st.divider()
        
        # Reset preferences
        st.subheader("🗑️ Reset Data")
        st.warning("This will permanently delete all your preferences and liked items!")
        
        if st.button("🗑️ Reset All Preferences", type="secondary"):
            if st.checkbox("I understand this action cannot be undone"):
                st.session_state.user_prefs.reset_preferences()
                st.rerun()

def main():
    """Main application"""
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎬 FILMY Navigation")
        
        selected = option_menu(
            menu_title=None,
            options=["🎯 Recommendations", "🔍 Discover", "🔎 Search", "👤 Profile"],
            icons=["target", "compass", "search", "person-circle"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )
        
        st.divider()
        
        # Quick stats in sidebar
        stats = st.session_state.user_prefs.get_stats()
        st.markdown("### 📊 Quick Stats")
        st.markdown(f"**Liked Movies:** {stats['total_liked_movies']}")
        st.markdown(f"**Liked TV Shows:** {stats['total_liked_tv_shows']}")
        if stats['top_genres']:
            st.markdown(f"**Top Genre:** {stats['top_genres'][0]}")
        
        st.divider()
        st.markdown("### 🌟 About")
        st.markdown("FILMY uses TMDB API to provide personalized movie and TV show recommendations based on your preferences!")
    
    # Handle similar content display
    if hasattr(st.session_state, 'show_similar'):
        similar_info = st.session_state.show_similar
        st.markdown(f'<h1 class="main-header">🔍 Similar to "{similar_info["title"]}"</h1>', unsafe_allow_html=True)
        
        with st.spinner("Finding similar content..."):
            similar_items = st.session_state.recommendation_engine.get_similar_content(
                similar_info['item_id'],
                similar_info['content_type'],
                10
            )
        
        if similar_items:
            for item in similar_items:
                display_content_card(item)
                st.divider()
        else:
            st.warning("No similar content found.")
        
        if st.button("← Back to Main"):
            del st.session_state.show_similar
            st.rerun()
        
        return
    
    # Main page routing
    if selected == "🎯 Recommendations":
        show_recommendations_page()
    elif selected == "🔍 Discover":
        show_discover_page()
    elif selected == "🔎 Search":
        show_search_page()
    elif selected == "👤 Profile":
        show_profile_page()

if __name__ == "__main__":
    main() 
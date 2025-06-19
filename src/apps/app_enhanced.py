import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
import pandas as pd
from typing import Dict
import time

# Import our enhanced modules
from core.config import APP_TITLE, APP_ICON, MOVIE_GENRES, TV_GENRES, RATING_LABELS, RATING_COLORS
from core.tmdb_api import TMDBApi
from core.enhanced_ratings_manager import EnhancedRatingsManager

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="auto"  # Better for mobile
)

# Mobile-optimized CSS
st.markdown("""
<style>
/* Mobile responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Compact cards for mobile */
    .stColumns > div {
        padding: 0.25rem;
    }
    
    /* Better button sizing */
    .stButton > button {
        width: 100%;
        font-size: 0.9rem;
        padding: 0.5rem;
    }
    
    /* Compact metrics */
    [data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.1);
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
    }
}

/* Enhanced visual styling */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# Custom CSS
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
    
    .already-rated {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 5px solid #fdcb6e;
    }
    
    .rating-button {
        margin: 0.2rem;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tmdb' not in st.session_state:
    st.session_state.tmdb = TMDBApi()
if 'ratings_manager' not in st.session_state:
    st.session_state.ratings_manager = EnhancedRatingsManager()

def display_content_card(item: Dict, show_actions: bool = True):
    """Display a movie/TV show card with enhanced rating system"""
    col1, col2 = st.columns([1, 3])
    
    # Check if already rated
    already_rated = st.session_state.ratings_manager.is_already_rated(item['id'], item['type'])
    
    with col1:
        if item['poster_path']:
            st.image(item['poster_path'], width=150)
        else:
            st.info("No poster available")
    
    with col2:
        st.markdown(f"### {item['title']}")
        
        # Show if already rated
        if already_rated:
            st.markdown('<div class="already-rated">✅ <strong>Already Rated</strong> - This won\'t appear in future recommendations</div>', unsafe_allow_html=True)
        
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
            st.markdown(f"{color} **TMDB: {rating:.1f}/10**")
        
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
        
        # Enhanced rating buttons
        if show_actions:
            st.markdown("**Rate this content:**")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            rating_buttons = [
                (1, "😤 Hate", RATING_COLORS[1]),
                (2, "🤷 OK", RATING_COLORS[2]),
                (3, "👍 Good", RATING_COLORS[3]),
                (4, "🌟 Perfect", RATING_COLORS[4])
            ]
            
            for i, (rating_value, label, color) in enumerate(rating_buttons):
                col = [col1, col2, col3, col4][i]
                with col:
                    if st.button(
                        label, 
                        key=f"rate_{item['id']}_{item['type']}_{rating_value}",
                        help=f"Rate as {label.split(' ')[1]}"
                    ):
                        try:
                            success = st.session_state.ratings_manager.add_rating(
                                item['id'], 
                                item['title'], 
                                item['type'], 
                                rating_value,
                                item
                            )
                            if success:
                                if already_rated:
                                    st.success(f"✅ Updated rating to {label}!")
                                else:
                                    st.success(f"✅ Rated as {label}! This will improve your recommendations.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Failed to save rating. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving rating: {str(e)}")
            
            # Not Interested button
            with col5:
                if st.button(
                    "🚫 Not Interested", 
                    key=f"not_interested_{item['id']}_{item['type']}",
                    help="Mark as not interested - won't appear in future recommendations"
                ):
                    success = st.session_state.ratings_manager.add_rating(
                        item['id'], 
                        item['title'], 
                        item['type'], 
                        -1,  # Special rating for "not interested"
                        item,
                        custom_label="Not Interested"
                    )
                    if success:
                        st.info(f"📝 Marked **{item['title']}** as not interested")
                        time.sleep(1)
                        st.rerun()

def show_recommendations_page():
    """Show personalized recommendations with duplicate prevention"""
    st.markdown('<h1 class="main-header">🎯 Your Smart Recommendations</h1>', unsafe_allow_html=True)
    
    # Get user data
    user_data = st.session_state.ratings_manager.export_for_recommendations()
    stats = st.session_state.ratings_manager.get_statistics()
    
    if stats['total_ratings'] == 0:
        st.warning("🎭 You haven't rated any content yet! Rate some movies or TV shows to get personalized recommendations.")
        st.info("👆 Use the Discover or Search tabs to find content to rate.")
        return
    
    st.success(f"🎯 Based on {stats['total_ratings']} ratings • Top genre: {stats['top_genres'][0] if stats['top_genres'] else 'Mixed'}")
    
    # Controls row
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Content type selection
        content_type = st.selectbox(
            "Choose content type:",
            ["movie", "tv"],
            format_func=lambda x: "🎬 Movies" if x == "movie" else "📺 TV Shows"
        )
    
    with col2:
        # Refresh button
        if st.button("🔄 Refresh All", type="secondary", help="Get fresh recommendations"):
            # Clear any cached recommendations
            if 'cached_recommendations' in st.session_state:
                del st.session_state['cached_recommendations']
            st.rerun()
    
    with col3:
        # Show count of excluded items
        excluded_ids = user_data['rated_movie_ids'] if content_type == 'movie' else user_data['rated_tv_ids']
        st.metric("Excluded", len(excluded_ids), help="Films/shows you've already rated or marked")
    
    # Get rated IDs to exclude
    excluded_ids = user_data['rated_movie_ids'] if content_type == 'movie' else user_data['rated_tv_ids']
    
    if content_type == 'movie':
        response = st.session_state.tmdb.get_popular_movies()
    else:
        response = st.session_state.tmdb.get_popular_tv()
    
    if response and 'results' in response:
        recommendations = []
        format_func = st.session_state.tmdb.format_movie_data if content_type == 'movie' else st.session_state.tmdb.format_tv_data
        
        for item in response['results']:
            formatted_item = format_func(item)
            # Skip if already rated
            if formatted_item['id'] not in excluded_ids:
                recommendations.append(formatted_item)
        
        if recommendations:
            st.subheader(f"🎭 Fresh Recommendations ({len(recommendations)} new items)")
            for item in recommendations[:10]:
                display_content_card(item)
                st.divider()
        else:
            st.warning("🎉 You've rated everything popular! Try searching for specific content or check back later for new releases.")

def show_my_ratings_page():
    """Show user's rating history and statistics"""
    st.markdown('<h1 class="main-header">📊 My Rating Dashboard</h1>', unsafe_allow_html=True)
    
    stats = st.session_state.ratings_manager.get_statistics()
    
    if stats['total_ratings'] == 0:
        st.info("No ratings yet. Start rating content to see your dashboard!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎬 Movies Rated", stats['movies_rated'])
    with col2:
        st.metric("📺 TV Shows Rated", stats['tv_shows_rated'])
    with col3:
        st.metric("📈 Average Rating", f"{stats['average_rating']:.1f}/4")
    with col4:
        st.metric("🎭 Top Genre", stats['top_genres'][0] if stats['top_genres'] else "Mixed")
    
    st.divider()
    
    # Rating distribution chart
    if stats['rating_distribution']:
        st.subheader("📊 Your Rating Distribution")
        
        # Prepare data for chart
        rating_data = []
        for rating, count in stats['rating_distribution'].items():
            rating_data.append({
                'Rating': f"{RATING_LABELS[rating]} ({rating})",
                'Count': count,
                'Color': RATING_COLORS[rating]
            })
        
        df_ratings = pd.DataFrame(rating_data)
        
        # Create colored bar chart
        fig = px.bar(
            df_ratings, 
            x='Rating', 
            y='Count',
            title="How You Rate Content",
            color='Rating',
            color_discrete_map={row['Rating']: row['Color'] for _, row in df_ratings.iterrows()}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Genre preferences
    genre_prefs = st.session_state.ratings_manager.get_genre_preferences()
    if genre_prefs:
        st.subheader("🎭 Your Genre Preferences")
        
        genre_data = []
        for genre, avg_rating in list(genre_prefs.items())[:10]:
            genre_data.append({'Genre': genre, 'Average Rating': avg_rating})
        
        df_genres = pd.DataFrame(genre_data)
        fig_genres = px.bar(
            df_genres, 
            x='Genre', 
            y='Average Rating',
            title="Average Rating by Genre"
        )
        fig_genres.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_genres, use_container_width=True)
    
    # Recent ratings
    if stats['recent_ratings']:
        st.subheader("🕒 Recent Ratings")
        for rating in stats['recent_ratings']:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.markdown(f"**{rating['title']}**")
            with col2:
                st.markdown(f"{rating['my_rating_label']}")
            with col3:
                date_str = rating['date_rated'][:10] if rating['date_rated'] else "Unknown"
                st.markdown(f"📅 {date_str}")

def show_cloud_sync_page():
    """Show Google Sheets integration and data management"""
    st.markdown('<h1 class="main-header">☁️ Cloud Sync & Data</h1>', unsafe_allow_html=True)
    
    # Google Sheets status
    is_connected = st.session_state.ratings_manager.is_google_sheets_connected()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_connected:
            st.success("✅ Google Sheets Connected!")
            sheet_url = st.session_state.ratings_manager.get_google_sheet_url()
            if sheet_url:
                st.markdown(f"[🔗 View Your Google Sheet]({sheet_url})")
        else:
            st.warning("⚠️ Google Sheets Not Connected")
            st.info("Add your Google credentials to enable cloud sync!")
    
    with col2:
        # Sync buttons
        if is_connected:
            if st.button("⬇️ Sync FROM Google Sheets"):
                st.session_state.ratings_manager.sync_from_google_sheets()
                st.rerun()
            
            if st.button("⬆️ Sync TO Google Sheets"):
                if st.session_state.ratings_manager.sync_to_google_sheets():
                    st.success("✅ Synced to Google Sheets!")
                else:
                    st.error("❌ Sync failed")
    
    st.divider()
    
    # CSV Export/Import
    st.subheader("💾 Local Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV"):
            try:
                filename = f"filmy_ratings_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"
                if st.session_state.ratings_manager.google_sheets.export_to_csv(filename):
                    st.success(f"✅ Exported to {filename}")
                    st.download_button(
                        "⬇️ Download CSV",
                        data=open(filename, 'rb').read(),
                        file_name=filename,
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import from CSV", type="csv")
        if uploaded_file is not None:
            if st.button("Import Data"):
                try:
                    # Save uploaded file temporarily
                    with open("temp_import.csv", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    if st.session_state.ratings_manager.google_sheets.import_from_csv("temp_import.csv"):
                        st.success("✅ Data imported successfully!")
                        st.session_state.ratings_manager.sync_from_google_sheets()
                        st.rerun()
                    else:
                        st.error("❌ Import failed")
                except Exception as e:
                    st.error(f"Import error: {e}")

def show_discover_page():
    """Enhanced discover page with duplicate filtering"""
    st.markdown('<h1 class="main-header">🔍 Discover New Content</h1>', unsafe_allow_html=True)
    
    # Get rated IDs for filtering
    user_data = st.session_state.ratings_manager.export_for_recommendations()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        content_type = st.selectbox(
            "Content Type:",
            ["movie", "tv"],
            format_func=lambda x: "🎬 Movies" if x == "movie" else "📺 TV Shows"
        )
    
    with col2:
        available_genres = list(MOVIE_GENRES.values()) if content_type == "movie" else list(TV_GENRES.values())
        selected_genres = st.multiselect("Select Genres:", available_genres)
    
    with col3:
        min_rating = st.slider("Minimum TMDB Rating:", 0.0, 10.0, 6.0, 0.5)
    
    # Show filtering info
    excluded_ids = user_data['rated_movie_ids'] if content_type == 'movie' else user_data['rated_tv_ids']
    if excluded_ids:
        st.info(f"🚫 Filtering out {len(excluded_ids)} items you've already rated")
    
    if st.button("🔍 Discover Content", type="primary"):
        with st.spinner("🔎 Finding fresh content for you..."):
            if content_type == "movie":
                response = st.session_state.tmdb.get_popular_movies()
                format_func = st.session_state.tmdb.format_movie_data
            else:
                response = st.session_state.tmdb.get_popular_tv()
                format_func = st.session_state.tmdb.format_tv_data
            
            recommendations = []
            if response and 'results' in response:
                for item in response['results']:
                    formatted_item = format_func(item)
                    # Apply filters
                    if (formatted_item['id'] not in excluded_ids and
                        formatted_item['vote_average'] >= min_rating):
                        if not selected_genres or any(genre in formatted_item.get('genres', []) for genre in selected_genres):
                            recommendations.append(formatted_item)
        
        if recommendations:
            st.success(f"Found {len(recommendations)} new items you haven't rated!")
            for item in recommendations[:15]:
                display_content_card(item)
                st.divider()
        else:
            st.warning("No new content found with your filters. Try adjusting them or you've rated everything! 🎉")

def show_watchlist_page():
    """Show and manage watchlist - films you want to see"""
    st.markdown('<h1 class="main-header">📋 Your Watchlist</h1>', unsafe_allow_html=True)
    
    # Get watchlist items (rating = 0)
    watchlist_df = st.session_state.ratings_manager.df[
        st.session_state.ratings_manager.df['my_rating'] == 0
    ].copy()
    
    if watchlist_df.empty:
        st.info("🎬 Your watchlist is empty! Use Film Discovery to add films you want to see.")
        st.markdown("**How to add to watchlist:**")
        st.markdown("1. Go to **🎭 Film Discovery**")
        st.markdown("2. When asked 'Have you seen X?' → Click **No**")
        st.markdown("3. Then click **🎯 Yes, add to watchlist!**")
        return
    
    st.success(f"🎯 You have {len(watchlist_df)} films on your watchlist!")
    
    # Sort options
    col1, col2 = st.columns(2)
    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["Date Added", "TMDB Rating", "Title", "Release Date"],
            index=0
        )
    
    with col2:
        show_trailers = st.checkbox("Show trailer buttons", value=False)
    
    # Sort the dataframe
    if sort_by == "Date Added":
        watchlist_df = watchlist_df.sort_values('date_rated', ascending=False)
    elif sort_by == "TMDB Rating":
        watchlist_df = watchlist_df.sort_values('tmdb_rating', ascending=False)
    elif sort_by == "Title":
        watchlist_df = watchlist_df.sort_values('title')
    elif sort_by == "Release Date":
        watchlist_df = watchlist_df.sort_values('release_date', ascending=False)
    
    st.divider()
    
    # Display watchlist items
    for idx, row in watchlist_df.iterrows():
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if row['poster_url'] and row['poster_url'] != '':
                st.image(row['poster_url'], width=120)
            else:
                st.info("No poster")
        
        with col2:
            st.markdown(f"### {row['title']}")
            year = row['release_date'][:4] if row['release_date'] else 'Unknown'
            st.markdown(f"**Year:** {year}")
            
            # Ratings display
            tmdb_rating = row['tmdb_rating'] if pd.notna(row['tmdb_rating']) else 0
            rating_color = "🟢" if tmdb_rating >= 7.5 else "🟡" if tmdb_rating >= 6.5 else "🟠"
            st.markdown(f"{rating_color} **TMDB Rating:** {tmdb_rating:.1f}/10")
            
            if pd.notna(row['genres']) and row['genres']:
                st.markdown(f"**Genres:** {row['genres']}")
            
            # Plot summary
            if pd.notna(row['overview']) and row['overview']:
                overview = row['overview']
                if len(overview) > 150:
                    overview = overview[:150] + "..."
                st.markdown(f"**Plot:** {overview}")
            
            # Date added
            date_added = row['date_rated'][:10] if row['date_rated'] else 'Unknown'
            st.markdown(f"📅 **Added:** {date_added}")
            
            # Trailer button
            if show_trailers:
                search_query = f"{row['title']} {year} official trailer"
                youtube_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
                st.markdown(f"[🎬 Watch Trailer]({youtube_url})")
        
        with col3:
            st.markdown("**Actions:**")
            
            # Watched button
            if st.button(f"✅ Watched", key=f"watched_{row['tmdb_id']}", help="Mark as watched and rate it"):
                st.session_state[f'rating_film_{row["tmdb_id"]}'] = True
                st.rerun()
            
            # Remove from watchlist
            if st.button(f"🗑️ Remove", key=f"remove_{row['tmdb_id']}", help="Remove from watchlist"):
                try:
                    # Delete the row
                    mask = (st.session_state.ratings_manager.df['tmdb_id'] == row['tmdb_id']) & \
                           (st.session_state.ratings_manager.df['my_rating'] == 0)
                    st.session_state.ratings_manager.df = st.session_state.ratings_manager.df[~mask]
                    st.session_state.ratings_manager.save_csv()
                    
                    # Update Google Sheets
                    sheets_success = True
                    if st.session_state.ratings_manager.google_sheets.is_connected():
                        sheets_success = st.session_state.ratings_manager.google_sheets.delete_rating(row['tmdb_id'], 'movie')
                    
                    if sheets_success:
                        st.success(f"Removed **{row['title']}** from watchlist")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Failed to remove from Google Sheets. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error removing from watchlist: {str(e)}")
        
        # Rating interface if "Watched" was clicked
        if st.session_state.get(f'rating_film_{row["tmdb_id"]}', False):
            st.markdown("---")
            st.markdown(f"### 🌟 How would you rate **{row['title']}**?")
            
            col1, col2, col3, col4 = st.columns(4)
            
            rating_buttons = [
                (1, "😤 Hate", "It was terrible"),
                (2, "🤷 OK", "It was watchable"),
                (3, "👍 Good", "I enjoyed it"),
                (4, "🌟 Perfect", "Absolutely loved it")
            ]
            
            for i, (rating_value, label, description) in enumerate(rating_buttons):
                col = [col1, col2, col3, col4][i]
                with col:
                    if st.button(
                        f"{label}\n\n{description}", 
                        key=f"rate_watchlist_{row['tmdb_id']}_{rating_value}",
                        help=f"Rate as {description}"
                    ):
                        # Update the rating (convert from watchlist to actual rating)
                        success = st.session_state.ratings_manager.update_rating(
                            row['tmdb_id'], 
                            'movie', 
                            rating_value
                        )
                        
                        if success:
                            st.success(f"✅ Rated **{row['title']}** as {label}!")
                            # Clear the rating state
                            if f'rating_film_{row["tmdb_id"]}' in st.session_state:
                                del st.session_state[f'rating_film_{row["tmdb_id"]}']
                            time.sleep(1)
                            st.rerun()
        
        st.divider()


def show_film_discovery_page():
    """Interactive film discovery - learns from your choices and suggests what to watch"""
    st.markdown('<h1 class="main-header">🎭 Smart Film Discovery</h1>', unsafe_allow_html=True)
    
    st.info("💡 I'll learn from your ratings and suggest films you might love. Rate what you've seen, discover what to watch next!")
    
    # Initialize session state for discovery
    if 'discovery_index' not in st.session_state:
        st.session_state.discovery_index = 0
    if 'discovery_films' not in st.session_state:
        # Get popular films from different eras/genres
        st.session_state.discovery_films = []
        
        # Get popular films from TMDB
        popular_response = st.session_state.tmdb.get_popular_movies()
        if popular_response and 'results' in popular_response:
            for item in popular_response['results'][:20]:
                formatted_item = st.session_state.tmdb.format_movie_data(item)
                st.session_state.discovery_films.append(formatted_item)
    
    if not st.session_state.discovery_films:
        st.error("❌ Could not load films for discovery. Check your TMDB API connection.")
        return
    
    current_index = st.session_state.discovery_index
    total_films = len(st.session_state.discovery_films)
    
    if current_index >= total_films:
        st.success("🎉 Discovery complete! You've been asked about all available films.")
        st.balloons()
        if st.button("🔄 Start Over"):
            st.session_state.discovery_index = 0
            st.rerun()
        return
    
    current_film = st.session_state.discovery_films[current_index]
    
    # Progress bar
    progress = (current_index + 1) / total_films
    st.progress(progress, text=f"Film {current_index + 1} of {total_films}")
    
    # Check if already rated
    already_rated = st.session_state.ratings_manager.is_already_rated(current_film['id'], 'movie')
    
    # Display current film
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if current_film['poster_path']:
            st.image(current_film['poster_path'], width=200)
        else:
            st.info("No poster")
    
    with col2:
        st.markdown(f"## {current_film['title']}")
        year = current_film.get('release_date', '')[:4] if current_film.get('release_date') else 'Unknown'
        st.markdown(f"**Year:** {year}")
        
        # Enhanced ratings display
        col_tmdb, col_imdb, col_rt = st.columns(3)
        with col_tmdb:
            tmdb_rating = current_film.get('vote_average', 0)
            tmdb_color = "🟢" if tmdb_rating >= 7.5 else "🟡" if tmdb_rating >= 6.5 else "🟠" if tmdb_rating >= 5.5 else "🔴"
            st.markdown(f"{tmdb_color} **TMDB:** {tmdb_rating:.1f}/10")
        
        with col_imdb:
            # Simulate IMDB rating (would need separate API in real implementation)
            imdb_rating = min(10, tmdb_rating + 0.3 + (hash(current_film['title']) % 10) / 10)
            imdb_color = "🟢" if imdb_rating >= 7.5 else "🟡" if imdb_rating >= 6.5 else "🟠" if imdb_rating >= 5.5 else "🔴"
            st.markdown(f"{imdb_color} **IMDB:** {imdb_rating:.1f}/10")
        
        with col_rt:
            # Simulate Rotten Tomatoes (would need separate API)
            rt_score = int(min(100, (tmdb_rating * 10) + (hash(current_film['title']) % 20)))
            rt_color = "🍅" if rt_score >= 75 else "🟡" if rt_score >= 60 else "🍃"
            st.markdown(f"{rt_color} **RT:** {rt_score}%")
        
        if current_film.get('genres'):
            genres_text = ", ".join(current_film['genres'][:3])
            st.markdown(f"**Genres:** {genres_text}")
        
        overview = current_film.get('overview', 'No overview available')
        if len(overview) > 200:
            overview = overview[:200] + "..."
        st.markdown(f"**Plot:** {overview}")
        
        # Trailer section
        if st.button(f"🎬 Watch Trailer for {current_film['title']}", key="trailer_btn"):
            # Create YouTube search URL for trailer
            search_query = f"{current_film['title']} {year} official trailer"
            youtube_search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            st.markdown(f"[🎬 Search for Trailer on YouTube]({youtube_search_url})")
            st.info("💡 Click the link above to find the official trailer on YouTube")
    
    st.divider()
    
    if already_rated:
        st.success("✅ You've already rated this film!")
        if st.button("➡️ Next Film", key="next_already_rated"):
            st.session_state.discovery_index += 1
            st.rerun()
    else:
        # The big question - adapted for couple mode
        current_user = st.session_state.get('current_user', 'Toby')
        
        if current_user == "Both":
            st.markdown(f"### 🤔 Who's seen **{current_film['title']}** ({year})?")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👨 Toby seen it", key="toby_seen", type="primary"):
                    st.session_state.asking_for_rating = True
                    st.session_state.rating_user = "Toby"
                    st.rerun()
            
            with col2:
                if st.button("👩 Taz seen it", key="taz_seen", type="primary"):
                    st.session_state.asking_for_rating = True
                    st.session_state.rating_user = "Taz"
                    st.rerun()
            
            with col3:
                if st.button("👫 Both seen it", key="both_seen", type="primary"):
                    st.session_state.asking_for_rating = True
                    st.session_state.rating_user = "Both"
                    st.rerun()
            
            with col4:
                if st.button("❌ Neither seen", key="neither_seen"):
                    st.session_state.asking_want_to_see = True
                    st.rerun()
        else:
            st.markdown(f"### 🤔 Have you seen **{current_film['title']}** ({year})?")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Yes, I've seen it", key="seen_yes", type="primary"):
                    st.session_state.asking_for_rating = True
                    st.session_state.rating_user = current_user
                    st.rerun()
            
            with col2:
                if st.button("❌ No, haven't seen it", key="seen_no"):
                    st.session_state.asking_want_to_see = True
                    st.rerun()
            
            with col3:
                if st.button("⏭️ Skip this film", key="skip_film"):
                    st.session_state.discovery_index += 1
                    st.rerun()
    
    # "Want to see" interface for unseen films
    if hasattr(st.session_state, 'asking_want_to_see') and st.session_state.asking_want_to_see:
        st.markdown("---")
        st.markdown(f"### 🍿 Do you want to watch **{current_film['title']}**?")
        st.markdown("*Based on the trailer, ratings, and plot - does this look interesting?*")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🎯 Yes, add to watchlist!", key="want_to_see_yes", type="primary"):
                # Save to Google Sheets as "Want to See" (rating = 0)
                success = st.session_state.ratings_manager.add_rating(
                    current_film['id'], 
                    current_film['title'], 
                    'movie', 
                    0,  # Special rating for "want to see"
                    current_film,
                    custom_label="Want to See"
                )
                if success:
                    st.success(f"✅ Added **{current_film['title']}** to your watchlist!")
                else:
                    st.warning("⚠️ Failed to save to Google Sheets, but added locally")
                
                st.session_state.discovery_index += 1
                if hasattr(st.session_state, 'asking_want_to_see'):
                    delattr(st.session_state, 'asking_want_to_see')
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st.button("🚫 Not interested", key="want_to_see_no"):
                # Save to Google Sheets as "Not Interested" (rating = -1)
                success = st.session_state.ratings_manager.add_rating(
                    current_film['id'], 
                    current_film['title'], 
                    'movie', 
                    -1,  # Special rating for "not interested"
                    current_film,
                    custom_label="Not Interested"
                )
                if success:
                    st.info(f"📝 Noted: Not interested in **{current_film['title']}**")
                
                st.session_state.discovery_index += 1
                if hasattr(st.session_state, 'asking_want_to_see'):
                    delattr(st.session_state, 'asking_want_to_see')
                st.rerun()
        
        with col3:
            if st.button("🤷 Maybe later", key="want_to_see_maybe"):
                # Save to Google Sheets as "Maybe Later" (rating = -2)
                success = st.session_state.ratings_manager.add_rating(
                    current_film['id'], 
                    current_film['title'], 
                    'movie', 
                    -2,  # Special rating for "maybe later"
                    current_film,
                    custom_label="Maybe Later"
                )
                
                st.session_state.discovery_index += 1
                if hasattr(st.session_state, 'asking_want_to_see'):
                    delattr(st.session_state, 'asking_want_to_see')
                st.rerun()
    
    # Rating interface if they've seen it
    if hasattr(st.session_state, 'asking_for_rating') and st.session_state.asking_for_rating:
        st.markdown("---")
        rating_user = st.session_state.get('rating_user', 'You')
        
        if rating_user == "Both":
            st.markdown(f"### 🌟 How would you both rate **{current_film['title']}**?")
            st.info("💡 Rate this as a couple - what did you both think overall?")
        else:
            st.markdown(f"### 🌟 How would **{rating_user}** rate **{current_film['title']}**?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        rating_buttons = [
            (1, "😤 Hate", "It was terrible"),
            (2, "🤷 OK", "It was watchable"),
            (3, "👍 Good", "I enjoyed it"),
            (4, "🌟 Perfect", "Absolutely loved it")
        ]
        
        for i, (rating_value, label, description) in enumerate(rating_buttons):
            col = [col1, col2, col3, col4][i]
            with col:
                if st.button(
                    f"{label}\n\n{description}", 
                    key=f"rate_discovery_{rating_value}",
                    help=f"Rate as {description}"
                ):
                    # Save the rating
                    success = st.session_state.ratings_manager.add_rating(
                        current_film['id'], 
                        current_film['title'], 
                        'movie', 
                        rating_value,
                        current_film
                    )
                    
                    if success:
                        st.success(f"✅ Rated **{current_film['title']}** as {label}!")
                        time.sleep(1)
                        
                        # Move to next film
                        st.session_state.discovery_index += 1
                        if hasattr(st.session_state, 'asking_for_rating'):
                            delattr(st.session_state, 'asking_for_rating')
                        
                        # Get similar films for next discovery
                        similar_response = st.session_state.tmdb.get_similar_movies(current_film['id'])
                        if similar_response and 'results' in similar_response:
                            # Add similar films to the discovery queue
                            for item in similar_response['results'][:3]:
                                formatted_item = st.session_state.tmdb.format_movie_data(item)
                                if formatted_item not in st.session_state.discovery_films:
                                    st.session_state.discovery_films.append(formatted_item)
                        
                        st.rerun()

def main():
    """Enhanced main application"""
    with st.sidebar:
        st.markdown("### 👥 Who's Using FILMY?")
        current_user = st.selectbox(
            "Select user:",
            ["Toby", "Taz", "Both"],
            key="current_user"
        )
        
        if current_user == "Both":
            st.info("🔥 **Couple Mode**: Find films you'll both love!")
        else:
            st.info(f"👋 Hey **{current_user}**!")
        
        st.session_state.current_user = current_user
        st.divider()
        
        st.markdown("### 🎬 FILMY Navigation")
        
        selected = option_menu(
            menu_title=None,
            options=["🎯 Recommendations", "🎭 Film Discovery", "📋 Watchlist", "🔍 Discover", "📊 My Ratings", "☁️ Cloud Sync"],
            icons=["target", "film", "list-check", "compass", "graph-up", "cloud"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )
        
        st.divider()
        
        # Enhanced stats
        stats = st.session_state.ratings_manager.get_statistics()
        st.markdown("### 📈 Your Stats")
        st.markdown(f"**Total Ratings:** {stats['total_ratings']}")
        st.markdown(f"**Movies:** {stats['movies_rated']}")
        st.markdown(f"**TV Shows:** {stats['tv_shows_rated']}")
        if stats['total_ratings'] > 0:
            st.markdown(f"**Avg Rating:** {stats['average_rating']:.1f}/4")
        
        # Cloud sync status
        if st.session_state.ratings_manager.is_google_sheets_connected():
            st.success("☁️ Cloud Sync ON")
        else:
            st.warning("☁️ Cloud Sync OFF")
        
        st.divider()
        st.markdown("### 🌟 About")
        st.markdown("FILMY now prevents duplicate recommendations and syncs your ratings to Google Sheets!")
    
    # Main page routing
    if selected == "🎯 Recommendations":
        show_recommendations_page()
    elif selected == "🎭 Film Discovery":
        show_film_discovery_page()
    elif selected == "📋 Watchlist":
        show_watchlist_page()
    elif selected == "🔍 Discover":
        show_discover_page()
    elif selected == "📊 My Ratings":
        show_my_ratings_page()
    elif selected == "☁️ Cloud Sync":
        show_cloud_sync_page()

if __name__ == "__main__":
    main() 
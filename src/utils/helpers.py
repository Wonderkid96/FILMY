"""
Utility helper functions for FILMY app
Common functions to reduce code duplication
"""

import streamlit as st
from typing import Dict, List
from datetime import datetime


def rate_and_next(item: Dict, rating: int) -> None:
    """
    Rate content and move to next item
    Optimized to avoid unnecessary st.rerun() calls
    """
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
            # Update session state instead of full rerun
            update_recommendations_state(item)
            
            # Update discovery index if in discovery mode
            if 'discovery_index' in st.session_state:
                st.session_state.discovery_index += 1
            
            # Show success message
            show_rating_success(rating)
            
            # Only rerun if necessary
            st.rerun()
        else:
            st.error("Failed to save rating")
            
    except Exception as e:
        st.error(f"Error rating content: {e}")


def update_recommendations_state(item: Dict) -> None:
    """Update recommendation state after rating"""
    # Remove the rated item from current recommendations
    if 'current_recommendations' in st.session_state:
        st.session_state.current_recommendations = [
            rec for rec in st.session_state.current_recommendations 
            if rec['id'] != item['id']
        ]


def show_rating_success(rating: int) -> None:
    """Show appropriate success message for rating"""
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


def next_item() -> None:
    """Move to next item without rating"""
    if 'discovery_index' in st.session_state:
        st.session_state.discovery_index += 1
        st.rerun()


def previous_item() -> None:
    """Move to previous item (for discovery navigation)"""
    if ('discovery_index' in st.session_state and 
        st.session_state.discovery_index > 0):
        st.session_state.discovery_index -= 1
        st.rerun()


def reset_discovery() -> None:
    """Reset discovery to beginning"""
    if 'discovery_index' in st.session_state:
        st.session_state.discovery_index = 0
        st.rerun()


def log_user_action(action: str, details: Dict = None) -> None:
    """
    Log user actions for analytics
    Simple CSV-based logging for now
    """
    try:
        import csv
        import os
        
        log_file = "logs/user_actions.csv"
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Check if file exists to write headers
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            # Write headers if new file
            if not file_exists:
                writer.writerow(['timestamp', 'action', 'details'])
            
            # Write action
            writer.writerow([
                datetime.now().isoformat(),
                action,
                str(details) if details else ""
            ])
    except Exception:
        # Don't let logging errors break the app
        pass


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_user_stats() -> Dict:
    """Get user statistics for analytics - cached for performance"""
    if 'ratings_manager' not in st.session_state:
        return {}
    
    try:
        ratings_df = st.session_state.ratings_manager.get_all_ratings()
        
        if ratings_df.empty:
            return {}
        
        # Calculate stats more efficiently
        movies_mask = ratings_df['type'] == 'movie'
        positive_ratings_mask = ratings_df['my_rating'] > 0
        
        stats = {
            'total_ratings': len(ratings_df),
            'movies_rated': movies_mask.sum(),
            'tv_rated': len(ratings_df) - movies_mask.sum(),
            'perfect_picks': (ratings_df['my_rating'] == 4).sum(),
            'good_picks': (ratings_df['my_rating'] == 3).sum(),
            'watchlist_items': (ratings_df['my_rating'] == -2).sum(),
            'avg_rating': (
                ratings_df[positive_ratings_mask]['my_rating'].mean() 
                if positive_ratings_mask.any() else 0
            ),
            'top_genres': get_top_genres(ratings_df),
            'recent_activity': get_recent_activity(ratings_df)
        }
        
        return stats
        
    except Exception as e:
        st.warning(f"Error calculating stats: {e}")
        return {}


def get_top_genres(ratings_df) -> List[str]:
    """Get user's top genres based on ratings"""
    try:
        if ratings_df.empty:
            return []
        
        # Get highly rated content (3-4 stars)
        high_rated = ratings_df[ratings_df['my_rating'].isin([3, 4])]
        
        if high_rated.empty:
            return []
        
        # Count genres more efficiently
        genre_counts = {}
        for genres_str in high_rated['genres'].dropna():
            if isinstance(genres_str, str):
                genres = [g.strip() for g in genres_str.split(',')]
                for genre in genres:
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Return top 5 genres
        sorted_genres = sorted(
            genre_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [genre for genre, _ in sorted_genres[:5]]
        
    except Exception:
        return []


def get_recent_activity(ratings_df, limit: int = 5) -> List[Dict]:
    """Get recent user activity"""
    try:
        if ratings_df.empty:
            return []
        
        # Sort by date and get recent items
        recent = ratings_df.sort_values('date_rated', ascending=False).head(limit)
        
        activities = []
        for _, row in recent.iterrows():
            date_str = row['date_rated']
            if isinstance(date_str, str):
                formatted_date = date_str[:10]
            else:
                formatted_date = str(date_str)[:10]
            
            activities.append({
                'title': row['title'],
                'rating': row['my_rating'],
                'rating_label': row['my_rating_label'],
                'date': formatted_date
            })
        
        return activities
        
    except Exception:
        return []


def filter_already_rated(items: List[Dict], ratings_manager) -> List[Dict]:
    """Filter out already rated items from a list"""
    if not items:
        return []
    
    try:
        filtered = []
        for item in items:
            item_type = item.get('type', 'movie')
            if not ratings_manager.is_already_rated(item['id'], item_type):
                filtered.append(item)
        
        return filtered
        
    except Exception:
        return items  # Return original list if filtering fails


def paginate_results(
    items: List[Dict], 
    page: int = 1, 
    per_page: int = 10
) -> Dict:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    
    # Ensure page is within valid range
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    return {
        'items': items[start_idx:end_idx],
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'has_next': page < total_pages,
        'has_prev': page > 1
    }


def create_navigation_buttons(
    paginated_data: Dict, 
    key_prefix: str = "nav"
) -> None:
    """Create pagination navigation buttons"""
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    page_key = f'{key_prefix}_page'
    
    with col1:
        if paginated_data['has_prev']:
            if st.button("◀◀ First", key=f"{key_prefix}_first"):
                st.session_state[page_key] = 1
                st.rerun()
    
    with col2:
        if paginated_data['has_prev']:
            if st.button("◀ Prev", key=f"{key_prefix}_prev"):
                current = paginated_data['current_page']
                st.session_state[page_key] = max(1, current - 1)
                st.rerun()
    
    with col3:
        current_page = paginated_data['current_page']
        total_pages = paginated_data['total_pages']
        st.markdown(
            f"""
            <div style='text-align: center; padding: 0.5rem;'>
                Page {current_page} of {total_pages}
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col4:
        if paginated_data['has_next']:
            if st.button("Next ▶", key=f"{key_prefix}_next"):
                current = paginated_data['current_page']
                total = paginated_data['total_pages']
                st.session_state[page_key] = min(total, current + 1)
                st.rerun()
    
    with col5:
        if paginated_data['has_next']:
            if st.button("Last ▶▶", key=f"{key_prefix}_last"):
                st.session_state[page_key] = paginated_data['total_pages']
                st.rerun()


def safe_get(dictionary: Dict, key: str, default=None):
    """Safely get value from dictionary with fallback"""
    try:
        return dictionary.get(key, default)
    except (AttributeError, TypeError):
        return default


def initialize_session_state():
    """Initialize all required session state variables"""
    defaults = {
        'discovery_index': 0,
        'current_recommendations': [],
        'last_action': None,
        'nav_page': 1,
        'swipes_page': 1,
        'search_results': [],
        'selected_genres': [],
        'min_rating': 0.0,
        'content_type': 'movie'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value 
"""
FILMY - Modular Main Application
Clean, organized structure using separated components and pages
"""

import streamlit as st
from streamlit_option_menu import option_menu

# Import core modules
from core.enhanced_ratings_manager import EnhancedRatingsManager
from core.dynamic_recommendations import DynamicRecommendationManager

# Import modular components
from components.cards import load_css
from utils.helpers import initialize_session_state


# Page configuration
st.set_page_config(
    page_title="FILMY - Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_ratings_manager():
    """Cached ratings manager initialization"""
    return EnhancedRatingsManager()


def initialize_app():
    """Initialize app with all required managers and session state"""
    
    # Load CSS styles
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize ratings manager (cached)
    if 'ratings_manager' not in st.session_state:
        st.session_state.ratings_manager = get_ratings_manager()
    
    # Initialize dynamic recommendations manager
    if 'dynamic_recommendations' not in st.session_state:
        st.session_state.dynamic_recommendations = DynamicRecommendationManager(
            st.session_state.ratings_manager
        )


def show_recommendations_page():
    """Recommendations page with optimized loading"""
    st.markdown(
        '<h1 class="main-header">🎯 Your Recommendations</h1>', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="subtitle">Personalized picks based on your ratings</p>', 
        unsafe_allow_html=True
    )
    
    try:
        # Get dynamic recommendations
        recs = st.session_state.dynamic_recommendations.get_endless_recommendations(
            count=10
        )
        
        if not recs:
            st.info("🎬 Start rating movies to get personalized recommendations!")
            return
        
        # Lazy import to avoid circular dependencies
        from components.cards import display_content_card
        
        for i, rec in enumerate(recs):
            display_content_card(
                rec, 
                show_actions=True, 
                show_rec_reason=True,
                card_key=f"rec_{i}"
            )
            
    except Exception as e:
        st.error(f"Error loading recommendations: {e}")
        st.info("Please try refreshing the page.")


def show_your_swipes_page():
    """Your swipes/ratings page with pagination and search"""
    st.markdown(
        '<h1 class="main-header">⭐ Your Swipes</h1>', 
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="subtitle">Manage and edit your ratings</p>', 
        unsafe_allow_html=True
    )
    
    try:
        ratings_df = st.session_state.ratings_manager.get_all_ratings()
        
        if ratings_df.empty:
            st.info("🎬 No ratings yet! Start swiping to build your profile.")
            return
        
        # Add search functionality
        search_term = st.text_input("🔍 Search your ratings", placeholder="Movie or TV show title...")
        
        # Filter by search term
        if search_term:
            mask = ratings_df['title'].str.contains(search_term, case=False, na=False)
            filtered_df = ratings_df[mask]
        else:
            filtered_df = ratings_df
        
        # Sort by date
        recent_ratings = filtered_df.sort_values('date_rated', ascending=False)
        
        # Pagination
        items_per_page = 10
        total_pages = (len(recent_ratings) + items_per_page - 1) // items_per_page
        
        if 'swipes_page' not in st.session_state:
            st.session_state.swipes_page = 1
        
        # Page controls
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("◀ Previous") and st.session_state.swipes_page > 1:
                    st.session_state.swipes_page -= 1
                    st.rerun()
            with col2:
                st.markdown(
                    f"<div style='text-align: center;'>Page {st.session_state.swipes_page} of {total_pages}</div>",
                    unsafe_allow_html=True
                )
            with col3:
                if st.button("Next ▶") and st.session_state.swipes_page < total_pages:
                    st.session_state.swipes_page += 1
                    st.rerun()
        
        # Show current page items
        start_idx = (st.session_state.swipes_page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_ratings = recent_ratings.iloc[start_idx:end_idx]
        
        # Display ratings
        for idx, row in page_ratings.iterrows():
            display_rating_item(row, idx)
            
    except Exception as e:
        st.error(f"Error loading ratings: {e}")


def display_rating_item(row, idx):
    """Display individual rating item with actions"""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            rating_class = get_rating_class(row['my_rating'])
            release_year = row.get('release_date', 'N/A')[:4] if row.get('release_date') else 'N/A'
            date_formatted = row.get('date_rated', '')[:10] if row.get('date_rated') else 'N/A'
            
            st.markdown(
                f"""
                <div class="movie-card {rating_class}">
                    <strong>{row['title']}</strong> ({release_year})<br>
                    <small>{row['my_rating_label']} • {date_formatted}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            if st.button("✏️ Edit", key=f"edit_{idx}"):
                st.session_state[f'editing_{row["tmdb_id"]}'] = True
        
        with col3:
            if st.button("🗑️ Delete", key=f"delete_{idx}"):
                success = st.session_state.ratings_manager.delete_rating(
                    row['tmdb_id'], row['type']
                )
                if success:
                    st.success("Deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete")


def get_rating_class(rating):
    """Get CSS class for rating - optimized lookup"""
    rating_classes = {
        4: "loved-it",
        3: "liked-it", 
        2: "it-was-ok",
        1: "didnt-like-it",
        0: "want-to-see",
        -1: "not-interested",
        -2: "watchlist-item"
    }
    return rating_classes.get(rating, "")


def main():
    """Main application entry point"""
    
    try:
        # Initialize everything
        initialize_app()
        
        # Navigation menu with CSS variables
        with st.sidebar:
            selected = option_menu(
                menu_title="FILMY",
                options=["Home", "Recommendations", "Your Swipes"],
                icons=["house", "stars", "heart"],
                menu_icon="film",
                default_index=0,
                styles={
                    "container": {
                        "padding": "0!important", 
                        "background-color": "var(--soft-bg, #fafafa)"
                    },
                    "icon": {
                        "color": "var(--primary, #FF6B6B)", 
                        "font-size": "18px"
                    }, 
                    "nav-link": {
                        "font-size": "16px", 
                        "text-align": "left", 
                        "margin": "0px", 
                        "--hover-color": "#eee",
                        "color": "var(--text-primary, #333333)"
                    },
                    "nav-link-selected": {
                        "background-color": "var(--primary, #FF6B6B)"
                    },
                }
            )
        
        # Route to selected page with lazy imports
        if selected == "Home":
            from pages.home import show_home_page
            show_home_page()
        elif selected == "Recommendations":
            show_recommendations_page()
        elif selected == "Your Swipes":
            show_your_swipes_page()
        
        # Footer with CSS variables
        st.markdown(
            """
            <div class="footer">
                Made with ❤️ for epic movie nights | 
                <a href="#" style="color: var(--primary, #FF6B6B);">FILMY</a> by Toby the fuck lord
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page or contact support.")


if __name__ == "__main__":
    main() 
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

# Import page modules
from pages.home import show_home_page


# Page configuration
st.set_page_config(
    page_title="FILMY - Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def initialize_app():
    """Initialize app with all required managers and session state"""
    
    # Load CSS styles
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize ratings manager
    if 'ratings_manager' not in st.session_state:
        st.session_state.ratings_manager = EnhancedRatingsManager()
    
    # Initialize dynamic recommendations manager
    if 'dynamic_recommendations' not in st.session_state:
        st.session_state.dynamic_recommendations = DynamicRecommendationManager(
            st.session_state.ratings_manager
        )


def show_recommendations_page():
    """Recommendations page - placeholder for now"""
    st.markdown('<h1 class="main-header">🎯 Your Recommendations</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Personalized picks based on your ratings</p>', unsafe_allow_html=True)
    
    # Get dynamic recommendations
    recs = st.session_state.dynamic_recommendations.get_mixed_recommendations(limit=10)
    
    if not recs:
        st.info("🎬 Start rating movies to get personalized recommendations!")
        return
    
    # Import and use the display function from cards
    from components.cards import display_content_card
    
    for i, rec in enumerate(recs):
        display_content_card(
            rec, 
            show_actions=True, 
            show_rec_reason=True,
            card_key=f"rec_{i}"
        )


def show_your_swipes_page():
    """Your swipes/ratings page - placeholder for now"""
    st.markdown('<h1 class="main-header">⭐ Your Swipes</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Manage and edit your ratings</p>', unsafe_allow_html=True)
    
    ratings_df = st.session_state.ratings_manager.get_all_ratings()
    
    if ratings_df.empty:
        st.info("🎬 No ratings yet! Start swiping to build your profile.")
        return
    
    # Show recent ratings
    recent_ratings = ratings_df.sort_values('date_rated', ascending=False).head(20)
    
    for idx, row in recent_ratings.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                rating_class = get_rating_class(row['my_rating'])
                st.markdown(
                    f"""
                    <div class="movie-card {rating_class}">
                        <strong>{row['title']}</strong> ({row.get('release_date', 'N/A')[:4]})<br>
                        <small>{row['my_rating_label']} • {row.get('date_rated', '')[:10]}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                if st.button("Edit", key=f"edit_{idx}"):
                    st.session_state[f'editing_{row["tmdb_id"]}'] = True
            
            with col3:
                if st.button("Delete", key=f"delete_{idx}"):
                    success = st.session_state.ratings_manager.delete_rating(
                        row['tmdb_id'], row['type']
                    )
                    if success:
                        st.success("Deleted!")
                        st.rerun()


def get_rating_class(rating):
    """Get CSS class for rating"""
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
    
    # Initialize everything
    initialize_app()
    
    # Navigation menu
    with st.sidebar:
        selected = option_menu(
            menu_title="FILMY",
            options=["Home", "Recommendations", "Your Swipes"],
            icons=["house", "stars", "heart"],
            menu_icon="film",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "#fafafa"},
                "icon": {"color": "#FF6B6B", "font-size": "18px"}, 
                "nav-link": {
                    "font-size": "16px", 
                    "text-align": "left", 
                    "margin":"0px", 
                    "--hover-color": "#eee",
                    "color": "#333333"
                },
                "nav-link-selected": {"background-color": "#FF6B6B"},
            }
        )
    
    # Route to selected page
    if selected == "Home":
        show_home_page()
    elif selected == "Recommendations":
        show_recommendations_page()
    elif selected == "Your Swipes":
        show_your_swipes_page()
    
    # Footer
    st.markdown(
        """
        <div class="footer">
            Made with ❤️ for epic movie nights | 
            <a href="#" style="color: #FF6B6B;">FILMY</a> by Toby the fuck lord
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main() 
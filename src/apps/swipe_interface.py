import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List

# Import our core modules
from core.config import TMDB_IMAGE_BASE_URL
from core.tmdb_api import TMDBApi
from core.enhanced_ratings_manager import EnhancedRatingsManager


class SwipeInterface:
    """
    Mobile-first swipe interface for rating movies.
    Tinder-style swipe gestures with intelligent rating logic.
    """
    
    def __init__(self, ratings_manager: EnhancedRatingsManager):
        self.ratings_manager = ratings_manager
        self.tmdb = TMDBApi()
        
    def create_swipe_card_html(self, item: Dict, card_id: str) -> str:
        """Generate HTML for a swipeable movie card"""
        poster_url = f"{TMDB_IMAGE_BASE_URL}{item['poster_path']}" if item.get('poster_path') else ""
        
        # Calculate recommendation info
        rec_reason = item.get('rec_reason', '')
        match_score = int(item.get('final_score', 0.5) * 100)
        
        genres = ", ".join(item.get('genres', [])) if isinstance(item.get('genres'), list) else str(item.get('genres', ''))
        
        html = f"""
        <div id="card-{card_id}" class="swipe-card" data-movie-id="{item['id']}" data-movie-type="{item['type']}">
            <div class="card-content">
                <div class="poster-section">
                    {f'<img src="{poster_url}" class="poster-img" alt="Poster" onerror="this.style.display=\'none\'">' if poster_url else ''}
                    <div class="poster-fallback">🎬</div>
                </div>
                
                <div class="info-section">
                    <h2 class="movie-title">{item['title']}</h2>
                    
                    <div class="movie-meta">
                        <span class="year">📅 {item.get('release_date', 'N/A')[:4]}</span>
                        <span class="rating">⭐ {item.get('vote_average', 0):.1f}/10</span>
                        <span class="type">{'🎬 Movie' if item['type'] == 'movie' else '📺 TV'}</span>
                    </div>
                    
                    {f'<div class="rec-reason">🎯 {rec_reason} ({match_score}% match)</div>' if rec_reason else ''}
                    
                    <div class="genres">{genres}</div>
                    
                    <div class="overview">{item.get('overview', 'No description available')[:200]}...</div>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-havent-seen" onclick="handleHaventSeen('{card_id}')">
                    🤷 Haven't Seen
                </button>
                <button class="btn btn-have-seen" onclick="handleHaveSeen('{card_id}')">
                    👀 Have Seen
                </button>
            </div>
            
            <div class="rating-mode" id="rating-mode-{card_id}" style="display: none;">
                <div class="rating-instruction">
                    <p>👈 Swipe left: Didn't like it</p>
                    <p>👉 Swipe right: Liked it</p>
                </div>
                <div class="quick-rate-buttons">
                    <button class="btn btn-hate" onclick="quickRate('{card_id}', 1)">😤 Hate</button>
                    <button class="btn btn-ok" onclick="quickRate('{card_id}', 2)">🤷 OK</button>
                    <button class="btn btn-good" onclick="quickRate('{card_id}', 3)">👍 Good</button>
                    <button class="btn btn-perfect" onclick="quickRate('{card_id}', 4)">🌟 Perfect</button>
                </div>
            </div>
            
            <!-- Swipe indicators -->
            <div class="swipe-indicator left-indicator" id="left-indicator-{card_id}">
                <div class="indicator-content">
                    <span class="indicator-text" id="left-text-{card_id}">❌</span>
                </div>
            </div>
            <div class="swipe-indicator right-indicator" id="right-indicator-{card_id}">
                <div class="indicator-content">
                    <span class="indicator-text" id="right-text-{card_id}">✅</span>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def get_swipe_css(self) -> str:
        """CSS for the swipe interface"""
        return """
        <style>
        .swipe-container {
            position: relative;
            width: 100%;
            max-width: 400px;
            margin: 0 auto;
            height: 600px;
            perspective: 1000px;
        }
        
        .swipe-card {
            position: absolute;
            width: 100%;
            height: 100%;
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            cursor: grab;
            user-select: none;
            overflow: hidden;
            transform-origin: center bottom;
            transition: transform 0.3s ease;
            z-index: 10;
        }
        
        .swipe-card:active {
            cursor: grabbing;
        }
        
        .card-content {
            height: calc(100% - 120px);
            display: flex;
            flex-direction: column;
        }
        
        .poster-section {
            position: relative;
            height: 300px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .poster-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .poster-fallback {
            font-size: 4rem;
            color: white;
        }
        
        .info-section {
            padding: 16px;
            flex: 1;
            overflow-y: auto;
        }
        
        .movie-title {
            font-size: 1.4rem;
            font-weight: bold;
            margin: 0 0 12px 0;
            color: #333;
        }
        
        .movie-meta {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            font-size: 0.9rem;
            color: #666;
        }
        
        .rec-reason {
            background: rgba(67, 56, 202, 0.1);
            color: #4338ca;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            margin-bottom: 12px;
            font-weight: 500;
        }
        
        .genres {
            font-size: 0.85rem;
            color: #888;
            margin-bottom: 12px;
        }
        
        .overview {
            font-size: 0.9rem;
            line-height: 1.4;
            color: #555;
        }
        
        .action-buttons {
            display: flex;
            gap: 12px;
            padding: 16px;
            background: #f8f9fa;
        }
        
        .btn {
            flex: 1;
            padding: 12px 16px;
            border: none;
            border-radius: 8px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-havent-seen {
            background: #6c757d;
            color: white;
        }
        
        .btn-have-seen {
            background: #007bff;
            color: white;
        }
        
        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .rating-mode {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 16px;
            text-align: center;
        }
        
        .rating-instruction {
            margin-bottom: 12px;
        }
        
        .rating-instruction p {
            margin: 4px 0;
            font-size: 0.9rem;
        }
        
        .quick-rate-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 12px;
        }
        
        .btn-hate { background: #dc3545; color: white; }
        .btn-ok { background: #ffc107; color: black; }
        .btn-good { background: #28a745; color: white; }
        .btn-perfect { background: #ffd700; color: black; }
        
        .swipe-indicator {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s ease;
            pointer-events: none;
            z-index: 20;
        }
        
        .left-indicator {
            left: 20px;
            background: rgba(220, 53, 69, 0.9);
        }
        
        .right-indicator {
            right: 20px;
            background: rgba(40, 167, 69, 0.9);
        }
        
        .indicator-content {
            font-size: 2rem;
            color: white;
            font-weight: bold;
        }
        
        /* Swipe animations */
        .swipe-left {
            transform: translateX(-100%) rotate(-30deg);
            opacity: 0;
        }
        
        .swipe-right {
            transform: translateX(100%) rotate(30deg);
            opacity: 0;
        }
        
        .swipe-up {
            transform: translateY(-100%) scale(0.8);
            opacity: 0;
        }
        
        /* Mobile responsive */
        @media (max-width: 480px) {
            .swipe-container {
                height: 70vh;
                max-height: 600px;
            }
            
            .movie-title {
                font-size: 1.2rem;
            }
            
            .movie-meta {
                font-size: 0.8rem;
            }
            
            .quick-rate-buttons {
                grid-template-columns: 1fr 1fr;
            }
        }
        </style>
        """
    
    def get_swipe_javascript(self) -> str:
        """JavaScript for swipe functionality"""
        return """
        <script>
        let currentCard = null;
        let cardMode = 'default'; // 'default' or 'rating'
        let startX = 0;
        let startY = 0;
        let currentX = 0;
        let currentY = 0;
        let cardInitialTransform = '';
        
        function initializeSwipe() {
            const cards = document.querySelectorAll('.swipe-card');
            cards.forEach(card => {
                card.addEventListener('touchstart', handleTouchStart, {passive: false});
                card.addEventListener('touchmove', handleTouchMove, {passive: false});
                card.addEventListener('touchend', handleTouchEnd, {passive: false});
                
                // Mouse events for desktop testing
                card.addEventListener('mousedown', handleMouseDown);
                card.addEventListener('mousemove', handleMouseMove);
                card.addEventListener('mouseup', handleMouseEnd);
                card.addEventListener('mouseleave', handleMouseEnd);
            });
        }
        
        function handleTouchStart(e) {
            currentCard = e.target.closest('.swipe-card');
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            currentX = startX;
            currentY = startY;
            cardInitialTransform = currentCard.style.transform;
        }
        
        function handleMouseDown(e) {
            currentCard = e.target.closest('.swipe-card');
            startX = e.clientX;
            startY = e.clientY;
            currentX = startX;
            currentY = startY;
            cardInitialTransform = currentCard.style.transform;
            e.preventDefault();
        }
        
        function handleTouchMove(e) {
            if (!currentCard) return;
            e.preventDefault();
            
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;
            updateCardPosition();
        }
        
        function handleMouseMove(e) {
            if (!currentCard) return;
            e.preventDefault();
            
            currentX = e.clientX;
            currentY = e.clientY;
            updateCardPosition();
        }
        
        function updateCardPosition() {
            const deltaX = currentX - startX;
            const deltaY = currentY - startY;
            const rotation = deltaX * 0.1;
            
            currentCard.style.transform = `translateX(${deltaX}px) translateY(${deltaY}px) rotate(${rotation}deg)`;
            
            // Show swipe indicators
            const leftIndicator = currentCard.querySelector('.left-indicator');
            const rightIndicator = currentCard.querySelector('.right-indicator');
            
            if (Math.abs(deltaX) > 50) {
                if (deltaX < 0) {
                    leftIndicator.style.opacity = Math.min(Math.abs(deltaX) / 150, 1);
                    rightIndicator.style.opacity = 0;
                } else {
                    rightIndicator.style.opacity = Math.min(deltaX / 150, 1);
                    leftIndicator.style.opacity = 0;
                }
            } else {
                leftIndicator.style.opacity = 0;
                rightIndicator.style.opacity = 0;
            }
        }
        
        function handleTouchEnd(e) {
            handleSwipeEnd();
        }
        
        function handleMouseEnd(e) {
            handleSwipeEnd();
        }
        
        function handleSwipeEnd() {
            if (!currentCard) return;
            
            const deltaX = currentX - startX;
            const deltaY = currentY - startY;
            
            // Reset indicators
            const leftIndicator = currentCard.querySelector('.left-indicator');
            const rightIndicator = currentCard.querySelector('.right-indicator');
            leftIndicator.style.opacity = 0;
            rightIndicator.style.opacity = 0;
            
            // Determine swipe action
            if (Math.abs(deltaX) > 100) {
                if (deltaX < 0) {
                    handleSwipeLeft(currentCard);
                } else {
                    handleSwipeRight(currentCard);
                }
            } else {
                // Snap back to center
                currentCard.style.transform = cardInitialTransform;
            }
            
            currentCard = null;
        }
        
        function handleSwipeLeft(card) {
            const cardId = card.id.replace('card-', '');
            const movieId = card.dataset.movieId;
            const movieType = card.dataset.movieType;
            
            // Animate card away
            card.classList.add('swipe-left');
            
            // Determine action based on mode
            if (card.querySelector('.rating-mode').style.display === 'none') {
                // Default mode: Not interested
                rateMovie(movieId, movieType, -1, 'Not Interested');
            } else {
                // Rating mode: Bad rating (hate or ok)
                showQuickRating(cardId, 'bad');
            }
            
            setTimeout(() => {
                card.remove();
                loadNextCard();
            }, 300);
        }
        
        function handleSwipeRight(card) {
            const cardId = card.id.replace('card-', '');
            const movieId = card.dataset.movieId;
            const movieType = card.dataset.movieType;
            
            // Animate card away
            card.classList.add('swipe-right');
            
            // Determine action based on mode
            if (card.querySelector('.rating-mode').style.display === 'none') {
                // Default mode: Want to see
                rateMovie(movieId, movieType, 0, 'Want to See');
            } else {
                // Rating mode: Good rating (good or perfect)
                showQuickRating(cardId, 'good');
            }
            
            setTimeout(() => {
                card.remove();
                loadNextCard();
            }, 300);
        }
        
        function handleHaventSeen(cardId) {
            const card = document.getElementById(`card-${cardId}`);
            card.classList.add('swipe-up');
            
            setTimeout(() => {
                card.remove();
                loadNextCard();
            }, 300);
        }
        
        function handleHaveSeen(cardId) {
            const ratingMode = document.getElementById(`rating-mode-${cardId}`);
            const actionButtons = document.querySelector(`#card-${cardId} .action-buttons`);
            
            ratingMode.style.display = 'block';
            actionButtons.style.display = 'none';
            
            // Update swipe indicators
            const leftText = document.getElementById(`left-text-${cardId}`);
            const rightText = document.getElementById(`right-text-${cardId}`);
            leftText.textContent = '👎';
            rightText.textContent = '👍';
        }
        
        function quickRate(cardId, rating) {
            const card = document.getElementById(`card-${cardId}`);
            const movieId = card.dataset.movieId;
            const movieType = card.dataset.movieType;
            
            rateMovie(movieId, movieType, rating, getRatingLabel(rating));
            
            card.classList.add('swipe-up');
            setTimeout(() => {
                card.remove();
                loadNextCard();
            }, 300);
        }
        
        function showQuickRating(cardId, type) {
            // Show quick rating options based on swipe direction
            const ratings = type === 'bad' ? [1, 2] : [3, 4];
            const labels = type === 'bad' ? ['😤 Hate', '🤷 OK'] : ['👍 Good', '🌟 Perfect'];
            
            // For now, just pick the middle option
            const rating = type === 'bad' ? 1 : 4;
            const card = document.getElementById(`card-${cardId}`);
            const movieId = card.dataset.movieId;
            const movieType = card.dataset.movieType;
            
            rateMovie(movieId, movieType, rating, getRatingLabel(rating));
        }
        
        function rateMovie(movieId, movieType, rating, label) {
            // Send rating to Streamlit
            window.parent.postMessage({
                type: 'rate_movie',
                movieId: movieId,
                movieType: movieType,
                rating: rating,
                label: label
            }, '*');
        }
        
        function getRatingLabel(rating) {
            const labels = {
                '-1': 'Not Interested',
                '0': 'Want to See',
                '1': 'Hate',
                '2': 'OK',
                '3': 'Good',
                '4': 'Perfect'
            };
            return labels[rating.toString()] || 'Unknown';
        }
        
        function loadNextCard() {
            // Signal to load next card
            window.parent.postMessage({
                type: 'load_next_card'
            }, '*');
        }
        
        // Initialize when DOM is loaded
        document.addEventListener('DOMContentLoaded', initializeSwipe);
        setTimeout(initializeSwipe, 100);
        </script>
        """
    
    def render_swipe_interface(self, recommendations: List[Dict], key: str = "swipe"):
        """Render the swipe interface with recommendations"""
        if not recommendations:
            st.info("🎬 No recommendations available. Rate some movies to get started!")
            return
        
        # Show current recommendation
        current_rec = recommendations[0] if recommendations else None
        
        if current_rec:
            # Create the swipe card HTML
            card_html = self.create_swipe_card_html(current_rec, "current")
            
            # Combine CSS, HTML, and JavaScript
            full_html = f"""
            {self.get_swipe_css()}
            <div class="swipe-container">
                {card_html}
            </div>
            {self.get_swipe_javascript()}
            """
            
            # Render the component
            components.html(full_html, height=650, key=key)
            
            # Handle messages from JavaScript
            if 'swipe_action' in st.session_state:
                action = st.session_state.swipe_action
                if action['type'] == 'rate_movie':
                    # Process the rating
                    success = self.ratings_manager.add_rating(
                        int(action['movieId']),
                        current_rec['title'],
                        action['movieType'],
                        int(action['rating']),
                        current_rec
                    )
                    
                    if success:
                        st.success(f"✅ Rated as {action['label']}!")
                        # Remove the processed recommendation
                        recommendations.pop(0)
                        st.rerun()
                
                # Clear the action
                del st.session_state.swipe_action
        
        # Show stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📚 Recommendations Left", len(recommendations))
        
        with col2:
            total_ratings = len(self.ratings_manager.get_all_ratings())
            st.metric("⭐ Total Ratings", total_ratings)
        
        with col3:
            if st.button("🔄 Refresh Recommendations"):
                st.rerun()


def create_swipe_page():
    """Create the swipe interface page"""
    st.markdown("## 📱 Swipe to Rate")
    st.markdown("*Swipe right for content you want to see, left for content you don't*")
    
    # Initialize the swipe interface
    swipe_interface = SwipeInterface(st.session_state.ratings_manager)
    
    # Get fresh recommendations
    if 'swipe_recommendations' not in st.session_state:
        st.session_state.swipe_recommendations = []
    
    # Load more recommendations if needed
    if len(st.session_state.swipe_recommendations) < 5:
        new_recs = st.session_state.ratings_manager.get_recommendations(limit=20)
        st.session_state.swipe_recommendations.extend(new_recs)
    
    # Render the swipe interface
    swipe_interface.render_swipe_interface(
        st.session_state.swipe_recommendations,
        key="main_swipe"
    ) 
from typing import Dict, List, Optional
import random
from datetime import datetime
from .enhanced_ratings_manager import EnhancedRatingsManager
from .dynamic_recommendations import DynamicRecommendationManager
from .recommendation_engine import IntelligentRecommendationEngine


class SmartSwipeManager:
    """
    Intelligent swipe manager that pre-loads recommendations,
    learns from user behavior in real-time, and ensures instant loading.
    """
    
    def __init__(self, ratings_manager: EnhancedRatingsManager):
        self.ratings_manager = ratings_manager
        self.dynamic_manager = DynamicRecommendationManager(ratings_manager)
        self.intelligent_engine = IntelligentRecommendationEngine(ratings_manager)
        
        # Queue management
        self.queue_size = 10  # Always keep 10 items ready
        self.min_queue_size = 3  # Refill when below 3
        
        # Real-time learning
        self.user_patterns = {
            'recent_likes': [],  # Last 10 liked items
            'recent_dislikes': [],  # Last 10 disliked items
            'swipe_speed': [],  # Track engagement speed
            'genre_momentum': {},  # Hot genres right now
            'last_update': datetime.now()
        }
    
    def get_smart_queue(self, force_refresh: bool = False) -> List[Dict]:
        """Get pre-loaded smart recommendation queue"""
        # Check if we need to refresh the queue
        if force_refresh or self._needs_queue_refresh():
            return self._build_smart_queue()
        
        # Return existing queue or build new one
        return self._get_existing_queue()
    
    def process_swipe(self, item: Dict, action: str, rating: int = None) -> Dict:
        """Process user swipe and update patterns instantly"""
        swipe_time = datetime.now()
        
        # Record the action
        self._record_user_action(item, action, rating, swipe_time)
        
        # Update real-time patterns
        self._update_user_patterns(item, action, rating)
        
        # Re-sort remaining queue based on new data
        self._resort_queue()
        
        # Trigger background refresh if needed
        if self._queue_needs_refill():
            self._background_queue_refresh()
        
        return {
            'action': action,
            'item_id': item['id'],
            'learning_updated': True,
            'queue_size': len(self._get_existing_queue())
        }
    
    def _needs_queue_refresh(self) -> bool:
        """Check if queue needs refreshing"""
        try:
            import streamlit as st
            queue = st.session_state.get('smart_swipe_queue', [])
            return len(queue) < self.min_queue_size
        except:
            return True
    
    def _get_existing_queue(self) -> List[Dict]:
        """Get existing queue from session state"""
        try:
            import streamlit as st
            return st.session_state.get('smart_swipe_queue', [])
        except:
            return []
    
    def _build_smart_queue(self) -> List[Dict]:
        """Build intelligent pre-loaded queue"""
        queue = []
        
        # Get base recommendations from multiple sources
        intelligent_recs = self.intelligent_engine.get_personalized_recommendations(15)
        dynamic_recs = self.dynamic_manager.get_endless_recommendations(15)
        
        # Combine and deduplicate
        all_recs = intelligent_recs + dynamic_recs
        seen_ids = set()
        unique_recs = []
        
        for rec in all_recs:
            rec_id = (rec['id'], rec['type'])
            if rec_id not in seen_ids and not self._is_already_rated(rec):
                unique_recs.append(rec)
                seen_ids.add(rec_id)
        
        # Apply smart sorting based on user patterns
        sorted_recs = self._apply_smart_sorting(unique_recs)
        
        # Take top items for queue
        queue = sorted_recs[:self.queue_size]
        
        # Pre-load additional metadata for instant display
        queue = self._preload_metadata(queue)
        
        # Store in session state
        self._store_queue(queue)
        
        return queue
    
    def _apply_smart_sorting(self, recommendations: List[Dict]) -> List[Dict]:
        """Apply intelligent sorting based on real-time user patterns"""
        scored_recs = []
        
        for rec in recommendations:
            score = self._calculate_smart_score(rec)
            rec['smart_score'] = score
            scored_recs.append(rec)
        
        # Sort by smart score (highest first)
        return sorted(scored_recs, key=lambda x: x['smart_score'], reverse=True)
    
    def _calculate_smart_score(self, item: Dict) -> float:
        """Calculate smart recommendation score based on real-time patterns"""
        base_score = item.get('rec_score', 0.5)
        
        # Genre momentum boost
        genre_boost = self._get_genre_momentum_boost(item)
        
        # Similarity to recent likes
        like_similarity = self._get_like_similarity_score(item)
        
        # Quality and popularity factors
        quality_score = min(item.get('vote_average', 5) / 10, 1.0)
        popularity_factor = min(item.get('popularity', 0) / 100, 0.3)
        
        # Recency boost for new releases
        recency_boost = self._get_recency_boost(item)
        
        # Combine all factors
        smart_score = (
            base_score * 0.4 +
            genre_boost * 0.25 +
            like_similarity * 0.2 +
            quality_score * 0.1 +
            popularity_factor * 0.03 +
            recency_boost * 0.02
        )
        
        return min(smart_score, 1.0)
    
    def _get_genre_momentum_boost(self, item: Dict) -> float:
        """Boost based on recently liked genres"""
        item_genres = item.get('genres', [])
        if not item_genres:
            return 0.0
        
        genre_scores = []
        for genre in item_genres:
            momentum = self.user_patterns['genre_momentum'].get(genre, 0)
            genre_scores.append(momentum)
        
        return max(genre_scores) if genre_scores else 0.0
    
    def _get_like_similarity_score(self, item: Dict) -> float:
        """Score based on similarity to recently liked items"""
        recent_likes = self.user_patterns['recent_likes']
        if not recent_likes:
            return 0.5
        
        # Simple genre overlap scoring
        item_genres = set(item.get('genres', []))
        
        similarity_scores = []
        for liked_item in recent_likes[-5:]:  # Last 5 likes
            liked_genres = set(liked_item.get('genres', []))
            if item_genres and liked_genres:
                overlap = len(item_genres & liked_genres) / len(item_genres | liked_genres)
                similarity_scores.append(overlap)
        
        return max(similarity_scores) if similarity_scores else 0.5
    
    def _get_recency_boost(self, item: Dict) -> float:
        """Boost for recent releases"""
        try:
            release_date = item.get('release_date', '')
            if release_date:
                from datetime import datetime, timedelta
                release_dt = datetime.strptime(release_date, '%Y-%m-%d')
                days_old = (datetime.now() - release_dt).days
                
                if days_old < 30:  # Very new
                    return 0.3
                elif days_old < 90:  # Recent
                    return 0.2
                elif days_old < 365:  # This year
                    return 0.1
        except:
            pass
        
        return 0.0
    
    def _record_user_action(self, item: Dict, action: str, rating: int, timestamp: datetime):
        """Record user action for learning"""
        # Add to ratings manager
        if rating is not None:
            self.ratings_manager.add_rating(
                item['id'], 
                item['title'], 
                item['type'], 
                rating, 
                item
            )
    
    def _update_user_patterns(self, item: Dict, action: str, rating: int):
        """Update real-time user patterns"""
        # Track likes and dislikes
        if action == 'like' or (rating and rating >= 3):
            self.user_patterns['recent_likes'].append(item)
            if len(self.user_patterns['recent_likes']) > 10:
                self.user_patterns['recent_likes'].pop(0)
            
            # Boost genre momentum
            for genre in item.get('genres', []):
                current = self.user_patterns['genre_momentum'].get(genre, 0)
                self.user_patterns['genre_momentum'][genre] = min(current + 0.2, 1.0)
        
        elif action == 'dislike' or (rating and rating <= 2):
            self.user_patterns['recent_dislikes'].append(item)
            if len(self.user_patterns['recent_dislikes']) > 10:
                self.user_patterns['recent_dislikes'].pop(0)
            
            # Reduce genre momentum
            for genre in item.get('genres', []):
                current = self.user_patterns['genre_momentum'].get(genre, 0)
                self.user_patterns['genre_momentum'][genre] = max(current - 0.1, 0)
        
        self.user_patterns['last_update'] = datetime.now()
    
    def _resort_queue(self):
        """Re-sort remaining queue based on updated patterns"""
        try:
            import streamlit as st
            queue = st.session_state.get('smart_swipe_queue', [])
            
            if len(queue) > 1:
                # Re-score and sort remaining items
                sorted_queue = self._apply_smart_sorting(queue)
                st.session_state['smart_swipe_queue'] = sorted_queue
        except:
            pass
    
    def _queue_needs_refill(self) -> bool:
        """Check if queue needs background refill"""
        queue = self._get_existing_queue()
        return len(queue) < self.min_queue_size
    
    def _background_queue_refresh(self):
        """Refresh queue in background"""
        try:
            import streamlit as st
            
            # Get new recommendations
            new_recs = self.dynamic_manager.get_endless_recommendations(10)
            new_recs = self._apply_smart_sorting(new_recs)
            
            # Add to existing queue
            current_queue = st.session_state.get('smart_swipe_queue', [])
            extended_queue = current_queue + new_recs[:5]
            
            # Remove duplicates and limit size
            seen_ids = set()
            final_queue = []
            for item in extended_queue:
                item_id = (item['id'], item['type'])
                if item_id not in seen_ids:
                    final_queue.append(item)
                    seen_ids.add(item_id)
            
            st.session_state['smart_swipe_queue'] = final_queue[:self.queue_size]
        except:
            pass
    
    def _preload_metadata(self, queue: List[Dict]) -> List[Dict]:
        """Pre-load any additional metadata for instant display"""
        # TODO: Pre-load images, additional details, etc.
        return queue
    
    def _store_queue(self, queue: List[Dict]):
        """Store queue in session state"""
        try:
            import streamlit as st
            st.session_state['smart_swipe_queue'] = queue
        except:
            pass
    
    def _is_already_rated(self, item: Dict) -> bool:
        """Check if item is already rated"""
        return self.ratings_manager.is_already_rated(item['id'], item['type'])
    
    def get_queue_stats(self) -> Dict:
        """Get current queue statistics"""
        queue = self._get_existing_queue()
        return {
            'queue_size': len(queue),
            'recent_likes': len(self.user_patterns['recent_likes']),
            'recent_dislikes': len(self.user_patterns['recent_dislikes']),
            'active_genres': len([g for g, score in self.user_patterns['genre_momentum'].items() if score > 0.1]),
            'last_update': self.user_patterns['last_update'].strftime('%H:%M:%S')
        } 
import random
from typing import Dict, List, Optional
from .tmdb_api import TMDBApi
from .recommendation_engine import IntelligentRecommendationEngine


class DynamicRecommendationManager:
    """
    Dynamic recommendation system that constantly generates fresh recommendations
    and ensures users never run out of content to rate.
    """
    
    def __init__(self, ratings_manager):
        self.ratings_manager = ratings_manager
        self.tmdb = TMDBApi()
        self.intelligent_engine = IntelligentRecommendationEngine(ratings_manager)
        self.recommendation_pools = {
            'intelligent': [],
            'trending': [],
            'popular': [],
            'discovery': [],
            'genre_deep_dive': []
        }
        self.used_ids: set = set()
    
    def get_endless_recommendations(self, count: int = 20) -> List[Dict]:
        """
        Get a mix of intelligent and discovery recommendations 
        that never runs out.
        """
        recommendations = []
        
        # Refresh pools if needed
        self._refresh_recommendation_pools()
        
        # Mix different types of recommendations
        rec_mix = self._create_recommendation_mix(count)
        
        for rec_type, amount in rec_mix.items():
            pool_recs = self._get_from_pool(rec_type, amount)
            recommendations.extend(pool_recs)
        
        # Shuffle to avoid predictable patterns
        random.shuffle(recommendations)
        
        return recommendations[:count]
    
    def _refresh_recommendation_pools(self):
        """Refresh all recommendation pools"""
        try:
            # 1. Intelligent recommendations (best quality)
            if len(self.recommendation_pools['intelligent']) < 10:
                intelligent_recs = self.intelligent_engine.get_personalized_recommendations(30)
                self.recommendation_pools['intelligent'].extend(
                    [r for r in intelligent_recs if not self._is_used(r)]
                )
            
            # 2. Trending content (current hot stuff)
            if len(self.recommendation_pools['trending']) < 15:
                trending_recs = self._get_trending_content()
                self.recommendation_pools['trending'].extend(
                    [r for r in trending_recs if not self._is_used(r)]
                )
            
            # 3. Popular content (reliable quality)
            if len(self.recommendation_pools['popular']) < 20:
                popular_recs = self._get_popular_content()
                self.recommendation_pools['popular'].extend(
                    [r for r in popular_recs if not self._is_used(r)]
                )
            
            # 4. Discovery content (explore new genres/years)
            if len(self.recommendation_pools['discovery']) < 25:
                discovery_recs = self._get_discovery_content()
                self.recommendation_pools['discovery'].extend(
                    [r for r in discovery_recs if not self._is_used(r)]
                )
            
            # 5. Genre deep dives (based on user preferences)
            if len(self.recommendation_pools['genre_deep_dive']) < 15:
                genre_recs = self._get_genre_deep_dive()
                self.recommendation_pools['genre_deep_dive'].extend(
                    [r for r in genre_recs if not self._is_used(r)]
                )
                
        except Exception as e:
            print(f"Error refreshing recommendation pools: {e}")
    
    def _create_recommendation_mix(self, total_count: int) -> Dict[str, int]:
        """Create a balanced mix of recommendation types"""
        user_ratings_count = len(self.ratings_manager.get_all_ratings())
        
        if user_ratings_count < 5:
            # New user: focus on popular and trending
            return {
                'popular': int(total_count * 0.4),
                'trending': int(total_count * 0.3),
                'discovery': int(total_count * 0.2),
                'intelligent': int(total_count * 0.1)
            }
        elif user_ratings_count < 20:
            # Growing user: mix of intelligent and discovery
            return {
                'intelligent': int(total_count * 0.3),
                'popular': int(total_count * 0.25),
                'discovery': int(total_count * 0.25),
                'trending': int(total_count * 0.15),
                'genre_deep_dive': int(total_count * 0.05)
            }
        else:
            # Experienced user: focus on intelligent recommendations
            return {
                'intelligent': int(total_count * 0.5),
                'genre_deep_dive': int(total_count * 0.2),
                'discovery': int(total_count * 0.15),
                'trending': int(total_count * 0.1),
                'popular': int(total_count * 0.05)
            }
    
    def _get_from_pool(self, pool_name: str, count: int) -> List[Dict]:
        """Get recommendations from a specific pool"""
        pool = self.recommendation_pools.get(pool_name, [])
        selected = pool[:count]
        
        # Remove selected items from pool
        self.recommendation_pools[pool_name] = pool[count:]
        
        # Mark as used
        for item in selected:
            self._mark_as_used(item)
        
        return selected
    
    def _get_trending_content(self) -> List[Dict]:
        """Get trending movies and TV shows, prioritizing new releases"""
        recommendations = []
        
        try:
            # Get new releases first (last 30 days)
            new_releases = self._get_new_releases()
            recommendations.extend(new_releases)
            
            # Trending movies
            trending_movies = self.tmdb.get_trending('movie', 'week')
            if trending_movies and 'results' in trending_movies:
                for movie in trending_movies['results'][:10]:
                    movie_data = self.tmdb.format_movie_data(movie)
                    if movie_data:
                        movie_data['rec_reason'] = 'Trending this week'
                        movie_data['rec_score'] = 0.7
                        recommendations.append(movie_data)
            
            # Trending TV shows
            trending_tv = self.tmdb.get_trending('tv', 'week')
            if trending_tv and 'results' in trending_tv:
                for show in trending_tv['results'][:10]:
                    show_data = self.tmdb.format_tv_data(show)
                    if show_data:
                        show_data['rec_reason'] = 'Trending TV this week'
                        show_data['rec_score'] = 0.7
                        recommendations.append(show_data)
                        
        except Exception as e:
            print(f"Error getting trending content: {e}")
        
        return recommendations
    
    def _get_new_releases(self) -> List[Dict]:
        """Get very recent releases (last 30 days) that match user preferences"""
        recommendations = []
        
        try:
            from datetime import datetime, timedelta
            
            # Get date 30 days ago
            thirty_days_ago = datetime.now() - timedelta(days=30)
            date_str = thirty_days_ago.strftime('%Y-%m-%d')
            
            # Get user's favorite genres for filtering
            genre_prefs = self.ratings_manager.get_genre_preferences()
            top_genres = list(genre_prefs.keys())[:3] if genre_prefs else []
            
            # Search for new releases in user's favorite genres
            for genre in top_genres:
                genre_id = self._get_tmdb_genre_id(genre)
                if not genre_id:
                    continue
                    
                # New movies in this genre
                new_movies = self.tmdb.discover_movies(
                    primary_release_date_gte=date_str,
                    with_genres=genre_id,
                    sort_by="primary_release_date.desc",
                    vote_count_gte=10
                )
                
                if new_movies and 'results' in new_movies:
                    for movie in new_movies['results'][:3]:
                        movie_data = self.tmdb.format_movie_data(movie)
                        if movie_data:
                            movie_data['rec_reason'] = f'NEW: {genre} release you might love'
                            movie_data['rec_score'] = 0.8  # High score for new releases
                            recommendations.append(movie_data)
            
            # Also get general new releases (highly rated)
            general_new = self.tmdb.discover_movies(
                primary_release_date_gte=date_str,
                sort_by="vote_average.desc",
                vote_count_gte=50,
                vote_average_gte=7.0
            )
            
            if general_new and 'results' in general_new:
                for movie in general_new['results'][:5]:
                    movie_data = self.tmdb.format_movie_data(movie)
                    if movie_data:
                        movie_data['rec_reason'] = 'NEW: Highly rated recent release'
                        movie_data['rec_score'] = 0.75
                        recommendations.append(movie_data)
                        
        except Exception as e:
            print(f"Error getting new releases: {e}")
            
        return recommendations
    
    def _get_tmdb_genre_id(self, genre_name: str) -> Optional[int]:
        """Get TMDB genre ID from genre name"""
        genre_mapping = {
            "Action": 28,
            "Adventure": 12,
            "Animation": 16,
            "Comedy": 35,
            "Crime": 80,
            "Documentary": 99,
            "Drama": 18,
            "Family": 10751,
            "Fantasy": 14,
            "History": 36,
            "Horror": 27,
            "Music": 10402,
            "Mystery": 9648,
            "Romance": 10749,
            "Science Fiction": 878,
            "TV Movie": 10770,
            "Thriller": 53,
            "War": 10752,
            "Western": 37
        }
        return genre_mapping.get(genre_name)
    
    def _get_popular_content(self) -> List[Dict]:
        """Get popular high-quality content"""
        recommendations = []
        
        try:
            # Popular movies
            popular_movies = self.tmdb.get_popular_movies()
            if popular_movies and 'results' in popular_movies:
                for movie in popular_movies['results'][:20]:
                    if movie.get('vote_average', 0) >= 6.5:  # Quality filter
                        movie_data = self.tmdb.format_movie_data(movie)
                        if movie_data:
                            movie_data['rec_reason'] = '⭐ Popular & highly rated'
                            movie_data['rec_score'] = 0.6
                            recommendations.append(movie_data)
            
            # Popular TV shows
            popular_tv = self.tmdb.get_popular_tv()
            if popular_tv and 'results' in popular_tv:
                for show in popular_tv['results'][:20]:
                    if show.get('vote_average', 0) >= 6.5:  # Quality filter
                        show_data = self.tmdb.format_tv_data(show)
                        if show_data:
                            show_data['rec_reason'] = '📺 Popular TV series'
                            show_data['rec_score'] = 0.6
                            recommendations.append(show_data)
                            
        except Exception as e:
            print(f"Error getting popular content: {e}")
        
        return recommendations
    
    def _get_discovery_content(self) -> List[Dict]:
        """Get discovery content from different eras and genres"""
        recommendations = []
        
        # Different time periods to explore
        time_periods = [
            ('2020-2024', 'Recent releases'),
            ('2015-2019', 'Recent classics'),
            ('2010-2014', 'Early 2010s gems'),
            ('2000-2009', '2000s favorites'),
            ('1990-1999', '90s classics'),
            ('1980-1989', '80s hits'),
            ('1970-1979', '70s cinema'),
        ]
        
        # Different genres to explore (not currently used in logic)
        # genres = [28, 35, 18, 53, 27, 10749, 878, 9648]
        
        try:
            for year_range, description in time_periods[:3]:  # Limit to 3 periods
                start_year, end_year = year_range.split('-')
                
                # Movies from this period
                movies = self.tmdb.discover_movies(
                    primary_release_date_gte=f"{start_year}-01-01",
                    primary_release_date_lte=f"{end_year}-12-31",
                    sort_by="vote_average.desc",
                    vote_count_gte=100
                )
                
                if movies and 'results' in movies:
                    for movie in movies['results'][:5]:
                        movie_data = self.tmdb.format_movie_data(movie)
                        if movie_data:
                            movie_data['rec_reason'] = f'🎭 Discover: {description}'
                            movie_data['rec_score'] = 0.5
                            recommendations.append(movie_data)
                            
        except Exception as e:
            print(f"Error getting discovery content: {e}")
        
        return recommendations
    
    def _get_genre_deep_dive(self) -> List[Dict]:
        """Get deep dive recommendations in user's favorite genres"""
        recommendations = []
        
        try:
            # Get user's genre preferences
            genre_prefs = self.ratings_manager.get_genre_preferences()
            
            if not genre_prefs:
                return recommendations
            
            # Focus on top 3 genres user loves
            top_genres = list(genre_prefs.keys())[:3]
            
            for genre in top_genres:
                genre_id = self._get_tmdb_genre_id(genre)
                if not genre_id:
                    continue
                
                # Get high-quality content in this genre
                movies = self.tmdb.discover_movies(
                    with_genres=genre_id,
                    sort_by="vote_average.desc",
                    vote_count_gte=50,
                    vote_average_gte=7.0
                )
                
                if movies and 'results' in movies:
                    for movie in movies['results'][:5]:
                        movie_data = self.tmdb.format_movie_data(movie)
                        if movie_data:
                            avg_rating = genre_prefs[genre]
                            movie_data['rec_reason'] = f'🎯 More {genre} (you rate it {avg_rating:.1f}/4)'
                            movie_data['rec_score'] = avg_rating / 4.0
                            recommendations.append(movie_data)
                            
        except Exception as e:
            print(f"Error getting genre deep dive: {e}")
        
        return recommendations
    
# Duplicate function removed - using the one defined above at line 225
    
    def _is_used(self, item: Dict) -> bool:
        """Check if item has been used before"""
        item_id = (item['id'], item['type'])
        return (item_id in self.used_ids or 
                self.ratings_manager.is_already_rated(item['id'], item['type']))
    
    def _mark_as_used(self, item: Dict):
        """Mark item as used"""
        item_id = (item['id'], item['type'])
        self.used_ids.add(item_id)
    
    def clear_used_items(self):
        """Clear the used items cache (for fresh sessions)"""
        self.used_ids.clear()
        for pool in self.recommendation_pools.values():
            pool.clear()
    
    def get_pool_stats(self) -> Dict[str, int]:
        """Get statistics about recommendation pools"""
        return {
            pool_name: len(pool) 
            for pool_name, pool in self.recommendation_pools.items()
        } 
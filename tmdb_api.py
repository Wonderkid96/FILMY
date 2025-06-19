import requests
import streamlit as st
from typing import Dict, List, Optional, Tuple
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL, MOVIE_GENRES, TV_GENRES

class TMDBApi:
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.image_base_url = TMDB_IMAGE_BASE_URL
        
        if not self.api_key:
            st.error("🚨 TMDB API key not found! Please add your API key to the .env file.")
            st.stop()
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request to TMDB"""
        if params is None:
            params = {}
        
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return None
    
    def search_movies(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search for movies"""
        return self._make_request("/search/movie", {"query": query, "page": page})
    
    def search_tv(self, query: str, page: int = 1) -> Optional[Dict]:
        """Search for TV shows"""
        return self._make_request("/search/tv", {"query": query, "page": page})
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information"""
        return self._make_request(f"/movie/{movie_id}")
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed TV show information"""
        return self._make_request(f"/tv/{tv_id}")
    
    def discover_movies(self, **kwargs) -> Optional[Dict]:
        """Discover movies with filters"""
        return self._make_request("/discover/movie", kwargs)
    
    def discover_tv(self, **kwargs) -> Optional[Dict]:
        """Discover TV shows with filters"""
        return self._make_request("/discover/tv", kwargs)
    
    def get_popular_movies(self, page: int = 1) -> Optional[Dict]:
        """Get popular movies"""
        return self._make_request("/movie/popular", {"page": page})
    
    def get_popular_tv(self, page: int = 1) -> Optional[Dict]:
        """Get popular TV shows"""
        return self._make_request("/tv/popular", {"page": page})
    
    def get_top_rated_movies(self, page: int = 1) -> Optional[Dict]:
        """Get top rated movies"""
        return self._make_request("/movie/top_rated", {"page": page})
    
    def get_top_rated_tv(self, page: int = 1) -> Optional[Dict]:
        """Get top rated TV shows"""
        return self._make_request("/tv/top_rated", {"page": page})
    
    def get_movie_recommendations(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get movie recommendations based on a movie"""
        return self._make_request(f"/movie/{movie_id}/recommendations", {"page": page})
    
    def get_tv_recommendations(self, tv_id: int, page: int = 1) -> Optional[Dict]:
        """Get TV recommendations based on a TV show"""
        return self._make_request(f"/tv/{tv_id}/recommendations", {"page": page})
    
    def get_similar_movies(self, movie_id: int, page: int = 1) -> Optional[Dict]:
        """Get similar movies"""
        return self._make_request(f"/movie/{movie_id}/similar", {"page": page})
    
    def get_similar_tv(self, tv_id: int, page: int = 1) -> Optional[Dict]:
        """Get similar TV shows"""
        return self._make_request(f"/tv/{tv_id}/similar", {"page": page})
    
    def get_trending(self, media_type: str = "all", time_window: str = "day") -> Optional[Dict]:
        """Get trending content"""
        return self._make_request(f"/trending/{media_type}/{time_window}")
    
    def get_movie_credits(self, movie_id: int) -> Optional[Dict]:
        """Get movie cast and crew"""
        return self._make_request(f"/movie/{movie_id}/credits")
    
    def get_tv_credits(self, tv_id: int) -> Optional[Dict]:
        """Get TV show cast and crew"""
        return self._make_request(f"/tv/{tv_id}/credits")
    
    def get_full_image_url(self, image_path: str) -> str:
        """Get full image URL"""
        if image_path:
            return f"{self.image_base_url}{image_path}"
        return ""
    
    def format_movie_data(self, movie: Dict) -> Dict:
        """Format movie data for display"""
        return {
            'id': movie.get('id'),
            'title': movie.get('title', 'Unknown Title'),
            'original_title': movie.get('original_title', ''),
            'overview': movie.get('overview', 'No overview available'),
            'release_date': movie.get('release_date', ''),
            'vote_average': movie.get('vote_average', 0),
            'vote_count': movie.get('vote_count', 0),
            'popularity': movie.get('popularity', 0),
            'poster_path': self.get_full_image_url(movie.get('poster_path')),
            'backdrop_path': self.get_full_image_url(movie.get('backdrop_path')),
            'genres': [MOVIE_GENRES.get(genre_id, 'Unknown') for genre_id in movie.get('genre_ids', [])],
            'adult': movie.get('adult', False),
            'runtime': movie.get('runtime'),
            'budget': movie.get('budget'),
            'revenue': movie.get('revenue'),
            'type': 'movie'
        }
    
    def format_tv_data(self, tv_show: Dict) -> Dict:
        """Format TV show data for display"""
        return {
            'id': tv_show.get('id'),
            'title': tv_show.get('name', 'Unknown Title'),
            'original_title': tv_show.get('original_name', ''),
            'overview': tv_show.get('overview', 'No overview available'),
            'release_date': tv_show.get('first_air_date', ''),
            'vote_average': tv_show.get('vote_average', 0),
            'vote_count': tv_show.get('vote_count', 0),
            'popularity': tv_show.get('popularity', 0),
            'poster_path': self.get_full_image_url(tv_show.get('poster_path')),
            'backdrop_path': self.get_full_image_url(tv_show.get('backdrop_path')),
            'genres': [TV_GENRES.get(genre_id, 'Unknown') for genre_id in tv_show.get('genre_ids', [])],
            'number_of_seasons': tv_show.get('number_of_seasons'),
            'number_of_episodes': tv_show.get('number_of_episodes'),
            'episode_run_time': tv_show.get('episode_run_time', []),
            'type': 'tv'
        } 
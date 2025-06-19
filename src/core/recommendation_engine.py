import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import streamlit as st
from tmdb_api import TMDBApi

class RecommendationEngine:
    def __init__(self):
        self.tmdb = TMDBApi()
        self.content_matrix = None
        self.content_features = None
        self.scaler = StandardScaler()
        
    def create_content_features(self, items: List[Dict]) -> np.ndarray:
        """Create content-based features from movies/TV shows"""
        features = []
        
        for item in items:
            # Text features
            text_content = f"{item.get('title', '')} {' '.join(item.get('genres', []))} {item.get('overview', '')}"
            
            # Numerical features
            rating = item.get('vote_average', 0)
            popularity = item.get('popularity', 0)
            vote_count = item.get('vote_count', 0)
            
            # Create feature vector
            feature_dict = {
                'text': text_content,
                'rating': rating,
                'popularity': popularity,
                'vote_count': vote_count,
                'year': self._extract_year(item.get('release_date', '')),
                'genre_count': len(item.get('genres', []))
            }
            features.append(feature_dict)
        
        return features
    
    def _extract_year(self, date_str: str) -> int:
        """Extract year from date string"""
        try:
            return int(date_str.split('-')[0]) if date_str else 0
        except:
            return 0
    
    def build_content_similarity_matrix(self, items: List[Dict]) -> np.ndarray:
        """Build content-based similarity matrix"""
        features = self.create_content_features(items)
        
        # Text similarity using TF-IDF
        texts = [f['text'] for f in features]
        tfidf = TfidfVectorizer(stop_words='english', max_features=1000)
        text_matrix = tfidf.fit_transform(texts)
        text_similarity = cosine_similarity(text_matrix)
        
        # Numerical features similarity
        numerical_features = np.array([[
            f['rating'], f['popularity'], f['vote_count'], 
            f['year'], f['genre_count']
        ] for f in features])
        
        # Normalize numerical features
        numerical_features_scaled = self.scaler.fit_transform(numerical_features)
        numerical_similarity = cosine_similarity(numerical_features_scaled)
        
        # Combine similarities (weighted)
        combined_similarity = 0.7 * text_similarity + 0.3 * numerical_similarity
        
        return combined_similarity
    
    def get_content_based_recommendations(self, items: List[Dict], liked_indices: List[int], 
                                        num_recommendations: int = 10) -> List[Tuple[int, float]]:
        """Get content-based recommendations"""
        if not liked_indices:
            return []
        
        similarity_matrix = self.build_content_similarity_matrix(items)
        
        # Calculate average similarity scores for liked items
        user_profile = np.mean(similarity_matrix[liked_indices], axis=0)
        
        # Get recommendations (exclude already liked items)
        recommendations = []
        for i, score in enumerate(user_profile):
            if i not in liked_indices:
                recommendations.append((i, score))
        
        # Sort by similarity score
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations[:num_recommendations]
    
    def get_genre_based_recommendations(self, preferred_genres: List[str], 
                                      content_type: str = 'movie',
                                      min_rating: float = 6.0,
                                      num_recommendations: int = 20) -> List[Dict]:
        """Get recommendations based on preferred genres"""
        recommendations = []
        
        # Convert genre names to IDs
        genre_mapping = self.tmdb.MOVIE_GENRES if content_type == 'movie' else self.tmdb.TV_GENRES
        genre_ids = []
        for genre_name in preferred_genres:
            for genre_id, name in genre_mapping.items():
                if name.lower() == genre_name.lower():
                    genre_ids.append(genre_id)
                    break
        
        if not genre_ids:
            return []
        
        # Discover content with preferred genres
        params = {
            'with_genres': ','.join(map(str, genre_ids)),
            'vote_average.gte': min_rating,
            'sort_by': 'vote_average.desc',
            'page': 1
        }
        
        if content_type == 'movie':
            response = self.tmdb.discover_movies(**params)
            format_func = self.tmdb.format_movie_data
        else:
            response = self.tmdb.discover_tv(**params)
            format_func = self.tmdb.format_tv_data
        
        if response and 'results' in response:
            for item in response['results'][:num_recommendations]:
                recommendations.append(format_func(item))
        
        return recommendations
    
    def get_hybrid_recommendations(self, user_preferences: Dict, 
                                 num_recommendations: int = 20) -> List[Dict]:
        """Get hybrid recommendations combining multiple approaches"""
        all_recommendations = []
        
        # Genre-based recommendations
        if user_preferences.get('preferred_genres'):
            genre_recs = self.get_genre_based_recommendations(
                user_preferences['preferred_genres'],
                user_preferences.get('content_type', 'movie'),
                user_preferences.get('min_rating', 6.0),
                num_recommendations // 2
            )
            all_recommendations.extend(genre_recs)
        
        # Popular recommendations as fallback
        content_type = user_preferences.get('content_type', 'movie')
        if content_type == 'movie':
            popular_response = self.tmdb.get_popular_movies()
            format_func = self.tmdb.format_movie_data
        else:
            popular_response = self.tmdb.get_popular_tv()
            format_func = self.tmdb.format_tv_data
        
        if popular_response and 'results' in popular_response:
            for item in popular_response['results'][:num_recommendations // 2]:
                formatted_item = format_func(item)
                if formatted_item not in all_recommendations:
                    all_recommendations.append(formatted_item)
        
        # Remove duplicates and apply rating filter
        unique_recommendations = []
        seen_ids = set()
        min_rating = user_preferences.get('min_rating', 0)
        
        for rec in all_recommendations:
            if (rec['id'] not in seen_ids and 
                rec['vote_average'] >= min_rating):
                unique_recommendations.append(rec)
                seen_ids.add(rec['id'])
        
        return unique_recommendations[:num_recommendations]
    
    def get_similar_content(self, item_id: int, content_type: str = 'movie',
                          num_recommendations: int = 10) -> List[Dict]:
        """Get similar content based on an item"""
        recommendations = []
        
        if content_type == 'movie':
            response = self.tmdb.get_similar_movies(item_id)
            format_func = self.tmdb.format_movie_data
        else:
            response = self.tmdb.get_similar_tv(item_id)
            format_func = self.tmdb.format_tv_data
        
        if response and 'results' in response:
            for item in response['results'][:num_recommendations]:
                recommendations.append(format_func(item))
        
        return recommendations
    
    def calculate_recommendation_score(self, item: Dict, user_preferences: Dict) -> float:
        """Calculate a recommendation score for an item based on user preferences"""
        score = 0.0
        
        # Base score from TMDB rating
        score += item.get('vote_average', 0) * 0.3
        
        # Genre preference bonus
        item_genres = set(item.get('genres', []))
        preferred_genres = set(user_preferences.get('preferred_genres', []))
        if preferred_genres:
            genre_overlap = len(item_genres.intersection(preferred_genres)) / len(preferred_genres)
            score += genre_overlap * 30
        
        # Popularity bonus (normalized)
        popularity = item.get('popularity', 0)
        if popularity > 0:
            score += min(popularity / 100, 2.0)  # Cap at 2 points
        
        # Vote count reliability bonus
        vote_count = item.get('vote_count', 0)
        if vote_count > 100:
            score += min(vote_count / 1000, 1.0)  # Cap at 1 point
        
        # Recent release bonus
        if item.get('release_date'):
            year = self._extract_year(item['release_date'])
            current_year = 2024
            if year >= current_year - 3:  # Released in last 3 years
                score += 1.0
        
        return score 
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import streamlit as st
from .tmdb_api import TMDBApi
from collections import defaultdict, Counter
from .config import RATING_LABELS

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

class IntelligentRecommendationEngine:
    """
    Smart recommendation engine that learns from user preferences
    and finds content based on actual taste patterns.
    """

    def __init__(self, ratings_manager):
        self.ratings_manager = ratings_manager
        self.tmdb = TMDBApi()
        
    def get_personalized_recommendations(self, limit: int = 20) -> List[Dict]:
        """
        Generate intelligent recommendations based on user's actual preferences.
        Uses multiple algorithms and combines results.
        """
        user_data = self.ratings_manager.export_for_recommendations()
        
        if not user_data["liked_content"].empty:
            recommendations = []
            
            # 1. Genre-based recommendations (40% weight)
            genre_recs = self._get_genre_based_recommendations(user_data, limit // 2)
            recommendations.extend(genre_recs)
            
            # 2. Similar content recommendations (35% weight)  
            similar_recs = self._get_similar_content_recommendations(user_data, limit // 2)
            recommendations.extend(similar_recs)
            
            # 3. Director/actor pattern recommendations (25% weight)
            talent_recs = self._get_talent_based_recommendations(user_data, limit // 4)
            recommendations.extend(talent_recs)
            
            # Score and rank all recommendations
            scored_recs = self._score_recommendations(recommendations, user_data)
            
            # Remove duplicates and return top recommendations
            return self._deduplicate_and_limit(scored_recs, limit)
        
        return []
    
    def _get_genre_based_recommendations(self, user_data: Dict, limit: int) -> List[Dict]:
        """Find content in genres the user loves, weighted by rating patterns."""
        recommendations = []
        genre_prefs = user_data["genre_preferences"]
        
        if not genre_prefs:
            return []
            
        # Focus on top genres the user actually likes (rating >= 3)
        loved_genres = [genre for genre, avg_rating in genre_prefs.items() if avg_rating >= 3.0]
        
        for genre in loved_genres[:5]:  # Top 5 loved genres
            # Search for highly rated content in this genre
            movie_results = self.tmdb.discover_movies(
                with_genres=self._get_tmdb_genre_id(genre),
                sort_by="vote_average.desc",
                vote_count_gte=100  # Ensure quality
            )
            
            tv_results = self.tmdb.discover_tv(
                with_genres=self._get_tmdb_genre_id(genre),
                sort_by="vote_average.desc", 
                vote_count_gte=50
            )
            
            # Process movies
            if movie_results and "results" in movie_results:
                for movie in movie_results["results"][:3]:
                    if not self.ratings_manager.is_already_rated(movie["id"], "movie"):
                        movie_data = self.tmdb.format_movie_data(movie)
                        if movie_data:
                            movie_data["rec_reason"] = f"You love {genre} movies"
                            movie_data["rec_score"] = genre_prefs[genre]
                            recommendations.append(movie_data)
            
            # Process TV shows  
            if tv_results and "results" in tv_results:
                for show in tv_results["results"][:3]:
                    if not self.ratings_manager.is_already_rated(show["id"], "tv"):
                        show_data = self.tmdb.format_tv_data(show)
                        if show_data:
                            show_data["rec_reason"] = f"You love {genre} shows"
                            show_data["rec_score"] = genre_prefs[genre]
                            recommendations.append(show_data)
        
        return recommendations[:limit]
    
    def _get_similar_content_recommendations(self, user_data: Dict, limit: int) -> List[Dict]:
        """Find content similar to user's highly rated items."""
        recommendations = []
        liked_content = user_data["liked_content"]
        
        # Focus on perfect and good ratings (4 and 3)
        perfect_content = liked_content[liked_content["my_rating"] == 4]
        good_content = liked_content[liked_content["my_rating"] == 3]
        
        # Prioritize perfect ratings
        priority_content = pd.concat([perfect_content, good_content]).head(10)
        
        for _, item in priority_content.iterrows():
            weight = 1.0 if item["my_rating"] == 4 else 0.7
            
            if item["type"] == "movie":
                similar = self.tmdb.get_similar_movies(item["tmdb_id"])
                tmdb_recs = self.tmdb.get_movie_recommendations(item["tmdb_id"])
            else:
                similar = self.tmdb.get_similar_tv(item["tmdb_id"])
                tmdb_recs = self.tmdb.get_tv_recommendations(item["tmdb_id"])
            
            # Process similar content
            sources = [
                (similar, "Similar to"),
                (tmdb_recs, "Recommended because you liked")
            ]
            
            for source, reason_prefix in sources:
                if source and "results" in source:
                    for rec in source["results"][:2]:
                        if not self.ratings_manager.is_already_rated(rec["id"], item["type"]):
                            rec_data = (
                                self.tmdb.format_movie_data(rec)
                                if item["type"] == "movie"
                                else self.tmdb.format_tv_data(rec)
                            )
                            if rec_data:
                                rec_data["rec_reason"] = f"{reason_prefix} '{item['title']}'"
                                rec_data["rec_score"] = weight * (rec.get("vote_average", 5.0) / 10.0)
                                recommendations.append(rec_data)
        
        return recommendations[:limit]
    
    def _get_talent_based_recommendations(self, user_data: Dict, limit: int) -> List[Dict]:
        """Find content from directors/actors in highly rated content."""
        recommendations = []
        liked_content = user_data["liked_content"]
        
        # Get cast/crew info for highly rated content
        talent_scores = defaultdict(list)
        
        for _, item in liked_content.head(5).iterrows():  # Top 5 liked items
            try:
                if item["type"] == "movie":
                    credits = self.tmdb.get_movie_credits(item["tmdb_id"])
                    movie_details = self.tmdb.get_movie_details(item["tmdb_id"])
                    
                    # Track directors
                    if credits and "crew" in credits:
                        directors = [person for person in credits["crew"] if person["job"] == "Director"]
                        for director in directors[:2]:
                            talent_scores[f"director_{director['id']}"].append({
                                "rating": item["my_rating"],
                                "name": director["name"],
                                "type": "director"
                            })
                    
                    # Track main cast
                    if credits and "cast" in credits:
                        for actor in credits["cast"][:3]:  # Top 3 actors
                            talent_scores[f"actor_{actor['id']}"].append({
                                "rating": item["my_rating"],
                                "name": actor["name"],
                                "type": "actor"
                            })
                            
            except Exception as e:
                continue  # Skip if can't get credits
        
        # Find top talent based on average ratings
        top_talent = []
        for talent_id, ratings in talent_scores.items():
            if len(ratings) >= 1:  # At least 1 rating
                avg_rating = sum(r["rating"] for r in ratings) / len(ratings)
                if avg_rating >= 3.0:  # Only if you generally like their work
                    top_talent.append({
                        "id": talent_id,
                        "avg_rating": avg_rating,
                        "name": ratings[0]["name"],
                        "type": ratings[0]["type"]
                    })
        
        # Sort by rating and get top talent
        top_talent.sort(key=lambda x: x["avg_rating"], reverse=True)
        
        # Find content featuring this talent
        for talent in top_talent[:3]:  # Top 3 talent
            try:
                if talent["type"] == "director":
                    # Search for movies by this director
                    person_id = int(talent["id"].split("_")[1])
                    person_credits = self.tmdb.get_person_movie_credits(person_id)
                    
                    if person_credits and "crew" in person_credits:
                        directed_movies = [
                            movie for movie in person_credits["crew"] 
                            if movie.get("job") == "Director"
                        ][:3]
                        
                        for movie in directed_movies:
                            if not self.ratings_manager.is_already_rated(movie["id"], "movie"):
                                movie_data = self.tmdb.format_movie_data(movie)
                                if movie_data:
                                    movie_data["rec_reason"] = f"Directed by {talent['name']}"
                                    movie_data["rec_score"] = talent["avg_rating"] / 4.0
                                    recommendations.append(movie_data)
                
                elif talent["type"] == "actor":
                    # Search for movies with this actor
                    person_id = int(talent["id"].split("_")[1])
                    person_credits = self.tmdb.get_person_movie_credits(person_id)
                    
                    if person_credits and "cast" in person_credits:
                        for movie in person_credits["cast"][:3]:
                            if not self.ratings_manager.is_already_rated(movie["id"], "movie"):
                                movie_data = self.tmdb.format_movie_data(movie)
                                if movie_data:
                                    movie_data["rec_reason"] = f"Starring {talent['name']}"
                                    movie_data["rec_score"] = talent["avg_rating"] / 4.0
                                    recommendations.append(movie_data)
                                    
            except Exception as e:
                continue
        
        return recommendations[:limit]
    
    def _score_recommendations(self, recommendations: List[Dict], user_data: Dict) -> List[Dict]:
        """Score recommendations based on user preferences and content quality."""
        genre_prefs = user_data.get("genre_preferences", {})
        avg_user_rating = user_data.get("average_user_rating", 2.5)
        
        for rec in recommendations:
            base_score = rec.get("rec_score", 0.5)
            
            # Genre preference bonus
            genre_bonus = 0
            if "genres" in rec and rec["genres"]:
                rec_genres = rec["genres"] if isinstance(rec["genres"], list) else rec["genres"].split(", ")
                for genre in rec_genres:
                    if genre in genre_prefs:
                        genre_bonus += (genre_prefs[genre] / 4.0) * 0.2  # Max 20% bonus per genre
            
            # TMDB rating bonus (quality filter)
            tmdb_rating = rec.get("vote_average", 5.0)
            quality_bonus = (tmdb_rating / 10.0) * 0.3  # Max 30% bonus
            
            # Popularity bonus (but not too much)
            popularity = rec.get("popularity", 1)
            popularity_bonus = min(popularity / 1000.0, 0.1)  # Max 10% bonus
            
            # Final score
            final_score = base_score + genre_bonus + quality_bonus + popularity_bonus
            rec["final_score"] = min(final_score, 1.0)  # Cap at 1.0
        
        return sorted(recommendations, key=lambda x: x.get("final_score", 0), reverse=True)
    
    def _deduplicate_and_limit(self, recommendations: List[Dict], limit: int) -> List[Dict]:
        """Remove duplicates and limit results."""
        seen = set()
        unique_recs = []
        
        for rec in recommendations:
            key = (rec["id"], rec["type"])
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
                if len(unique_recs) >= limit:
                    break
        
        return unique_recs
    
    def _get_tmdb_genre_id(self, genre_name: str) -> str:
        """Map genre name to TMDB genre ID."""
        # Common genre mappings
        genre_map = {
            "Action": "28",
            "Adventure": "12", 
            "Animation": "16",
            "Comedy": "35",
            "Crime": "80",
            "Documentary": "99",
            "Drama": "18",
            "Family": "10751",
            "Fantasy": "14",
            "History": "36",
            "Horror": "27",
            "Music": "10402",
            "Mystery": "9648",
            "Romance": "10749",
            "Science Fiction": "878",
            "TV Movie": "10770",
            "Thriller": "53",
            "War": "10752",
            "Western": "37"
        }
        
        return genre_map.get(genre_name, "")
    
    def explain_recommendation(self, rec: Dict) -> str:
        """Generate a detailed explanation for why this was recommended."""
        reason = rec.get("rec_reason", "Recommended for you")
        score = rec.get("final_score", 0.5)
        
        explanation = f"**{reason}**\n"
        explanation += f"Match score: {score*100:.0f}%\n"
        
        if "vote_average" in rec:
            explanation += f"TMDB Rating: {rec['vote_average']:.1f}/10\n"
            
        return explanation 
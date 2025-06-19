import json
import os
from typing import Dict, List, Set
from datetime import datetime
import streamlit as st

class UserPreferencesManager:
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self.preferences_file = f"user_preferences_{user_id}.json"
        self.preferences = self.load_preferences()
    
    def load_preferences(self) -> Dict:
        """Load user preferences from file"""
        default_preferences = {
            'liked_movies': [],
            'disliked_movies': [],
            'liked_tv_shows': [],
            'disliked_tv_shows': [],
            'favorite_genres': [],
            'disliked_genres': [],
            'min_rating_preference': 6.0,
            'preferred_content_types': ['movie', 'tv'],
            'viewing_history': [],
            'last_updated': None
        }
        
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r') as f:
                    loaded_prefs = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in default_preferences.items():
                        if key not in loaded_prefs:
                            loaded_prefs[key] = value
                    return loaded_prefs
            except Exception as e:
                st.warning(f"Could not load preferences: {e}")
                return default_preferences
        
        return default_preferences
    
    def save_preferences(self):
        """Save user preferences to file"""
        self.preferences['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            st.error(f"Could not save preferences: {e}")
    
    def add_liked_item(self, item: Dict):
        """Add an item to liked list"""
        item_data = {
            'id': item['id'],
            'title': item['title'],
            'type': item['type'],
            'genres': item.get('genres', []),
            'vote_average': item.get('vote_average', 0),
            'liked_date': datetime.now().isoformat()
        }
        
        if item['type'] == 'movie':
            # Remove from disliked if present
            self.preferences['disliked_movies'] = [
                x for x in self.preferences['disliked_movies'] if x['id'] != item['id']
            ]
            # Add to liked if not already present
            if not any(x['id'] == item['id'] for x in self.preferences['liked_movies']):
                self.preferences['liked_movies'].append(item_data)
        else:
            # Remove from disliked if present
            self.preferences['disliked_tv_shows'] = [
                x for x in self.preferences['disliked_tv_shows'] if x['id'] != item['id']
            ]
            # Add to liked if not already present
            if not any(x['id'] == item['id'] for x in self.preferences['liked_tv_shows']):
                self.preferences['liked_tv_shows'].append(item_data)
        
        # Update favorite genres
        self.update_favorite_genres(item.get('genres', []), liked=True)
        self.save_preferences()
    
    def add_disliked_item(self, item: Dict):
        """Add an item to disliked list"""
        item_data = {
            'id': item['id'],
            'title': item['title'],
            'type': item['type'],
            'genres': item.get('genres', []),
            'vote_average': item.get('vote_average', 0),
            'disliked_date': datetime.now().isoformat()
        }
        
        if item['type'] == 'movie':
            # Remove from liked if present
            self.preferences['liked_movies'] = [
                x for x in self.preferences['liked_movies'] if x['id'] != item['id']
            ]
            # Add to disliked if not already present
            if not any(x['id'] == item['id'] for x in self.preferences['disliked_movies']):
                self.preferences['disliked_movies'].append(item_data)
        else:
            # Remove from liked if present
            self.preferences['liked_tv_shows'] = [
                x for x in self.preferences['liked_tv_shows'] if x['id'] != item['id']
            ]
            # Add to disliked if not already present
            if not any(x['id'] == item['id'] for x in self.preferences['disliked_tv_shows']):
                self.preferences['disliked_tv_shows'].append(item_data)
        
        # Update disliked genres
        self.update_favorite_genres(item.get('genres', []), liked=False)
        self.save_preferences()
    
    def update_favorite_genres(self, genres: List[str], liked: bool = True):
        """Update favorite/disliked genres based on user feedback"""
        for genre in genres:
            if liked:
                # Add to favorites (with weight)
                found = False
                for fav_genre in self.preferences['favorite_genres']:
                    if fav_genre['name'] == genre:
                        fav_genre['weight'] += 1
                        found = True
                        break
                if not found:
                    self.preferences['favorite_genres'].append({
                        'name': genre,
                        'weight': 1
                    })
                
                # Remove from disliked if present
                self.preferences['disliked_genres'] = [
                    x for x in self.preferences['disliked_genres'] if x['name'] != genre
                ]
            else:
                # Add to disliked
                if not any(x['name'] == genre for x in self.preferences['disliked_genres']):
                    self.preferences['disliked_genres'].append({
                        'name': genre,
                        'weight': 1
                    })
                
                # Reduce weight in favorites
                for fav_genre in self.preferences['favorite_genres']:
                    if fav_genre['name'] == genre:
                        fav_genre['weight'] = max(0, fav_genre['weight'] - 1)
                        break
    
    def get_top_genres(self, limit: int = 5) -> List[str]:
        """Get top favorite genres"""
        # Sort by weight and return top genres
        sorted_genres = sorted(
            self.preferences['favorite_genres'], 
            key=lambda x: x['weight'], 
            reverse=True
        )
        return [g['name'] for g in sorted_genres[:limit] if g['weight'] > 0]
    
    def is_liked(self, item_id: int, content_type: str) -> bool:
        """Check if an item is liked"""
        if content_type == 'movie':
            return any(x['id'] == item_id for x in self.preferences['liked_movies'])
        else:
            return any(x['id'] == item_id for x in self.preferences['liked_tv_shows'])
    
    def is_disliked(self, item_id: int, content_type: str) -> bool:
        """Check if an item is disliked"""
        if content_type == 'movie':
            return any(x['id'] == item_id for x in self.preferences['disliked_movies'])
        else:
            return any(x['id'] == item_id for x in self.preferences['disliked_tv_shows'])
    
    def get_recommendation_preferences(self) -> Dict:
        """Get preferences formatted for recommendation engine"""
        return {
            'preferred_genres': self.get_top_genres(),
            'min_rating': self.preferences['min_rating_preference'],
            'content_types': self.preferences['preferred_content_types'],
            'liked_items': self.preferences['liked_movies'] + self.preferences['liked_tv_shows'],
            'disliked_items': self.preferences['disliked_movies'] + self.preferences['disliked_tv_shows']
        }
    
    def add_to_viewing_history(self, item: Dict):
        """Add item to viewing history"""
        history_item = {
            'id': item['id'],
            'title': item['title'],
            'type': item['type'],
            'viewed_date': datetime.now().isoformat()
        }
        
        # Remove if already in history
        self.preferences['viewing_history'] = [
            x for x in self.preferences['viewing_history'] if x['id'] != item['id']
        ]
        
        # Add to beginning of history
        self.preferences['viewing_history'].insert(0, history_item)
        
        # Keep only last 100 items
        self.preferences['viewing_history'] = self.preferences['viewing_history'][:100]
        
        self.save_preferences()
    
    def get_stats(self) -> Dict:
        """Get user preference statistics"""
        return {
            'total_liked_movies': len(self.preferences['liked_movies']),
            'total_liked_tv_shows': len(self.preferences['liked_tv_shows']),
            'total_disliked_movies': len(self.preferences['disliked_movies']),
            'total_disliked_tv_shows': len(self.preferences['disliked_tv_shows']),
            'top_genres': self.get_top_genres(),
            'viewing_history_count': len(self.preferences['viewing_history']),
            'last_updated': self.preferences.get('last_updated')
        }
    
    def reset_preferences(self):
        """Reset all preferences"""
        if os.path.exists(self.preferences_file):
            os.remove(self.preferences_file)
        self.preferences = self.load_preferences()
        st.success("Preferences reset successfully!") 
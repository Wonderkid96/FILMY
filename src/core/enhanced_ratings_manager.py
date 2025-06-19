import pandas as pd
import streamlit as st
import os
from typing import Dict, List
from datetime import datetime
from .google_sheets_manager import GoogleSheetsManager
from .config import RATING_SYSTEM, RATING_LABELS, CSV_HEADERS


class EnhancedRatingsManager:
    """
    Manages movie/TV ratings with CSV storage and Google Sheets sync.
    Prevents duplicate recommendations and tracks all viewing history.
    """
    
    def __init__(self, csv_file: str = 'filmy_ratings.csv'):
        self.csv_file = csv_file
        self.df = self.load_csv()
        self.google_sheets = GoogleSheetsManager()
        
        # Sync with Google Sheets on startup if available
        if self.google_sheets.is_connected():
            self.sync_from_google_sheets()
    
    def load_csv(self) -> pd.DataFrame:
        """Load ratings from CSV file"""
        if os.path.exists(self.csv_file):
            try:
                df = pd.read_csv(self.csv_file)
                # Ensure all required columns exist
                for col in CSV_HEADERS:
                    if col not in df.columns:
                        df[col] = ''
                return df
            except Exception as e:
                st.warning(f"Error loading CSV: {e}")
                return self.create_empty_dataframe()
        else:
            return self.create_empty_dataframe()
    
    def create_empty_dataframe(self) -> pd.DataFrame:
        """Create empty DataFrame with correct structure"""
        return pd.DataFrame(columns=CSV_HEADERS)
    
    def save_csv(self):
        """Save ratings to CSV file"""
        try:
            self.df.to_csv(self.csv_file, index=False)
        except Exception as e:
            st.error(f"Error saving CSV: {e}")
    
    def add_rating(self, tmdb_id: int, title: str, content_type: str,
                   rating: int, item_data: Dict, custom_label: str = None) -> bool:
        """Add a new rating (prevents duplicates)"""
        # Check if already rated
        if self.is_already_rated(tmdb_id, content_type):
            return self.update_rating(tmdb_id, content_type, rating, custom_label)
        
        # Determine rating label
        if custom_label:
            rating_label = custom_label
        elif rating in RATING_LABELS:
            rating_label = RATING_LABELS[rating]
        else:
            # Handle special ratings (0, -1, -2)
            special_labels = {
                0: "Want to See",
                -1: "Not Interested", 
                -2: "Maybe Later"
            }
            rating_label = special_labels.get(rating, "Unknown")
        
        # Prepare rating data
        rating_data = {
            'tmdb_id': tmdb_id,
            'title': title,
            'type': content_type,
            'release_date': item_data.get('release_date', ''),
            'genres': item_data.get('genres', []),
            'tmdb_rating': item_data.get('vote_average', 0),
            'my_rating': rating,
            'my_rating_label': rating_label,
            'date_rated': datetime.now().isoformat(),
            'overview': item_data.get('overview', ''),
            'poster_url': item_data.get('poster_path', '')
        }
        
        # Add to local DataFrame
        new_row = pd.DataFrame([{
            'tmdb_id': rating_data['tmdb_id'],
            'title': rating_data['title'],
            'type': rating_data['type'],
            'release_date': rating_data['release_date'],
            'genres': ', '.join(rating_data['genres']) if isinstance(rating_data['genres'], list) else rating_data['genres'],
            'tmdb_rating': rating_data['tmdb_rating'],
            'my_rating': rating_data['my_rating'],
            'my_rating_label': rating_data['my_rating_label'],
            'date_rated': rating_data['date_rated'],
            'overview': rating_data['overview'],
            'poster_url': rating_data['poster_url']
        }])
        
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_csv()
        
        # Sync to Google Sheets if connected
        if self.google_sheets.is_connected():
            self.google_sheets.add_rating(rating_data)
        
        return True
    
    def update_rating(self, tmdb_id: int, content_type: str, new_rating: int, custom_label: str = None) -> bool:
        """Update existing rating"""
        mask = (self.df['tmdb_id'] == tmdb_id) & (self.df['type'] == content_type)
        
        if mask.any():
            # Determine rating label
            if custom_label:
                rating_label = custom_label
            elif new_rating in RATING_LABELS:
                rating_label = RATING_LABELS[new_rating]
            else:
                special_labels = {0: "Want to See", -1: "Not Interested", -2: "Maybe Later"}
                rating_label = special_labels.get(new_rating, "Unknown")
            
            self.df.loc[mask, 'my_rating'] = new_rating
            self.df.loc[mask, 'my_rating_label'] = rating_label
            self.df.loc[mask, 'date_rated'] = datetime.now().isoformat()
            self.save_csv()
            
            # Update in Google Sheets
            if self.google_sheets.is_connected():
                self.google_sheets.update_rating(
                    tmdb_id, content_type, new_rating, rating_label
                )
            
            return True
        
        return False
    
    def delete_rating(self, tmdb_id: int, content_type: str) -> bool:
        """Delete a rating"""
        mask = (self.df['tmdb_id'] == tmdb_id) & (self.df['type'] == content_type)
        
        if mask.any():
            # Remove from local DataFrame
            self.df = self.df[~mask]
            self.save_csv()
            
            # Delete from Google Sheets
            if self.google_sheets.is_connected():
                return self.google_sheets.delete_rating(tmdb_id, content_type)
            
            return True
        
        return False
    
    def is_already_rated(self, tmdb_id: int, content_type: str) -> bool:
        """Check if content is already rated (prevents duplicates)"""
        if self.df.empty:
            return False
        
        return not self.df[
            (self.df['tmdb_id'] == tmdb_id) & (self.df['type'] == content_type)
        ].empty
    
    def get_rated_ids(self, content_type: str = None) -> List[int]:
        """Get list of all rated TMDB IDs (for filtering recommendations)"""
        if self.df.empty:
            return []
        
        filtered_df = self.df
        if content_type:
            filtered_df = self.df[self.df['type'] == content_type]
        
        return filtered_df['tmdb_id'].dropna().astype(int).tolist()
    
    def get_all_ratings(self) -> pd.DataFrame:
        """Get all ratings data"""
        return self.df.copy()
    
    def get_recommendations(self, limit: int = 15) -> List[Dict]:
        """Get personalized recommendations based on user ratings"""
        from .tmdb_api import TMDBApi
        
        if self.df.empty:
            return []
        
        # Get highly rated content (3+ stars)
        good_ratings = self.df[self.df['my_rating'] >= 3]
        
        if good_ratings.empty:
            return []
        
        tmdb = TMDBApi()
        recommendations = []
        
        try:
            # Get recommendations based on highly rated movies/shows
            for _, item in good_ratings.iterrows():
                if item['type'] == 'movie':
                    similar = tmdb.get_similar_movies(item['tmdb_id'])
                    recs = tmdb.get_movie_recommendations(item['tmdb_id'])
                else:
                    similar = tmdb.get_similar_tv(item['tmdb_id'])
                    recs = tmdb.get_tv_recommendations(item['tmdb_id'])
                
                # Process similar content
                if similar and 'results' in similar:
                    for rec in similar['results'][:3]:  # Top 3 similar
                        if not self.is_already_rated(rec['id'], item['type']):
                            rec_data = tmdb.format_movie_data(rec) if item['type'] == 'movie' else tmdb.format_tv_data(rec)
                            if rec_data:
                                recommendations.append(rec_data)
                
                # Process TMDB recommendations
                if recs and 'results' in recs:
                    for rec in recs['results'][:2]:  # Top 2 recommendations
                        if not self.is_already_rated(rec['id'], item['type']):
                            rec_data = tmdb.format_movie_data(rec) if item['type'] == 'movie' else tmdb.format_tv_data(rec)
                            if rec_data:
                                recommendations.append(rec_data)
        
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
        
        # Remove duplicates and limit results
        seen = set()
        unique_recs = []
        for rec in recommendations:
            key = (rec['id'], rec['type'])
            if key not in seen:
                seen.add(key)
                unique_recs.append(rec)
                if len(unique_recs) >= limit:
                    break
        
        return unique_recs
    
    def get_user_rating(self, tmdb_id: int, content_type: str) -> int:
        """Get user's rating for a specific item"""
        if self.df.empty:
            return None
        
        mask = (self.df['tmdb_id'] == tmdb_id) & (self.df['type'] == content_type)
        matches = self.df[mask]
        
        if not matches.empty:
            return matches.iloc[0]['my_rating']
        
        return None
    
    def get_ratings_by_score(self, min_score: int, content_type: str = None) -> pd.DataFrame:
        """Get all items with rating >= min_score"""
        if self.df.empty:
            return pd.DataFrame()
        
        filtered_df = self.df[self.df['my_rating'] >= min_score]
        
        if content_type:
            filtered_df = filtered_df[filtered_df['type'] == content_type]
        
        return filtered_df
    
    def get_genre_preferences(self) -> Dict[str, float]:
        """Calculate genre preferences based on ratings"""
        if self.df.empty:
            return {}
        
        genre_scores = {}
        
        for _, row in self.df.iterrows():
            if pd.isna(row['genres']) or row['genres'] == '':
                continue
                
            genres = row['genres'].split(', ') if isinstance(row['genres'], str) else []
            rating = row['my_rating']
            
            for genre in genres:
                genre = genre.strip()
                if genre:
                    if genre not in genre_scores:
                        genre_scores[genre] = []
                    genre_scores[genre].append(rating)
        
        # Calculate average score per genre
        genre_averages = {
            genre: sum(scores) / len(scores) 
            for genre, scores in genre_scores.items()
        }
        
        return dict(sorted(genre_averages.items(), key=lambda x: x[1], reverse=True))
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        if self.df.empty:
            return {
                'total_ratings': 0,
                'movies_rated': 0,
                'tv_shows_rated': 0,
                'average_rating': 0,
                'rating_distribution': {},
                'top_genres': [],
                'recent_ratings': []
            }
        
        stats = {
            'total_ratings': len(self.df),
            'movies_rated': len(self.df[self.df['type'] == 'movie']),
            'tv_shows_rated': len(self.df[self.df['type'] == 'tv']),
            'average_rating': self.df['my_rating'].mean(),
            'rating_distribution': self.df['my_rating'].value_counts().to_dict(),
            'top_genres': list(self.get_genre_preferences().keys())[:5],
            'recent_ratings': self.df.sort_values('date_rated', ascending=False).head(5)[['title', 'my_rating_label', 'date_rated']].to_dict('records')
        }
        
        return stats
    
    def export_for_recommendations(self) -> Dict:
        """Export data in format suitable for recommendation engine"""
        genre_prefs = self.get_genre_preferences()
        
        return {
            'rated_movie_ids': self.get_rated_ids('movie'),
            'rated_tv_ids': self.get_rated_ids('tv'),
            'liked_content': self.get_ratings_by_score(3),  # Good or Perfect
            'disliked_content': self.get_ratings_by_score(1),  # Only Hate
            'genre_preferences': genre_prefs,
            'preferred_genres': list(genre_prefs.keys())[:5] if genre_prefs else [],
            'average_user_rating': self.df['my_rating'].mean() if not self.df.empty else 2.5
        }
    
    def sync_from_google_sheets(self):
        """Sync data from Google Sheets to local CSV"""
        if not self.google_sheets.is_connected():
            return
        
        try:
            remote_df = self.google_sheets.get_all_ratings()
            if not remote_df.empty:
                # Merge with local data (remote takes precedence)
                self.df = remote_df.copy()
                self.save_csv()
                st.success("✅ Synced data from Google Sheets!")
        except Exception as e:
            st.warning(f"Could not sync from Google Sheets: {e}")
    
    def sync_to_google_sheets(self):
        """Sync local data to Google Sheets"""
        if not self.google_sheets.is_connected():
            st.warning("Google Sheets not connected")
            return False
        
        try:
            # Export current CSV to Google Sheets
            if os.path.exists(self.csv_file):
                return self.google_sheets.import_from_csv(self.csv_file)
        except Exception as e:
            st.error(f"Failed to sync to Google Sheets: {e}")
            return False
    
    def get_google_sheet_url(self) -> str:
        """Get URL to view Google Sheet"""
        return self.google_sheets.get_sheet_url()
    
    def is_google_sheets_connected(self) -> bool:
        """Check if Google Sheets is connected"""
        return self.google_sheets.is_connected() 
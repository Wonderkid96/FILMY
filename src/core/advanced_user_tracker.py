import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .enhanced_ratings_manager import EnhancedRatingsManager
from .google_sheets_manager import GoogleSheetsManager
from .config import CSV_HEADERS, RATING_LABELS


class AdvancedUserTracker:
    """
    Sophisticated user tracking system for couples
    Tracks who's seen what, joint ratings, and provides intelligent recommendations
    """
    
    def __init__(self):
        self.ratings_manager = EnhancedRatingsManager()
        self.google_sheets = GoogleSheetsManager()
        
        # Enhanced CSV headers for user tracking
        self.enhanced_headers = CSV_HEADERS + [
            'toby_seen', 'taz_seen', 'both_seen', 'who_rated', 
            'couple_score', 'recommendation_type', 'date_discovered'
        ]
    
    def track_viewing_status(self, tmdb_id: int, title: str, content_type: str, 
                           item_data: Dict, viewer: str) -> bool:
        """
        Track who has seen what content
        viewer can be: 'Toby', 'Taz', 'Both', or 'Neither'
        """
        # Check if item already exists
        existing_entry = self._get_existing_entry(tmdb_id, content_type)
        
        if existing_entry is not None:
            # Update existing entry
            return self._update_viewing_status(existing_entry, viewer)
        else:
            # Create new entry
            return self._create_new_viewing_entry(
                tmdb_id, title, content_type, item_data, viewer
            )
    
    def _get_existing_entry(self, tmdb_id: int, content_type: str) -> Optional[Dict]:
        """Get existing entry for a film/show"""
        if self.ratings_manager.df.empty:
            return None
        
        mask = ((self.ratings_manager.df['tmdb_id'] == tmdb_id) & 
                (self.ratings_manager.df['type'] == content_type))
        
        if mask.any():
            return self.ratings_manager.df[mask].iloc[0].to_dict()
        return None
    
    def _update_viewing_status(self, existing_entry: Dict, viewer: str) -> bool:
        """Update viewing status for existing entry"""
        try:
            # Get the row index
            mask = ((self.ratings_manager.df['tmdb_id'] == existing_entry['tmdb_id']) & 
                    (self.ratings_manager.df['type'] == existing_entry['type']))
            
            # Update viewing status based on viewer
            if viewer == 'Toby':
                self.ratings_manager.df.loc[mask, 'toby_seen'] = True
                self.ratings_manager.df.loc[mask, 'both_seen'] = (
                    existing_entry.get('taz_seen', False)
                )
            elif viewer == 'Taz':
                self.ratings_manager.df.loc[mask, 'taz_seen'] = True
                self.ratings_manager.df.loc[mask, 'both_seen'] = (
                    existing_entry.get('toby_seen', False)
                )
            elif viewer == 'Both':
                self.ratings_manager.df.loc[mask, 'toby_seen'] = True
                self.ratings_manager.df.loc[mask, 'taz_seen'] = True
                self.ratings_manager.df.loc[mask, 'both_seen'] = True
            
            self.ratings_manager.df.loc[mask, 'date_discovered'] = datetime.now().isoformat()
            self.ratings_manager.save_csv()
            
            # Sync to Google Sheets
            if self.google_sheets.is_connected():
                self._sync_enhanced_data_to_sheets()
            
            return True
            
        except Exception as e:
            st.error(f"Error updating viewing status: {e}")
            return False
    
    def _create_new_viewing_entry(self, tmdb_id: int, title: str, content_type: str, 
                                 item_data: Dict, viewer: str) -> bool:
        """Create new viewing entry"""
        try:
            # Prepare enhanced rating data
            enhanced_data = {
                'tmdb_id': tmdb_id,
                'title': title,
                'type': content_type,
                'release_date': item_data.get('release_date', ''),
                'genres': ', '.join(item_data.get('genres', [])) if isinstance(item_data.get('genres', []), list) else item_data.get('genres', ''),
                'tmdb_rating': item_data.get('vote_average', 0),
                'my_rating': 0,  # Default to "Want to See"
                'my_rating_label': 'Discovered',
                'date_rated': datetime.now().isoformat(),
                'overview': item_data.get('overview', ''),
                'poster_url': item_data.get('poster_path', ''),
                'toby_seen': viewer in ['Toby', 'Both'],
                'taz_seen': viewer in ['Taz', 'Both'],
                'both_seen': viewer == 'Both',
                'who_rated': viewer,
                'couple_score': 0,
                'recommendation_type': 'Discovery',
                'date_discovered': datetime.now().isoformat()
            }
            
            # Add to DataFrame
            new_row = pd.DataFrame([enhanced_data])
            self.ratings_manager.df = pd.concat([self.ratings_manager.df, new_row], ignore_index=True)
            self.ratings_manager.save_csv()
            
            # Sync to Google Sheets
            if self.google_sheets.is_connected():
                self._sync_enhanced_data_to_sheets()
            
            return True
            
        except Exception as e:
            st.error(f"Error creating viewing entry: {e}")
            return False
    
    def add_couple_rating(self, tmdb_id: int, content_type: str, toby_rating: int, 
                         taz_rating: int) -> bool:
        """Add ratings from both users and calculate couple score"""
        try:
            mask = ((self.ratings_manager.df['tmdb_id'] == tmdb_id) & 
                    (self.ratings_manager.df['type'] == content_type))
            
            if mask.any():
                # Calculate couple score (average + bonus for agreement)
                couple_score = (toby_rating + taz_rating) / 2
                
                # Bonus for perfect agreement
                if toby_rating == taz_rating:
                    couple_score += 0.5
                
                # Update the entry
                self.ratings_manager.df.loc[mask, 'my_rating'] = couple_score
                self.ratings_manager.df.loc[mask, 'my_rating_label'] = f"Toby:{RATING_LABELS[toby_rating]}, Taz:{RATING_LABELS[taz_rating]}"
                self.ratings_manager.df.loc[mask, 'couple_score'] = couple_score
                self.ratings_manager.df.loc[mask, 'who_rated'] = 'Both'
                self.ratings_manager.df.loc[mask, 'both_seen'] = True
                self.ratings_manager.df.loc[mask, 'toby_seen'] = True
                self.ratings_manager.df.loc[mask, 'taz_seen'] = True
                self.ratings_manager.df.loc[mask, 'date_rated'] = datetime.now().isoformat()
                
                self.ratings_manager.save_csv()
                
                # Sync to Google Sheets
                if self.google_sheets.is_connected():
                    self._sync_enhanced_data_to_sheets()
                
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error adding couple rating: {e}")
            return False
    
    def get_couple_compatibility_analysis(self) -> Dict:
        """Advanced analysis of couple's movie compatibility"""
        if self.ratings_manager.df.empty:
            return {'compatibility_score': 0, 'analysis': 'No data yet'}
        
        # Get movies both have seen and rated
        both_seen = self.ratings_manager.df[
            (self.ratings_manager.df['both_seen'] == True) & 
            (self.ratings_manager.df['my_rating'] > 0)
        ]
        
        if both_seen.empty:
            return {'compatibility_score': 0, 'analysis': 'No joint ratings yet'}
        
        # Calculate compatibility metrics
        avg_couple_score = both_seen['couple_score'].mean()
        total_agreements = len(both_seen[both_seen['who_rated'] == 'Both'])
        
        # Genre analysis
        genre_compatibility = self._analyze_genre_compatibility()
        
        # Viewing pattern analysis
        viewing_patterns = self._analyze_viewing_patterns()
        
        return {
            'compatibility_score': round(avg_couple_score * 25, 1),  # Convert to percentage
            'total_joint_ratings': len(both_seen),
            'perfect_agreements': total_agreements,
            'genre_compatibility': genre_compatibility,
            'viewing_patterns': viewing_patterns,
            'recommendation': self._get_compatibility_recommendation(avg_couple_score)
        }
    
    def _analyze_genre_compatibility(self) -> Dict:
        """Analyze genre preferences compatibility"""
        # Implementation for genre analysis
        return {'shared_favorites': [], 'differences': []}
    
    def _analyze_viewing_patterns(self) -> Dict:
        """Analyze viewing patterns and habits"""
        toby_only = len(self.ratings_manager.df[
            (self.ratings_manager.df['toby_seen'] == True) & 
            (self.ratings_manager.df['taz_seen'] == False)
        ])
        
        taz_only = len(self.ratings_manager.df[
            (self.ratings_manager.df['taz_seen'] == True) & 
            (self.ratings_manager.df['toby_seen'] == False)
        ])
        
        both_seen = len(self.ratings_manager.df[self.ratings_manager.df['both_seen'] == True])
        
        return {
            'toby_solo_viewing': toby_only,
            'taz_solo_viewing': taz_only,
            'joint_viewing': both_seen,
            'sync_percentage': round((both_seen / max(1, toby_only + taz_only + both_seen)) * 100, 1)
        }
    
    def _get_compatibility_recommendation(self, score: float) -> str:
        """Get compatibility recommendation based on score"""
        if score >= 3.5:
            return "🔥 Perfect movie compatibility! You're cinematic soulmates!"
        elif score >= 3.0:
            return "💫 Great compatibility! You love similar films."
        elif score >= 2.5:
            return "👍 Good compatibility with some differences to explore."
        elif score >= 2.0:
            return "🤔 Mixed tastes - perfect for discovering new genres together!"
        else:
            return "🎭 Very different tastes - adventure awaits in compromise picks!"
    
    def get_smart_couple_recommendations(self, num_recommendations: int = 10) -> List[Dict]:
        """Get intelligent recommendations based on couple's viewing history"""
        compatibility = self.get_couple_compatibility_analysis()
        
        # Use different strategies based on compatibility
        if compatibility['compatibility_score'] > 75:
            # High compatibility - recommend similar to what you both love
            return self._get_similar_taste_recommendations(num_recommendations)
        elif compatibility['compatibility_score'] > 50:
            # Medium compatibility - balanced recommendations
            return self._get_balanced_recommendations(num_recommendations)
        else:
            # Low compatibility - compromise and exploration recommendations
            return self._get_compromise_recommendations(num_recommendations)
    
    def _get_similar_taste_recommendations(self, num: int) -> List[Dict]:
        """Recommendations for couples with similar tastes"""
        # Implementation for similar taste recommendations
        return []
    
    def _get_balanced_recommendations(self, num: int) -> List[Dict]:
        """Balanced recommendations for medium compatibility"""
        # Implementation for balanced recommendations
        return []
    
    def _get_compromise_recommendations(self, num: int) -> List[Dict]:
        """Compromise recommendations for different tastes"""
        # Implementation for compromise recommendations
        return []
    
    def _sync_enhanced_data_to_sheets(self):
        """Sync enhanced tracking data to Google Sheets"""
        if not self.google_sheets.is_connected():
            return
        
        try:
            # This would need to be implemented to handle the enhanced data structure
            # For now, we'll use the existing sync method
            pass
        except Exception as e:
            st.warning(f"Could not sync enhanced data: {e}")
    
    def get_discovery_stats(self) -> Dict:
        """Get statistics about content discovery"""
        if self.ratings_manager.df.empty:
            return {}
        
        total_discovered = len(self.ratings_manager.df)
        toby_discoveries = len(self.ratings_manager.df[self.ratings_manager.df['toby_seen'] == True])
        taz_discoveries = len(self.ratings_manager.df[self.ratings_manager.df['taz_seen'] == True])
        joint_discoveries = len(self.ratings_manager.df[self.ratings_manager.df['both_seen'] == True])
        
        return {
            'total_discovered': total_discovered,
            'toby_discoveries': toby_discoveries,
            'taz_discoveries': taz_discoveries,
            'joint_discoveries': joint_discoveries,
            'discovery_sync_rate': round((joint_discoveries / max(1, total_discovered)) * 100, 1)
        } 
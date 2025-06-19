import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from config import (
    GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID, GOOGLE_WORKSHEET_NAME,
    CSV_HEADERS
)


class GoogleSheetsManager:
    """Manages Google Sheets integration for storing movie ratings"""
    
    def __init__(self):
        self.gc = None
        self.sheet = None
        self.worksheet = None
        self.credentials_file = GOOGLE_CREDENTIALS_FILE
        self.sheet_id = GOOGLE_SHEET_ID
        self.worksheet_name = GOOGLE_WORKSHEET_NAME
        
        # Try to initialize connection
        self.connect()
    
    def connect(self) -> bool:
        """Connect to Google Sheets API"""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Try to load credentials from file first
            if os.path.exists(self.credentials_file):
                credentials = Credentials.from_service_account_file(
                    self.credentials_file, scopes=scope
                )
            else:
                # Try to load from Streamlit secrets or environment
                try:
                    import streamlit as st
                    if hasattr(st, 'secrets') and 'google_credentials' in st.secrets:
                        credentials_dict = dict(st.secrets['google_credentials'])
                        credentials = Credentials.from_service_account_info(
                            credentials_dict, scopes=scope
                        )
                    else:
                        st.warning("Google credentials not found in file or secrets")
                        return False
                except Exception as e:
                    st.warning(f"Google credentials not available: {e}")
                    return False
            
            # Connect to Google Sheets
            self.gc = gspread.authorize(credentials)
            
            # Open the existing sheet by ID
            try:
                self.sheet = self.gc.open_by_key(self.sheet_id)
            except gspread.SpreadsheetNotFound:
                st.error("Could not access the specified Google Sheet. Check permissions.")
                return False
            
            # Get or create worksheet
            try:
                self.worksheet = self.sheet.worksheet(self.worksheet_name)
                # Check if headers exist, if not add them
                if self.worksheet.row_count == 0 or not self.worksheet.row_values(1):
                    self.worksheet.append_row(CSV_HEADERS)
                elif self.worksheet.row_values(1) != CSV_HEADERS:
                    # Headers exist but are different, update them
                    self.worksheet.update('A1:K1', [CSV_HEADERS])
            except gspread.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(
                    title=self.worksheet_name, 
                    rows=1000, 
                    cols=len(CSV_HEADERS)
                )
                # Add headers
                self.worksheet.append_row(CSV_HEADERS)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to connect to Google Sheets: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to Google Sheets"""
        return self.worksheet is not None
    
    def add_rating(self, rating_data: Dict) -> bool:
        """Add a new rating to Google Sheets"""
        if not self.is_connected():
            return False
        
        try:
            # Prepare row data in correct order
            row_data = [
                rating_data.get('tmdb_id', ''),
                rating_data.get('title', ''),
                rating_data.get('type', ''),
                rating_data.get('release_date', ''),
                ', '.join(rating_data.get('genres', [])),
                rating_data.get('tmdb_rating', 0),
                rating_data.get('my_rating', 0),
                rating_data.get('my_rating_label', ''),
                rating_data.get('date_rated', ''),
                rating_data.get('overview', ''),
                rating_data.get('poster_url', '')
            ]
            
            self.worksheet.append_row(row_data)
            return True
            
        except Exception as e:
            st.error(f"Failed to add rating to Google Sheets: {e}")
            return False
    
    def get_all_ratings(self) -> pd.DataFrame:
        """Get all ratings from Google Sheets"""
        if not self.is_connected():
            return pd.DataFrame()
        
        try:
            # Get all records
            records = self.worksheet.get_all_records()
            df = pd.DataFrame(records)
            
            # Convert data types
            if not df.empty:
                df['tmdb_id'] = pd.to_numeric(df['tmdb_id'], errors='coerce')
                df['my_rating'] = pd.to_numeric(df['my_rating'], errors='coerce')
                df['tmdb_rating'] = pd.to_numeric(df['tmdb_rating'], errors='coerce')
                df['date_rated'] = pd.to_datetime(df['date_rated'], errors='coerce')
            
            return df
            
        except Exception as e:
            st.error(f"Failed to get ratings from Google Sheets: {e}")
            return pd.DataFrame()
    
    def is_already_rated(self, tmdb_id: int, content_type: str) -> bool:
        """Check if content is already rated"""
        if not self.is_connected():
            return False
        
        try:
            df = self.get_all_ratings()
            if df.empty:
                return False
            
            return not df[
                (df['tmdb_id'] == tmdb_id) & (df['type'] == content_type)
            ].empty
            
        except Exception as e:
            st.error(f"Error checking if content is rated: {e}")
            return False
    
    def update_rating(self, tmdb_id: int, content_type: str, new_rating: int, 
                     new_rating_label: str) -> bool:
        """Update existing rating"""
        if not self.is_connected():
            return False
        
        try:
            # Find the row to update
            all_values = self.worksheet.get_all_values()
            headers = all_values[0]
            
            # Find column indices
            id_col = headers.index('tmdb_id') + 1
            type_col = headers.index('type') + 1
            rating_col = headers.index('my_rating') + 1
            label_col = headers.index('my_rating_label') + 1
            date_col = headers.index('date_rated') + 1
            
            # Find the row
            for i, row in enumerate(all_values[1:], start=2):
                if (str(row[id_col-1]) == str(tmdb_id) and 
                    row[type_col-1] == content_type):
                    
                    # Update the rating
                    self.worksheet.update_cell(i, rating_col, new_rating)
                    self.worksheet.update_cell(i, label_col, new_rating_label)
                    self.worksheet.update_cell(i, date_col, datetime.now().isoformat())
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"Failed to update rating: {e}")
            return False
    
    def delete_rating(self, tmdb_id: int, content_type: str) -> bool:
        """Delete a rating from Google Sheets"""
        if not self.is_connected():
            return False
        
        try:
            # Find the row to delete
            all_values = self.worksheet.get_all_values()
            headers = all_values[0]
            
            # Find column indices
            id_col = headers.index('tmdb_id') + 1
            type_col = headers.index('type') + 1
            
            # Find the row
            for i, row in enumerate(all_values[1:], start=2):
                if (str(row[id_col-1]) == str(tmdb_id) and 
                    row[type_col-1] == content_type):
                    
                    # Delete the row
                    self.worksheet.delete_rows(i)
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"Failed to delete rating: {e}")
            return False
    
    def export_to_csv(self, filename: str = 'filmy_ratings.csv') -> bool:
        """Export all ratings to CSV file"""
        try:
            df = self.get_all_ratings()
            if df.empty:
                st.warning("No ratings to export")
                return False
            
            df.to_csv(filename, index=False)
            return True
            
        except Exception as e:
            st.error(f"Failed to export CSV: {e}")
            return False
    
    def import_from_csv(self, filename: str) -> bool:
        """Import ratings from CSV file"""
        if not self.is_connected():
            return False
        
        try:
            df = pd.read_csv(filename)
            
            # Clear existing data (keep headers)
            self.worksheet.clear()
            self.worksheet.append_row(CSV_HEADERS)
            
            # Add all rows
            for _, row in df.iterrows():
                row_data = [str(row.get(col, '')) for col in CSV_HEADERS]
                self.worksheet.append_row(row_data)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to import CSV: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get rating statistics"""
        df = self.get_all_ratings()
        if df.empty:
            return {}
        
        stats = {
            'total_ratings': len(df),
            'movies_rated': len(df[df['type'] == 'movie']),
            'tv_shows_rated': len(df[df['type'] == 'tv']),
            'average_rating': df['my_rating'].mean(),
            'rating_distribution': df['my_rating'].value_counts().to_dict(),
            'most_recent': df['date_rated'].max() if 'date_rated' in df.columns else None
        }
        
        return stats
    
    def get_sheet_url(self) -> str:
        """Get the URL of the Google Sheet"""
        if self.sheet:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet.id}"
        return "" 
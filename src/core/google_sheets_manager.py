import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
from .config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_SHEET_ID,
    GOOGLE_WORKSHEET_NAME,
    CSV_HEADERS,
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
        self.last_api_call = 0
        self.min_call_interval = 1.0  # Minimum 1 second between API calls

        # Try to initialize connection
        self.connect()

    def _rate_limit(self):
        """Simple rate limiting to avoid quota issues"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_call_interval:
            time.sleep(self.min_call_interval - time_since_last_call)
        self.last_api_call = time.time()

    def connect(self) -> bool:
        """Connect to Google Sheets API"""
        try:
            # Define the scope
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
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

                    if hasattr(st, "secrets") and "google_credentials" in st.secrets:
                        credentials_dict = dict(st.secrets["google_credentials"])
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
                st.error(
                    "Could not access the specified Google Sheet. Check permissions."
                )
                return False

            # Get or create worksheet
            try:
                self.worksheet = self.sheet.worksheet(self.worksheet_name)
                # Check if headers exist, if not add them
                if self.worksheet.row_count == 0 or not self.worksheet.row_values(1):
                    self._setup_sophisticated_sheet()
                elif self.worksheet.row_values(1) != CSV_HEADERS:
                    # Headers exist but are different, update them
                    self._setup_sophisticated_sheet()
            except gspread.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(
                    title=self.worksheet_name, rows=1000, cols=len(CSV_HEADERS)
                )
                # Setup sophisticated formatting
                self._setup_sophisticated_sheet()

            return True

        except Exception as e:
            st.error(f"Failed to connect to Google Sheets: {e}")
            return False

    def _setup_sophisticated_sheet(self):
        """Set up sophisticated sheet formatting with colors and layout"""
        try:
            # Clear existing content
            self.worksheet.clear()

            # Add headers with enhanced formatting for user tracking
            enhanced_headers = [
                "TMDB ID",
                "Title",
                "Type",
                "Release Date",
                "Genres",
                "TMDB Rating",
                "My Rating",
                "Rating Label",
                "Date Rated",
                "Overview",
                "Poster URL",
                "Toby Seen",
                "Taz Seen",
                "Both Seen",
                "Who Rated",
                "Couple Score",
                "Rec Type",
                "Date Discovered",
                "Statistics",
                "Live Data",
            ]

            # Set headers
            self.worksheet.update("A1:T1", [enhanced_headers])

            # Format header row - bold, centered, colored background
            self.worksheet.format(
                "A1:T1",
                {
                    "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        "fontSize": 12,
                    },
                    "horizontalAlignment": "CENTER",
                    "verticalAlignment": "MIDDLE",
                },
            )

            # Set column widths for better readability
            requests = [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 0,  # TMDB ID
                            "endIndex": 1,
                        },
                        "properties": {"pixelSize": 80},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 1,  # Title
                            "endIndex": 2,
                        },
                        "properties": {"pixelSize": 200},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 2,  # Type
                            "endIndex": 3,
                        },
                        "properties": {"pixelSize": 80},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 3,  # Release Date
                            "endIndex": 4,
                        },
                        "properties": {"pixelSize": 100},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 4,  # Genres
                            "endIndex": 5,
                        },
                        "properties": {"pixelSize": 150},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 6,  # My Rating
                            "endIndex": 7,
                        },
                        "properties": {"pixelSize": 90},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 7,  # Rating Label
                            "endIndex": 8,
                        },
                        "properties": {"pixelSize": 120},
                    }
                },
            ]

            # Apply column width requests
            self.worksheet.spreadsheet.batch_update({"requests": requests})

            # Add conditional formatting for ratings
            self._add_rating_conditional_formatting()

            # Freeze header row
            self.worksheet.freeze(rows=1)

            # Add summary section
            self._add_summary_section()

        except Exception as e:
            st.warning(f"Could not apply sophisticated formatting: {e}")
            # Fallback to basic headers
            self.worksheet.update("A1:K1", [CSV_HEADERS])

    def _add_rating_conditional_formatting(self):
        """Add conditional formatting for rating colors - Updated for 6-level system"""
        try:
            # Color coding for My Rating column (column G) - New 6-level system
            rating_rules = [
                # Perfect (4) - Gold
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,  # My Rating column
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "4"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 1,
                                "green": 0.84,
                                "blue": 0,
                            },  # Gold
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 0, "green": 0, "blue": 0},
                            },
                        },
                    },
                },
                # Good (3) - Green
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "3"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.2,
                                "green": 0.8,
                                "blue": 0.2,
                            },  # Green
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            },
                        },
                    },
                },
                # OK (2) - Orange
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "2"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 1,
                                "green": 0.65,
                                "blue": 0,
                            },  # Orange
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            },
                        },
                    },
                },
                # Hate (1) - Red
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "1"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 1,
                                "green": 0.27,
                                "blue": 0.27,
                            },  # Red
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            },
                        },
                    },
                },
                # Want to See (0) - Light Blue
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "0"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.39,
                                "green": 0.4,
                                "blue": 0.95,
                            },  # Indigo for watchlist
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            },
                        },
                    },
                },
                # Don't Want to See (-1) - Gray
                {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "startRowIndex": 1,
                        "endRowIndex": 1000,
                        "startColumnIndex": 6,
                        "endColumnIndex": 7,
                    },
                    "booleanRule": {
                        "condition": {
                            "type": "NUMBER_EQ",
                            "values": [{"userEnteredValue": "-1"}],
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.61,
                                "green": 0.64,
                                "blue": 0.69,
                            },  # Gray
                            "textFormat": {
                                "bold": True,
                                "strikethrough": True,
                                "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                            },
                        },
                    },
                },
            ]

            # Apply conditional formatting
            self.worksheet.spreadsheet.batch_update(
                {
                    "requests": [
                        {"addConditionalFormatRule": {"rule": rule, "index": i}}
                        for i, rule in enumerate(rating_rules)
                    ]
                }
            )

        except Exception as e:
            st.warning(f"Could not apply conditional formatting: {e}")

    def _format_new_row(self, row_number: int):
        """Apply formatting to a newly added row"""
        try:
            # Alternate row colors for better readability
            if row_number % 2 == 0:
                bg_color = {"red": 0.95, "green": 0.95, "blue": 0.95}
            else:
                bg_color = {"red": 1, "green": 1, "blue": 1}

            # Format the entire row
            self.worksheet.format(
                f"A{row_number}:K{row_number}",
                {
                    "backgroundColor": bg_color,
                    "textFormat": {"fontSize": 10},
                    "borders": {
                        "bottom": {
                            "style": "SOLID",
                            "width": 1,
                            "color": {"red": 0.8, "green": 0.8, "blue": 0.8},
                        }
                    },
                },
            )

            # Center align certain columns
            self.worksheet.format(
                f"A{row_number}:A{row_number}", {"horizontalAlignment": "CENTER"}
            )  # TMDB ID
            self.worksheet.format(
                f"C{row_number}:C{row_number}", {"horizontalAlignment": "CENTER"}
            )  # Type
            self.worksheet.format(
                f"D{row_number}:D{row_number}", {"horizontalAlignment": "CENTER"}
            )  # Release Date
            self.worksheet.format(
                f"F{row_number}:G{row_number}", {"horizontalAlignment": "CENTER"}
            )  # Ratings
            self.worksheet.format(
                f"I{row_number}:I{row_number}", {"horizontalAlignment": "CENTER"}
            )  # Date Rated

        except Exception as e:
            # Formatting failed, but don't break the main functionality
            pass

    def _add_summary_section(self):
        """Add a summary statistics section to the sheet"""
        try:
            # Add summary headers in column M
            summary_data = [
                ["📊 FILMY STATS", ""],
                ["Total Items:", "=COUNTA(G:G)-1"],
                ["🌟 Perfect (4):", "=COUNTIF(G:G,4)"],
                ["👍 Good (3):", "=COUNTIF(G:G,3)"],
                ["🤷 OK (2):", "=COUNTIF(G:G,2)"],
                ["😤 Hate (1):", "=COUNTIF(G:G,1)"],
                ["👀 Want to See (0):", "=COUNTIF(G:G,0)"],
                ["❌ Don't Want (-1):", "=COUNTIF(G:G,-1)"],
                ["Watched Items:", '=COUNTIF(G:G,">0")'],
                ["Avg Watched Rating:", "=AVERAGE(G2:G1000)"],
                ["Movies Watched:", '=COUNTIFS(C:C,"movie",G:G,">0")'],
                ["TV Shows Watched:", '=COUNTIFS(C:C,"tv",G:G,">0")'],
                ["Last Updated:", "=NOW()"],
            ]

            # Add summary data starting from M1
            for i, row in enumerate(summary_data, 1):
                self.worksheet.update(f"M{i}:N{i}", [row])

            # Format summary section
            self.worksheet.format(
                "M1:N1",
                {
                    "backgroundColor": {"red": 0.8, "green": 0.2, "blue": 0.2},
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                        "fontSize": 14,
                    },
                    "horizontalAlignment": "CENTER",
                },
            )

            # Format stats rows
            self.worksheet.format(
                "M2:N11",
                {
                    "backgroundColor": {"red": 0.95, "green": 0.95, "blue": 1},
                    "textFormat": {"fontSize": 11, "bold": True},
                    "borders": {
                        "top": {"style": "SOLID", "width": 1},
                        "bottom": {"style": "SOLID", "width": 1},
                        "left": {"style": "SOLID", "width": 1},
                        "right": {"style": "SOLID", "width": 1},
                    },
                },
            )

            # Set column widths for summary
            requests = [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 12,  # Column M
                            "endIndex": 13,
                        },
                        "properties": {"pixelSize": 150},
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "dimension": "COLUMNS",
                            "startIndex": 13,  # Column N
                            "endIndex": 14,
                        },
                        "properties": {"pixelSize": 120},
                    }
                },
            ]

            self.worksheet.spreadsheet.batch_update({"requests": requests})

        except Exception as e:
            st.warning(f"Could not add summary section: {e}")

    def is_connected(self) -> bool:
        """Check if connected to Google Sheets"""
        return self.worksheet is not None

    def add_rating(self, rating_data: Dict) -> bool:
        """Add a new rating to Google Sheets"""
        if not self.is_connected():
            return False

        try:
            self._rate_limit()  # Rate limiting
            # Prepare row data in correct order
            row_data = [
                rating_data.get("tmdb_id", ""),
                rating_data.get("title", ""),
                rating_data.get("type", ""),
                rating_data.get("release_date", ""),
                ", ".join(rating_data.get("genres", [])),
                rating_data.get("tmdb_rating", 0),
                rating_data.get("my_rating", 0),
                rating_data.get("my_rating_label", ""),
                rating_data.get("date_rated", ""),
                rating_data.get("overview", ""),
                rating_data.get("poster_url", ""),
            ]

            self.worksheet.append_row(row_data)

            # Apply formatting to the new row
            self._format_new_row(self.worksheet.row_count)

            return True

        except Exception as e:
            st.error(f"Failed to add rating to Google Sheets: {e}")
            return False

    def get_all_ratings(self) -> pd.DataFrame:
        """Get all ratings from Google Sheets"""
        if not self.is_connected():
            return pd.DataFrame()

        try:
            self._rate_limit()  # Rate limiting
            # Get all records
            records = self.worksheet.get_all_records()
            df = pd.DataFrame(records)

            # Convert data types
            if not df.empty:
                df["tmdb_id"] = pd.to_numeric(df["tmdb_id"], errors="coerce")
                df["my_rating"] = pd.to_numeric(df["my_rating"], errors="coerce")
                df["tmdb_rating"] = pd.to_numeric(df["tmdb_rating"], errors="coerce")
                df["date_rated"] = pd.to_datetime(df["date_rated"], errors="coerce")

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
                (df["tmdb_id"] == tmdb_id) & (df["type"] == content_type)
            ].empty

        except Exception as e:
            st.error(f"Error checking if content is rated: {e}")
            return False

    def update_rating(
        self, tmdb_id: int, content_type: str, new_rating: int, new_rating_label: str
    ) -> bool:
        """Update existing rating"""
        if not self.is_connected():
            return False

        try:
            # Find the row to update
            all_values = self.worksheet.get_all_values()
            headers = all_values[0]

            # Find column indices
            id_col = headers.index("tmdb_id") + 1
            type_col = headers.index("type") + 1
            rating_col = headers.index("my_rating") + 1
            label_col = headers.index("my_rating_label") + 1
            date_col = headers.index("date_rated") + 1

            # Find the row
            for i, row in enumerate(all_values[1:], start=2):
                if (
                    str(row[id_col - 1]) == str(tmdb_id)
                    and row[type_col - 1] == content_type
                ):

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
            id_col = headers.index("tmdb_id") + 1
            type_col = headers.index("type") + 1

            # Find the row
            for i, row in enumerate(all_values[1:], start=2):
                if (
                    str(row[id_col - 1]) == str(tmdb_id)
                    and row[type_col - 1] == content_type
                ):

                    # Delete the row
                    self.worksheet.delete_rows(i)
                    return True

            return False

        except Exception as e:
            st.error(f"Failed to delete rating: {e}")
            return False

    def export_to_csv(self, filename: str = "filmy_ratings.csv") -> bool:
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
                row_data = [str(row.get(col, "")) for col in CSV_HEADERS]
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
            "total_ratings": len(df),
            "movies_rated": len(df[df["type"] == "movie"]),
            "tv_shows_rated": len(df[df["type"] == "tv"]),
            "average_rating": df["my_rating"].mean(),
            "rating_distribution": df["my_rating"].value_counts().to_dict(),
            "most_recent": (
                df["date_rated"].max() if "date_rated" in df.columns else None
            ),
        }

        return stats

    def get_sheet_url(self) -> str:
        """Get the URL of the Google Sheet"""
        if self.sheet:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet.id}"
        return ""

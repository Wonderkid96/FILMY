import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Fallback to Streamlit secrets if running on Streamlit Cloud
if not TMDB_API_KEY:
    try:
        import streamlit as st

        TMDB_API_KEY = st.secrets.get("TMDB_API_KEY")
    except:
        pass
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE", "credentials/google_credentials.json"
)
GOOGLE_SHEET_ID = "1cEGSoX7b1458QAQn1ORLPlrqXVI9-hDqqjp7LL9kpOc"
GOOGLE_WORKSHEET_NAME = os.getenv("GOOGLE_WORKSHEET_NAME", "Sheet1")

# App Configuration
APP_TITLE = "🎬 FILMY - Your Personal Movie & TV Recommendation Engine"
APP_ICON = "🎬"

# Rating System - Toby's preference scale
RATING_SYSTEM = {
    "dont_want_to_see": -1,
    "want_to_see": 0,
    "hate": 1,
    "ok": 2,
    "good": 3,
    "perfect": 4,
}

RATING_LABELS = {
    -1: "❌ Don't Want to See",
    0: "👀 Want to See",
    1: "😤 Hate",
    2: "🤷 OK",
    3: "👍 Good",
    4: "🌟 Perfect",
}

RATING_COLORS = {
    -1: "#9CA3AF",  # Gray - for don't want to see
    0: "#6366F1",  # Indigo - for want to see
    1: "#FF4444",  # Red
    2: "#FFA500",  # Orange
    3: "#32CD32",  # Green
    4: "#FFD700",  # Gold
}

# Genre mappings for TMDB
MOVIE_GENRES = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

TV_GENRES = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    10762: "Kids",
    9648: "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37: "Western",
}

# Rating thresholds for recommendations
RATING_THRESHOLDS = {"excellent": 8.0, "good": 7.0, "average": 6.0, "poor": 5.0}

# CSV Headers for data export
CSV_HEADERS = [
    "tmdb_id",
    "title",
    "type",
    "release_date",
    "genres",
    "tmdb_rating",
    "my_rating",
    "my_rating_label",
    "date_rated",
    "overview",
    "poster_url",
]

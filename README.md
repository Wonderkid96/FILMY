# 🎬💕 FILMY - Advanced Movie & TV Recommendation Engine

A sophisticated movie and TV show recommendation system with **Couples Edition** featuring advanced user tracking, mobile optimization, and intelligent compatibility analysis. Built with Python and Streamlit, powered by The Movie Database (TMDB) API with enhanced Google Sheets integration.

![FILMY Demo](https://img.shields.io/badge/Status-Ready%20to%20Use-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)

## ✨ Features

### 🎯 Personalized Recommendations
- **Smart Learning**: Learns from your likes/dislikes to improve recommendations
- **Genre-based Filtering**: Get recommendations based on your favorite genres
- **Hybrid Algorithm**: Combines content-based and collaborative filtering
- **Rating Filters**: Set minimum rating thresholds for recommendations

### 💕 **NEW: Couples Edition**
- **Advanced User Tracking**: "Toby seen" / "Taz seen" / "Both seen" system
- **Compatibility Analysis**: Smart scoring with percentage compatibility
- **Mobile-First Design**: Fully responsive for phone usage
- **Google Sheets Integration**: 20-column sophisticated tracking with live stats
- **Joint Decision Making**: Couple ratings with agreement bonuses

### 🔍 Advanced Discovery
- **Multi-Genre Search**: Filter by multiple genres simultaneously
- **Smart Sorting**: Sort by popularity, rating, release date, or review count
- **Content Type Selection**: Choose between movies and TV shows
- **Real-time Results**: Instant search and filtering

### 🎭 Content Management
- **Like/Dislike System**: Rate content to improve your recommendations
- **Viewing History**: Track what you've explored
- **Similar Content**: Find movies/shows similar to ones you love
- **Detailed Information**: Rich metadata including cast, genres, ratings

### 📊 Personal Analytics
- **Preference Dashboard**: Visualize your genre preferences
- **Statistics Tracking**: Monitor your viewing patterns
- **Profile Management**: Customize your recommendation settings
- **Data Export**: Your preferences are saved locally

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- TMDB API key (free from [themoviedb.org](https://www.themoviedb.org/settings/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FILMY
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your TMDB API key
   TMDB_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

5. **Choose your experience**
   - The app will open at `http://localhost:8501` with a beautiful mode selector
   - **💕 Couples Edition**: Advanced user tracking for both partners (recommended!)
   - **🎬 Original Mode**: Classic single-user experience
   - Start exploring and rating content to get personalized recommendations!

## 🔑 Getting Your TMDB API Key

1. Go to [The Movie Database](https://www.themoviedb.org/)
2. Create a free account
3. Go to Settings → API
4. Request an API key (choose "Developer" option)
5. Fill out the form (you can use "Personal/Educational" for usage)
6. Copy your API key to the `.env` file

## 📱 How to Use

### 1. **Start Rating Content**
   - Use the 🔍 **Discover** or 🔎 **Search** pages to find movies/TV shows
   - Click 👍 **Like** or 👎 **Dislike** to rate content
   - The system learns your preferences automatically

### 2. **Get Recommendations**
   - Visit 🎯 **Recommendations** to see personalized suggestions
   - Adjust filters like minimum rating and content type
   - The more you rate, the better your recommendations become!

### 3. **Explore Your Profile**
   - Check 👤 **Profile** to see your statistics
   - View your favorite genres and liked content
   - Adjust your default preferences

### 4. **Discover New Content**
   - Use genre filters to find content in specific categories
   - Sort by popularity, rating, or release date
   - Find similar content to movies/shows you love

## 🏗️ Architecture

### Core Components

- **`main.py`**: Main application entry point with mode selection
- **`src/apps/`**: Streamlit applications (couples & original modes)
- **`src/core/tmdb_api.py`**: TMDB API wrapper for fetching movie/TV data
- **`src/core/recommendation_engine.py`**: ML-based recommendation algorithms
- **`src/core/user_preferences.py`**: User preference management and persistence
- **`src/core/advanced_user_tracker.py`**: Couples tracking and compatibility analysis
- **`src/core/config.py`**: Configuration settings and constants

### Recommendation Algorithm

FILMY uses a hybrid recommendation system:

1. **Content-Based Filtering**: Analyzes movie/TV show features (genres, ratings, cast)
2. **Collaborative Filtering**: Uses user behavior patterns
3. **Popularity Scoring**: Incorporates trending and highly-rated content
4. **User Preference Learning**: Adapts based on your likes/dislikes

## 🎨 Features Showcase

### Beautiful UI
- Modern, responsive design with gradient themes
- Intuitive navigation with sidebar menu
- Rich content cards with posters and metadata
- Interactive charts and statistics

### Smart Recommendations
- Learns from your viewing history
- Considers genre preferences, ratings, and popularity
- Provides explanations for recommendations
- Continuously improves with more data

### Data Privacy
- All preferences stored locally on your machine
- No personal data sent to external servers
- Full control over your recommendation data

## 🛠️ Customization

### Adding New Features
The modular architecture makes it easy to extend:

- Add new recommendation algorithms in `recommendation_engine.py`
- Implement additional data sources in the API layer
- Create new UI components in `app.py`
- Add preference categories in `user_preferences.py`

### Configuration
Modify `config.py` to:
- Adjust rating thresholds
- Add new genre mappings
- Change API endpoints
- Customize UI settings

## 📊 Technical Details

### APIs Used
- **TMDB API**: Primary source for movie/TV data
- **Free Tier**: 1000 requests per day (more than enough for personal use)
- **Rich Data**: Includes ratings, cast, crew, images, and detailed metadata

### Machine Learning
- **Scikit-learn**: For similarity calculations and feature processing
- **TF-IDF Vectorization**: For text-based content analysis
- **Cosine Similarity**: For finding similar content
- **Hybrid Scoring**: Combines multiple recommendation strategies

### Data Storage
- **Local JSON Files**: User preferences stored locally
- **No Database Required**: Simple file-based persistence
- **Privacy First**: No external data storage

## 🤝 Contributing

We welcome contributions! Here are some ways you can help:

- 🐛 Report bugs or suggest features
- 📝 Improve documentation
- 🧪 Add new recommendation algorithms
- 🎨 Enhance the UI/UX
- 🔧 Optimize performance

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [The Movie Database (TMDB)](https://www.themoviedb.org/) for providing the excellent API
- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Plotly](https://plotly.com/) for beautiful interactive charts

## 🆘 Support

If you encounter any issues:

1. Check that your TMDB API key is correctly set in `.env`
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Verify you have Python 3.8+ installed
4. Check the terminal for any error messages

For additional help, please create an issue in the repository.

---

**Happy movie watching! 🍿🎬**

*Built with ❤️ using Python, Streamlit, and the power of machine learning* 
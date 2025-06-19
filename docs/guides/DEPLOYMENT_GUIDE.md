# 🚀 FILMY Deployment Guide

## 📋 Prerequisites

1. **TMDB API Key** - Get from https://www.themoviedb.org/settings/api
2. **Google Service Account** - Set up from Google Cloud Console
3. **Google Sheet** - Your sheet ID: `1cEGSoX7b1458QAQn1ORLPlrqXVI9-hDqqjp7LL9kpOc`

## 🔧 Local Development Setup

### 1. Environment Variables
Create a `.env` file:
```
TMDB_API_KEY=your_tmdb_api_key_here
```

### 2. Google Credentials
Place your Google service account JSON file at:
```
credentials/google_credentials.json
```

## ☁️ Cloud Deployment (Streamlit Cloud)

### 1. TMDB API Key
In Streamlit Cloud secrets, add:
```toml
TMDB_API_KEY = "your_tmdb_api_key_here"
```

### 2. Google Credentials
In Streamlit Cloud secrets, add your Google service account details:
```toml
GOOGLE_SHEET_ID = "1cEGSoX7b1458QAQn1ORLPlrqXVI9-hDqqjp7LL9kpOc"

[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-full-private-key-here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

## 🎯 Quick Deploy Steps

1. **Push to GitHub** ✅ (Already done)
2. **Go to** https://share.streamlit.io/
3. **Connect your GitHub** account
4. **Select** `Wonderkid96/FILMY` repository
5. **Set main file** to `app_enhanced.py`
6. **Add secrets** (TMDB API key + Google credentials)
7. **Deploy!**

## 🔍 Troubleshooting

- **"TMDB API key not found"** → Add to secrets
- **"Google credentials not found"** → Add Google credentials to secrets
- **"Permission denied"** → Check Google Sheet sharing settings

Your app will be live at: `https://wonderkid96-filmy-app-enhanced-xyz.streamlit.app/` 
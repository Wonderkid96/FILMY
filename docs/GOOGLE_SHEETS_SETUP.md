# 🔗 Google Sheets API Setup Guide

This guide will connect FILMY to your specific Google Sheet for cloud sync of movie ratings.

**Your Sheet:** https://docs.google.com/spreadsheets/d/1cEGSoX7b1458QAQn1ORLPlrqXVI9-hDqqjp7LL9kpOc/

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Name it something like "FILMY-Ratings"

## Step 2: Enable Google Sheets API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Sheets API"
3. Click on it and press **Enable**
4. Also enable "Google Drive API" (needed for sheet access)

## Step 3: Create Service Account

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **Service Account**
3. Name: `filmy-service-account`
4. Description: `Service account for FILMY movie ratings sync`
5. Click **Create and Continue**
6. Skip the optional steps, click **Done**

## Step 4: Generate Credentials JSON

1. In **Credentials**, find your service account
2. Click on the service account email
3. Go to **Keys** tab
4. Click **Add Key** → **Create New Key**
5. Choose **JSON** format
6. Download the file
7. **IMPORTANT:** Rename it to `google_credentials.json`
8. Move it to `FILMY/credentials/google_credentials.json`

## Step 5: Share Your Google Sheet

1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1cEGSoX7b1458QAQn1ORLPlrqXVI9-hDqqjp7LL9kpOc/
2. Click **Share** button (top right)
3. Copy the **service account email** from the JSON file (looks like: `filmy-service-account@your-project.iam.gserviceaccount.com`)
4. Add this email as **Editor** to your sheet
5. Click **Send**

## Step 6: Prepare Your Sheet

The app will automatically create the following columns in your sheet:
- `tmdb_id` - Unique movie/TV ID
- `title` - Movie/TV show title  
- `type` - "movie" or "tv"
- `release_date` - Release date
- `genres` - Comma-separated genres
- `tmdb_rating` - TMDB rating (0-10)
- `my_rating` - Your rating (1-4)
- `my_rating_label` - "Hate", "OK", "Good", "Perfect"
- `date_rated` - When you rated it
- `overview` - Plot summary
- `poster_url` - Movie poster URL

## Step 7: Test Connection

1. Run FILMY: `streamlit run app_enhanced.py`
2. Go to **☁️ Cloud Sync** tab
3. You should see "✅ Google Sheets Connected!"
4. Rate a movie to test sync

## File Structure

Your workspace should look like:
```
FILMY/
├── credentials/
│   └── google_credentials.json    # Your service account key
├── docs/
│   └── GOOGLE_SHEETS_SETUP.md    # This file
├── app_enhanced.py                # Main app
├── config.py                     # Configuration
├── filmy_ratings.csv            # Local backup
└── ...
```

## Security Notes

- **Never commit** `google_credentials.json` to git
- The credentials folder is already in `.gitignore`
- Your sheet will sync automatically when you rate content
- Local CSV backup is always maintained

## Troubleshooting

### "Could not access the specified Google Sheet"
- Check that you shared the sheet with the service account email
- Verify the service account has **Editor** permissions
- Make sure both Google Sheets API and Google Drive API are enabled

### "Google credentials file not found"
- Ensure file is at `credentials/google_credentials.json`
- Check the filename is exactly `google_credentials.json`
- Verify JSON file is valid (not corrupted download)

### "Failed to connect to Google Sheets"
- Check your internet connection
- Verify the project has Google Sheets API enabled
- Ensure service account key is valid and not expired

---

**Once connected, FILMY will:**
- ✅ Never recommend the same film twice
- ✅ Sync ratings to your Google Sheet in real-time
- ✅ Maintain local CSV backup
- ✅ Track your viewing history with timestamps
- ✅ Provide smart recommendations based on your taste 
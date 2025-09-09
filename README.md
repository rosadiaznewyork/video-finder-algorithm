# Video Inspiration Finder

AI-powered YouTube video recommendation system that learns your preferences.

## Quick Start

```bash
./setup.sh
```

Select option 1 for web dashboard (recommended).

## Requirements

- **Python 3.7+** 
- **YouTube Data API v3 Key** from [Google Cloud Console](https://console.cloud.google.com/)

## Setup

1. **Get YouTube API Key**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create project and enable YouTube Data API v3
   - Create API key

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key:
   # YOUTUBE_API_KEY=your_actual_api_key_here
   ```

3. **Run setup**:
   ```bash
   ./setup.sh
   ```

## Available Commands

```bash
# Interactive setup menu
./setup.sh

# Web dashboard
python3 dashboard_api.py

# CLI mode
python3 main.py

# Search for more videos
python3 search_more_videos.py
```

## Web Dashboard

- Access at: http://localhost:5001
- YouTube-like interface with AI confidence scores
- Rate videos to train the AI model

## Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests pandas scikit-learn numpy python-dotenv flask flask-cors

# Run dashboard
python3 dashboard_api.py
```

## Troubleshooting

**Python not found**: Use `python3` instead of `python`

**API Key Issues**: 
- Ensure YouTube Data API v3 is enabled
- Check your API key has quota remaining

**Database Issues**: Delete `video_inspiration.db` and run `./setup.sh` again
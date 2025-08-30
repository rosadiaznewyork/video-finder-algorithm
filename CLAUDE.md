# Video Inspiration Finder - Project Overview

## Project Purpose
An intelligent YouTube video recommendation system that learns user preferences through machine learning to suggest coding videos. Features AI-powered personalized search, topic-based discovery, and both CLI and web dashboard interfaces with advanced search history management.

## Core Architecture

### 1. Enhanced Data Flow
```
YouTube API ← AI Query Generation (Ollama LLM) ← Personalized Tags from Liked Videos
     ↓
Search/Fetch Videos → SQLite Database → Feature Extraction → ML Model → 24 Personalized Recommendations
     ↓
User Interface (CLI/Dashboard) ← Search Sessions & History Management
```

### 2. Key Components

#### Service Layer (`src/services/`)
- **VideoSearchService**: Unified search logic eliminating duplicate patterns across codebase
- **YouTubeAPIClient**: Centralized YouTube API interactions with consistent error handling
- **QueryService**: AI-powered query generation with fallback to static queries
- **TagService**: Personalized keyword management using liked video tags
- **TopicRatingService**: Combined search and rating workflows for topic-based discovery

#### YouTube Integration (`src/youtube/`)
- **search.py**: Compatibility module for legacy functions
- **details.py**: Video metadata processing with centralized keyword filtering

#### AI Integration (`src/ollama/`)
- **keyword_generator.py**: AI-powered search query generation using Ollama LLMs
  - Personalized prompts using tags from liked videos
  - Fallback to manual keyword generation
  - Dynamic keyword selection for query diversity

#### Database Layer (`src/database/`)
- **manager.py**: SQLite schema setup with search sessions tracking
- **video_operations.py**: CRUD operations for videos with transaction safety
- **preference_operations.py**: User ratings management + personalized tag extraction
- **search_operations.py**: Search session management and history tracking  
- **connection.py**: Context manager for safe database connections
- Tables: videos, video_features, preferences, search_sessions

#### Configuration (`src/config/`)
- **app_config.py**: Centralized configuration classes
  - **AppConfig**: Database paths, ML thresholds, search defaults
  - **YouTubeConfig**: API URLs, content filtering, programming keywords
  - **OllamaConfig**: LLM integration settings, model selection
  - **UIConfig**: Dashboard settings, rating prompts

#### Machine Learning (`src/ml/`)
- **feature_extraction.py**: Extracts 11 features from videos:
  - Content: title length, description length, keywords
  - Engagement: view count, like ratio, engagement score
  - Semantic: sentiment, tutorial/beginner/AI keywords
  - Behavioral: time constraints, challenge keywords
- **model_training.py**: RandomForest classifier (100 trees)
- **predictions.py**: Configurable confidence scores with top_n parameter (now returns 24 videos)

#### User Interfaces
- **CLI Mode** (`main.py`, `src/rating/`): Interactive terminal rating system
- **Web Dashboard** (`dashboard_api.py`, `templates/dashboard.html`): 
  - Flask API on port 5001
  - YouTube-like grid layout showing 24 personalized recommendations
  - Real-time rating with visual feedback
  - AI confidence scores with personalized match percentages
  - Topic-based search with AI keyword generation
  - MyTube section for curated liked videos
  - Search history management with session tracking
  - Manual video addition by URL

### 3. AI-Powered Personalization
1. **Personalized Keywords**: System extracts unique tags from liked videos
2. **Dynamic Query Generation**: Ollama LLM creates varied search queries using personal tags
3. **Cold Start**: Random videos until 10+ ratings, then switches to personalized mode
4. **Model Training**: Activates after 10 ratings, retrains after each interaction
5. **Smart Recommendations**: 24 videos ranked by ML confidence with personalized keywords

## Entry Points

### Main Scripts
- `setup.sh`: Enhanced automated setup (venv, dependencies, 6 menu options)
- `main.py`: CLI application with service architecture
- `dashboard_api.py`: Web server with advanced features
- `run_dashboard.py`: Dashboard launcher
- `search_more_videos.py`: AI-powered additional video search
- `search_by_topic.py`: Topic-based search with Ollama integration
- `topic_rate.py`: Combined topic search and rating workflow

### Setup Options
1. **Dashboard Only**: Launch web interface
2. **CLI Mode**: Terminal-based rating  
3. **Search Videos**: Populate database with AI queries
4. **Full Setup**: Search + Rate + Dashboard
5. **Topic Search**: Search by specific topics using AI
6. **Topic Rating**: Interactive topic search and rating sessions

## Configuration

### Environment Variables
- `YOUTUBE_API_KEY`: Required for YouTube API access
- `OLLAMA_MODEL`: Optional Ollama model selection (default: llama3.2:3b)
- Located in `.env` file

### Dependencies
- Core: requests, pandas, scikit-learn, numpy
- Web: flask, flask-cors
- Database: sqlite3 (built-in)
- AI: Ollama LLM integration (local)
- Utilities: python-dotenv

## Database Schema

### videos table
- id, title, channel_name, view_count, url, tags (JSON), search_session_id, search_topic

### video_features table  
- video_id, title_length, description_length
- view_like_ratio, engagement_score, title_sentiment
- has_tutorial_keywords, has_beginner_keywords, has_ai_keywords, etc.

### preferences table
- video_id, liked (boolean), notes, created_at

### search_sessions table
- id, topic, created_at, video_count, status

## API Endpoints

### Dashboard API (port 5001)
- `GET /`: Serve dashboard HTML
- `GET /api/recommendations`: Get 24 personalized video recommendations
- `POST /api/rate`: Submit video rating with model retraining
- `GET /api/liked`: Get curated liked videos
- `POST /api/remove-liked`: Remove liked videos
- `POST /api/search-topic`: AI-powered topic search with Ollama
- `POST /api/add-video-by-url`: Manually add videos by YouTube URL
- `GET /api/search-history`: Search session management
- `GET /api/search-session/<id>`: View videos from specific search
- `DELETE /api/delete-search-session/<id>`: Delete search sessions
- `POST /api/cleanup-searches`: Archive old search sessions

## Current Status
- **Personalization**: Tags extracted from liked videos
- **Recommendations**: 24 AI-ranked videos per session (up from 10)
- **Database**: video_inspiration.db with search session tracking
- **AI Integration**: Ollama LLM for dynamic query generation
- **Model threshold**: 10 ratings minimum for AI activation
- **Dashboard URL**: http://localhost:5001 with 4 main views
- **Architecture**: Service-oriented with 60-73% code reduction

## Quick Commands
```bash
# Interactive setup with 6 options
./setup.sh

# Direct commands
python3 main.py                    # CLI mode with service architecture
python3 dashboard_api.py           # Enhanced web dashboard  
python3 search_more_videos.py      # AI-powered video search
python3 search_by_topic.py <topic> # Topic-based search with Ollama
python3 topic_rate.py              # Interactive topic rating sessions
```

## Key Features & Improvements
- **AI Personalization**: Uses 144+ tags from liked videos for truly personalized recommendations
- **Service Architecture**: Clean, maintainable code with 60-73% reduction in duplicate patterns
- **Enhanced Dashboard**: 24 recommendations, topic search, search history, MyTube curation
- **Ollama Integration**: Local LLM for intelligent keyword generation and query diversity
- **Search Sessions**: Complete search history management with session tracking
- **Transaction Safety**: Database operations with automatic rollback and resource cleanup
- **Configuration Management**: Centralized settings for all components

## Technical Notes
- **All data stored locally** in SQLite - no external tracking or data sharing
- **Model**: RandomForest with 100 estimators, configurable top_n predictions
- **Content filtering**: Project-focused keywords, Science & Technology category
- **API Integration**: YouTube Data API v3 with comprehensive error handling
- **LLM Requirements**: Ollama with llama3.2:3b model (or user-configured)
- **Scalability**: Handles 500+ videos with personalized ranking
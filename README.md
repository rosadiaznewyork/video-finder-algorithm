# Video Inspiration Finder 🎯

An intelligent AI-powered YouTube video recommendation system that learns your preferences to suggest coding videos you'll love. Features personalized search using your liked video tags, Ollama LLM integration, and a sophisticated web dashboard with search history management.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![AI Powered](https://img.shields.io/badge/AI-Ollama%20LLM-purple.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)

Based on a project by [rosadiaznewyork](https://github.com/rosadiaznewyork)

## ✨ Revolutionary Features

- 🧠 **AI Personalization**: Extracts unique tags from your liked videos for truly personalized search queries
- 🤖 **Ollama LLM Integration**: Local AI generates dynamic search keywords from your preferences  
- 📊 **Enhanced Dashboard**: 24 personalized recommendations (up from 10) with 4 main views
- 🔍 **Topic-Based Search**: AI-powered search for any coding topic with intelligent keyword generation
- 📜 **Search History**: Complete session management with video tracking and cleanup tools
- 🎯 **MyTube Curation**: Personal collection of videos ranked by AI confidence
- 🔒 **Privacy First**: All data stored locally - no external tracking, local LLM processing
- ⚡ **Service Architecture**: Clean, maintainable code with 60-73% reduction in duplicate patterns
- 📱 **Advanced UI**: Real-time rating, manual video addition, search session management

## 🚀 Quick Start

### Enhanced Setup Script (6 Options)
```bash
git clone https://github.com/yourusername/video-idea-finder-algorithm.git
cd video-idea-finder-algorithm
./setup.sh
```

**Setup Options:**
1. **Dashboard Only** - Launch web interface with AI recommendations
2. **CLI Mode** - Terminal-based rating system
3. **Search Videos** - Populate database with AI-generated queries  
4. **Full Setup** - Search + Rate + Dashboard
5. **Topic Search** - Search specific topics using Ollama AI
6. **Topic Rating** - Interactive topic search and rating sessions

The setup script will:
1. Create a Python virtual environment
2. Install all dependencies  
3. Help you configure your YouTube API key
4. Optionally set up Ollama for AI features
5. Launch your preferred interface

## 📋 Prerequisites

- **Python 3.7+**
- **YouTube Data API v3 Key** (free from [Google Cloud Console](https://console.cloud.google.com/))
- **Ollama** (optional, for AI features) - Install from [ollama.ai](https://ollama.ai)

## ⚙️ Configuration

1. **Get YouTube API Key**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select existing one
   - Enable YouTube Data API v3
   - Create credentials (API key)

2. **Set up environment**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your configuration
   YOUTUBE_API_KEY=your_actual_api_key_here
   OLLAMA_MODEL=llama3.2:3b  # Optional: specify Ollama model
   ```

3. **AI Setup (Optional but Recommended)**:
   ```bash
   # Install Ollama for AI features
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the default model
   ollama pull llama3.2:3b
   
   # Start Ollama service
   ollama serve
   ```

## 🏗️ Enhanced Project Structure

```
video-idea-finder-algorithm/
├── src/
│   ├── services/          # 🆕 SERVICE ARCHITECTURE
│   │   ├── video_search_service.py   # Unified search logic  
│   │   ├── youtube_client.py         # Centralized API client
│   │   ├── query_service.py          # AI query generation
│   │   ├── tag_service.py            # Personalized keywords
│   │   └── topic_rating_service.py   # Topic search + rating
│   ├── config/            # 🆕 CENTRALIZED CONFIGURATION
│   │   └── app_config.py   # AppConfig, YouTubeConfig, OllamaConfig
│   ├── ollama/            # 🆕 AI INTEGRATION
│   │   └── keyword_generator.py      # LLM-powered search queries
│   ├── database/          # Enhanced database operations
│   │   ├── manager.py      # Database setup + search sessions
│   │   ├── connection.py   # 🆕 Safe connection context manager
│   │   ├── video_operations.py       # Video CRUD + transactions
│   │   ├── preference_operations.py  # Ratings + tag extraction
│   │   └── search_operations.py      # 🆕 Search history management
│   ├── youtube/           # YouTube API integration
│   │   ├── search.py      # Legacy compatibility functions
│   │   └── details.py     # Video metadata + filtering
│   ├── ml/               # Enhanced ML pipeline
│   │   ├── feature_extraction.py    # 11 video features
│   │   ├── model_training.py        # RandomForest training
│   │   └── predictions.py           # 🆕 Configurable recommendations
│   └── rating/           # Interactive rating system
├── static/               # 🆕 ADVANCED FRONTEND
│   └── js/               # Modular JavaScript architecture
│       ├── app.js        # Main application controller
│       ├── api.js        # API service layer
│       ├── views.js      # View management
│       ├── components.js # Reusable components
│       └── utils.js      # Helper functions
├── templates/            # Enhanced web dashboard
│   └── dashboard.html    # 4-view SPA with AI features
├── main.py              # Enhanced CLI with services
├── dashboard_api.py     # 🆕 Advanced API (11 endpoints)
├── search_more_videos.py # AI-powered search
├── search_by_topic.py   # 🆕 Topic-based search with Ollama
├── topic_rate.py        # 🆕 Interactive topic rating
├── setup.sh            # Enhanced setup (6 options)
└── README.md           # This file
```

## 🧠 Dual AI System: ML + LLM

### 🤖 Machine Learning Pipeline (Video Recommendations)

#### Feature Engineering
The system extracts 11 key features from each video:
- **Content Features**: Title length, description length, keyword presence
- **Engagement Metrics**: View count, like ratio, engagement score
- **Semantic Analysis**: Title sentiment, tutorial/beginner/AI keyword detection
- **Behavioral Patterns**: Time constraints, challenge keywords

#### ML Training & Prediction Process
1. **Data Collection**: YouTube API provides video metadata
2. **Feature Extraction**: Convert raw video data into numerical features
3. **User Feedback**: Collect like/dislike ratings with optional notes
4. **Model Training**: RandomForest classifier with 100 trees
5. **Prediction**: Generate confidence scores (0-100%) for 24 personalized recommendations

#### ML Learning Process
- **Cold Start**: Shows random videos until you have 10+ ratings
- **Model Training**: RandomForest activates after 10 ratings
- **Continuous Learning**: Model retrains after each new rating
- **Personalized Ranking**: Videos sorted by ML confidence scores

### 🧠 LLM Integration (Search Query Generation)

#### Personalized Query Engine  
1. **Tag Extraction**: System analyzes tags from your liked videos
2. **Dynamic Keywords**: Randomly selects 8-10 personalized tags for each search
3. **LLM Generation**: Ollama creates varied search queries using your preferences
4. **Fallback System**: Uses static programming keywords when no liked videos exist

#### AI Search Process
1. **Personalized Prompts**: "Generate search queries using: react, python, machine learning..."
2. **Query Diversity**: Random keyword selection ensures varied results each time
3. **Topic Search**: LLM generates keywords for any coding topic you specify
4. **Session Tracking**: All searches saved with full history management

### 🎓 Combined Learning Stages
- **Stage 1**: Random videos + static search queries (0-10 ratings)
- **Stage 2**: ML recommendations + personalized LLM queries (10+ ratings)
- **Stage 3**: Advanced personalization with continuous ML/LLM learning

## 🖥️ Enhanced Commands

```bash
# Interactive setup with 6 options
./setup.sh

# Core applications
python main.py                    # Enhanced CLI with service architecture
python dashboard_api.py           # Advanced web dashboard (11 API endpoints)
python run_dashboard.py           # Dashboard launcher

# AI-powered search
python search_more_videos.py      # Search using personalized AI queries
python search_by_topic.py "rust"  # Topic search with Ollama integration
python topic_rate.py              # Interactive topic search + rating

# Utilities
ollama serve                      # Start AI service for personalization
```

## 🎨 Advanced Dashboard Features

### 📊 Four Main Views
1. **AI Recommendations** - 24 personalized videos with confidence scores
2. **MyTube** - Your curated collection ranked by AI match confidence  
3. **Search Results** - AI-generated topic searches with keyword insights
4. **Search History** - Complete session management with cleanup tools

### ✨ Smart Features
- **Personalized Match %**: AI confidence based on your viewing history
- **Real-time Model Updates**: Visual feedback when AI learns from your ratings
- **Manual Video Addition**: Add any YouTube video by URL to your collection
- **Search Session Tracking**: View videos from previous searches anytime
- **Advanced Filtering**: Content filtered using project-focused keywords
- **Responsive Design**: Perfect experience on desktop and mobile

## 🔧 Customization

### Search Queries
Edit the search queries in `src/youtube/search.py`:
```python
def get_coding_search_queries() -> List[str]:
    return [
        "python machine learning tutorial",
        "javascript react project",
        "web development 2024",
        # Add your own search terms
    ]
```

### ML Model Parameters
Modify model settings in `src/ml/model_training.py`:
```python
model = RandomForestClassifier(
    n_estimators=100,        # Number of trees
    max_depth=10,           # Tree depth
    min_samples_split=5,    # Minimum samples for split
    random_state=42
)
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/video-idea-finder-algorithm.git

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **YouTube Data API v3** for video data
- **scikit-learn** for machine learning capabilities
- **Flask** for the web framework
- **SQLite** for local data storage

## 📚 Learn More

This project demonstrates several key concepts:
- **API Integration**: YouTube Data API v3 usage
- **Machine Learning**: Feature engineering and model training
- **Web Development**: Flask API and responsive frontend
- **Database Design**: SQLite schema and operations
- **DevOps**: Environment management and deployment

Perfect for learning about ML-powered recommendation systems!

## 🐛 Troubleshooting

### Common Issues

**API Key Issues**:
- Ensure your YouTube API key is valid and has quota remaining
- Check that YouTube Data API v3 is enabled in Google Cloud Console

**Database Issues**:
- Delete `video_inspiration.db` to reset the database
- Run `./setup.sh` again to reinitialize

**Import Errors**:
- Activate the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Port Conflicts**:
- Dashboard runs on port 5001 by default
- Change the port in `dashboard_api.py` if needed

### Need Help?

- 📧 Open an issue on GitHub
- 💬 Check existing issues for solutions
- 🔍 Review the troubleshooting section above

---

⭐ **Found this helpful? Give it a star!** ⭐

Built with ❤️ for the coding community
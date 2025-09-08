# Video Inspiration Finder 🎯

An intelligent YouTube video recommendation system that learns your preferences to suggest coding videos you'll love. Built with machine learning and featuring a beautiful web dashboard.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)

## 🌟 Features

- 🔍 **Smart YouTube Search**: Automatically finds trending coding videos using configurable search queries
- 🤖 **Machine Learning Recommendations**: RandomForest model learns your preferences from ratings
- 📊 **Beautiful Web Dashboard**: YouTube-like interface with AI confidence scores
- 🔒 **Privacy First**: All data stored locally in SQLite - no external tracking
- ⚡ **One-Command Setup**: Get started with a single command
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- 🎯 **Real-time Learning**: Model updates instantly as you rate more videos

## 🚀 Quick Start

### Option 1: Web Dashboard (Recommended)
```bash
git clone https://github.com/yourusername/video-idea-finder-algorithm.git
cd video-idea-finder-algorithm
./setup.sh
# Select option 1 for Dashboard
```

### Option 2: Command Line Interface
```bash
./setup.sh
# Select option 2 for CLI mode
```

The setup script will:
1. Create a Python virtual environment
2. Install all dependencies
3. Help you configure your YouTube API key
4. Launch your preferred interface

### Option 3: Docker
```bash
docker build -t video-finder-algorithm:latest .
docker run -d \
  --name video-finder \
  -p 5001:5001 \
  -v $(pwd):/app \
  --env YOUTUBE_API_KEY=your_actual_api_key_here \
  video-finder-algorithm:latest
```

### Option 4: Docker Compose
```bash
docker compose up -d
```


## 📋 Prerequisites

- **Python 3.7+**
- **YouTube Data API v3 Key** (free from [Google Cloud Console](https://console.cloud.google.com/))

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
   
   # Edit .env and add your API key
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

3. **Add your search queries**:
   - Edit `src/youtube/search.py` in the `get_coding_search_queries()` function
   - Add search terms relevant to your interests
   - Example: `"python machine learning"`, `"react tutorial"`, etc.

## 🏗️ Project Structure

```
video-idea-finder-algorithm/
├── src/
│   ├── database/           # SQLite database operations
│   │   ├── manager.py      # Database setup and schema
│   │   ├── video_operations.py    # Video data CRUD
│   │   └── preference_operations.py # User ratings CRUD
│   ├── youtube/            # YouTube API integration
│   │   ├── search.py       # Video search functionality
│   │   ├── details.py      # Video metadata retrieval
│   │   └── utils.py        # Helper functions
│   ├── ml/                # Machine learning pipeline
│   │   ├── feature_extraction.py  # Video feature engineering
│   │   ├── model_training.py      # ML model management
│   │   └── predictions.py         # Recommendation engine
│   └── rating/            # Interactive rating system
│       ├── display.py      # Video information display
│       ├── session.py      # Rating session management
│       └── user_input.py   # User interaction handling
├── templates/             # Web dashboard frontend
│   └── dashboard.html     # Single-page application
├── main.py               # CLI application entry point
├── dashboard_api.py      # Web API server
├── run_dashboard.py      # Dashboard launcher
├── search_more_videos.py # Additional video search utility
├── setup.sh             # Automated setup script
├── .env.example         # Environment template
└── README.md           # This file
```

## 🧠 How the AI Works

### Feature Engineering
The system extracts 11 key features from each video:
- **Content Features**: Title length, description length, keyword presence
- **Engagement Metrics**: View count, like ratio, engagement score
- **Semantic Analysis**: Title sentiment, tutorial/beginner/AI keyword detection
- **Behavioral Patterns**: Time constraints, challenge keywords

### Machine Learning Pipeline
1. **Data Collection**: YouTube API provides video metadata
2. **Feature Extraction**: Convert raw video data into numerical features
3. **User Feedback**: Collect like/dislike ratings with optional notes
4. **Model Training**: RandomForest classifier with 100 trees
5. **Prediction**: Generate confidence scores for new videos

### Learning Process
- **Cold Start**: Shows random videos until you have 10+ ratings
- **Warm Start**: AI model activates and provides personalized recommendations
- **Continuous Learning**: Model retrains after each new rating

## 🖥️ Available Commands

```bash
# Full interactive setup
./setup.sh

# CLI-only mode
python main.py

# Web dashboard
python run_dashboard.py

# Search for additional videos
python search_more_videos.py

# Start API server directly
python dashboard_api.py
```

## 🎨 Dashboard Features

- **YouTube-like Interface**: Familiar grid layout with thumbnails
- **AI Confidence Scores**: See how confident the AI is about each recommendation
- **Real-time Feedback**: Rate videos with instant visual feedback
- **Model Status**: Track learning progress and training status
- **Liked Videos**: Review your previously liked videos
- **Responsive Design**: Perfect on any screen size

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
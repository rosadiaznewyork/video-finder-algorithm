"""
Application-wide configuration constants.
"""

import os
from typing import List


class AppConfig:
    """Main application configuration."""
    
    # Database
    DATABASE_PATH = "video_inspiration.db"
    
    # Machine Learning
    ML_TRAINING_THRESHOLD = 10  # Minimum ratings needed to train model
    
    # Search defaults
    DEFAULT_RESULTS_PER_QUERY = 15
    TOPIC_SEARCH_RESULTS_PER_QUERY = 5
    TOPIC_SEARCH_MAX_QUERIES = 8
    
    # File paths
    ENV_FILE = ".env"
    

class YouTubeConfig:
    """YouTube API configuration."""
    
    # API URLs
    BASE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
    BASE_DETAILS_URL = "https://www.googleapis.com/youtube/v3/videos"
    
    # API Parameters
    SCIENCE_TECH_CATEGORY_ID = "28"
    DEFAULT_PUBLISHED_AFTER = "2020-01-01T00:00:00Z"
    REQUEST_TIMEOUT = 10
    
    # Content filtering
    MIN_VIEW_COUNT_THRESHOLD = 100000
    
    # Project-focused programming keywords for content filtering
    PROGRAMMING_KEYWORDS = [
        # Project building & development
        'build', 'building', 'project', 'app', 'application', 'website', 'platform',
        'create', 'creating', 'develop', 'developing', 'implementation', 'deploy',
        
        # Technology & frameworks
        'javascript', 'python', 'react', 'node.js', 'typescript', 'flutter',
        'docker', 'kubernetes', 'aws', 'api', 'microservices', 'database', 'sqlite',
        
        # Project types & domains  
        'web development', 'mobile app', 'machine learning', 'ai', 'data science',
        'devops', 'backend', 'frontend', 'fullstack', 'blockchain', 'game dev',
        
        # Project-specific terms
        'architecture', 'system design', 'scalable', 'performance', 'optimization',
        'startup', 'saas', 'mvp', 'prototype', 'production', 'enterprise',
        
        # Development workflow
        'git', 'github', 'ci/cd', 'testing', 'debugging', 'refactoring', 'code review'
    ]


class OllamaConfig:
    """Ollama integration configuration."""
    
    # API
    BASE_URL = "http://localhost:11434"
    GENERATE_ENDPOINT = f"{BASE_URL}/api/generate"
    TAGS_ENDPOINT = f"{BASE_URL}/api/tags"
    
    # Default model
    DEFAULT_MODEL = "llama3.2:3b"
    
    # Generation parameters
    DEFAULT_NUM_QUERIES = 15
    TOPIC_SEARCH_NUM_QUERIES = 10
    REQUEST_TIMEOUT = 30
    
    @classmethod
    def get_model_from_env(cls) -> str:
        """Get Ollama model from environment variable."""
        return os.getenv('OLLAMA_MODEL', cls.DEFAULT_MODEL)


class UIConfig:
    """User interface configuration."""
    
    # Dashboard
    DASHBOARD_PORT = 5001
    DASHBOARD_HOST = "localhost"
    
    # CLI messages
    QUOTA_RESET_MESSAGE = "YouTube API quota resets daily at midnight Pacific Time"
    
    # Rating prompts
    RATING_PROMPT = "Rate this video (y/n/q): "
    LIKE_NOTES_PROMPT = "Why did you like it? (optional): "
    DISLIKE_NOTES_PROMPT = "Why didn't you like it? (optional): "


# Default search queries for coding videos
DEFAULT_CODING_QUERIES = [
    "coding passion project ideas",
    "weekend programming projects", 
    "creative coding projects",
    "fun programming side projects",
    "indie developer projects",
    "building passion projects programming",
    "personal coding project showcase", 
    "hobby programming projects",
    "weekend coding challenge",
    "solo developer projects",
    "build something cool programming",
    "coding project inspiration",
    "unique programming projects",
    "developer side project success",
    "open source passion projects"
]

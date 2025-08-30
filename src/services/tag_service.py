"""
Centralized service for managing tags and keywords.
Provides personalized keywords based on liked video tags with fallback to static keywords.
"""

import random
from typing import List

from src.database.preference_operations import get_liked_video_tags
from src.config.app_config import YouTubeConfig


class TagService:
    """
    Centralized service for managing tags and keywords.
    Provides personalized keywords based on user's liked videos.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the TagService with database path.
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db_path = db_path
    
    def get_personalized_keywords(self, num_keywords: int = 10) -> List[str]:
        """
        Get personalized keywords based on liked video tags with fallback to static keywords.
        
        Args:
            num_keywords: Number of keywords to return
            
        Returns:
            List of keywords (tags from liked videos or fallback to PROGRAMMING_KEYWORDS)
        """
        # First try to get tags from liked videos
        liked_tags = self.extract_tags_from_liked_videos()
        
        if liked_tags:
            # Use random selection from liked video tags
            return self.get_random_keywords(liked_tags, num_keywords)
        else:
            # Fallback to static programming keywords
            return self.get_random_keywords(YouTubeConfig.PROGRAMMING_KEYWORDS, num_keywords)
    
    def extract_tags_from_liked_videos(self) -> List[str]:
        """
        Extract all tags from liked videos.
        
        Returns:
            List of unique tags from liked videos
        """
        return get_liked_video_tags(self.db_path)
    
    def get_random_keywords(self, keywords: List[str], count: int) -> List[str]:
        """
        Get random selection of keywords from the provided list.
        
        Args:
            keywords: List of available keywords
            count: Number of keywords to select
            
        Returns:
            Randomly selected keywords
        """
        if not keywords:
            return []
        
        # If we need more keywords than available, return all
        if count >= len(keywords):
            return keywords.copy()
        
        # Random sample without replacement
        return random.sample(keywords, count)
    
    def has_liked_videos(self) -> bool:
        """
        Check if there are any liked videos with tags in the database.
        
        Returns:
            True if liked videos with tags exist, False otherwise
        """
        liked_tags = self.extract_tags_from_liked_videos()
        return len(liked_tags) > 0
    
    def get_keyword_source(self) -> str:
        """
        Get information about the source of keywords being used.
        
        Returns:
            String describing the keyword source
        """
        if self.has_liked_videos():
            liked_tags = self.extract_tags_from_liked_videos()
            return f"personalized tags from {len(liked_tags)} unique tags from liked videos"
        else:
            return f"fallback to {len(YouTubeConfig.PROGRAMMING_KEYWORDS)} static programming keywords"
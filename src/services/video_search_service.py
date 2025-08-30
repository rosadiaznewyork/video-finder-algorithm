"""
Video search service that consolidates the search-save pipeline.
"""

from typing import List, Dict
from datetime import datetime

from src.services.youtube_client import YouTubeAPIClient
from src.database.manager import setup_database_tables
from src.database.video_operations import save_videos_to_database, save_video_features_to_database
from src.youtube.utils import remove_duplicate_videos
from src.ml.feature_extraction import extract_all_features_from_video
from src.config.app_config import AppConfig


class VideoSearchService:
    """Service to handle the complete video search and save pipeline."""
    
    def __init__(self, api_key: str, db_path: str = None):
        """
        Initialize the video search service.
        
        Args:
            api_key: YouTube API key
            db_path: Database path (uses default if None)
        """
        self.youtube_client = YouTubeAPIClient(api_key)
        self.db_path = db_path or AppConfig.DATABASE_PATH
        setup_database_tables(self.db_path)
    
    def search_and_save_videos(self, queries: List[str], max_results_per_query: int = None, 
                              session_metadata: dict = None) -> List[Dict]:
        """
        Search for videos using multiple queries and save them to the database.
        
        Args:
            queries: List of search queries
            max_results_per_query: Maximum results per query (uses default if None)
            session_metadata: Optional metadata to add to videos (e.g., search topic)
            
        Returns:
            List of unique videos found and saved
        """
        if max_results_per_query is None:
            max_results_per_query = AppConfig.DEFAULT_RESULTS_PER_QUERY
        
        print(f"🔍 Searching YouTube with {len(queries)} queries...")
        print("-" * 40)
        
        all_videos = []
        total_found = 0
        
        for i, query in enumerate(queries, 1):
            print(f"  [{i}/{len(queries)}] Searching: {query[:50]}...")
            
            try:
                video_ids = self.youtube_client.search_videos(query, max_results_per_query)
                
                if video_ids:
                    videos = self.youtube_client.get_video_details(video_ids)
                    all_videos.extend(videos)
                    total_found += len(videos)
                    print(f"       ✓ Found {len(videos)} videos")
                else:
                    # Check for early exit on quota issues
                    if i == 1:  # First query failed
                        print(f"       - No videos found (possible quota exceeded)")
                        print(f"       💡 {AppConfig.DATABASE_PATH}")
                        break
                    else:
                        print(f"       - No videos found")
                    
            except Exception as e:
                print(f"       ✗ Error: {str(e)}")
        
        print(f"\n📊 Total videos found: {total_found}")
        
        # Remove duplicates
        unique_videos = remove_duplicate_videos(all_videos)
        print(f"📊 Unique videos: {len(unique_videos)}")
        
        if unique_videos:
            # Add session metadata if provided
            if session_metadata:
                for video in unique_videos:
                    video.update(session_metadata)
            
            # Save videos and extract features
            self._save_videos_with_features(unique_videos)
            
            print(f"\n✅ Successfully saved {len(unique_videos)} unique videos!")
            self._show_sample_videos(unique_videos)
        else:
            print("\n❌ No unique videos found.")
        
        return unique_videos
    
    def search_by_topic(self, topic: str, keywords: List[str], max_results_per_query: int = None) -> List[Dict]:
        """
        Search for videos on a specific topic with session tracking.
        
        Args:
            topic: The search topic
            keywords: List of generated keywords for the topic
            max_results_per_query: Maximum results per query
            
        Returns:
            List of unique videos found and saved
        """
        session_metadata = {
            'search_session': datetime.now().isoformat(),
            'search_topic': topic
        }
        
        print(f"\n🎯 Topic: {topic}")
        print("=" * 50)
        print(f"📋 Generated {len(keywords)} search queries")
        
        return self.search_and_save_videos(
            queries=keywords,
            max_results_per_query=max_results_per_query,
            session_metadata=session_metadata
        )
    
    def test_api_connection(self) -> bool:
        """
        Test if the YouTube API is working.
        
        Returns:
            True if API is working, False otherwise
        """
        return self.youtube_client.test_connection()
    
    def _save_videos_with_features(self, videos: List[Dict]):
        """
        Save videos to database and extract features.
        
        Args:
            videos: List of video dictionaries to save
        """
        print("💾 Saving videos to database...")
        save_videos_to_database(videos, self.db_path)
        
        print("🧮 Extracting features...")
        for video in videos:
            features = extract_all_features_from_video(video)
            save_video_features_to_database(video['id'], features, self.db_path)
    
    def _show_sample_videos(self, videos: List[Dict], num_samples: int = 3):
        """
        Display a sample of found videos.
        
        Args:
            videos: List of video dictionaries
            num_samples: Number of sample videos to show
        """
        print(f"\n🎬 Sample videos found:")
        for video in videos[:num_samples]:
            title = video['title'][:70] + "..." if len(video['title']) > 70 else video['title']
            print(f"  • {title}")
            print(f"    Channel: {video['channel_name']}")
            print(f"    Views: {video['view_count']:,}")
            print()
    

class TopicVideoSearchService(VideoSearchService):
    """Specialized service for topic-based video searching."""
    
    def search_topic_with_keywords(self, topic: str, keywords: List[str]) -> List[Dict]:
        """
        Search for videos on a topic using provided keywords.
        
        Args:
            topic: The search topic
            keywords: List of search keywords
            
        Returns:
            List of unique videos found and saved
        """
        # Use topic-specific configuration
        max_results = AppConfig.TOPIC_SEARCH_RESULTS_PER_QUERY
        limited_keywords = keywords[:AppConfig.TOPIC_SEARCH_MAX_QUERIES]
        
        return self.search_by_topic(topic, limited_keywords, max_results)
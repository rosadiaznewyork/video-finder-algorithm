"""
Refactored topic rating service with clean separation of concerns.
"""

from typing import List, Dict, Optional
from datetime import datetime

from src.services.video_search_service import TopicVideoSearchService
from src.database.connection import get_database_connection
from src.database.preference_operations import save_video_rating_to_database, get_rated_count_from_database
from src.rating.display import display_video_information_for_rating
from src.rating.user_input import get_user_rating_response, get_user_notes_for_rating
from src.rating.session import process_user_rating_for_video, should_continue_rating_session
from src.ollama.keyword_generator import generate_keywords_from_topic, fallback_manual_keywords
from src.config.app_config import AppConfig


class TopicRatingService:
    """Service for topic-based video search and rating sessions."""
    
    def __init__(self, api_key: str):
        """
        Initialize the topic rating service.
        
        Args:
            api_key: YouTube API key
        """
        self.search_service = TopicVideoSearchService(api_key)
        self.db_path = AppConfig.DATABASE_PATH
        self.current_session_videos = []
        self.current_topic = ""
    
    def run_rating_session_for_topic(self, topic: str, use_fallback: bool = False) -> int:
        """
        Run a complete rating session for a topic.
        
        Args:
            topic: The topic to search for and rate
            use_fallback: Whether to use fallback keyword generation
            
        Returns:
            Number of videos rated in this session
        """
        self.current_topic = topic
        
        # Generate keywords and search for videos
        keywords = self._generate_keywords_for_topic(topic, use_fallback)
        if not keywords:
            print("❌ Could not generate keywords for this topic.")
            return 0
        
        # Search for videos
        videos = self.search_service.search_topic_with_keywords(topic, keywords)
        if not videos:
            print("❌ No videos found for this topic.")
            return 0
        
        self.current_session_videos = videos
        
        # Start interactive rating session
        return self._run_interactive_rating_session()
    
    def _generate_keywords_for_topic(self, topic: str, use_fallback: bool = False) -> List[str]:
        """
        Generate search keywords for a topic.
        
        Args:
            topic: The topic to generate keywords for
            use_fallback: Whether to use fallback generation
            
        Returns:
            List of search keywords
        """
        if use_fallback:
            print("📝 Using fallback keyword generation...")
            return fallback_manual_keywords(topic)
        else:
            print("🤖 Generating search keywords with Ollama...")
            keywords = generate_keywords_from_topic(topic, num_queries=AppConfig.TOPIC_SEARCH_MAX_QUERIES)
            
            if not keywords:
                print("⚠️  Falling back to manual keyword generation...")
                return fallback_manual_keywords(topic)
            
            return keywords
    
    def _run_interactive_rating_session(self) -> int:
        """
        Run the interactive rating session for found videos.
        
        Returns:
            Number of videos rated
        """
        if not self.current_session_videos:
            return 0
        
        self._display_rating_session_header()
        
        rated_count = 0
        unrated_videos = self._get_unrated_videos_from_session()
        
        for i, video in enumerate(unrated_videos, 1):
            print(f"\n[{i}/{len(unrated_videos)}] Video from topic: {self.current_topic}")
            print("-" * 40)
            
            display_video_information_for_rating(video)
            response = get_user_rating_response()
            
            if not should_continue_rating_session(response):
                break
            
            self._save_video_rating(video, response)
            rated_count += 1
        
        self._display_session_summary(rated_count)
        return rated_count
    
    def _display_rating_session_header(self):
        """Display the rating session header with instructions."""
        print("\n" + "=" * 50)
        print("📺 RATING SESSION")
        print("=" * 50)
        print(f"Topic: {self.current_topic}")
        print(f"Videos to rate: {len(self.current_session_videos)}")
        print("\nInstructions:")
        print("  y = Like this video")
        print("  n = Don't like this video")
        print("  q = Quit rating session")
        print("-" * 50)
    
    def _get_unrated_videos_from_session(self) -> List[Dict]:
        """
        Get unrated videos from the current session.
        
        Returns:
            List of unrated video dictionaries
        """
        if not self.current_session_videos:
            return []
        
        video_ids = [v['id'] for v in self.current_session_videos]
        
        with get_database_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get videos from this session that haven't been rated
            placeholders = ','.join(['?' for _ in video_ids])
            cursor.execute(f'''
                SELECT v.*
                FROM videos v
                LEFT JOIN preferences p ON v.id = p.video_id
                WHERE p.video_id IS NULL
                AND v.id IN ({placeholders})
                ORDER BY v.view_count DESC
            ''', video_ids)
            
            unrated_videos = []
            for row in cursor.fetchall():
                unrated_videos.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'view_count': row[3],
                    'like_count': row[4],
                    'comment_count': row[5],
                    'duration': row[6],
                    'published_at': row[7],
                    'channel_name': row[8],
                    'thumbnail_url': row[9],
                    'tags': row[10],
                    'url': f"https://youtube.com/watch?v={row[0]}"
                })
            
            return unrated_videos
    
    def _save_video_rating(self, video: Dict, response: str):
        """
        Save a video rating to the database.
        
        Args:
            video: Video dictionary
            response: User response ('y' or 'n')
        """
        def save_rating(video_id, liked, notes):
            save_video_rating_to_database(video_id, liked, notes, self.db_path)
        
        process_user_rating_for_video(video, response, save_rating, get_user_notes_for_rating)
    
    def _display_session_summary(self, rated_count: int):
        """
        Display summary after rating session.
        
        Args:
            rated_count: Number of videos rated in this session
        """
        print(f"\n✅ Completed rating session for '{self.current_topic}'")
        print(f"   Rated {rated_count} videos")
        
        # Show overall progress
        total_rated = get_rated_count_from_database(self.db_path)
        print(f"\n📊 Total videos rated overall: {total_rated}")
        
        if total_rated >= AppConfig.ML_TRAINING_THRESHOLD:
            print("🤖 ML model is now active for recommendations!")


class MultiTopicRatingService:
    """Service for handling multiple topic rating sessions."""
    
    def __init__(self, api_key: str):
        """
        Initialize the multi-topic rating service.
        
        Args:
            api_key: YouTube API key
        """
        self.topic_service = TopicRatingService(api_key)
        self.search_service = TopicVideoSearchService(api_key)
    
    def run_continuous_rating_sessions(self, use_fallback: bool = False) -> None:
        """
        Run continuous topic rating sessions until user quits.
        
        Args:
            use_fallback: Whether to use fallback keyword generation
        """
        total_sessions = 0
        total_rated = 0
        
        while True:
            topic = self._get_topic_input()
            if not topic:
                break
            
            # Check API status
            if not self._check_api_status():
                if input("Continue anyway? (y/n): ").lower() != 'y':
                    continue
            
            # Run rating session for this topic
            rated_count = self.topic_service.run_rating_session_for_topic(topic, use_fallback)
            total_sessions += 1
            total_rated += rated_count
            
            # Ask if user wants to continue
            if not self._should_continue():
                break
        
        self._display_final_summary(total_sessions, total_rated)
    
    def _get_topic_input(self) -> Optional[str]:
        """
        Get topic input from user.
        
        Returns:
            Topic string or None to quit
        """
        print("\n🎯 Topic-Based Video Rating")
        print("=" * 40)
        
        topic = input("\n📝 Enter topic to search and rate (or 'quit' to exit): ").strip()
        
        if topic.lower() in ['quit', 'exit', 'q']:
            return None
        
        if not topic:
            print("❌ Topic cannot be empty")
            return self._get_topic_input()  # Recursive retry
        
        return topic
    
    def _check_api_status(self) -> bool:
        """
        Check if YouTube API is working.
        
        Returns:
            True if API is working, False otherwise
        """
        print("🔍 Checking YouTube API status...")
        if not self.search_service.test_api_connection():
            print("❌ YouTube API quota exceeded or API key invalid")
            print("💡 YouTube API quota resets daily at midnight Pacific Time")
            print("   You can still rate existing videos in the database")
            return False
        return True
    
    def _should_continue(self) -> bool:
        """
        Ask user if they want to continue with another topic.
        
        Returns:
            True if user wants to continue, False otherwise
        """
        another = input("\n🔄 Search and rate another topic? (y/n): ")
        return another.lower() == 'y'
    
    def _display_final_summary(self, total_sessions: int, total_rated: int):
        """
        Display final summary of all rating sessions.
        
        Args:
            total_sessions: Total number of topic sessions completed
            total_rated: Total number of videos rated across all sessions
        """
        print("\n🏁 Session complete!")
        print(f"📊 Topics explored: {total_sessions}")
        print(f"📊 Videos rated this session: {total_rated}")
        
        overall_total = get_rated_count_from_database(AppConfig.DATABASE_PATH)
        print(f"📊 Total videos rated overall: {overall_total}")
        
        if overall_total >= AppConfig.ML_TRAINING_THRESHOLD:
            print("\n💡 You can now use the dashboard to see AI-powered recommendations!")
            print("   Run: python dashboard_api.py")
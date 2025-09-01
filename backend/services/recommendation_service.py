import os
import sqlite3
import pandas as pd
from ..database.manager import setup_database_tables
from ..database.preference_operations import (
    get_training_data_from_database,
    get_unrated_videos_with_features_from_database,
    get_rated_count_from_database,
    save_video_rating_to_database
)
from ..database.video_operations import get_unrated_videos_from_database
from ..ml.model_training import create_recommendation_model, train_model_on_user_preferences
from ..ml.predictions import predict_video_preferences_with_model

class RecommendationService:
    """Service for handling video recommendations and ML model management"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.model = None
        self.model_trained = False
        setup_database_tables(self.db_path)
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the ML model if we have enough ratings"""
        rated_count = get_rated_count_from_database(self.db_path)
        if rated_count >= 3:
            self.model = create_recommendation_model()
            training_data = get_training_data_from_database(self.db_path)
            success = train_model_on_user_preferences(self.model, training_data)
            if success:
                self.model_trained = True

    def get_recommendations(self):
        """Get video recommendations based on user preferences"""
        self._ensure_sufficient_videos()
        
        if self.model_trained and self.model:
            video_features = get_unrated_videos_with_features_from_database(self.db_path)
            recommendations = predict_video_preferences_with_model(self.model, video_features)
            return recommendations[:12]
        else:
            fallback_videos = get_unrated_videos_from_database(12, self.db_path)
            for video in fallback_videos:
                video['like_probability'] = 0.5
            return fallback_videos

    def _ensure_sufficient_videos(self):
        """Check if we have sufficient videos (auto-search disabled to save API quota)"""
        unrated_videos = get_unrated_videos_from_database(20, self.db_path)

        if len(unrated_videos) < 5:
            print("🔍 Running low on videos, automatically searching for more...")
            self._search_more_videos()

    def _search_more_videos(self):
        """Search for more videos using the search_more_videos functionality"""
        try:
            from .youtube_service import YouTubeService
            from ..ml.feature_extraction import extract_all_features_from_video
            from ..database.video_operations import save_videos_to_database, save_video_features_to_database
            from ..config.search_config import get_search_queries
            import random

            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                print("Warning: No YouTube API key found, cannot fetch more videos")
                return

            youtube_service = YouTubeService(api_key)
            all_queries = get_search_queries()

            if len(all_queries) > 5:
                search_queries = all_queries[5:]
            else:
                search_queries = all_queries.copy()
                random.shuffle(search_queries)

            search_queries = search_queries[:3]

            all_videos = []
            for query in search_queries:
                videos = youtube_service.search_and_get_details(query, 10)
                all_videos.extend(videos)

            unique_videos = YouTubeService.remove_duplicate_videos(all_videos)

            if unique_videos:
                save_videos_to_database(unique_videos, self.db_path)

                for video in unique_videos:
                    features = extract_all_features_from_video(video)
                    save_video_features_to_database(video['id'], features, self.db_path)

                print(f"✅ Automatically found and saved {len(unique_videos)} new videos!")

        except Exception as e:
            print(f"Error searching for more videos: {e}")

    def rate_video(self, video_id, liked):
        """Rate a video and potentially retrain the model"""
        # Save the rating
        save_video_rating_to_database(video_id, liked, "", self.db_path)

        # Check if we should retrain the model
        model_retrained = False
        rated_count = get_rated_count_from_database(self.db_path)

        if rated_count >= 3:
            if not self.model:
                self.model = create_recommendation_model()

            training_data = get_training_data_from_database(self.db_path)
            success = train_model_on_user_preferences(self.model, training_data)

            if success:
                self.model_trained = True
                model_retrained = True

        return {
            'model_retrained': model_retrained,
            'total_ratings': rated_count
        }

    def get_liked_videos(self):
        """Get all liked videos with confidence scores"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT v.id, v.title, v.channel_name, v.view_count, v.url
                FROM videos v
                JOIN preferences p ON v.id = p.video_id
                WHERE p.liked = 1
                ORDER BY p.created_at DESC
            """)

            liked_videos = []
            for row in cursor.fetchall():
                liked_videos.append({
                    'id': row[0],
                    'title': row[1],
                    'channel_name': row[2],
                    'view_count': row[3],
                    'url': row[4]
                })

            conn.close()

            if self.model_trained and self.model and liked_videos:
                cursor = sqlite3.connect(self.db_path).cursor()

                df_data = []
                for video in liked_videos:
                    cursor.execute("SELECT * FROM video_features WHERE video_id = ?", (video['id'],))
                    features = cursor.fetchone()
                    if features:
                        df_data.append({
                            'video_id': features[0],
                            'title_length': features[1],
                            'description_length': features[2],
                            'view_like_ratio': features[3],
                            'engagement_score': features[4],
                            'title_sentiment': features[5],
                            'has_tutorial_keywords': features[6],
                            'has_time_constraint': features[7],
                            'has_beginner_keywords': features[8],
                            'has_tech_keywords': features[9],
                            'has_project_keywords': features[10]
                        })

                if df_data:
                    video_features_df = pd.DataFrame(df_data)
                    predictions = predict_video_preferences_with_model(self.model, video_features_df)
                    return sorted(predictions, key=lambda x: x.get('like_probability', 0), reverse=True)

            for video in liked_videos:
                video['like_probability'] = 0.8

            return liked_videos

        except Exception as e:
            print(f"Error getting liked videos: {e}")
            return []

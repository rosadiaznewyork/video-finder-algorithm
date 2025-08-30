import os
from dotenv import load_dotenv

from src.config.app_config import AppConfig
from src.services.video_search_service import VideoSearchService
from src.database.manager import setup_database_tables
from src.database.video_operations import get_unrated_videos_from_database
from src.database.preference_operations import save_video_rating_to_database, get_training_data_from_database, get_unrated_videos_with_features_from_database, get_rated_count_from_database

from src.youtube.search import get_coding_search_queries
from src.ml.model_training import create_recommendation_model, train_model_on_user_preferences
from src.ml.predictions import predict_video_preferences_with_model

from src.rating.display import display_video_information_for_rating, display_rating_session_header, display_session_type_message
from src.rating.user_input import get_user_rating_response, get_user_notes_for_rating
from src.rating.session import process_user_rating_for_video, should_continue_rating_session, has_videos_to_rate

load_dotenv()

class VideoInspirationFinderApp:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.db_path = AppConfig.DATABASE_PATH
        self.model = None
        self.model_trained = False
        
        setup_database_tables(self.db_path)

    def search_and_save_coding_videos(self):
        """Search and save coding videos using the VideoSearchService."""
        print("🔍 Searching for coding videos...")
        
        # Use the new VideoSearchService for clean, unified search
        search_service = VideoSearchService(self.api_key, self.db_path)
        search_queries = get_coding_search_queries()[:5]  # Use first 5 queries
        
        unique_videos = search_service.search_and_save_videos(
            queries=search_queries, 
            max_results_per_query=AppConfig.DEFAULT_RESULTS_PER_QUERY
        )
        
        print(f"🏁 Search complete! Found and saved {len(unique_videos)} videos")

    def start_interactive_rating_session(self):
        display_rating_session_header()
        
        while True:
            videos = self._get_videos_for_rating()
            rated_count = get_rated_count_from_database(self.db_path)
            session_message = display_session_type_message(self.model_trained, rated_count)
            
            print(f"\n{session_message}")
            
            if not has_videos_to_rate(videos):
                print("No more videos to rate!")
                break
            
            for video in videos:
                display_video_information_for_rating(video)
                
                response = get_user_rating_response()
                
                if not should_continue_rating_session(response):
                    return
                
                def save_rating(video_id, liked, notes):
                    save_video_rating_to_database(video_id, liked, notes, self.db_path)
                
                process_user_rating_for_video(video, response, save_rating, get_user_notes_for_rating)
                self._try_train_model()

    def _get_videos_for_rating(self):
        if self.model_trained and self.model:
            video_features = get_unrated_videos_with_features_from_database(self.db_path)
            return predict_video_preferences_with_model(self.model, video_features)
        else:
            return get_unrated_videos_from_database(AppConfig.DEFAULT_RESULTS_PER_QUERY, self.db_path)

    def _try_train_model(self):
        if not self.model_trained:
            if self.model is None:
                self.model = create_recommendation_model()
            
            training_data = get_training_data_from_database(self.db_path)
            success = train_model_on_user_preferences(self.model, training_data)
            if success:
                self.model_trained = True

def main():
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in environment variables")
        print("Please create a .env file with your YouTube API key")
        return
    
    app = VideoInspirationFinderApp(api_key)
    app.search_and_save_coding_videos()
    app.start_interactive_rating_session()

if __name__ == "__main__":
    main()
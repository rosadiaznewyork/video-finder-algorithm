import os
from dotenv import load_dotenv

from src.database.manager import setup_database_tables
from src.database.video_operations import save_videos_to_database, save_video_features_to_database, get_unrated_videos_from_database
from src.database.preference_operations import save_video_rating_to_database, get_training_data_from_database, get_unrated_videos_with_features_from_database, get_rated_count_from_database

from src.youtube.search import search_youtube_videos_by_query, get_coding_search_queries
from src.youtube.details import get_video_details_from_youtube
from src.youtube.utils import remove_duplicate_videos

from src.ml.feature_extraction import extract_all_features_from_video
from src.ml.model_training import create_recommendation_model, train_model_on_user_preferences
from src.ml.predictions import predict_video_preferences_with_model

from src.rating.display import display_video_information_for_rating, display_rating_session_header, display_session_type_message
from src.rating.user_input import get_user_rating_response, get_user_notes_for_rating
from src.rating.session import process_user_rating_for_video, should_continue_rating_session, has_videos_to_rate

load_dotenv()

class VideoInspirationFinderApp:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.db_path = "video_inspiration.db"
        self.model = None
        self.model_trained = False
        
        setup_database_tables(self.db_path)

    def search_and_save_coding_videos(self):
        print("🔍 Searching for coding videos...")
        
        all_videos = []
        search_queries = get_coding_search_queries()
        
        for query in search_queries[:5]:
            video_ids = search_youtube_videos_by_query(self.api_key, query, 10)
            videos = get_video_details_from_youtube(self.api_key, video_ids)
            all_videos.extend(videos)
        
        unique_videos = remove_duplicate_videos(all_videos)
        
        save_videos_to_database(unique_videos, self.db_path)
        
        for video in unique_videos:
            features = extract_all_features_from_video(video)
            save_video_features_to_database(video['id'], features, self.db_path)
        
        print(f"Found and saved {len(unique_videos)} videos")

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
            return get_unrated_videos_from_database(10, self.db_path)

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
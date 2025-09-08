import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv

from src.database.manager import setup_database_tables
from src.database.preference_operations import get_training_data_from_database, get_unrated_videos_with_features_from_database, get_rated_count_from_database, save_video_rating_to_database
from src.database.video_operations import get_unrated_videos_from_database
from src.ml.model_training import create_recommendation_model, train_model_on_user_preferences
from src.ml.predictions import predict_video_preferences_with_model

load_dotenv()

app = Flask(__name__)
CORS(app)

class DashboardAPI:
    def __init__(self):
        self.db_path = "video_inspiration.db"
        self.model = None
        self.model_trained = False
        setup_database_tables(self.db_path)
        self._initialize_model()

    def _initialize_model(self):
        rated_count = get_rated_count_from_database(self.db_path)
        if rated_count >= 10:
            self.model = create_recommendation_model()
            training_data = get_training_data_from_database(self.db_path)
            success = train_model_on_user_preferences(self.model, training_data)
            if success:
                self.model_trained = True

    def get_recommendations(self):
        if self.model_trained and self.model:
            video_features = get_unrated_videos_with_features_from_database(self.db_path)
            recommendations = predict_video_preferences_with_model(self.model, video_features)
            return recommendations[:12]  # Return 12 videos for dashboard
        else:
            fallback_videos = get_unrated_videos_from_database(12, self.db_path)
            for video in fallback_videos:
                video['like_probability'] = 0.5  # Default probability
            return fallback_videos
    
    def get_liked_videos(self):
        """Get videos that user liked, ordered by AI match confidence"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get liked videos with features
            query = """
            SELECT v.*, vf.*, p.liked
            FROM videos v 
            JOIN video_features vf ON v.id = vf.video_id
            JOIN preferences p ON v.id = p.video_id
            WHERE p.liked = 1
            ORDER BY v.view_count DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            
            liked_videos = []
            for row in results:
                video = {
                    'id': row['id'],
                    'title': row['title'],
                    'channel_name': row['channel_name'],
                    'view_count': row['view_count'],
                    'url': f"https://www.youtube.com/watch?v={row['id']}"
                }
                liked_videos.append(video)
            
            # If model is trained, predict confidence for liked videos
            if self.model_trained and self.model and liked_videos:
                # Create pandas DataFrame for prediction
                import pandas as pd
                
                df_data = []
                for row in results:
                    row_data = {
                        'id': row['id'],
                        'title': row['title'],
                        'channel_name': row['channel_name'],
                        'view_count': row['view_count'],
                        'title_length': row['title_length'],
                        'description_length': row['description_length'],
                        'view_like_ratio': row['view_like_ratio'],
                        'engagement_score': row['engagement_score'],
                        'title_sentiment': row['title_sentiment'],
                        'has_tutorial_keywords': row['has_tutorial_keywords'],
                        'has_beginner_keywords': row['has_beginner_keywords'],
                        'has_ai_keywords': row['has_ai_keywords'],
                        'has_challenge_keywords': row['has_challenge_keywords'],
                        'has_time_constraint': row['has_time_constraint']
                    }
                    df_data.append(row_data)
                
                video_features_df = pd.DataFrame(df_data)
                
                # Get predictions for confidence scores
                predictions = predict_video_preferences_with_model(self.model, video_features_df)
                
                # Sort by confidence and return
                return sorted(predictions, key=lambda x: x.get('like_probability', 0), reverse=True)
            
            # If no model, return with default confidence
            for video in liked_videos:
                video['like_probability'] = 0.8  # High default for liked videos
                
            return liked_videos
            
        except Exception as e:
            print(f"Error getting liked videos: {e}")
            return []

dashboard_api = DashboardAPI()

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/recommendations')
def get_recommendations():
    try:
        recommendations = dashboard_api.get_recommendations()
        
        formatted_recommendations = []
        for video in recommendations:
            formatted_recommendations.append({
                'id': video['id'],
                'title': video['title'],
                'channel_name': video['channel_name'],
                'view_count': video['view_count'],
                'url': video['url'],
                'thumbnail': f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg",
                'confidence': round(video.get('like_probability', 0.5) * 100),
                'views_formatted': format_view_count(video['view_count'])
            })
        
        return jsonify({
            'success': True,
            'videos': formatted_recommendations,
            'model_trained': dashboard_api.model_trained,
            'total_ratings': get_rated_count_from_database(dashboard_api.db_path)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rate', methods=['POST'])
def rate_video():
    try:
        data = request.json
        video_id = data.get('video_id')
        liked = data.get('liked')
        
        if not video_id or liked is None:
            return jsonify({
                'success': False,
                'error': 'Missing video_id or liked parameter'
            }), 400
        
        # Save the rating
        save_video_rating_to_database(video_id, liked, "", dashboard_api.db_path)
        
        # Check if we should retrain the model
        model_retrained = False
        rated_count = get_rated_count_from_database(dashboard_api.db_path)
        
        if rated_count >= 10:  # Minimum ratings needed for training
            # Retrain the model with new data
            if not dashboard_api.model:
                dashboard_api.model = create_recommendation_model()
            
            training_data = get_training_data_from_database(dashboard_api.db_path)
            success = train_model_on_user_preferences(dashboard_api.model, training_data)
            
            if success:
                dashboard_api.model_trained = True
                model_retrained = True
        
        return jsonify({
            'success': True,
            'message': 'Rating saved successfully',
            'model_retrained': model_retrained,
            'total_ratings': rated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/liked')
def get_liked_videos():
    try:
        liked_videos = dashboard_api.get_liked_videos()
        
        formatted_videos = []
        for video in liked_videos:
            formatted_videos.append({
                'id': video['id'],
                'title': video['title'],
                'channel_name': video['channel_name'],
                'view_count': video['view_count'],
                'url': video['url'],
                'thumbnail': f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg",
                'confidence': round(video.get('like_probability', 0.8) * 100),
                'views_formatted': format_view_count(video['view_count'])
            })
        
        return jsonify({
            'success': True,
            'videos': formatted_videos,
            'total_liked': len(formatted_videos)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_view_count(count):
    if count >= 1000000:
        return f"{count/1000000:.1f}M views"
    elif count >= 1000:
        return f"{count/1000:.1f}K views"
    else:
        return f"{count} views"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5001)
import os
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from dotenv import load_dotenv

from src.config.app_config import AppConfig
from src.database.manager import setup_database_tables
from src.database.connection import get_database_connection
from src.database.preference_operations import get_training_data_from_database, get_unrated_videos_with_features_from_database, get_rated_count_from_database, save_video_rating_to_database, remove_video_preference
from src.database.search_operations import get_recent_search_sessions, get_videos_by_search_session, get_search_sessions_stats, cleanup_old_search_sessions, delete_search_session, create_search_session, update_search_session_video_count
from src.services.video_search_service import TopicVideoSearchService
from src.database.video_operations import get_unrated_videos_from_database
from src.ml.model_training import create_recommendation_model, train_model_on_user_preferences
from src.ml.predictions import predict_video_preferences_with_model

load_dotenv()

app = Flask(__name__)
CORS(app)

class DashboardAPI:
    def __init__(self):
        self.db_path = AppConfig.DATABASE_PATH
        self.model = None
        self.model_trained = False
        setup_database_tables(self.db_path)
        self._initialize_model()

    def _initialize_model(self):
        rated_count = get_rated_count_from_database(self.db_path)
        if rated_count >= AppConfig.ML_TRAINING_THRESHOLD:
            self.model = create_recommendation_model()
            training_data = get_training_data_from_database(self.db_path)
            success = train_model_on_user_preferences(self.model, training_data)
            if success:
                self.model_trained = True

    def get_recommendations(self):
        if self.model_trained and self.model:
            video_features = get_unrated_videos_with_features_from_database(self.db_path)
            recommendations = predict_video_preferences_with_model(self.model, video_features, top_n=24)
            return recommendations  # Return 24 videos for dashboard
        else:
            fallback_videos = get_unrated_videos_from_database(24, self.db_path)
            for video in fallback_videos:
                video['like_probability'] = 0.5  # Default probability
            return fallback_videos
    
    def get_liked_videos(self):
        """Get videos that user liked, ordered by AI match confidence"""
        import sqlite3
        
        try:
            with get_database_connection(self.db_path) as conn:
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
        
        if rated_count >= AppConfig.ML_TRAINING_THRESHOLD:  # Minimum ratings needed for training
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

@app.route('/api/remove-liked', methods=['POST'])
def remove_liked_video():
    """Remove a liked video (delete the preference)."""
    try:
        data = request.json
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400
        
        # Remove the preference from database
        removed = remove_video_preference(video_id, dashboard_api.db_path)
        
        if not removed:
            return jsonify({
                'success': False,
                'error': 'Video preference not found'
            }), 404
        
        # Check if we should retrain the model
        rated_count = get_rated_count_from_database(dashboard_api.db_path)
        model_retrained = False
        
        if rated_count >= AppConfig.ML_TRAINING_THRESHOLD:
            # Retrain the model with updated data
            if not dashboard_api.model:
                dashboard_api.model = create_recommendation_model()
            
            training_data = get_training_data_from_database(dashboard_api.db_path)
            success = train_model_on_user_preferences(dashboard_api.model, training_data)
            if success:
                dashboard_api.model_trained = True
                model_retrained = True
        
        return jsonify({
            'success': True,
            'model_retrained': model_retrained,
            'remaining_rated': rated_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search-topic', methods=['POST'])
def search_topic():
    """Search for videos by topic using AI keyword generation."""
    try:
        data = request.json
        topic = data.get('topic', '').strip()
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Check if we have a YouTube API key
        import os
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_api_key:
            return jsonify({
                'success': False,
                'error': 'YouTube API key not configured'
            }), 500
        
        # Create search session
        session_id = create_search_session(topic, dashboard_api.db_path)
        
        # Initialize the search service
        search_service = TopicVideoSearchService(youtube_api_key, dashboard_api.db_path)
        
        # Test API connection first
        if not search_service.test_api_connection():
            return jsonify({
                'success': False,
                'error': 'YouTube API connection failed. Please check your API key and quota.',
                'session_id': session_id
            }), 500
        
        # Generate keywords using Ollama
        from src.ollama.keyword_generator import generate_keywords_from_topic
        keywords = generate_keywords_from_topic(topic)
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': 'Failed to generate search keywords. Please check if Ollama is running.',
                'session_id': session_id
            }), 500
        
        # Add session metadata to the search service
        # We need to pass the session metadata to the search service so it gets saved with the videos
        session_metadata = {
            'search_session_id': session_id,
            'search_topic': topic
        }
        
        # Search for videos using the generated keywords with session metadata  
        max_queries = 5  # Limit to avoid overwhelming the API
        max_results_per_query = 3  # Conservative per-query limit
        
        videos = search_service.search_and_save_videos(
            queries=keywords[:max_queries],
            max_results_per_query=max_results_per_query,
            session_metadata=session_metadata
        )
        
        # Update search session with video count
        update_search_session_video_count(session_id, len(videos), dashboard_api.db_path)
        
        # Format videos for frontend
        formatted_videos = []
        for video in videos:
            formatted_videos.append({
                'id': video['id'],
                'title': video['title'],
                'channel_name': video['channel_name'],
                'view_count': video['view_count'],
                'url': video['url'],
                'thumbnail': f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg",
                'views_formatted': format_view_count(video['view_count']),
                'search_topic': topic,
                'search_session_id': session_id
            })
        
        return jsonify({
            'success': True,
            'videos': formatted_videos,
            'session_id': session_id,
            'topic': topic,
            'keywords_used': keywords,
            'total_videos': len(formatted_videos),
            'message': f'Found {len(formatted_videos)} videos for "{topic}"'
        })
        
    except Exception as e:
        import traceback
        print(f"Search error: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@app.route('/api/add-video-by-url', methods=['POST'])
def add_video_by_url():
    """Add a YouTube video to liked videos by URL or video ID."""
    try:
        data = request.json
        url_or_id = data.get('url', '').strip()
        
        if not url_or_id:
            return jsonify({
                'success': False,
                'error': 'YouTube URL or video ID is required'
            }), 400
        
        # Extract video ID from URL
        video_id = extract_video_id_from_url(url_or_id)
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'Invalid YouTube URL or video ID format'
            }), 400
        
        # Check if video already exists in liked videos
        with get_database_connection(dashboard_api.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.title FROM videos v
                JOIN preferences p ON v.id = p.video_id
                WHERE v.id = ? AND p.liked = 1
            ''', (video_id,))
            existing = cursor.fetchone()
            
            if existing:
                return jsonify({
                    'success': False,
                    'error': f'Video already in your liked videos: "{existing[0]}"'
                }), 409
        
        # Get YouTube API key
        import os
        youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        if not youtube_api_key:
            return jsonify({
                'success': False,
                'error': 'YouTube API key not configured'
            }), 500
        
        # Initialize YouTube client
        from src.services.youtube_client import YouTubeAPIClient
        youtube_client = YouTubeAPIClient(youtube_api_key)
        
        # Fetch video details
        videos = youtube_client.get_video_details([video_id])
        
        if not videos:
            return jsonify({
                'success': False,
                'error': 'Video not found or could not fetch details. Check if the video exists and is public.'
            }), 404
        
        video = videos[0]
        
        # Save video to database
        from src.database.video_operations import save_videos_to_database, save_video_features_to_database
        save_videos_to_database([video], dashboard_api.db_path)
        
        # Extract and save features
        from src.ml.feature_extraction import extract_all_features_from_video
        features = extract_all_features_from_video(video)
        save_video_features_to_database(video['id'], features, dashboard_api.db_path)
        
        # Add to liked videos
        save_video_rating_to_database(video['id'], True, "Manually added via dashboard", dashboard_api.db_path)
        
        # Retrain model if threshold is met
        model_retrained = False
        rated_count = get_rated_count_from_database(dashboard_api.db_path)
        
        if rated_count >= AppConfig.ML_TRAINING_THRESHOLD:
            if not dashboard_api.model:
                dashboard_api.model = create_recommendation_model()
            
            training_data = get_training_data_from_database(dashboard_api.db_path)
            success = train_model_on_user_preferences(dashboard_api.model, training_data)
            
            if success:
                dashboard_api.model_trained = True
                model_retrained = True
        
        return jsonify({
            'success': True,
            'message': f'Successfully added "{video["title"]}" to your liked videos',
            'video': {
                'id': video['id'],
                'title': video['title'],
                'channel_name': video['channel_name'],
                'view_count': video['view_count'],
                'url': video['url']
            },
            'model_retrained': model_retrained,
            'total_liked': rated_count
        })
        
    except Exception as e:
        import traceback
        print(f"Error adding video: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'error': f'Failed to add video: {str(e)}'
        }), 500

def extract_video_id_from_url(url_or_id):
    """Extract YouTube video ID from various URL formats."""
    import re
    
    # If it's already just a video ID (11 characters)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # Regular YouTube watch URL
    match = re.search(r'(?:youtube\.com/watch\?v=|youtube\.com/watch\?.*&v=)([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    
    # Short YouTube URL
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    
    # YouTube embed URL
    match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    
    # YouTube video URL with timestamp
    match = re.search(r'youtube\.com/v/([a-zA-Z0-9_-]{11})', url_or_id)
    if match:
        return match.group(1)
    
    return None

@app.route('/api/search-history')
def get_search_history():
    """Get recent search sessions with metadata."""
    try:
        # Get recent search sessions
        sessions = get_recent_search_sessions(20, dashboard_api.db_path)
        
        # Get search statistics
        stats = get_search_sessions_stats(dashboard_api.db_path)
        
        # Format sessions with additional metadata
        formatted_sessions = []
        for session in sessions:
            # Calculate time ago
            from datetime import datetime
            created_at = datetime.fromisoformat(session['created_at'])
            time_ago = get_time_ago(created_at)
            
            formatted_sessions.append({
                'id': session['id'],
                'topic': session['topic'],
                'video_count': session['video_count'],
                'created_at': session['created_at'],
                'time_ago': time_ago,
                'status': session['status']
            })
        
        return jsonify({
            'success': True,
            'sessions': formatted_sessions,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search-session/<session_id>')
def get_search_session_videos(session_id):
    """Get videos from a specific search session."""
    try:
        videos = get_videos_by_search_session(session_id, dashboard_api.db_path)
        
        formatted_videos = []
        for video in videos:
            formatted_videos.append({
                'id': video['id'],
                'title': video['title'],
                'channel_name': video['channel_name'],
                'view_count': video['view_count'],
                'url': video['url'],
                'thumbnail': f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg",
                'views_formatted': format_view_count(video['view_count']),
                'search_topic': video.get('search_topic', 'Unknown')
            })
        
        return jsonify({
            'success': True,
            'videos': formatted_videos,
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/cleanup-searches', methods=['POST'])
def cleanup_searches():
    """Clean up old search sessions."""
    try:
        data = request.json or {}
        days_old = data.get('days_old', 7)
        
        cleaned_count = cleanup_old_search_sessions(days_old, dashboard_api.db_path)
        
        # Get updated stats
        stats = get_search_sessions_stats(dashboard_api.db_path)
        
        return jsonify({
            'success': True,
            'cleaned_sessions': cleaned_count,
            'message': f'Archived {cleaned_count} old search sessions',
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/delete-search-session/<session_id>', methods=['DELETE'])
def delete_search_session_endpoint(session_id):
    """Delete a specific search session."""
    try:
        data = request.json or {}
        remove_videos = data.get('remove_videos', False)
        
        success = delete_search_session(session_id, dashboard_api.db_path, remove_videos)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Search session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Search session deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_time_ago(datetime_obj):
    """Convert datetime to human-readable time ago string."""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    diff = now - datetime_obj
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

def format_view_count(count):
    if count >= 1000000:
        return f"{count/1000000:.1f}M views"
    elif count >= 1000:
        return f"{count/1000:.1f}K views"
    else:
        return f"{count} views"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
from flask import Blueprint, jsonify, request, current_app
from ...services.recommendation_service import RecommendationService
from ...database.preference_operations import save_video_rating_to_database, get_rated_count_from_database
from ...ml.model_training import create_recommendation_model, train_model_on_user_preferences
from ...database.preference_operations import get_training_data_from_database

videos_api_bp = Blueprint('videos_api', __name__, url_prefix='/api')



def get_recommendation_service():
    """Get a fresh recommendation service instance"""
    db_path = current_app.config.get('DATABASE_PATH', 'video_inspiration.db')
    return RecommendationService(db_path)

@videos_api_bp.route('/recommendations')
def get_recommendations():
    """Get video recommendations"""
    try:
        service = get_recommendation_service()
        recommendations = service.get_recommendations()

        # Format for web response
        formatted_recommendations = [
            _format_video_for_api(video) for video in recommendations
        ]

        return jsonify({
            'success': True,
            'videos': formatted_recommendations,
            'model_trained': service.model_trained,
            'total_ratings': get_rated_count_from_database(service.db_path)
        })

    except Exception as e:
        error_msg = str(e).lower()
        error_type = 'unknown'
        user_message = str(e)

        if 'quota' in error_msg or 'exceeded' in error_msg:
            error_type = 'quota_exceeded'
            user_message = 'YouTube API quota exceeded. Quotas reset daily - try again tomorrow!'
        elif 'api' in error_msg and 'key' in error_msg:
            error_type = 'invalid_api_key'
            user_message = 'Invalid YouTube API key. Please check your .env file.'
        elif 'network' in error_msg or 'connection' in error_msg:
            error_type = 'network_error'
            user_message = 'Network error. Please check your internet connection.'

        return jsonify({
            'success': False,
            'error': user_message,
            'error_type': error_type,
            'videos': []
        }), 500

@videos_api_bp.route('/rate', methods=['POST'])
def rate_video():
    """Rate a video"""
    try:
        data = request.json
        video_id = data.get('video_id')
        liked = data.get('liked')

        if not video_id or liked is None:
            return jsonify({
                'success': False,
                'error': 'Missing video_id or liked parameter'
            }), 400

        service = get_recommendation_service()

        # Save rating and potentially retrain model
        result = service.rate_video(video_id, liked)

        return jsonify({
            'success': True,
            'message': 'Rating saved successfully',
            'model_retrained': result.get('model_retrained', False),
            'total_ratings': result.get('total_ratings', 0)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@videos_api_bp.route('/liked')
def get_liked_videos():
    """Get liked videos"""
    try:
        service = get_recommendation_service()
        liked_videos = service.get_liked_videos()

        # Format for web response
        formatted_videos = [
            _format_video_for_api(video) for video in liked_videos
        ]

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

def _format_video_for_api(video):
    """Format a video object for API response"""
    return {
        'id': video['id'],
        'title': video['title'],
        'channel_name': video['channel_name'],
        'view_count': video['view_count'],
        'url': video['url'],
        'thumbnail': f"https://img.youtube.com/vi/{video['id']}/hqdefault.jpg",
        'confidence': round(video.get('like_probability', 0.5) * 100),
        'views_formatted': _format_view_count(video['view_count'])
    }

def _format_view_count(count):
    """Format view count for display"""
    if count >= 1000000:
        return f"{count/1000000:.1f}M views"
    elif count >= 1000:
        return f"{count/1000:.1f}K views"
    else:
        return f"{count} views"

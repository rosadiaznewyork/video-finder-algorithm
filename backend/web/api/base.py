from flask import Blueprint, jsonify

# Base API blueprint for common functionality
api_base_bp = Blueprint('api_base', __name__, url_prefix='/api')

@api_base_bp.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MyTube Video Recommendation API',
        'version': '1.0.0'
    })

@api_base_bp.errorhandler(404)
def api_not_found(error):
    """Handle 404 errors for API endpoints"""
    return jsonify({
        'success': False,
        'error': 'API endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@api_base_bp.errorhandler(500)
def api_internal_error(error):
    """Handle 500 errors for API endpoints"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

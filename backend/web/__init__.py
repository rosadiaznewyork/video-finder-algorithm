from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .config import config

def create_app(config_name=None):
    """Flask application factory"""
    load_dotenv()

    # Get configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app_config = config[config_name]

    # Configure Flask to serve Vue SPA directly from dist folder
    app = Flask(__name__,
                static_folder=app_config.get_frontend_path(),
                static_url_path='')
    CORS(app)

    # Load configuration
    app.config.from_object(app_config)

    # Register API blueprints
    from .api.base import api_base_bp
    from .api.videos import videos_api_bp

    app.register_blueprint(api_base_bp)
    app.register_blueprint(videos_api_bp)

    # Simple SPA routing - serve Vue app for all non-API routes
    from flask import send_from_directory, jsonify

    @app.route('/')
    @app.route('/<path:path>')
    def serve_spa(path=''):
        """Serve Vue SPA for all routes except API"""
        # API routes are handled by blueprints above
        try:
            return send_from_directory(app.static_folder, 'index.html')
        except FileNotFoundError:
            return jsonify({
                'error': 'Frontend not built',
                'message': 'Run "cd frontend && npm run build" to build the Vue application',
                'frontend_path': app.static_folder
            }), 404

    return app

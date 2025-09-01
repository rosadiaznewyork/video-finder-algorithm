"""
Web application configuration
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'video_inspiration.db')
    
    # Frontend settings
    FRONTEND_DIST_PATH = os.getenv('FRONTEND_DIST_PATH', 'frontend/dist')
    
    @classmethod
    def get_frontend_path(cls):
        """Get the absolute path to the frontend dist directory"""
        base_dir = Path(__file__).parent.parent.parent  # Go up to project root
        return str(base_dir / cls.FRONTEND_DIST_PATH)
    
    @classmethod
    def frontend_exists(cls):
        """Check if the frontend build exists"""
        frontend_path = Path(cls.get_frontend_path())
        return frontend_path.exists() and (frontend_path / 'index.html').exists()

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    def __init__(self):
        # Only check for SECRET_KEY when actually using production config
        if not os.getenv('SECRET_KEY'):
            raise ValueError("SECRET_KEY must be set in production")

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

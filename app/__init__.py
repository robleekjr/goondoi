"""
Goondoi Wetlands Application Factory
Professional Flask application with clean architecture
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os
from pathlib import Path

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name (str): Configuration name ('development', 'production', 'testing')
                          Defaults to environment variable or 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Determine configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin section.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # Ensure upload directories exist
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    (upload_folder / 'images').mkdir(parents=True, exist_ok=True)
    (upload_folder / 'media').mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register context processors
    register_context_processors(app)
    
    # Create database tables (only in development)
    if config_name == 'development':
        with app.app_context():
            db.create_all()
    
    return app

def register_blueprints(app):
    """Register application blueprints"""
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

def register_context_processors(app):
    """Register context processors for injecting data into templates"""
    from flask import request
    from app.services.story_service import StoryService
    from app.models.flora_fauna_settings import FloraFaunaTileSettings
    
    @app.context_processor
    def inject_sidebar_data():
        """Inject sidebar navigation data into all templates"""
        # Determine if sidebar should be shown
        # Hide sidebar on home page (/) and admin pages (/admin/*)
        show_sidebar = not (
            request.path == '/' or 
            request.path.startswith('/admin')
        )
        
        # Get stories for sidebar
        sidebar_stories = []
        current_story_id = None
        flora_fauna_tile_settings = None
        
        if show_sidebar:
            sidebar_stories = StoryService.get_all_stories()
            flora_fauna_tile_settings = FloraFaunaTileSettings.get_settings()
            # Extract story_id from URL if viewing a story
            if '/story/' in request.path:
                path_parts = request.path.split('/')
                if len(path_parts) > 2 and path_parts[1] == 'story':
                    current_story_id = path_parts[2]
        
        return {
            'show_sidebar': show_sidebar,
            'sidebar_stories': sidebar_stories,
            'current_story_id': current_story_id,
            'flora_fauna_tile_settings': flora_fauna_tile_settings
        } 
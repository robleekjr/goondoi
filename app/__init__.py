"""
Goondoi Wetlands Application Factory
Professional Flask application with clean architecture
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os
from pathlib import Path

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

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
    
    # Ensure upload directories exist
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    (upload_folder / 'images').mkdir(parents=True, exist_ok=True)
    (upload_folder / 'media').mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
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
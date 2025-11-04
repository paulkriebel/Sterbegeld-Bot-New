"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
import os


def create_app(config_name='default'):
    """
    Create and configure Flask application
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.api import chat_routes
    app.register_blueprint(chat_routes.bp)
    
    # Add index route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    return app

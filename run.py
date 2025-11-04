"""
Application Entry Point
Run with: python run.py
"""
from app import create_app
from app.utils.logger import setup_logging
import os

# Setup logging
log_level = os.getenv('LOG_LEVEL', 'DEBUG')
setup_logging(log_level)

# Create app with appropriate config
env = os.getenv('FLASK_ENV', 'development')
config_name = 'development' if env == 'development' else 'production'

app = create_app(config_name)

if __name__ == '__main__':
    # Development server
    print(f"\n🚀 Sterbegeld Bot starting on http://localhost:5000\n")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

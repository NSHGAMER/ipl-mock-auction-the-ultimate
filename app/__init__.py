from flask import Flask
from . import routes
import os

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        # For production (e.g., Render): Use GOOGLE_CREDENTIALS_JSON env var containing the actual JSON
        # For local development: Can use GSHEET_CREDENTIALS file path or credentials.json in app folder
        GSHEET_CREDENTIALS=os.environ.get('GSHEET_CREDENTIALS', 'credentials.json')
    )

    # Note: Credentials are now loaded from GOOGLE_CREDENTIALS_JSON env var in production,
    # or from a local credentials.json file for development.
    # This is handled in routes.py get_sheet() function.

    # Register blueprints or routes
    routes.init_app(app)

    # Make utility functions available in templates
    from .utils import format_currency
    @app.context_processor
    def utility_processor():
        return dict(format_currency=format_currency)

    return app

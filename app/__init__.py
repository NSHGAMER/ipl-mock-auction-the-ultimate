from flask import Flask
from . import routes
import os

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'),
        # Google Sheets credentials file path; placed inside the `app` package.
        # Can also be overridden via env var GSHEET_CREDENTIALS.
        GSHEET_CREDENTIALS="credentials.json"
    )

    # Allow overriding via environment variables
    app.config['GSHEET_CREDENTIALS'] = os.environ.get('GSHEET_CREDENTIALS', app.config['GSHEET_CREDENTIALS'])

    # Sanity-check for required config
    if not app.config['GSHEET_CREDENTIALS']:
        raise RuntimeError('GSHEET_CREDENTIALS must be set either in code or via env vars.')

    # Register blueprints or routes
    routes.init_app(app)

    # Make utility functions available in templates
    from .utils import format_currency
    @app.context_processor
    def utility_processor():
        return dict(format_currency=format_currency)

    return app

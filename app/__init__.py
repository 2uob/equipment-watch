from flask import Flask

from app.models.db import init_db
from app.routes.diagnostic import bp as diagnostic_bp

def create_app() -> Flask:
    """Build the Flask app and register routes."""
    init_db()
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(diagnostic_bp)
    return app
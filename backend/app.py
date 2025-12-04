"""
Main Flask application for Email Data Generation project.
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
import logging
from pathlib import Path

from backend.api.routes import api
from backend.scheduler import start_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# Register API blueprint
app.register_blueprint(api, url_prefix="/api")

# Start background scheduler (runs only in one worker due to file locking)
start_scheduler()

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent


@app.route("/")
def index():
    """Serve main dashboard."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/config")
def config():
    """Serve configuration page."""
    return send_from_directory(app.static_folder, "config.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


from flask import Flask
from flask_cors import CORS
from flask_session import Session
from authlib.integrations.flask_client import OAuth
import os


oauth = OAuth()
def create_app():
    # Initialize Flask app
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.getenv("SECRET_KEY", "lFqm4oNge6YDWfGi8gvDXWJSJkTXeaRrgxOey4k9zHg")
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_COOKIE_NAME"] = "oauth_session"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["SESSION_COOKIE_SECURE"] = False

    # Initialize extensions
    Session(app)
    CORS(app)
    oauth.init_app(app)

    # Import and register routes
    from src.app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Static files
    app.static_folder = "static"

    return app
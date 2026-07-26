"""Composition root: wire config, DB, routes and error handling."""
import logging

from flask import Flask
from flask_cors import CORS

from src.config import settings
from src.config.database import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import register_routes


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    init_db()
    register_routes(app)
    register_error_handlers(app)
    return app

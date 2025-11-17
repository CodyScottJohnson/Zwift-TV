import os

from dotenv import load_dotenv
from flask import Flask

from .extensions import cors, sock


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development").lower()
    if env == "production":
        from .config import ProductionConfig

        app.config.from_object(ProductionConfig)
    else:
        from .config import DevelopmentConfig

        app.config.from_object(DevelopmentConfig)

    # CORS: allow frontend origin for /api and /ws
    cors.init_app(
        app,
        resources={
            r"/api/*": {"origins": app.config["API_CORS_ORIGINS"]},
            r"/ws/*": {"origins": app.config["API_CORS_ORIGINS"]},
        },
    )

    # Register API routes
    from .api.v1 import v1_bp

    app.register_blueprint(v1_bp, url_prefix="/api/v1")

    # WebSockets
    sock.init_app(app)
    from .ws.connections import register_app_ws

    register_app_ws(sock)

    return app

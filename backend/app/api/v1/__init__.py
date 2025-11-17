from flask import Blueprint

v1_bp = Blueprint("api_v1", __name__)

# Import modules that attach routes to v1_bp
from . import health, users, tv  # noqa: E402,F401

from flask import jsonify

from . import v1_bp


@v1_bp.get("/health")
def health():
    return jsonify(status="ok")
